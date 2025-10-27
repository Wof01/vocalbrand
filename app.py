
from __future__ import annotations
# Note: Removed top-level docstring to avoid unintended rendering in UI

import streamlit as st
from error_handling import safe_execute, handle_error, RecordingError
import time
import numpy as np
from io import BytesIO
import wave
import streamlit.components.v1 as components
from datetime import datetime
import os
import logging
import queue
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union
from components.audio_recorder_pro import render_audio_recorder_pro

# Centralized supported audio formats for all upload widgets
ACCEPTED_AUDIO_EXTS: list[str] = [
    "wav", "mp3", "m4a", "aac", "ogg", "flac", "aiff", "webm"
]

def accepted_formats_display() -> str:
    return ", ".join(ext.upper() for ext in ACCEPTED_AUDIO_EXTS)


def _maybe_force_flow_progression() -> None:
    """Harden the flow so recording always advances beyond Step 1.

    If audio bytes exist in any staging key and flow_state is still 'initial',
    promote to 'processing' and rerun. This protects against rare cases where
    the 'Use This Recording' click didn't trigger Streamlit's event cycle but
    the audio is already available or recently captured.
    """
    try:
        ss = st.session_state
        if ss.get("flow_state", "initial") != "initial":
            return
        staged = ss.get("audio_data") or ss.get("pending_audio_bytes") or ss.get("pro_recorder_audio_preview")
        if not staged:
            return
        # Normalize: if only pending/pro_preview exist, promote to audio_data
        if not ss.get("audio_data"):
            if ss.get("pending_audio_bytes"):
                ss["audio_data"] = ss["pending_audio_bytes"]
                if not ss.get("audio_meta"):
                    ss["audio_meta"] = ss.get("pending_audio_meta") or {"source": "recorder"}
            elif ss.get("pro_recorder_audio_preview"):
                ss["audio_data"] = ss["pro_recorder_audio_preview"]
                if not ss.get("audio_meta"):
                    ss["audio_meta"] = {"source": "recorder", "filename": "recording.wav"}
        ss["flow_state"] = "processing"
        st.rerun()
    except Exception:
        # Never block UI if this helper fails
        pass

# Initialize session state defaults
SESSION_DEFAULTS = {
    # Cloning related
    "clone_history": [],  # List of voice clone attempts
    "clone_status": "",  # Last clone operation status
    "clone_timestamp": "",  # ISO timestamp of last clone
    "clone_voice_id": "",  # Active voice ID for generation
    "clone_voice_label": "",  # User-provided label for active voice
    
    # Recording preferences
    "trim_silence_toggle": False,  # If enabled, trim leading/trailing silence before cloning
    "auto_clone_toggle": False,  # If enabled, auto-clone immediately after recording lock-in
    "use_pro_recorder": True,  # Enable enhanced recorder with timer and waveform
    
    # Recording state
    "recording_start": None,  # When recording started
    "recording_duration": 0,  # Current recording duration
    "recording_locked_in": False,  # Whether recording is finalized
    "waveform_data": [],  # Store waveform visualization data
    "audio_level": 0,  # Current audio input level
    "recorder_initialized": False,  # Track recorder initialization
    
    # Audio data
    "audio_data": None,  # Current audio data
    "audio_source": None,  # Source of current audio (upload/record)
    "ready_to_proceed": False,  # Whether audio is ready for cloning
    "pending_audio_bytes": b"",  # Audio bytes waiting for processing
    "pending_audio_meta": None,  # Metadata for pending audio
    
    # Processing state
    "last_auto_clone_hash": "",  # To avoid double auto-clone on reruns
    "last_recorder_type": None,  # Track last used recorder type for state management
    "processing_complete": False  # Track whether processing is complete
}

def ensure_session_defaults():
    """Ensure all session state defaults are initialized."""
    for key, default in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default.copy() if isinstance(default, (list, dict)) else default
            
def handle_audio_data(audio_data: Union[bytes, BytesIO], source: str, filename: str = "recording.wav") -> None:
    """Process audio data and update session state."""
    if not audio_data:
        return
        
    if isinstance(audio_data, BytesIO):
        audio_bytes = audio_data.getvalue()
    else:
        audio_bytes = audio_data
        
    st.session_state.pending_audio_bytes = audio_bytes
    st.session_state.pending_audio_meta = {
        "ok": True,
        "filename": filename,
        "type": "audio/wav",
        "source": source
    }
    st.session_state.audio_data = audio_bytes
    st.session_state.audio_source = source
    st.session_state.ready_to_proceed = True

# Initialize session state
ensure_session_defaults()

def get_pending_recording_from_browser() -> Optional[bytes]:
    """
    Attempt to retrieve recorded audio from browser localStorage.
    
    The JavaScript component stores audio as base64 in localStorage when the user
    clicks "Use This Recording". This function creates JavaScript that will:
    1. Check for audio in localStorage
    2. Convert base64 to bytes
    3. Store in Streamlit session state
    4. Trigger a rerun with the audio data
    
    Returns:
        bytes: The audio data if available, None otherwise
    """
    # Inject JavaScript to check for and transfer audio from localStorage
    check_and_transfer_js = """
    <script>
    (function() {
        // Check if audio is in localStorage and ready to transfer
        const audioB64 = localStorage.getItem('vb_recorded_audio');
        const recordingStatus = localStorage.getItem('vb_recording_ready');
        
        if (audioB64 && recordingStatus === '1' && audioB64.length > 100) {
            // Extract base64 portion
            let base64Data = audioB64;
            if (audioB64.includes(',')) {
                base64Data = audioB64.split(',')[1];
            }
            
            // Store in window object for retrieval
            try {
                // Convert base64 to binary
                const binaryString = atob(base64Data);
                const len = binaryString.length;
                const bytes = new Uint8Array(len);
                for (let i = 0; i < len; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }
                
                // Store compressed info in window
                window.vb_audio_bytes_len = len;
                window.vb_audio_b64_ready = true;
                window.vb_audio_b64_data = base64Data;
                
                // Mark as transferred
                localStorage.setItem('vb_recording_ready', '2');
                
                console.log('✅ VocalBrand audio ready in window:', len, 'bytes');
            } catch (e) {
                console.error('Audio transfer error:', e);
            }
        }
    })();
    </script>
    """
    
    st.markdown(check_and_transfer_js, unsafe_allow_html=True)
    
    # Check session state for transferred audio
    if st.session_state.get("vb_audio_bytes_pending"):
        audio_bytes = st.session_state.vb_audio_bytes_pending
        st.session_state.vb_audio_bytes_pending = None
        return audio_bytes
    
    return None

def render_audio_capture_area() -> Optional[Union[bytes, st.runtime.uploaded_file_manager.UploadedFile]]:
    """Render world-class audio capture with pro recorder and elegant UI.
    
    CRITICAL FLOW FOR RECORDING AUDIO:
    1. User records audio in JavaScript component
    2. Clicks "Use This Recording" button
    3. JavaScript stores audio as base64 in localStorage
    4. JavaScript changes URL hash to trigger Streamlit reload
    5. On reload, Python injects JavaScript that reads localStorage
    6. JavaScript passes audio via query parameters back to Python
    7. Python retrieves audio from query params and returns it
    """
    ensure_session_defaults()
    
    # CRITICAL: Check if query parameter indicates audio is present in browser storage
    query_params = st.query_params
    if query_params.get("vb_audio_present") == "true":
        logging.info("🎯 Detected vb_audio_present=true in query params - AUDIO IS READY!")
        
        # IMMEDIATE EXTRACTION: Don't wait, extract it RIGHT NOW via JavaScript
        extract_audio_immediate_js = """
        <script>
        (function() {
            // Get audio from storage IMMEDIATELY
            const audioB64 = sessionStorage.getItem('vb_audio_b64') || 
                           localStorage.getItem('vb_recorded_audio') ||
                           window.vb_audio_data;
            
            console.log('🎤 IMMEDIATE EXTRACTION starting...');
            console.log('Audio found:', !!audioB64);
            
            if (audioB64 && audioB64.length > 100 && !window.vb_already_transferred) {
                window.vb_already_transferred = true;
                
                console.log('📤 EXTRACTING audio to URL NOW!');
                
                try {
                    // Extract base64 part
                    let base64Data = audioB64;
                    if (audioB64.includes(',')) {
                        base64Data = audioB64.split(',')[1];
                    }
                    
                    // Calculate size
                    let audioBytes = 0;
                    try {
                        audioBytes = atob(base64Data).length;
                    } catch (e) {
                        console.error('Size calc error:', e);
                    }
                    
                    console.log('✅ Audio size:', audioBytes, 'bytes');
                    
                    // Update URL with audio
                    const url = new URL(window.location);
                    url.searchParams.set('vb_audio_b64', base64Data);
                    url.searchParams.set('vb_audio_bytes', audioBytes);
                    url.searchParams.delete('vb_audio_present');  // Remove the marker
                    
                    console.log('🔄 Updating URL and reloading...');
                    window.location.href = url.toString();
                    
                } catch (e) {
                    console.error('❌ Extraction error:', e);
                }
            } else {
                console.log('⚠️ No audio found in storage!');
            }
        })();
        </script>
        """
        st.markdown(extract_audio_immediate_js, unsafe_allow_html=True)
        
        # Don't continue - let the JavaScript reload the page with audio data
        return None
    
    # Also check if audio came via URL parameters
    if "vb_audio_b64" in query_params:
        try:
            audio_b64 = query_params.get("vb_audio_b64", "")
            audio_bytes_str = query_params.get("vb_audio_bytes", "0")
            
            if audio_b64 and len(audio_b64) > 100:
                logging.info(f"✅ Retrieved audio from URL params: {audio_bytes_str} bytes")
                
                # Decode the base64 to bytes
                import base64 as b64_module
                try:
                    audio_bytes = b64_module.b64decode(audio_b64)
                    logging.info(f"✅ Successfully decoded audio: {len(audio_bytes)} bytes")
                    
                    # Clear query params
                    st.query_params.clear()
                    
                    # Clean up storage
                    cleanup = """
                    <script>
                    localStorage.removeItem('vb_recorded_audio');
                    localStorage.removeItem('vb_recording_ready');
                    sessionStorage.removeItem('vb_audio_b64');
                    sessionStorage.removeItem('vb_audio_ready');
                    console.log('✅ Cleaned up audio storage');
                    </script>
                    """
                    st.markdown(cleanup, unsafe_allow_html=True)
                    
                    return audio_bytes
                except Exception as e:
                    logging.error(f"Error decoding audio: {e}")
        except Exception as e:
            logging.error(f"Error retrieving audio from params: {e}")
    
    try:
        
        # World-class styling for recording interface
        st.markdown("""
            <style>
            .recorder-header-section {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2);
                color: white;
            }
            .recorder-title {
                font-size: 28px;
                font-weight: 800;
                margin-bottom: 8px;
                letter-spacing: -0.5px;
            }
            .recorder-subtitle {
                font-size: 15px;
                opacity: 0.95;
                font-weight: 500;
            }
            .recorder-container {
                background: #f8fafc;
                padding: 25px;
                border-radius: 12px;
                border: 2px solid #e2e8f0;
                margin: 20px 0;
                transition: all 0.3s ease;
            }
            .upload-zone {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                padding: 30px;
                border-radius: 12px;
                border: 2px dashed #667eea;
                text-align: center;
                margin: 20px 0;
                transition: all 0.3s ease;
            }
            .upload-zone:hover {
                border-color: #764ba2;
                background: linear-gradient(135deg, #eef2f8 0%, #bfd4e3 100%);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.1);
            }
            .divider {
                height: 2px;
                background: linear-gradient(90deg, transparent, #cbd5e0, transparent);
                margin: 30px 0;
                border-radius: 1px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Only show recorder if no audio is captured yet
        if not st.session_state.get("audio_data"):
            # Professional header
            st.markdown("""
                <div class="recorder-header-section">
                    <div class="recorder-title">🎙️ Voice Recording</div>
                    <div class="recorder-subtitle">Record a sample of your voice or upload an audio file (30-60 seconds)</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Pro Recorder Component with world-class styling
            st.markdown('<div class="recorder-container">', unsafe_allow_html=True)
            try:
                from components.audio_recorder_pro import render_audio_recorder_pro
                
                # Create a callback function that will be triggered when JavaScript clicks the hidden button
                def process_recorded_audio():
                    """Callback triggered by JavaScript when audio is ready"""
                    st.session_state.vb_audio_processing_triggered = True
                
                # Add a hidden Streamlit button that JavaScript will trigger
                # This button has a callback that will set session state
                hidden_button_html = """
                <div style="display: none;">
                    <button id="vb_trigger_audio_processing" type="button" onclick="
                        (function() {
                            console.log('🎯 Audio processing triggered by JavaScript');
                            // Signal that we're processing
                            window.vb_processing_started = true;
                        })();
                    ">Process Audio</button>
                </div>
                """
                st.markdown(hidden_button_html, unsafe_allow_html=True)
                
                # Add JavaScript that will read the stored audio and make it available
                extract_audio_js = """
                <script>
                (function() {
                    // Check if audio is in storage
                    const audioB64 = sessionStorage.getItem('vb_audio_b64') || 
                                    localStorage.getItem('vb_recorded_audio') ||
                                    window.vb_audio_data;
                    
                    if (audioB64 && audioB64.length > 100) {
                        console.log('🎤 Audio found, preparing for Python...');
                        
                        // Try to decode and validate
                        try {
                            let base64Part = audioB64;
                            if (audioB64.includes(',')) {
                                base64Part = audioB64.split(',')[1];
                            }
                            
                            // Convert to binary to check size
                            const binaryString = atob(base64Part);
                            const audioSize = binaryString.length;
                            
                            console.log('✅ Audio valid:', audioSize, 'bytes');
                            
                            // Store the size info in sessionStorage for Python to detect
                            sessionStorage.setItem('vb_audio_size_bytes', audioSize);
                            sessionStorage.setItem('vb_audio_status', 'ready_for_python');
                            
                            // Mark that we're ready
                            window.vb_audio_size_bytes = audioSize;
                            window.vb_audio_for_python = base64Part;
                            
                        } catch (e) {
                            console.error('Audio validation error:', e);
                        }
                    }
                })();
                </script>
                """
                st.markdown(extract_audio_js, unsafe_allow_html=True)
                
                # Render the pro recorder
                audio_data = render_audio_recorder_pro()
                
                # If recorder returned audio directly, use it
                if audio_data:
                    logging.info("✅ Audio returned directly from recorder")
                    return audio_data
                

                # Check for localStorage audio via JavaScript injection
                # This will be called on every page reload to check for pending recordings
                retrieve_audio_script = """
                <script>
                (function() {
                    // Check if audio is waiting in localStorage
                    const audioB64 = localStorage.getItem('vb_recorded_audio');
                    const timestamp = localStorage.getItem('vb_recording_timestamp');
                    const status = localStorage.getItem('vb_recording_ready');
                    
                    if (audioB64 && status === '1' && audioB64.length > 100) {
                        console.log('Found recorded audio in localStorage, status:', status);
                        
                        // Mark as being processed so we don't reprocess
                        localStorage.setItem('vb_recording_ready', '2');
                        
                        // Store in window for potential access
                        window.vb_audio_pending = audioB64;
                        window.vb_recording_timestamp = timestamp;
                        
                        // Try to find and interact with Streamlit's internal state
                        // This is a bit hacky but necessary since components.html() is stateless
                        if (window.parent && window.parent.parent) {
                            try {
                                // Signal through postMessage to parent that we have audio
                                window.parent.postMessage({
                                    type: 'vb_audio_ready',
                                    data: audioB64.substring(0, 50) + '...'
                                }, '*');
                            } catch (e) {
                                console.log('PostMessage failed:', e);
                            }
                        }
                    }
                })();
                </script>
                """
                
                st.markdown(retrieve_audio_script, unsafe_allow_html=True)
                
                # CRITICAL: Add JavaScript that transfers audio from localStorage to URL query params
                # This is the "bridge" that allows JavaScript to pass data back to Python
                transfer_audio_to_url_js = """
                <script>
                (function() {
                    // Only run once per session
                    if (window.vb_audio_bridge_installed) return;
                    window.vb_audio_bridge_installed = true;
                    
                    // Check if we have audio ready in localStorage after a reload
                    const audioB64 = localStorage.getItem('vb_recorded_audio');
                    const recordingStatus = localStorage.getItem('vb_recording_ready');
                    const recordingTs = localStorage.getItem('vb_recording_timestamp');
                    
                    if (audioB64 && (recordingStatus === '1' || recordingStatus === '2') && audioB64.length > 100) {
                        console.log('🎤 Found audio in localStorage after reload, transferring to URL...');
                        
                        try {
                            // Extract base64 data
                            let base64Data = audioB64;
                            if (audioB64.includes(',')) {
                                base64Data = audioB64.split(',')[1];
                            }
                            
                            const audioLen = base64Data.length;
                            
                            // Create URL with audio data as query parameters
                            // We use URL.searchParams to properly encode the data
                            const url = new URL(window.location);
                            url.searchParams.set('vb_audio_len', audioLen);
                            url.searchParams.set('vb_audio_b64', base64Data);
                            
                            console.log('📤 Transferring', audioLen, 'bytes via URL');
                            
                            // Replace history and navigate to new URL with audio data
                            window.history.replaceState({}, '', url);
                            
                            // Trigger Streamlit rerun by modifying the URL
                            // The rerun will cause Streamlit to reload and Python will read the query params
                            setTimeout(() => {
                                // After setting the URL, trigger a full reload so Streamlit picks it up
                                window.location.reload();
                            }, 100);
                            
                        } catch (e) {
                            console.error('Audio transfer failed:', e);
                        }
                    }
                })();
                </script>
                """
                st.markdown(transfer_audio_to_url_js, unsafe_allow_html=True)
                
            except Exception as e:
                logging.error(f"Pro recorder error: {str(e)}")
                st.error("⚠️ Pro recorder temporarily unavailable")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Elegant divider
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            # File upload alternative with world-class styling
            st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
            st.markdown("#### 📎 Or Upload Audio File")
            st.markdown(f"*Drag and drop an audio file ({accepted_formats_display()}) or click to browse*")
            uploaded_file = st.file_uploader(
                f"Upload Audio ({accepted_formats_display()})",
                type=ACCEPTED_AUDIO_EXTS,
                key="audio_file_uploader",
                label_visibility="collapsed",
                help=f"Supported formats: {accepted_formats_display()} • Max 200MB"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            if uploaded_file:
                return uploaded_file
            
            # CRITICAL: Check if we need to process a recorded audio from localStorage
            # This happens when JavaScript has stored audio and the page reloaded
            process_localStorage_audio = """
            <script>
            (function() {
                const audioB64 = localStorage.getItem('vb_recorded_audio');
                const status = localStorage.getItem('vb_recording_ready');
                
                if (audioB64 && (status === '1' || status === '2') && !window.vb_audio_processed) {
                    window.vb_audio_processed = true;
                    console.log('Processing localStorage audio...');
                    
                    // Convert base64 to blob
                    try {
                        let base64Data = audioB64;
                        if (audioB64.includes(',')) {
                            base64Data = audioB64.split(',')[1];
                        }
                        
                        const binaryString = atob(base64Data);
                        const bytes = new Uint8Array(binaryString.length);
                        for (let i = 0; i < binaryString.length; i++) {
                            bytes[i] = binaryString.charCodeAt(i);
                        }
                        
                        const audioBlob = new Blob([bytes], { type: 'audio/wav' });
                        const audioUrl = URL.createObjectURL(audioBlob);
                        
                        // Store in window for Python to access if possible
                        window.vb_audio_blob_data = audioBlob;
                        window.vb_audio_ready_for_python = true;
                        window.vb_audio_url = audioUrl;
                        
                        console.log('Audio blob created:', audioBlob.size, 'bytes');
                        
                        // Force a rerun by clicking on the file uploader or by changing URL
                        // Try to trigger Streamlit rerun
                        const inputs = document.querySelectorAll('input[type="file"]');
                        console.log('Found', inputs.length, 'file inputs');
                        
                    } catch (e) {
                        console.error('Audio processing error:', e);
                    }
                }
            })();
            </script>
            """
            st.markdown(process_localStorage_audio, unsafe_allow_html=True)
            
            # Tips with collapsible section
            with st.expander("💡 **Tips for Best Results**", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""
                    **Browser Tips:**
                    - Chrome or Edge recommended
                    - Allow microphone permissions
                    - Refresh if issues occur
                    """)
                with col2:
                    st.markdown("""
                    **Recording Tips:**
                    - Quiet environment
                    - Clear, natural speech
                    - 30-60 seconds duration
                    - Check preview before proceed
                    """)
            
            # CRITICAL: Attempt to retrieve recording from localStorage via direct injection
            retrieve_and_process_audio = """
            <script>
            (function() {
                // Try to retrieve the recorded audio from localStorage
                const audioB64 = localStorage.getItem('vb_recorded_audio');
                const recordingStatus = localStorage.getItem('vb_recording_ready');
                const recordingTs = localStorage.getItem('vb_recording_timestamp');
                
                // Only process if we haven't already processed it
                if (audioB64 && audioB64.length > 100 && recordingStatus === '1' && !window.vb_final_transfer_done) {
                    window.vb_final_transfer_done = true;
                    console.log('🎤 Recording detected in localStorage! Status:', recordingStatus);
                    
                    // Extract base64 data
                    let base64Data = audioB64;
                    if (audioB64.includes(',')) {
                        base64Data = audioB64.split(',')[1];
                    }
                    
                    // Store in window for any potential bridge
                    window.vb_audio_ready_to_process = true;
                    window.vb_audio_b64 = base64Data;
                    
                    // Mark as having processed
                    localStorage.setItem('vb_recording_ready', '2');
                    localStorage.setItem('vb_audio_processed_at', new Date().toISOString());
                    
                    console.log('✅ Audio prepared for Streamlit processing');
                    
                    // Try to trigger a Streamlit state update by modifying URL hash
                    if (window.location.hash.indexOf('vb_rec_') === -1) {
                        window.location.hash = '#vb_rec_processing_' + Date.now();
                    }
                }
            })();
            </script>
            """
            st.markdown(retrieve_and_process_audio, unsafe_allow_html=True)
            
            # ULTIMATE CRITICAL: Try to retrieve audio from sessionStorage and convert to bytes
            # This is the final attempt to get the audio from JavaScript storage
            try_retrieve_audio_python_js = """
            <script>
            (function() {
                // Get audio from storage
                const audioB64 = sessionStorage.getItem('vb_audio_b64') || 
                               localStorage.getItem('vb_recorded_audio') ||
                               window.vb_audio_data;
                
                if (audioB64 && audioB64.length > 100 && !window.vb_python_retrieve_attempted) {
                    window.vb_python_retrieve_attempted = true;
                    
                    console.log('🎯 FINAL RETRIEVAL: Found audio in storage');
                    console.log('🎯 Audio size:', audioB64.length);
                    console.log('🎯 Ready to transfer to Python');
                    
                    // Mark in window that we have audio ready
                    window.vb_audio_definitely_ready = true;
                    
                    // Store both the b64 and size
                    window.vb_audio_for_python_b64 = audioB64;
                    
                    // Try to compute size
                    try {
                        let base64Part = audioB64;
                        if (audioB64.includes(',')) {
                            base64Part = audioB64.split(',')[1];
                        }
                        window.vb_audio_size = atob(base64Part).length;
                        console.log('🎯 Audio decoded, size:', window.vb_audio_size, 'bytes');
                    } catch (e) {
                        console.log('Size calculation error:', e);
                    }
                }
            })();
            </script>
            """
            st.markdown(try_retrieve_audio_python_js, unsafe_allow_html=True)
            
            # NOW: The key step - Check if we have audio pending in JavaScript
            # We'll attempt to retrieve it by injecting code that puts it in a format Python can access
            # Since JavaScript window objects are accessible to subsequent code, we inject a retrieval script
            
            # **DIRECT RETRIEVAL ATTEMPT**: Use a Streamlit markdown to inject a retrieval script
            # that will run and potentially store data in a way Python can detect via re-renders
            direct_retrieval_final = """
            <script>
            (function() {
                // Final attempt: Store audio in base64 format in a hidden element's attribute
                const audioB64 = sessionStorage.getItem('vb_audio_b64') || 
                               localStorage.getItem('vb_recorded_audio') ||
                               window.vb_audio_data;
                
                if (audioB64 && audioB64.length > 100) {
                    // Create hidden element with audio data
                    let container = document.getElementById('vb_python_audio_container');
                    if (!container) {
                        container = document.createElement('div');
                        container.id = 'vb_python_audio_container';
                        container.style.display = 'none';
                        document.body.appendChild(container);
                    }
                    
                    // Store the base64 in the element's innerHTML encoded as a comment
                    container.setAttribute('data-audio-exists', 'true');
                    container.setAttribute('data-audio-b64-len', audioB64.length);
                    
                    // Store in text content (carefully to avoid memory issues with huge strings)
                    if (audioB64.length < 5000000) { // Less than 5MB
                        container.textContent = audioB64.substring(0, 100) + '...';
                        container.setAttribute('data-audio-complete', 'true');
                    }
                    
                    console.log('✅ Audio stored in container element');
                }
            })();
            </script>
            """
            st.markdown(direct_retrieval_final, unsafe_allow_html=True)
            
            # HERE: Python attempts to retrieve the audio by checking for the marker
            # We check sessionStorage via JavaScript injection that sets a Python-readable value
            final_python_check_js = """
            <script>
            (function() {
                // This script will set a marker that Python can detect on the next rerun
                if (sessionStorage.getItem('vb_audio_ready') === 'true' || 
                    localStorage.getItem('vb_recording_ready') === '1') {
                    
                    // Signal that audio is definitely available
                    window.vb_signal_audio_available = true;
                    
                    // If we get here, reload the page with a query param
                    if (!window.location.search.includes('vb_audio_present')) {
                        const url = new URL(window.location);
                        url.searchParams.set('vb_audio_present', 'true');
                        window.history.replaceState({}, '', url);
                        
                        // Trigger a page reload so Streamlit detects the parameter
                        console.log('🔄 Reloading with audio presence marker...');
                        window.location.reload();
                    }
                }
            })();
            </script>
            """
            st.markdown(final_python_check_js, unsafe_allow_html=True)
        
        return None
            
    except Exception as e:
        logging.error(f"Audio capture error: {str(e)}")
        st.error(f"❌ Audio capture error: {str(e)}")
        return None
        
        st.markdown("""
            <div class="recorder-section">
                <h4 style='margin-bottom: 1rem;'>🎙️ Record a Voice Sample</h4>
                <div class="instructions-box">
                    <div class="instruction-step">
                        <span class="step-number">1</span> Click the microphone button to start recording
                    </div>
                    <div class="instruction-step">
                        <span class="step-number">2</span> Speak clearly for 30-60 seconds
                    </div>
                    <div class="instruction-step">
                        <span class="step-number">3</span> Watch the timer and waveform as you speak
                    </div>
                    <div class="instruction-step">
                        <span class="step-number">4</span> Click the stop button when finished
                    </div>
                </div>
                <style>
                    .instructions-box {
                        background: #f8fafc;
                        border: 1px solid #e2e8f0;
                        border-radius: 8px;
                        padding: 1rem;
                        margin: 1rem 0;
                    }
                    .instruction-step {
                        display: flex;
                        align-items: center;
                        margin: 0.5rem 0;
                        font-size: 0.95rem;
                        color: #1a365d;
                    }
                    .step-number {
                        background: #3182ce;
                        color: white;
                        width: 24px;
                        height: 24px;
                        border-radius: 12px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 0.75rem;
                        font-weight: bold;
                        font-size: 0.85rem;
                    }
                </style>
                <div class="recording-info">
                    <div class="timer-display">⏱️ Recording Time: <span id="timer">00:00</span></div>
                    <div class="recording-status" id="recordingStatus"></div>
                </div>
                <div class="waveform-container" id="waveformContainer">
                    <canvas id="waveformCanvas"></canvas>
                </div>
            </div>
            <style>
                .recording-info {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin: 1rem 0;
                    padding: 0.5rem;
                    background: #f8fafc;
                    border-radius: 8px;
                    border: 1px solid #e2e8f0;
                }
                .timer-display {
                    font-family: monospace;
                    font-size: 1.2rem;
                    font-weight: bold;
                    color: #1a365d;
                }
                .waveform-container {
                    width: 100%;
                    height: 100px;
                    background: #fff;
                    border: 2px solid #3182ce;
                    border-radius: 8px;
                    overflow: hidden;
                    margin: 1rem 0;
                    position: relative;
                }
                #waveformCanvas {
                    width: 100%;
                    height: 100%;
                }
                .recording-active {
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.5; }
                    100% { opacity: 1; }
                }
            </style>
        """, unsafe_allow_html=True)
        
    try:
        from components.audio_recorder_pro import render_audio_recorder_pro
        
        # Display browser compatibility notice
        st.info("""💡 **Browser Compatibility:**
        - Works best in Chrome, Edge, or Firefox
        - Make sure your microphone is connected and permissions are allowed
        - If the timer or waveform don't appear, try refreshing the page""")
        
        # Call the recorder component
        render_audio_recorder_pro()
        
        st.markdown("""
            <script>
            let startTime = null;
            let animationFrame = null;
            let audioContext = null;
            let analyser = null;
                let microphone = null;
                
                function updateTimer() {
                    if (!startTime) return;
                    const now = Date.now();
                    const elapsed = Math.floor((now - startTime) / 1000);
                    const minutes = Math.floor(elapsed / 60);
                    const seconds = elapsed % 60;
                    document.getElementById('timer').textContent = 
                        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                }
                
                function drawWaveform(stream) {
                    if (!audioContext) {
                        audioContext = new (window.AudioContext || window.webkitAudioContext)();
                        analyser = audioContext.createAnalyser();
                        microphone = audioContext.createMediaStreamSource(stream);
                        microphone.connect(analyser);
                    }
                    
                    const canvas = document.getElementById('waveformCanvas');
                    const ctx = canvas.getContext('2d');
                    const dataArray = new Uint8Array(analyser.frequencyBinCount);
                    
                    function draw() {
                        animationFrame = requestAnimationFrame(draw);
                        analyser.getByteTimeDomainData(dataArray);
                        
                        ctx.fillStyle = '#ffffff';
                        ctx.fillRect(0, 0, canvas.width, canvas.height);
                        
                        ctx.lineWidth = 2;
                        ctx.strokeStyle = '#3182ce';
                        ctx.beginPath();
                        
                        const sliceWidth = canvas.width / dataArray.length;
                        let x = 0;
                        
                        for (let i = 0; i < dataArray.length; i++) {
                            const v = dataArray[i] / 128.0;
                            const y = v * canvas.height / 2;
                            
                            if (i === 0) ctx.moveTo(x, y);
                            else ctx.lineTo(x, y);
                            
                            x += sliceWidth;
                        }
                        
                        ctx.lineTo(canvas.width, canvas.height / 2);
                        ctx.stroke();
                        updateTimer();
                    }
                    
                    draw();
                }
                
                // Initialize recording handlers
                document.addEventListener('DOMContentLoaded', function() {
                    const recordButton = document.querySelector('.stAudioRecorder button');
                    if (recordButton) {
                        recordButton.addEventListener('click', async function() {
                            if (!startTime) {
                                startTime = Date.now();
                                document.getElementById('recordingStatus').textContent = '🔴 Recording...';
                                document.getElementById('recordingStatus').classList.add('recording-active');
                                
                                try {
                                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                                    drawWaveform(stream);
                                } catch (err) {
                                    console.error('Microphone access error:', err);
                                }
                            } else {
                                startTime = null;
                                document.getElementById('recordingStatus').textContent = '';
                                document.getElementById('recordingStatus').classList.remove('recording-active');
                                if (animationFrame) {
                                    cancelAnimationFrame(animationFrame);
                                    animationFrame = null;
                                }
                                if (audioContext) {
                                    audioContext.close();
                                    audioContext = null;
                                    analyser = null;
                                    microphone = null;
                                }
                            }
                        });
                    }
                });
                </script>
            """, unsafe_allow_html=True)
        
        # Enhanced recorder styling with timer and waveform
        st.markdown("""
            <style>
                .recorder-wrapper {
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                        border: 1px solid #dee2e6;
                        margin: 10px 0;
                        position: relative;
                        min-height: 200px;
                    }
                    .timer-display {
                        font-family: monospace;
                        font-size: 24px;
                        font-weight: bold;
                        padding: 10px;
                        background: white;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        display: inline-block;
                        margin-bottom: 10px;
                        font-size: 1.5em;
                        color: #FF4B4B;
                        text-align: center;
                        margin: 10px 0;
                        padding: 5px;
                        background: #fff;
                        border-radius: 5px;
                        border: 1px solid #dee2e6;
                    }
                    .waveform-container {
                        height: 120px;
                        background: #fff;
                        border-radius: 8px;
                        border: 2px solid #3182CE;
                        margin: 15px 0;
                        overflow: hidden;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        padding: 10px;
                        position: relative;
                    }
                    .waveform-container::before {
                        content: "Waveform";
                        position: absolute;
                        top: -10px;
                        left: 10px;
                        background: white;
                        padding: 0 8px;
                        font-size: 12px;
                        color: #3182CE;
                    }
                    .recording-indicator {
                        color: #FF4B4B;
                        animation: blink 1s infinite;
                    }
                    @keyframes blink {
                        50% { opacity: 0; }
                    }
                </style>
            """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="recorder-wrapper">', unsafe_allow_html=True)
            
            # Timer display
            timer_col, status_col = st.columns([1, 2])
            with timer_col:
                    if st.session_state.recording_start:
                        current_time = time.time()
                        duration = current_time - st.session_state.recording_start
                        st.markdown(f"""
                            <div class="timer-display">
                                {format_time(duration)} <span class="recording-indicator">●</span>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="timer-display">
                            00:00
                        </div>
                    """, unsafe_allow_html=True)
            
            with status_col:
                if st.session_state.recording_start:
                    st.info("🎙️ Recording in progress...")
                else:
                    st.info("Click to start recording")
                
                # Pro Recorder features
                if use_pro_recorder:
                    # Waveform visualization
                    st.markdown('<div class="waveform-container">', unsafe_allow_html=True)
                    if st.session_state.waveform_data:
                        chart_data = pd.DataFrame({"amplitude": st.session_state.waveform_data})
                        st.line_chart(chart_data, height=100)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Audio recorder component
                try:
                    audio = audio_recorder(
                        pause_threshold=60.0,
                        recording_color="#FF4B4B",
                        neutral_color="#6c757d",
                        icon_name="microphone",
                        icon_size="2x",
                        key=f"audio_recorder_{'pro' if use_pro_recorder else 'basic'}"
                    )
                    
                    if audio:
                        # Update recording state
                        if not st.session_state.recording_start:
                            st.session_state.recording_start = time.time()
                            st.session_state.waveform_data = []
                        
                        # Process audio for waveform if in Pro mode
                        if use_pro_recorder and isinstance(audio, bytes):
                            try:
                                with wave.open(BytesIO(audio)) as wav:
                                    frames = wav.readframes(wav.getnframes())
                                    audio_data = np.frombuffer(frames, dtype=np.int16)
                                    # Downsample for visualization
                                    st.session_state.waveform_data = audio_data[::100].tolist()
                            except Exception as e:
                                logger.warning(f"Waveform processing error: {str(e)}")

                        # Process the recording
                        st.success("✅ Recording successful!")
                        st.audio(audio, format="audio/wav")
                        
                        # Update session state
                        st.session_state.audio_data = audio
                        st.session_state.audio_source = "recorder"
                        st.session_state.ready_to_proceed = True
                        st.session_state.recording_duration = time.time() - st.session_state.recording_start
                        st.session_state.recording_start = None
                        
                        return audio
                except Exception as e:
                    st.error(f"Recording section error: {str(e)}")
                    return None
    except Exception as e:
        st.error(f"Recorder section error: {str(e)}")
        return None
    finally:
        st.markdown('</div>', unsafe_allow_html=True)


@safe_execute(show_details=True)
def render_upload_section():
    """Render the file upload section with drag & drop support."""
    try:
        # Set up styles first
        # Add styling
        style_html = """
            <style>
                .uploadArea {
                    border: 2px dashed #0066CC;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    background: #f8f9fa;
                    margin: 10px 0;
                }
                .upload-text {
                    color: #666;
                    font-size: 0.9em;
                    margin: 10px 0;
                }
            </style>
        """
        st.markdown(style_html, unsafe_allow_html=True)

        # Create upload section
        try:
            st.markdown("""
                <div class="upload-section">
                    <h4 style='margin-bottom: 1rem;'>📁 Upload Audio File</h4>
                    <p class="instruction-text">Or upload an existing audio file</p>
                </div>
                <div class="uploadArea">
                    <p><strong>Drop your audio file here</strong></p>
                    <p class="upload-text">Supported: WAV, MP3, M4A (max 200MB)</p>
                </div>
            """, unsafe_allow_html=True)

            # Add file uploader
            uploaded_file = st.file_uploader(
                f"Choose an audio file ({accepted_formats_display()})",
                type=ACCEPTED_AUDIO_EXTS,
                help=f"Supported: {accepted_formats_display()} — Max 200MB",
                key="audio_upload"
            )

            # Handle uploaded file
            if uploaded_file:
                st.success("✅ File uploaded successfully!")
                st.audio(uploaded_file, format="audio/wav")
                st.session_state.audio_data = uploaded_file
                st.session_state.audio_source = "upload"
                st.session_state.ready_to_proceed = True
                return uploaded_file

            return None

        except Exception as e:
            st.error(f"Upload failed: {str(e)}")
            return None

        finally:
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("""
                <div>
                    <p class="upload-text">Supported: WAV, MP3, M4A (max 200MB)</p>
                </div>
            """, unsafe_allow_html=True)

        # File uploader
        uploaded_file = st.file_uploader(
            f"Choose an audio file ({accepted_formats_display()})",
            type=ACCEPTED_AUDIO_EXTS,
            help=f"Supported: {accepted_formats_display()} — Max 200MB",
            key="audio_upload"
        )

        if uploaded_file:
            st.success("✅ File uploaded successfully!")
            st.audio(uploaded_file, format="audio/wav")
            st.session_state.audio_data = uploaded_file
            st.session_state.audio_source = "upload"
            st.session_state.ready_to_proceed = True
            return uploaded_file
        
        return None

    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None
    finally:
        st.markdown('</div>', unsafe_allow_html=True)

def render_upload_area():
    try:
        # Enhanced upload area styling
        st.markdown("""
            <style>
                .uploadArea {
                    border: 2px dashed #0066CC;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    background: #f8f9fa;
                    margin: 10px 0;
                }
                .upload-text {
                    color: #666;
                    font-size: 0.9em;
                    margin: 10px 0;
                }
            </style>
            <div class="uploadArea">
                <p><strong>Drop your audio file here</strong></p>
                <p class="upload-text">Supported: WAV, MP3, M4A (max 200MB)</p>
            </div>
        """, unsafe_allow_html=True)
    
        uploaded_file = st.file_uploader(
            f"Choose an audio file ({accepted_formats_display()})",
            type=ACCEPTED_AUDIO_EXTS,
            help=f"Supported: {accepted_formats_display()} — Max 200MB",
            key="audio_upload"
        )
        
        if uploaded_file:
            st.success("✅ File uploaded successfully!")
            st.audio(uploaded_file, format="audio/wav")
            # Update session state
            st.session_state.audio_data = uploaded_file
            st.session_state.audio_source = "upload"
            st.session_state.ready_to_proceed = True
            return uploaded_file
        return None
    except Exception as e:
        st.error(f"Upload failed: {str(e)}")
        return None
    finally:
        st.markdown('</div>', unsafe_allow_html=True)

# Main layout with two columns
@safe_execute(show_details=True)
def render_main_layout():
    try:
        col1, col2 = st.columns(2)
        
        with col1:
            audio_data = render_audio_capture_area()
            
        with col2:
            upload_data = render_upload_section()
        
        # Store the result in session state
        if audio_data or upload_data:
            st.session_state.audio_data = audio_data or upload_data
    except Exception as e:
        st.error(f"Error in main layout: {str(e)}")
        return None
    
    # Help text and instructions
    st.markdown("---")
    
    # Show appropriate message based on state
    if st.session_state.ready_to_proceed:
        st.success("✅ Audio ready! You can proceed with voice cloning.")
    else:
        st.info("""
            💡 **Tips for best results:**
            - Record in a quiet environment
            - Speak clearly and naturally
            - Keep the microphone at a consistent distance
            - Aim for 30-60 seconds of audio
        """)
    
    return st.session_state.audio_data if st.session_state.ready_to_proceed else None

import base64
import hashlib
import json
import logging
import os
import queue
import shutil
import sys
import threading
import time
import subprocess
import platform
from dataclasses import dataclass, field
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

from error_handling import (
    VocalBrandError, AudioProcessingError, RecordingError, CloneGenerationError,
    safe_execute, handle_error, ERROR_MESSAGES
)




def inject_css_overrides():
    """COSMIC FIX: Nuclear CSS override to eliminate ALL white artifacts, ensure button text visibility, and fix upgrade banner."""
    st.markdown('''
    <style>
    /* ========================================
       NUCLEAR OPTION: Force transparent backgrounds on EVERY element
       ======================================== */
    * {
        background: transparent !important;
        background-color: transparent !important;
    }
    
    /* ========================================
       STREAMLIT COMPONENT TARGETING - Eliminate white artifacts
       ======================================== */
    .stApp, 
    .main .block-container,
    .stVerticalBlock > div,
    .stHorizontalBlock > div,
    .element-container,
    .row-widget,
    .stButton > button,
    .stDownloadButton > button,
    .stFileUploader > div,
    section[data-testid],
    div[data-testid],
    .st-emotion-cache-*,
    [class*="st-emotion-cache-"],
    .stAlert,
    .stExpander,
    .stContainer,
    div[data-testid="stVerticalBlock"] > div, 
    div[data-testid="stHorizontalBlock"] > div,
    div[data-testid="element-container"] > div,
    div.element-container,
    div.row-widget,
    div.stButton,
    div.stDownloadButton,
    div.stFileUploader,
    div.block-container,
    span[class^="st-emotion-cache-"],
    span[class*=" st-emotion-cache-"],
    div.uploadInstructions {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
    }
    
    /* Specific problematic emotion cache elements */
    .st-emotion-cache-zg1hna,
    .st-emotion-cache-1okhd5l,
    .st-emotion-cache-1fttcpj,
    .st-emotion-cache-7ym5gk,
    .st-emotion-cache-16idsys,
    .st-emotion-cache-ocqp1h,
    .st-emotion-cache-1430ypo,
    .st-emotion-cache-ue6h4q,
    .st-emotion-cache-j5r0tf {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* ========================================
       UPGRADE BANNER VISIBILITY - CRITICAL FIX
       ======================================== */
    .vb-banner,
    .vb-banner--upgrade,
    .vb-sidebar-cta {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        z-index: 1000 !important;
        position: relative !important;
        display: block !important;
        padding: 20px !important;
        border-radius: 12px !important;
        color: white !important;
        margin-bottom: 20px !important;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2) !important;
        border: none !important;
    }
    
    .vb-banner__title,
    .vb-banner .ttl {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 8px !important;
        color: white !important;
    }
    
    .vb-banner__sub,
    .vb-banner .sub {
        font-size: 1rem !important;
        opacity: 0.95 !important;
        color: white !important;
    }
    
    /* ========================================
       BUTTON TEXT VISIBILITY GUARANTEE
       ======================================== */
    .stButton > button,
    .stDownloadButton > button,
    button[kind="primary"],
    button[kind="secondary"] {
        color: white !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        min-height: 2.5rem !important;
    }
    
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    button[kind="primary"]:hover,
    button[kind="secondary"]:hover {
        color: white !important;
        opacity: 0.9 !important;
    }
    
    /* Primary buttons */
    button[kind="primary"] {
        background: linear-gradient(to bottom, #3182CE, #2C5282) !important;
        color: white !important;
    }
    
    /* ========================================
       FILE UPLOADER STYLING
       ======================================== */
    [data-testid="stFileUploader"] {
        background: transparent !important;
        border: 2px dashed rgba(49, 51, 63, 0.2) !important;
        border-radius: 0.5rem !important;
        padding: 1rem !important;
    }
    
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] > section {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    [data-testid="stFileUploaderDropzone"] {
        border: 2px dashed rgba(49, 51, 63, 0.2) !important;
        border-radius: 10px !important;
        background: rgba(247, 248, 250, 0.1) !important;
        padding: 1rem !important;
        min-height: 125px !important;
    }
    
    /* ========================================
       AUDIO PLAYER STYLING
       ======================================== */
    audio {
        width: 100% !important;
        border-radius: 8px !important;
        background: rgba(247, 248, 250, 0.5) !important;
    }
    
    audio::-webkit-media-controls {
        background: transparent !important;
    }
    
    /* ========================================
       INFO BOXES AND ALERTS
       ======================================== */
    .stAlert {
        background: rgba(20, 110, 190, 0.05) !important;
        border: 1px solid rgba(20, 110, 190, 0.2) !important;
        border-radius: 0.5rem !important;
    }
    
    /* Status messages */
    [data-baseweb="notification"] {
        background: white !important;
    }
    
    /* ========================================
       IFRAME AND MISC FIXES
       ======================================== */
    iframe {
        border: none !important;
        background: transparent !important;
        overflow: hidden !important;
    }
    
    header[data-testid="stHeader"] {
        background: rgba(255,255,255,0.95) !important;
    }
    
    /* ========================================
       MOBILE FAB BUTTON - Ensure visibility on mobile
       ======================================== */
    @media (max-width: 992px) {
        #vb-fab-menu {
            display: flex !important;
            z-index: 2147483647 !important;
            position: fixed !important;
            bottom: 20px !important;
            right: 20px !important;
            pointer-events: auto !important;
        }
    }
    
    /* Hide FAB on desktop */
    @media (min-width: 993px) {
        #vb-fab-menu {
            display: none !important;
        }
    }
    </style>
    ''', unsafe_allow_html=True)


def inject_mobile_fab_nuclear():
    """Nuclear option - FAB that WILL appear on mobile with 100% toggle reliability."""
    st.markdown('''
    <style>
    /* ========================================
       MOBILE FAB - NUCLEAR DEPLOYMENT WITH TOGGLE
       ======================================== */
    @media (max-width: 992px) {
        .vb-fab-menu {
            position: fixed !important;
            bottom: 20px !important;
            right: 20px !important;
            width: 60px !important;
            height: 60px !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 8px 28px rgba(102, 126, 234, 0.4) !important;
            cursor: pointer !important;
            z-index: 2147483647 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 28px !important;
            font-weight: bold !important;
            transition: all 0.3s ease !important;
            -webkit-tap-highlight-color: transparent !important;
            user-select: none !important;
        }
        
        .vb-fab-menu.sidebar-open {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
            transform: rotate(90deg) !important;
        }
        
        .vb-fab-menu:hover {
            transform: translateY(-2px) scale(1.05) !important;
            box-shadow: 0 12px 36px rgba(102, 126, 234, 0.5) !important;
        }
        
        .vb-fab-menu.sidebar-open:hover {
            transform: translateY(-2px) scale(1.05) rotate(90deg) !important;
        }
        
        .vb-fab-menu:active {
            transform: scale(0.95) !important;
        }
        
        /* COMPLETELY HIDE SIDEBAR TOGGLE ARROWS ON MOBILE */
        [data-testid="stSidebarNav"],
        [data-testid="collapsedControl"],
        [data-testid="stSidebarNavOpen"],
        [data-testid="stSidebarNavClose"],
        button[kind="header"][data-testid*="sidebar"],
        button[aria-label*="navigation"],
        button[aria-label*="sidebar"] {
            display: none !important;
            opacity: 0 !important;
            visibility: hidden !important;
            pointer-events: none !important;
            width: 0 !important;
            height: 0 !important;
            overflow: hidden !important;
        }
    }
    
    /* DESKTOP: HIDE FAB COMPLETELY */
    @media (min-width: 993px) {
        .vb-fab-menu {
            display: none !important;
            visibility: hidden !important;
        }
    }
    </style>
    
    <!-- FORCE FAB INTO DOM -->
    <button class="vb-fab-menu" id="vb-fab-menu" aria-label="Toggle menu" title="Menu">☰</button>
    
    <script>
    (function() {
        'use strict';
        console.log('🚀 NUCLEAR FAB TOGGLE INITIALIZATION STARTED');
        
        // SIDEBAR STATE DETECTION - 100% RELIABLE
        function isSidebarOpen() {
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return false;
            
            // Method 1: Check aria-expanded attribute
            const ariaExpanded = sidebar.getAttribute('aria-expanded');
            if (ariaExpanded === 'true') return true;
            if (ariaExpanded === 'false') return false;
            
            // Method 2: Check transform style
            const transform = window.getComputedStyle(sidebar).transform;
            if (transform && transform !== 'none') {
                const matrix = new DOMMatrix(transform);
                if (matrix.m41 < -50) return false; // translateX < -50px means closed
            }
            
            // Method 3: Check display style
            const display = window.getComputedStyle(sidebar).display;
            if (display === 'none') return false;
            
            // Method 4: Check visibility
            const visibility = window.getComputedStyle(sidebar).visibility;
            if (visibility === 'hidden') return false;
            
            // Method 5: Check opacity
            const opacity = window.getComputedStyle(sidebar).opacity;
            if (parseFloat(opacity) < 0.1) return false;
            
            // Method 6: Check overlay presence (sidebar is open if overlay is visible)
            const overlay = document.querySelector('[data-testid="stSidebarOverlay"]');
            if (overlay) {
                const overlayDisplay = window.getComputedStyle(overlay).display;
                return overlayDisplay !== 'none';
            }
            
            // Default: assume closed
            return false;
        }
        
        // OPEN SIDEBAR - 7 FALLBACK METHODS
        function openSidebar() {
            console.log('🎯 Opening sidebar...');
            const methods = [
                function() {
                    const btn = document.querySelector('[data-testid="stSidebarNavOpen"] button') || 
                               document.querySelector('[data-testid="stSidebarNavOpen"]');
                    if (btn && btn.click) {
                        btn.click();
                        console.log('✅ Method 1: Open button clicked');
                        return true;
                    }
                    return false;
                },
                function() {
                    const nav = document.querySelector('[data-testid="stSidebarNav"] button');
                    if (nav && nav.click) {
                        nav.click();
                        console.log('✅ Method 2: Nav button clicked');
                        return true;
                    }
                    return false;
                },
                function() {
                    const btn = document.querySelector('button[kind="header"]');
                    if (btn && btn.click) {
                        btn.click();
                        console.log('✅ Method 3: Header button clicked');
                        return true;
                    }
                    return false;
                },
                function() {
                    const buttons = document.querySelectorAll('button');
                    for (let btn of buttons) {
                        const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                        const text = (btn.textContent || '').toLowerCase();
                        if (label.includes('navigation') || label.includes('menu') || 
                            label.includes('sidebar') || label.includes('open') ||
                            text.includes('☰') || text.includes('menu')) {
                            btn.click();
                            console.log('✅ Method 4: Search button clicked');
                            return true;
                        }
                    }
                    return false;
                },
                function() {
                    const sidebar = document.querySelector('[data-testid="stSidebar"]');
                    if (sidebar) {
                        sidebar.setAttribute('aria-expanded', 'true');
                        sidebar.style.transform = 'translateX(0)';
                        sidebar.style.display = 'block';
                        sidebar.style.visibility = 'visible';
                        sidebar.style.opacity = '1';
                        sidebar.style.left = '0';
                        console.log('✅ Method 5: CSS manipulation');
                        return true;
                    }
                    return false;
                },
                function() {
                    if (window.streamlitDebug && window.streamlitDebug.toggleSidebar) {
                        window.streamlitDebug.toggleSidebar();
                        console.log('✅ Method 6: Streamlit API');
                        return true;
                    }
                    return false;
                },
                function() {
                    const sidebar = document.querySelector('[data-testid="stSidebar"]');
                    if (sidebar) {
                        sidebar.style.cssText = 'transform: translateX(0) !important; display: block !important; visibility: visible !important; opacity: 1 !important; z-index: 999999 !important; position: fixed !important; left: 0 !important; top: 0 !important; bottom: 0 !important;';
                        sidebar.setAttribute('aria-expanded', 'true');
                        console.log('✅ Method 7: Nuclear CSS');
                        return true;
                    }
                    return false;
                }
            ];
            
            for (let i = 0; i < methods.length; i++) {
                try {
                    if (methods[i]()) return true;
                } catch (err) {
                    console.log('❌ Open method ' + (i + 1) + ' failed:', err.message);
                }
            }
            return false;
        }
        
        // CLOSE SIDEBAR - 7 FALLBACK METHODS
        function closeSidebar() {
            console.log('🎯 Closing sidebar...');
            const methods = [
                function() {
                    const btn = document.querySelector('[data-testid="stSidebarNavClose"] button') || 
                               document.querySelector('[data-testid="stSidebarNavClose"]');
                    if (btn && btn.click) {
                        btn.click();
                        console.log('✅ Method 1: Close button clicked');
                        return true;
                    }
                    return false;
                },
                function() {
                    const overlay = document.querySelector('[data-testid="stSidebarOverlay"]');
                    if (overlay && overlay.click) {
                        overlay.click();
                        console.log('✅ Method 2: Overlay clicked');
                        return true;
                    }
                    return false;
                },
                function() {
                    const nav = document.querySelector('[data-testid="stSidebarNav"] button');
                    if (nav && nav.click) {
                        nav.click();
                        console.log('✅ Method 3: Nav button clicked');
                        return true;
                    }
                    return false;
                },
                function() {
                    const buttons = document.querySelectorAll('button');
                    for (let btn of buttons) {
                        const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                        if (label.includes('close') || label.includes('collapse')) {
                            btn.click();
                            console.log('✅ Method 4: Search button clicked');
                            return true;
                        }
                    }
                    return false;
                },
                function() {
                    const sidebar = document.querySelector('[data-testid="stSidebar"]');
                    if (sidebar) {
                        sidebar.setAttribute('aria-expanded', 'false');
                        sidebar.style.transform = 'translateX(-100%)';
                        sidebar.style.display = 'none';
                        sidebar.style.visibility = 'hidden';
                        sidebar.style.opacity = '0';
                        console.log('✅ Method 5: CSS manipulation');
                        return true;
                    }
                    return false;
                },
                function() {
                    if (window.streamlitDebug && window.streamlitDebug.toggleSidebar) {
                        window.streamlitDebug.toggleSidebar();
                        console.log('✅ Method 6: Streamlit API');
                        return true;
                    }
                    return false;
                },
                function() {
                    const sidebar = document.querySelector('[data-testid="stSidebar"]');
                    if (sidebar) {
                        sidebar.style.cssText = 'transform: translateX(-100%) !important; display: none !important; visibility: hidden !important; opacity: 0 !important; pointer-events: none !important;';
                        sidebar.setAttribute('aria-expanded', 'false');
                        console.log('✅ Method 7: Nuclear CSS');
                        return true;
                    }
                    return false;
                }
            ];
            
            for (let i = 0; i < methods.length; i++) {
                try {
                    if (methods[i]()) return true;
                } catch (err) {
                    console.log('❌ Close method ' + (i + 1) + ' failed:', err.message);
                }
            }
            return false;
        }
        
        // UPDATE FAB VISUAL STATE
        function updateFABState(fab) {
            if (!fab) return;
            const isOpen = isSidebarOpen();
            if (isOpen) {
                fab.classList.add('sidebar-open');
                fab.setAttribute('aria-label', 'Close menu');
                fab.setAttribute('title', 'Close menu');
            } else {
                fab.classList.remove('sidebar-open');
                fab.setAttribute('aria-label', 'Open menu');
                fab.setAttribute('title', 'Open menu');
            }
        }
        
        // NUCLEAR FAB INITIALIZATION WITH TOGGLE
        function initFABNuclear() {
            try {
                let fab = document.getElementById('vb-fab-menu');
                if (!fab) {
                    fab = document.createElement('button');
                    fab.className = 'vb-fab-menu';
                    fab.id = 'vb-fab-menu';
                    fab.innerHTML = '☰';
                    document.body.appendChild(fab);
                    console.log('✅ FAB created manually');
                }
                
                const isMobile = window.innerWidth <= 992;
                if (isMobile) {
                    fab.style.display = 'flex';
                    fab.style.zIndex = '2147483647';
                    fab.style.pointerEvents = 'auto';
                    console.log('✅ FAB visible on mobile (width: ' + window.innerWidth + 'px)');
                } else {
                    fab.style.display = 'none';
                    console.log('ℹ️ FAB hidden on desktop (width: ' + window.innerWidth + 'px)');
                    return true;
                }
                
                // Update initial state
                updateFABState(fab);
                
                // Remove existing handlers
                const newFab = fab.cloneNode(true);
                fab.parentNode.replaceChild(newFab, fab);
                fab = newFab;
                
                // TOGGLE CLICK HANDLER
                fab.onclick = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const isOpen = isSidebarOpen();
                    console.log('🎯 FAB CLICKED - Sidebar is currently: ' + (isOpen ? 'OPEN' : 'CLOSED'));
                    
                    let success = false;
                    if (isOpen) {
                        success = closeSidebar();
                        console.log(success ? '🎉 Sidebar closed successfully' : '⚠️ Failed to close sidebar');
                    } else {
                        success = openSidebar();
                        console.log(success ? '🎉 Sidebar opened successfully' : '⚠️ Failed to open sidebar');
                    }
                    
                    // Update FAB visual state after toggle
                    setTimeout(function() {
                        updateFABState(fab);
                    }, 100);
                };
                
                // Touch feedback
                fab.addEventListener('touchstart', function(e) {
                    fab.style.transform = 'scale(0.95)';
                }, {passive: true});
                
                fab.addEventListener('touchend', function(e) {
                    fab.style.transform = '';
                    setTimeout(function() {
                        updateFABState(fab);
                    }, 100);
                }, {passive: true});
                
                // Monitor sidebar state changes
                const observer = new MutationObserver(function() {
                    updateFABState(fab);
                });
                
                const sidebar = document.querySelector('[data-testid="stSidebar"]');
                if (sidebar) {
                    observer.observe(sidebar, {
                        attributes: true,
                        attributeFilter: ['aria-expanded', 'class', 'style']
                    });
                }
                
                console.log('🎯 NUCLEAR FAB TOGGLE COMPLETE');
                return true;
            } catch (error) {
                console.error('❌ FAB init error:', error);
                return false;
            }
        }
        
        // AGGRESSIVE INITIALIZATION
        const delays = [0, 50, 100, 200, 350, 500, 750, 1000, 1500, 2000, 3000, 5000];
        delays.forEach(function(delay, index) {
            setTimeout(function() {
                initFABNuclear();
                console.log('🔄 FAB toggle init ' + (index + 1) + '/12 at ' + delay + 'ms');
            }, delay);
        });
        
        // Resize handling
        let resizeTimer;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                console.log('🔄 Resize - reinitializing FAB toggle');
                initFABNuclear();
            }, 250);
        });
        
        console.log('✅ NUCLEAR FAB TOGGLE SYSTEM ARMED');
    })();
    </script>
    ''', unsafe_allow_html=True)


def inject_sidebar_overlap_fix():
    """Nuclear fix for sidebar overlapping main content when closed."""
    st.markdown('''
    <style>
    /* ========================================
       SIDEBAR OVERLAP NUCLEAR FIX
       ======================================== */
    
    /* Sidebar base transition */
    [data-testid="stSidebar"] {
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    /* WHEN SIDEBAR IS CLOSED - COMPLETELY HIDDEN */
    [data-testid="stSidebar"][aria-expanded="false"],
    [data-testid="stSidebar"]:not([aria-expanded="true"]) {
        transform: translateX(-100%) !important;
        display: none !important;
        visibility: hidden !important;
        width: 0px !important;
        min-width: 0px !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    
    /* WHEN SIDEBAR IS OPEN - PROPERLY POSITIONED */
    [data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0) !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }
    
    /* MAIN CONTENT - PREVENT OVERLAP, ENSURE FULL WIDTH */
    .main .block-container {
        margin-left: 0 !important;
        padding-left: 1rem !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* MOBILE: MAIN CONTENT FULL WIDTH WHEN SIDEBAR CLOSED */
    @media (max-width: 992px) {
        .main .block-container {
            width: 100% !important;
            max-width: 100% !important;
            margin-left: 0 !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        /* Ensure main content doesn't get pushed by hidden sidebar */
        .main {
            margin-left: 0 !important;
            width: 100% !important;
        }
        
        /* Force sidebar to stay in fixed position overlay mode */
        [data-testid="stSidebar"] {
            position: fixed !important;
            left: 0 !important;
            top: 0 !important;
            height: 100vh !important;
        }
    }
    
    /* DESKTOP: Proper sidebar spacing */
    @media (min-width: 993px) {
        .main .block-container {
            padding-left: 1rem !important;
        }
    }
    </style>
    
    <script>
    (function() {
        'use strict';
        console.log('🛡️ SIDEBAR OVERLAP MONITOR STARTING');
        
        // SIDEBAR OVERLAP MONITOR - CONTINUOUS ENFORCEMENT
        function enforceSidebarState() {
            try {
                const sidebar = document.querySelector('[data-testid="stSidebar"]');
                const mainContent = document.querySelector('.main .block-container');
                const mainSection = document.querySelector('.main');
                
                if (!sidebar) return;
                
                const isExpanded = sidebar.getAttribute('aria-expanded') === 'true';
                const isMobile = window.innerWidth <= 992;
                
                if (!isExpanded) {
                    // SIDEBAR CLOSED - ENFORCE COMPLETE HIDING
                    sidebar.style.transform = 'translateX(-100%)';
                    sidebar.style.display = 'none';
                    sidebar.style.visibility = 'hidden';
                    sidebar.style.opacity = '0';
                    sidebar.style.pointerEvents = 'none';
                    sidebar.style.width = '0px';
                    sidebar.style.minWidth = '0px';
                    
                    // MAIN CONTENT - ENFORCE FULL WIDTH
                    if (mainContent) {
                        mainContent.style.marginLeft = '0';
                        mainContent.style.paddingLeft = '1rem';
                        mainContent.style.width = '100%';
                        mainContent.style.maxWidth = '100%';
                    }
                    
                    if (mainSection) {
                        mainSection.style.marginLeft = '0';
                        mainSection.style.width = '100%';
                    }
                } else {
                    // SIDEBAR OPEN - PROPER DISPLAY
                    sidebar.style.transform = 'translateX(0)';
                    sidebar.style.display = 'block';
                    sidebar.style.visibility = 'visible';
                    sidebar.style.opacity = '1';
                    sidebar.style.pointerEvents = 'auto';
                    sidebar.style.width = '';
                    sidebar.style.minWidth = '';
                    
                    // On mobile, ensure sidebar is overlay mode
                    if (isMobile) {
                        sidebar.style.position = 'fixed';
                        sidebar.style.left = '0';
                        sidebar.style.top = '0';
                        sidebar.style.height = '100vh';
                        sidebar.style.zIndex = '999999';
                    }
                }
            } catch (error) {
                // Silent fail - don't break the app
            }
        }
        
        // Run enforcement continuously
        setInterval(enforceSidebarState, 100);
        
        // Also run on mutation (when Streamlit updates DOM)
        if (window.MutationObserver) {
            const observer = new MutationObserver(enforceSidebarState);
            observer.observe(document.body, {
                attributes: true,
                attributeFilter: ['aria-expanded', 'class', 'style'],
                subtree: true
            });
            console.log('✅ Mutation observer attached to sidebar');
        }
        
        // Run on window resize
        window.addEventListener('resize', enforceSidebarState);
        
        // Initial enforcement
        enforceSidebarState();
        setTimeout(enforceSidebarState, 100);
        setTimeout(enforceSidebarState, 500);
        setTimeout(enforceSidebarState, 1000);
        
        console.log('✅ SIDEBAR OVERLAP MONITOR ACTIVE');
    })();
    </script>
    ''', unsafe_allow_html=True)


from dotenv import load_dotenv

# Optional native recorder components (preferred path).
# - PyPI: streamlit-audiorecorder → from audiorecorder import audiorecorder
# - GitHub/pip: streamlit_audio_recorder → from streamlit_audio_recorder import st_audiorec
# Try both to maximize compatibility across environments.
try:
    from audiorecorder import audiorecorder  # type: ignore
except Exception:  # pragma: no cover
    try:
        from streamlit_audiorecorder import audiorecorder  # type: ignore
    except Exception:  # pragma: no cover
        audiorecorder = None

try:
    from streamlit_audio_recorder import st_audiorec  # type: ignore
except Exception:  # pragma: no cover
    st_audiorec = None

# Third fallback: streamlit_mic_recorder (actively maintained)
try:
    from streamlit_mic_recorder import mic_recorder  # type: ignore
except Exception:  # pragma: no cover
    mic_recorder = None

# Runtime self-heal for missing recorder components on Streamlit Cloud/Linux.
def _try_import_recorders() -> Tuple[Optional[Any], Optional[Any], Optional[Any]]:
    _aud = None
    _st = None
    _mic = None
    try:
        from audiorecorder import audiorecorder as _ar  # type: ignore
        _aud = _ar
    except Exception:
        try:
            from streamlit_audiorecorder import audiorecorder as _ar  # type: ignore
            _aud = _ar
        except Exception:
            _aud = None
    try:
        from streamlit_audio_recorder import st_audiorec as _sa  # type: ignore
        _st = _sa
    except Exception:
        _st = None
    try:
        from streamlit_mic_recorder import mic_recorder as _mr  # type: ignore
        _mic = _mr
    except Exception:
        _mic = None
    return _aud, _st, _mic


def _pip_install_if_missing(pkgs: List[str], timeout: int = 240) -> bool:
    """Attempt to install packages via pip at runtime. Safe on Streamlit Cloud.

    Returns True if pip exited with code 0, False otherwise.
    """
    try:
        cmd = [sys.executable, "-m", "pip", "install", "-q"] + pkgs
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode == 0
    except Exception:
        return False


def ensure_native_recorder_available() -> None:
    """If recorder components are missing, try to auto-install on Linux/Cloud.

    This keeps the app "locked" functionally while self-healing the environment.
    No-op on Windows/local where the user already has everything.
    """
    global audiorecorder, st_audiorec, mic_recorder
    if (audiorecorder is not None) or (st_audiorec is not None) or (mic_recorder is not None):
        return
    # Heuristic: Streamlit Cloud is Linux. Avoid doing this on Windows.
    if platform.system().lower() != "linux":
        return
    # Allow disabling via env if ever needed.
    if os.getenv("AUTO_INSTALL_RECORDER", "1") != "1":
        return
    # Try installing both common recorder components, then reimport.
    pkgs = [
        "streamlit-audiorecorder>=0.0.2",
        "git+https://github.com/stefanrmmr/streamlit_audio_recorder.git@777d18114130137d492c0378a86631fff1ff1be5#egg=streamlit-audiorec",
        "streamlit-mic-recorder>=0.0.8",
    ]
    success = _pip_install_if_missing(pkgs)
    # Re-attempt imports regardless; success flag is just advisory.
    _aud, _st, _mic = _try_import_recorders()
    if _aud is not None:
        audiorecorder = _aud
    if _st is not None:
        st_audiorec = _st
    if _mic is not None:
        mic_recorder = _mic

AUTH_IMPORT_ERROR: Optional[Exception] = None
try:
    from auth import (
        authenticate,
        ensure_demo_user,
        get_user,
        get_free_usage,
        increment_free_usage,
        get_minutes_balance,
        get_setup_credits,
        get_user_by_email,
        hash_backend_status,
        init_db,
        register_user,
    )
except Exception as _auth_err:  # Attempt self-heal (install passlib) then retry
    AUTH_IMPORT_ERROR = _auth_err
    try:
        # Try installing passlib if missing; ignore result
        _pip_install_if_missing(["passlib[bcrypt]>=1.7.4"])  # best effort
        import importlib, importlib.util
        mod = None
        try:
            # First, try importing by module name (may resolve to third-party 'auth')
            mod = importlib.import_module("auth")
        except Exception:
            mod = None
        # If imported module doesn't have expected attributes, try loading local file explicitly
        if not mod or not hasattr(mod, "authenticate"):
            auth_path = str(Path(__file__).parent / "auth.py")
            spec = importlib.util.spec_from_file_location("vocalbrand_auth_local", auth_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
                except Exception:
                    mod = None
        if not mod:
            raise ImportError("Failed to import local auth module")
        authenticate = getattr(mod, "authenticate")  # type: ignore[misc]
        ensure_demo_user = getattr(mod, "ensure_demo_user")  # type: ignore[misc]
        get_user = getattr(mod, "get_user")  # type: ignore[misc]
        get_free_usage = getattr(mod, "get_free_usage")  # type: ignore[misc]
        increment_free_usage = getattr(mod, "increment_free_usage")  # type: ignore[misc]
        get_minutes_balance = getattr(mod, "get_minutes_balance")  # type: ignore[misc]
        get_setup_credits = getattr(mod, "get_setup_credits")  # type: ignore[misc]
        get_user_by_email = getattr(mod, "get_user_by_email")  # type: ignore[misc]
        hash_backend_status = getattr(mod, "hash_backend_status")  # type: ignore[misc]
        init_db = getattr(mod, "init_db")  # type: ignore[misc]
        register_user = getattr(mod, "register_user")  # type: ignore[misc]
        AUTH_IMPORT_ERROR = None
    except Exception as _auth_err2:  # Final fallback: define stubs which raise clear error on call
        AUTH_IMPORT_ERROR = _auth_err2
        def _fail(*_a, **_k):
            raise RuntimeError(f"Auth module failed to import: {_auth_err2}")
        authenticate = _fail  # type: ignore[assignment]
        ensure_demo_user = lambda: None  # type: ignore[assignment]
        get_user = _fail  # type: ignore[assignment]
        get_free_usage = _fail  # type: ignore[assignment]
        increment_free_usage = _fail  # type: ignore[assignment]
        get_minutes_balance = _fail  # type: ignore[assignment]
        get_setup_credits = _fail  # type: ignore[assignment]
        get_user_by_email = _fail  # type: ignore[assignment]
        hash_backend_status = _fail  # type: ignore[assignment]
        init_db = lambda: None  # type: ignore[assignment]
        register_user = _fail  # type: ignore[assignment]
from engine import DEFAULT_MODEL_ID, DEFAULT_OUTPUT_FORMAT, VocalBrandEngine
from payment import PaymentManager
from utils.audio_utils import validate_audio_bytes, quality_score
from utils.ffmpeg_auto import attempt_auto_ffmpeg
from utils.ui import inject_css, inject_mobile_nav_helpers
from utils.email_utils import send_contact_email, is_email_configured
from utils.seo import inject_seo_meta

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("vocalbrand.app")

FREE_LIMIT = int(os.getenv("VOCALBRAND_FREE_LIMIT", "3"))
BRIDGE_HISTORY_LIMIT = int(os.getenv("VOCALBRAND_BRIDGE_HISTORY_LIMIT", "25"))
BRIDGE_QUEUE: "queue.Queue[str]" = queue.Queue()

# Ensure recorder components are present on Streamlit Cloud before proceeding.
try:
    ensure_native_recorder_available()
    logger.info(
        "Recorder availability after auto-install: audiorecorder=%s, st_audiorec=%s, mic_recorder=%s",
        audiorecorder is not None,
        st_audiorec is not None,
        'mic_recorder' in globals() and (mic_recorder is not None),
    )
except Exception as _e:
    logger.warning("Auto-install for recorder components skipped or failed: %s", _e)
def handle_billing_return() -> None:
    """If redirected back from Stripe, verify session and flip subscription flag.

    Supports success and cancel flows via query params added by PaymentManager.
    """
    try:
        params = st.query_params  # Streamlit 1.30+
        billing = params.get("billing")
        sess_id = params.get("session_id")
    except Exception:
        billing = None
        sess_id = None
    if not billing:
        return
    if billing == "success" and sess_id and payment_manager:
        # Attempt to fetch session details (covers subscription and one-time payments)
        try:
            summary = payment_manager.get_line_items_summary(str(sess_id))
        except Exception:
            summary = None

        # Subscription activation path if created via in-app checkout
        try:
            sub_id = payment_manager.get_subscription_id_from_session(str(sess_id))
        except Exception:
            sub_id = None
        if sub_id and st.session_state.get("user_id"):
            try:
                from auth import set_subscription
                set_subscription(st.session_state["user_id"], True, stripe_sub_id=sub_id)
                st.session_state["subscription_active"] = True
                st.success("Subscription activated! 🎉")
            except Exception:
                st.session_state["subscription_active"] = True

        # One-time entitlements (Payment Links or one-off payments)
        try:
            if summary and summary.get("mode") == "payment":
                from auth import (
                    add_minutes_balance,
                    add_setup_credits,
                    get_user_by_email,
                    has_processed_session,
                    mark_processed_session,
                )
                # Resolve user: prefer logged-in; else match by email from checkout
                uid = st.session_state.get("user_id")
                if not uid:
                    email = summary.get("customer_email")
                    if email:
                        u = get_user_by_email(str(email))
                        uid = u.get("id") if u else None
                if uid:
                    if not has_processed_session(str(sess_id)):
                        minutes_added = 0
                        setup_added = 0
                        for item in summary.get("items", []) or []:
                            price_id = item.get("price_id")
                            qty = int(item.get("quantity") or 1)
                            grant = ENTITLEMENT_MAP.get(price_id or "")
                            if not grant:
                                continue
                            if grant.get("minutes"):
                                minutes_added += int(grant["minutes"]) * qty
                            if grant.get("setup"):
                                setup_added += int(grant["setup"]) * qty
                        if minutes_added > 0:
                            new_min = add_minutes_balance(int(uid), minutes_added)
                            st.success(f"Minutes pack activated: +{minutes_added} min (now {new_min})")
                        if setup_added > 0:
                            new_sc = add_setup_credits(int(uid), setup_added)
                            st.success(f"Setup credit added: +{setup_added} (now {new_sc})")
                        mark_processed_session(int(uid), str(sess_id), kind="payment", amount_cents=summary.get("amount_total"), currency=summary.get("currency"))
                    else:
                        st.info("Payment already processed. Your credits are up to date.")
                else:
                    st.warning("Payment received but cannot match to an account. Please sign in with the same email and refresh.")
        except Exception as e:
            st.warning(f"Post-payment processing note: {e}")

        # Clean query params and refresh
        try:
            st.query_params.clear()
        except Exception:
            pass
        safe_rerun(0.2)
    elif billing == "cancel":
        st.info("Checkout canceled. You can try again anytime.")
        try:
            st.query_params.clear()
        except Exception:
            pass


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Fetch secrets from environment variables or local TOML files."""
    if key in os.environ:
        return os.environ[key]
    for candidate in ("secrets.toml", "secrets.example.toml"):
        path = Path(candidate)
        if not path.exists():
            continue
        try:
            import tomllib  # type: ignore

            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if isinstance(data.get(key), str):
            return data[key]
        for section in ("default", "secrets"):
            section_data = data.get(section)
            if isinstance(section_data, dict) and isinstance(section_data.get(key), str):
                return section_data[key]
    return default


def safe_rerun(delay: float | None = None) -> None:
    """Compatibility wrapper around Streamlit rerun APIs."""
    if delay:
        time.sleep(delay)
    try:
        if hasattr(st, "rerun"):
            st.rerun()
        else:  # pragma: no cover
            st.experimental_rerun()
    except Exception:  # noqa: BLE001
        logger.debug("rerun swallow", exc_info=True)


@dataclass
class BridgeState:
    """Recorder bridge state shared between browser component and app."""

    lock: threading.Lock = field(default_factory=threading.Lock)
    latest: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    hits: int = 0

    def push(self, payload: Dict[str, Any]) -> None:
        with self.lock:
            self.latest = payload
            self.history.append(payload)
            if len(self.history) > BRIDGE_HISTORY_LIMIT:
                self.history.pop(0)
            self.hits += 1

    def snapshot(self) -> Dict[str, Any]:
        with self.lock:
            return dict(self.latest)


BRIDGE_STATE = BridgeState()


def _resolve_binary(name: str, env_key: str | None = None) -> Optional[str]:
    env_candidate = os.getenv(env_key or name.upper())
    if env_candidate and Path(env_candidate).exists():
        return env_candidate
    return shutil.which(name)


def _scan_local_ffmpeg() -> Tuple[str, str]:
    """Search project tree for bundled ffmpeg/ffprobe binaries if not on PATH.

    We purposely keep this lightweight (no heavy recursion limit) and only
    look a few levels deep to avoid large latency on first page load.
    """
    root = Path(__file__).parent
    # Common nested vendor folder patterns
    candidate_dirs = [root, root / "ffmpeg", root / "ffmpeg-2025-09-28-git-0fdb5829e3-full_build"]
    # Include any *ffmpeg* folders at depth 2
    for p in root.glob("*ffmpeg*/**/bin"):
        candidate_dirs.append(p)
    ffmpeg_path = ""
    ffprobe_path = ""
    # Support both Windows (.exe) and Linux (no extension)
    ffmpeg_names = ["ffmpeg.exe", "ffmpeg"]
    ffprobe_names = ["ffprobe.exe", "ffprobe"]
    
    for d in candidate_dirs:
        if not d.exists():
            continue
        # Try to find ffmpeg
        for fname in ffmpeg_names:
            fp = d / fname
            if fp.exists():
                ffmpeg_path = str(fp)
                break
        # Try to find ffprobe
        for fname in ffprobe_names:
            fp2 = d / fname
            if fp2.exists():
                ffprobe_path = str(fp2)
                break
        if ffmpeg_path and ffprobe_path:
            break
    return ffmpeg_path, ffprobe_path


def initialize_recorder_support() -> Tuple[bool, str, str, str, str]:
    attempt_auto_ffmpeg()
    
    # Try to find ffmpeg using multiple methods
    ffmpeg_path = _resolve_binary("ffmpeg", "FFMPEG_BINARY") or ""
    ffprobe_path = _resolve_binary("ffprobe", "FFPROBE_BINARY") or ""
    
    logger.info("FFmpeg detection attempt 1 (PATH/env): ffmpeg=%s, ffprobe=%s", ffmpeg_path, ffprobe_path)
    
    if not ffmpeg_path or not ffprobe_path:
        local_ffmpeg, local_ffprobe = _scan_local_ffmpeg()
        ffmpeg_path = ffmpeg_path or local_ffmpeg
        ffprobe_path = ffprobe_path or local_ffprobe
        logger.info("FFmpeg detection attempt 2 (local scan): ffmpeg=%s, ffprobe=%s", ffmpeg_path, ffprobe_path)
    
    if ffmpeg_path:
        os.environ.setdefault("FFMPEG_BINARY", ffmpeg_path)
        # Prepend bin directory to PATH for libraries (pydub) relying on PATH scan
        bin_dir = str(Path(ffmpeg_path).parent)
        if bin_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
        logger.info("FFmpeg configured: FFMPEG_BINARY=%s, PATH updated with %s", ffmpeg_path, bin_dir)
    if ffprobe_path:
        os.environ.setdefault("FFPROBE_BINARY", ffprobe_path)
        logger.info("FFprobe configured: FFPROBE_BINARY=%s", ffprobe_path)
    
    recorder_message = ""
    status = "ok"
    # Treat mic_recorder as a valid native component too (Cloud-friendly)
    has_component = (audiorecorder is not None) or (st_audiorec is not None) or (
        'mic_recorder' in globals() and (mic_recorder is not None)
    )
    
    logger.info(
        "Audio recorder components: audiorecorder=%s, st_audiorec=%s, mic_recorder=%s",
        audiorecorder is not None,
        st_audiorec is not None,
        'mic_recorder' in globals() and (mic_recorder is not None),
    )
    
    if not has_component:
        status = "component_missing"
        recorder_message = (
            "Install recorder: pip install streamlit-audiorecorder  (inside your venv). "
            "Or: pip install streamlit-audio-recorder. "
            "Imports: 'from audiorecorder import audiorecorder' or 'from streamlit_audio_recorder import st_audiorec'."
        )
        logger.error("Audio recorder component missing!")
    elif not ffmpeg_path:
        status = "ffmpeg_missing"
        recorder_message = "FFmpeg not detected. Place binaries under project /ffmpeg.../bin or add to PATH."
        logger.error("FFmpeg binary not found in PATH or local directories!")
    
    logger.info(
        "Recorder init | component=%s status=%s ffmpeg=%s ffprobe=%s path_in_env=%s",
        has_component,
        status,
        ffmpeg_path,
        ffprobe_path,
        os.environ.get("FFMPEG_BINARY"),
    )
    comp = (
        "audiorecorder"
        if audiorecorder is not None
        else ("st_audiorec" if st_audiorec is not None else ("mic_recorder" if ('mic_recorder' in globals() and mic_recorder is not None) else "none"))
    )
    msg = recorder_message or f"component={comp}"
    return has_component and status == "ok", status, ffmpeg_path, ffprobe_path, msg


HAS_NATIVE_RECORDER, RECORDER_STATUS, FFMPEG_PATH, FFPROBE_PATH, RECORDER_MSG = initialize_recorder_support()

ELEVENLABS_KEY = get_secret("ELEVENLABS_API_KEY", os.getenv("ELEVENLABS_API_KEY", "")) or ""

# Initialize voice manager for quota handling
from voice_manager import create_voice_manager
voice_manager = create_voice_manager(ELEVENLABS_KEY)

if voice_manager:
    logger.info("✅ Voice manager initialized successfully - auto-cleanup enabled")
else:
    logger.error("❌ Voice manager NOT initialized - auto-cleanup DISABLED!")

# Initialize engine with voice manager
engine = VocalBrandEngine(ELEVENLABS_KEY, voice_manager=voice_manager)
if engine.offline:
    logger.warning("Engine operating in offline mode (%s)", engine.offline_reason)

STRIPE_KEY = get_secret("STRIPE_API_KEY", os.getenv("STRIPE_API_KEY", "")) or ""
STRIPE_PRICE_ID = get_secret("STRIPE_PRICE_ID")
STRIPE_PRICE_ID_ANNUAL = get_secret("STRIPE_PRICE_ID_ANNUAL")
payment_manager = PaymentManager(
    STRIPE_KEY, 
    price_id=STRIPE_PRICE_ID,
    price_id_annual=STRIPE_PRICE_ID_ANNUAL
) if STRIPE_KEY else None

# Map price IDs (env) to entitlements for one-time purchases
PACK60_PRICE_ID = os.getenv("PACK60_PRICE_ID")
PACK300_PRICE_ID = os.getenv("PACK300_PRICE_ID")
PACK1000_PRICE_ID = os.getenv("PACK1000_PRICE_ID")
SETUP_PRO_PRICE_ID = os.getenv("SETUP_PRO_PRICE_ID")
SETUP_ENT_PRICE_ID = os.getenv("SETUP_ENT_PRICE_ID")

ENTITLEMENT_MAP: Dict[str, Dict[str, int]] = {}
if PACK60_PRICE_ID:
    ENTITLEMENT_MAP[PACK60_PRICE_ID] = {"minutes": 60}
if PACK300_PRICE_ID:
    ENTITLEMENT_MAP[PACK300_PRICE_ID] = {"minutes": 300}
if PACK1000_PRICE_ID:
    ENTITLEMENT_MAP[PACK1000_PRICE_ID] = {"minutes": 1000}
if SETUP_PRO_PRICE_ID:
    ENTITLEMENT_MAP[SETUP_PRO_PRICE_ID] = {"setup": 1}
if SETUP_ENT_PRICE_ID:
    ENTITLEMENT_MAP[SETUP_ENT_PRICE_ID] = {"setup": 1}

SESSION_DEFAULTS: Dict[str, Any] = {
    "user_id": None,
    "user_email": None,
    "user_is_admin": os.getenv("ADMIN_MODE") == "1",
    "subscription_active": False,
    "nav_page": "Onboarding",
    "clone_voice_id": "",
    "clone_voice_label": "",
    "clone_status": "",
    "clone_timestamp": "",
    "clone_history": [],
    "tts_history": [],
    "pending_audio_bytes": b"",
    "pending_audio_label": "",
    "pending_audio_meta": {},
    "latest_checkout_id": None,
    # UX and automation toggles
    "use_pro_recorder": False,  # Standard recorder by default; user can enable Pro (timer + waveform) via checkbox
    "trim_silence_toggle": False,  # If enabled, trim leading/trailing silence before cloning
    "auto_clone_toggle": False,  # If enabled, auto-clone immediately after recording lock-in
    "last_auto_clone_hash": "",  # To avoid double auto-clone on reruns
}


def configure_page() -> None:
    try:
        # Use logo.png as page icon if available
        icon_path = "logo.png"
        page_icon = icon_path if Path(icon_path).exists() else "🎙️"
        st.set_page_config(
            page_title="VocalBrand Supreme - Clone Your Voice in 30 Seconds | AI Voice Generator",
            page_icon=page_icon,
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                "Get Help": "https://vocalbrand.com/support",
                "Report a bug": "https://vocalbrand.com/bug",
                "About": "VocalBrand Supreme - Transform your voice into a digital asset. Clone once, generate unlimited professional audio in seconds.",
            },
        )
    except Exception:  # pragma: no cover - set_page_config only allowed once
        pass


def ensure_session_defaults() -> None:
    for key, default in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default.copy() if isinstance(default, (list, dict)) else default


def ensure_voice_reset_on_logout() -> None:
    if st.session_state.get("user_id"):
        return
    st.session_state["clone_voice_id"] = ""
    st.session_state["clone_voice_label"] = ""
    st.session_state["clone_status"] = ""
    st.session_state["clone_timestamp"] = ""
    st.session_state["clone_history"] = []
    st.session_state["tts_history"] = []
    st.session_state["pending_audio_bytes"] = b""
    st.session_state["pending_audio_label"] = ""
    st.session_state["pending_audio_meta"] = {}


def logout() -> None:
    st.session_state["user_id"] = None
    st.session_state["user_email"] = None
    st.session_state["subscription_active"] = False
    ensure_voice_reset_on_logout()
    safe_rerun(0.05)


def format_timestamp(ts: str) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return ts


def _ingest_audio_bytes(raw_bytes: bytes, *, source: str, filename: str | None = None) -> Dict[str, Any]:
    validation = validate_audio_bytes(raw_bytes)
    digest = hashlib.sha1(raw_bytes).hexdigest()[:12]
    quality = quality_score(validation["duration"], validation["loudness_dbfs"]) if validation["ok"] else None
    meta = {
        "source": source,
        "filename": filename or f"{source}_{digest}.wav",
        "hash": digest,
        "ingested_at": datetime.utcnow().isoformat(),
        "quality": quality,
    }
    meta.update({k: v for k, v in validation.items() if k != "raw_bytes"})
    BRIDGE_STATE.push(meta)
    st.session_state["pending_audio_bytes"] = raw_bytes
    st.session_state["pending_audio_label"] = meta["filename"]
    st.session_state["pending_audio_meta"] = meta
    st.session_state["recording_locked_in"] = True
    # 🔑 CRITICAL FIX: Also set audio_data so render_clone_section() can continue the flow
    st.session_state["audio_data"] = raw_bytes
    st.session_state["audio_meta"] = meta
    logger.info(
        "Ingested audio | source=%s hash=%s size=%sB ok=%s duration=%.2fs loudness=%s",
        source,
        digest,
        len(raw_bytes),
        meta.get("ok"),
        meta.get("duration", 0.0),
        meta.get("loudness_dbfs"),
    )
    return meta


def _maybe_trim_silence(raw_bytes: bytes) -> Tuple[bytes, Optional[Dict[str, Any]]]:
    """Optionally trim leading/trailing silence based on user toggle.

    Returns (bytes, info_dict|None). If no trimming applied, returns original bytes and None.
    """
    if not st.session_state.get("trim_silence_toggle"):
        return raw_bytes, None
    try:
        from pydub import AudioSegment  # type: ignore
        from pydub.silence import detect_nonsilent  # type: ignore
        seg = AudioSegment.from_file(BytesIO(raw_bytes))
        dur_ms = len(seg)
        # Conservative silence threshold and window
        # Users in noisy rooms: raise threshold (less negative)
        thresh = -40  # dBFS
        window = 20  # ms
        non_silent = detect_nonsilent(seg, min_silence_len=window, silence_thresh=thresh)
        if not non_silent:
            return raw_bytes, {"applied": False, "reason": "all_silent"}
        start = max(0, non_silent[0][0] - 20)
        end = min(dur_ms, non_silent[-1][1] + 20)
        if end <= start:
            return raw_bytes, {"applied": False, "reason": "invalid_bounds"}
        trimmed = seg[start:end]
        out = BytesIO()
        trimmed.export(out, format="wav")
        return out.getvalue(), {
            "applied": True,
            "orig_ms": dur_ms,
            "trimmed_ms": len(trimmed),
            "removed_ms": max(0, dur_ms - len(trimmed)),
            "threshold_dbfs": thresh,
        }
    except Exception as e:  # noqa: BLE001
        logger.warning("Silence trim failed: %s", e)
        return raw_bytes, {"applied": False, "reason": str(e)}



@safe_execute(show_details=True)
def render_file_upload_fallback() -> None:
    """Handle file upload with comprehensive error handling."""
    # 🎯 NOTE: Guidance message now shown at top of render_clone_section() instead
    # This ensures it displays BEFORE Step 1, regardless of flow state
    
    # Render upload section header
    # Provide an anchor to auto-scroll here
    st.markdown('<div id="vb-upload"></div>', unsafe_allow_html=True)
    st.markdown('''
    <div class="section-header">
        <h3 class="upload-title">
            <span class="icon">📁</span> Upload Audio
        </h3>
    </div>
    ''', unsafe_allow_html=True)
    
    # Make label visible so supported formats are obvious
    uploaded = st.file_uploader(
        f"Upload Audio File ({accepted_formats_display()})", type=ACCEPTED_AUDIO_EXTS, 
        key="clone_file_upload", label_visibility="visible"
    )
    # Explicit, persistent helper text regardless of Streamlit placeholder
    st.caption(f"Supported: {accepted_formats_display()} • Max 200 MB • Drag & drop or click Browse")
    
    if not uploaded:
        return
    
    raw_bytes = uploaded.read()
    if not raw_bytes:
        raise VocalBrandError(
            message="The uploaded file appears to be empty",
            recovery_hint="Please try uploading your file again",
            code="empty_file"
        )
    
    # Process the audio file
    meta = _ingest_audio_bytes(raw_bytes, source="upload", filename=uploaded.name)
    if not meta:
        raise AudioProcessingError(
            message="Could not process the audio file",
            recovery_hint="Make sure your file is a valid audio format (WAV, MP3, M4A, or AAC)",
            code="processing_failed"
        )
    
    _render_audio_feedback(meta, raw_bytes)
    
    # Force rerun to ensure UI updates
    if meta.get("duration"):
        st.session_state["file_upload_success"] = True
        st.rerun()
    
    return

    raw_bytes = uploaded.read()
    if not raw_bytes:
        st.warning("Uploaded file appears empty.")
        return


    def render_audio_capture_area() -> None:
        st.markdown("#### Record a 30-60s sample")
        st.info("Recorder UI will appear here. (Supreme placeholder)")
    st.markdown("#### Record a 30-60s sample")
    # Allow forcing Pro Recorder (HTML5) even if native is present, for live timer+waveform
    force_pro = bool(st.session_state.get("use_pro_recorder"))
    # If Pro is forced, or if native is missing AND we also don't have mic_recorder,
    # render the HTML5 Pro fallback. If mic_recorder exists, we'll skip this and use it below.
    if force_pro or (not HAS_NATIVE_RECORDER and not ('mic_recorder' in globals() and mic_recorder is not None)):
        st.markdown("### 🎙️ Pro Recorder")
        # Fallback with direct base64 injection + live loudness/duration estimation
        fallback_id = "fallback_recorder"
        js_template = """
<div id="__FALLBACK_ID__"></div>
<script>
(function(){
    const rootId = "__FALLBACK_ID__";
        function init(){
        const container = document.getElementById(rootId);
        if (!container) { setTimeout(init, 50); return; }
        if (container.dataset.vbInit === '1') return;
        container.dataset.vbInit = '1';
        container.innerHTML = `
<!-- Pro Recorder Container -->
<div class="pro-recorder">
    <div class="vbrec-toolbar">
        <button class="vbrec-btn vbrec-btn--start" id="startBtn">
            🎙️ Start Recording
        </button>
        <button class="vbrec-btn vbrec-btn--stop" id="stopBtn" disabled>
            ⏹️ Stop Recording
        </button>
    </div>
    <div id="vb_status" class="vbrec-status"></div>
    <div id="vb_level" class="vbrec-level"></div>
    <canvas id="vb_canvas" class="vbrec-canvas"></canvas>
    <audio id="vb_play" class="vbrec-audio" controls></audio>
    <div id="vb_download_wrap" class="vbrec-download-wrap"></div>
</div>
                font-size:1rem;
                box-shadow:0 4px 6px rgba(0,0,0,0.1);
                display:inline-flex;
                align-items:center;
                justify-content:center;
                gap:0.5rem;
              }
              #${rootId} .vbrec-btn--start { 
                background: linear-gradient(135deg,#1a365d 0%, #2d3748 100%); 
                color:#ffffff; 
              }
              #${rootId} .vbrec-btn--start:hover:not(:disabled) { 
                background: linear-gradient(135deg,#2d3748 0%, #1a365d 100%); 
                transform:translateY(-2px);
                box-shadow:0 8px 12px rgba(0,0,0,0.15);
              }
              #${rootId} .vbrec-btn--stop { 
                background:linear-gradient(135deg,#ef4444 0%, #dc2626 100%); 
                color:#ffffff;
                box-shadow:0 4px 6px rgba(239,68,68,0.2);
              }
              #${rootId} .vbrec-btn--stop:hover:not(:disabled) {
                background:linear-gradient(135deg,#dc2626 0%, #ef4444 100%);
                transform:translateY(-2px);
                box-shadow:0 8px 12px rgba(239,68,68,0.3);
              }
              #${rootId} .vbrec-btn:disabled { opacity:0.6; cursor:not-allowed; transform:none; }
              #${rootId} #vb_status { 
                font-size:0.95rem; 
                color:#0f172a; 
                font-weight:600;
                padding:0.5rem 1rem;
                background:#f8fafc;
                border-radius:8px;
              }
              #${rootId} #vb_level { 
                font-size:0.95rem; 
                color:#0f172a; 
                font-weight:600;
                padding:0.5rem 1rem;
                background:#f8fafc;
                border-radius:8px;
              }
              #${rootId} #vb_canvas { 
                margin-top:1rem; 
                width:100%; 
                height:64px; 
                background:#e2e8f0; 
                border:2px solid #cbd5e1;
                border-radius:8px; 
                box-shadow:inset 0 2px 4px rgba(0,0,0,0.05);
              }
              #${rootId} #vb_download_wrap { 
                margin-top:1rem; 
                text-align:center; 
              }
              #${rootId} #vb_download_wrap a { 
                display:inline-flex;
                align-items:center;
                gap:0.5rem;
                background:#e2e8f0;
                color:#1a365d; 
                padding:0.75rem 1.5rem;
                border-radius:10px;
                text-decoration:none;
                font-weight:600; 
                border:2px solid #94a3b8;
                transition:all 0.3s ease;
                box-shadow:0 2px 6px rgba(0,0,0,0.05);
              }
              #${rootId} #vb_download_wrap a:hover {
                background:#cbd5e1;
                border-color:#1a365d;
                transform:translateY(-2px);
                box-shadow:0 4px 12px rgba(0,0,0,0.1);
              }
            </style>
            <div class="vbrec-toolbar">
                <button id="vb_start" class="vbrec-btn vbrec-btn--start">🎙️ Start</button>
                <button id="vb_stop" class="vbrec-btn vbrec-btn--stop" disabled>⏹️ Stop</button>
                <span id="vb_status">Idle</span>
                <span id="vb_level">Level: -- dB | 0.0s</span>
            </div>
            <canvas id="vb_canvas" width="600" height="64"></canvas>
                        <audio id="vb_play" controls style="margin-top:1rem;width:100%;display:none;background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:0.5rem;"></audio>
                        <div id="vb_download_wrap" style="display:none;display:flex;gap:.5rem;align-items:center;justify-content:center;flex-wrap:wrap;margin-top:0.75rem;margin-bottom:0.75rem;">
                            <a id="vb_download" download="vocalbrand_recording.webm">⬇️ Download recording</a>
                            <button id="vb_use_btn" class="vbrec-btn vbrec-btn--primary" onClick="(function(){setTimeout(function(){window.streamlitRerun && window.streamlitRerun();}, 100)})()">
                                ✅ USE RECORDING
                            </button>
                        </div>
        `;
        const statusEl = container.querySelector('#vb_status');
        const levelEl = container.querySelector('#vb_level');
        const startBtn = container.querySelector('#vb_start');
        const stopBtn = container.querySelector('#vb_stop');
        const audioEl = container.querySelector('#vb_play');
        const canvas = container.querySelector('#vb_canvas');
        const ctx = canvas.getContext('2d');
        const STREAMLIT = window.Streamlit || null;
        let mediaRecorder, chunks = [], analyser, dataArray, rafId, startedAt = 0;
        const STORAGE_KEY = 'vb_pro_payload_v1';
        let pendingPayload = null; // {b64, mime, size, filename, ext}
        let currentObjectUrl = null;
        let autoSendScheduled = false;
        let sending = false;

        function log(m){ statusEl.textContent = m; }
        function postHeight(){
            if (STREAMLIT && STREAMLIT.setFrameHeight) {
                try { STREAMLIT.setFrameHeight(document.body.scrollHeight); } catch(_e) {}
            } else {
                try { window.parent.postMessage({isStreamlitMessage:true, type:'streamlit:setFrameHeight', height: document.body.scrollHeight }, '*'); } catch(_e) {}
            }
        }
        function postReady(){
            if (STREAMLIT && STREAMLIT.setComponentReady) {
                try { STREAMLIT.setComponentReady(); } catch(_e) {}
            } else {
                try { window.parent.postMessage({isStreamlitMessage:true, type:'streamlit:componentReady'}, '*'); } catch(_e) {}
            }
        }
        function postValue(val){
            if (STREAMLIT && STREAMLIT.setComponentValue) {
                try { STREAMLIT.setComponentValue(val); } catch(_e) {}
            } else {
                try { window.parent.postMessage({isStreamlitMessage:true, type:'streamlit:setComponentValue', value: val}, '*'); } catch(_e) {}
            }
        }

        function computeExt(mime){
            const m = (mime || '').toLowerCase();
            if (m.includes('wav')) return 'wav';
            if (m.includes('mp4') || m.includes('mpg4') || m.includes('m4a')) return 'mp4';
            if (m.includes('aac')) return 'aac';
            if (m.includes('mpeg') || m.includes('mp3')) return 'mp3';
            if (m.includes('ogg')) return 'ogg';
            return 'webm';
        }

        function savePayload(payload){
            try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(payload)); } catch(_e){}
        }

        function loadPayload(){
            try {
                const raw = sessionStorage.getItem(STORAGE_KEY);
                if (!raw) return null;
                const parsed = JSON.parse(raw);
                if (parsed && parsed.b64) return parsed;
            } catch(_e){}
            return null;
        }

        function revokeUrl(){
            if (currentObjectUrl) {
                try { URL.revokeObjectURL(currentObjectUrl); } catch(_e){}
                currentObjectUrl = null;
            }
        }

        function showPayload(payload){
            if (!payload || !payload.b64) return;
            try {
                const bin = atob(payload.b64);
                const len = bin.length;
                const bytes = new Uint8Array(len);
                for (let i = 0; i < len; i++) bytes[i] = bin.charCodeAt(i);
                const blob = new Blob([bytes], {type: payload.mime || 'audio/webm'});
                revokeUrl();
                const url = URL.createObjectURL(blob);
                currentObjectUrl = url;
                audioEl.src = url;
                audioEl.style.display = 'block';
                const dw = container.querySelector('#vb_download_wrap');
                const dl = container.querySelector('#vb_download');
                if (dw && dl) {
                    dw.style.display = 'flex';
                    const ext = payload.ext || computeExt(payload.mime || '');
                    const fname = payload.filename || `vocalbrand-recording.${ext}`;
                    dl.href = url;
                    dl.download = fname;
                }
                const kb = payload.size ? (payload.size / 1024) : (len / 1024);
                statusEl.textContent = 'Captured ' + kb.toFixed(1) + ' kB';
            } catch(err) {
                console.warn('[VB] Failed to render payload', err);
            }
        }

        function applyPayload(payload, opts = {}){
            if (!payload || !payload.b64) return;
            const ext = payload.ext || computeExt(payload.mime || '');
            const filename = payload.filename || `vocalbrand-recording.${ext}`;
            pendingPayload = {
                b64: payload.b64,
                mime: payload.mime || 'audio/webm',
                size: payload.size || 0,
                ext,
                filename,
            };
            autoSendScheduled = false;
            sending = false;
            showPayload(pendingPayload);
            savePayload(pendingPayload);
            postHeight();
            scheduleAutoSend(opts.forceRetry === true);
        }

        function scheduleAutoSend(force){
            if (!pendingPayload) return;
            if (autoSendScheduled && !force) return;
            autoSendScheduled = true;
            let attempts = 0;
            const attempt = ()=>{
                if (!pendingPayload) return;
                attempts += 1;
                sendPayload('auto');
                if (attempts < 5 && pendingPayload) {
                    setTimeout(attempt, 1200);
                } else {
                    autoSendScheduled = false;
                }
            };
            setTimeout(attempt, force ? 100 : 450);
        }

        function sendPayload(origin){
            if (!pendingPayload || sending) return;
            sending = true;
            try {
                const ta = window.parent.document && window.parent.document.getElementById('pro_recorder_payload');
                if (ta) {
                    ta.value = 'data:' + (pendingPayload.mime || 'audio/webm') + ';base64,' + pendingPayload.b64;
                    ta.dispatchEvent(new Event('input',{bubbles:true}));
                }
            } catch(_e) {}
            try { postValue({b64: pendingPayload.b64, size: pendingPayload.size || 0, mime: pendingPayload.mime || 'audio/webm'}); } catch(_e) {}
            pendingPayload.lastSent = Date.now();
            savePayload(pendingPayload);
            setTimeout(()=>{ sending = false; }, 1200);
            log(origin === 'manual' ? 'Locking in recording...' : 'Locking in recording (auto)...');
        }
        function meter(){
            if(!analyser) return;
            analyser.getByteTimeDomainData(dataArray);
            let peak=0; for(let i=0;i<dataArray.length;i++){ const v=(dataArray[i]-128)/128; const a=Math.abs(v); if(a>peak) peak=a; }
            const db = (peak>0)? (20*Math.log10(peak)).toFixed(1) : '-inf';
            const elapsed = ((performance.now()-startedAt)/1000).toFixed(1);
            levelEl.textContent = `Level: ${db} dB | ${elapsed}s`;
            // Draw waveform
            const W = canvas.width, H = canvas.height;
            ctx.fillStyle = '#e2e8f0'; ctx.fillRect(0,0,W,H);
            ctx.strokeStyle = '#1a365d'; ctx.lineWidth = 2; ctx.beginPath();
            for(let x=0; x<W; x++){
                const i = Math.floor(x / W * dataArray.length);
                const v = (dataArray[i]-128)/128;
                const y = H/2 - v * (H/2 - 4);
                if(x===0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }
            ctx.stroke();
            rafId = requestAnimationFrame(meter);
        }
        // Helper: encode an AudioBuffer to 16-bit PCM WAV (little-endian)
        function encodeWAV(audioBuffer){
            const numChannels = audioBuffer.numberOfChannels;
            const sampleRate = audioBuffer.sampleRate;
            const length = audioBuffer.length;
            const bytesPerSample = 2; // 16-bit PCM
            const blockAlign = numChannels * bytesPerSample;
            const dataSize = length * blockAlign;
            const buffer = new ArrayBuffer(44 + dataSize);
            const view = new DataView(buffer);

            function writeString(view, offset, string){
                for (let i = 0; i < string.length; i++) {
                    view.setUint8(offset + i, string.charCodeAt(i));
                }
            }

            let offset = 0;
            writeString(view, offset, 'RIFF'); offset += 4;
            view.setUint32(offset, 36 + dataSize, true); offset += 4; // ChunkSize
            writeString(view, offset, 'WAVE'); offset += 4;
            // fmt chunk
            writeString(view, offset, 'fmt '); offset += 4;
            view.setUint32(offset, 16, true); offset += 4; // Subchunk1Size (16 for PCM)
            view.setUint16(offset, 1, true); offset += 2;  // AudioFormat (1 = PCM)
            view.setUint16(offset, numChannels, true); offset += 2;
            view.setUint32(offset, sampleRate, true); offset += 4;
            view.setUint32(offset, sampleRate * blockAlign, true); offset += 4; // ByteRate
            view.setUint16(offset, blockAlign, true); offset += 2; // BlockAlign
            view.setUint16(offset, bytesPerSample * 8, true); offset += 2; // BitsPerSample
            // data chunk
            writeString(view, offset, 'data'); offset += 4;
            view.setUint32(offset, dataSize, true); offset += 4;

            // Interleave channels
            const channels = [];
            for (let c = 0; c < numChannels; c++) {
                channels.push(audioBuffer.getChannelData(c));
            }
            let pos = 44;
            for (let i = 0; i < length; i++) {
                for (let c = 0; c < numChannels; c++) {
                    let sample = channels[c][i];
                    // clamp
                    sample = Math.max(-1, Math.min(1, sample));
                    // scale to 16-bit signed int
                    view.setInt16(pos, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
                    pos += 2;
                }
            }
            return buffer;
        }

        startBtn.onclick = async ()=>{
            try{
                const stream = await navigator.mediaDevices.getUserMedia({audio:true});
                const actx = new (window.AudioContext||window.webkitAudioContext)();
                const src = actx.createMediaStreamSource(stream);
                analyser = actx.createAnalyser(); analyser.fftSize=1024;
                dataArray = new Uint8Array(analyser.fftSize);
                src.connect(analyser);
                // Initialize MediaRecorder and capture chunks (PRO RECORDER — LIGHT THEME)
                chunks = [];
                // Pick a widely-supported MIME, preferring webm+opus but falling back to mp4/aac for iOS Safari
                const mimeCandidates = [
                    'audio/webm;codecs=opus',
                    'audio/webm',
                    'audio/mp4;codecs=mp4a.40.2',
                    'audio/mp4',
                    'audio/aac',
                    'audio/mpeg',
                    'audio/ogg',
                    'audio/wav'
                ];
                let chosenMime = '';
                try {
                    const isSup = (m) => { try { return !!(window.MediaRecorder && MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(m)); } catch(e){ return false; } };
                    chosenMime = mimeCandidates.find(isSup) || '';
                } catch(e) { chosenMime = ''; }
                try {
                    mediaRecorder = chosenMime ? new MediaRecorder(stream, { mimeType: chosenMime }) : new MediaRecorder(stream);
                } catch(e) {
                    // Fallback without mimeType if browser rejects the option
                    mediaRecorder = new MediaRecorder(stream);
                }
                mediaRecorder.ondataavailable = (ev)=>{ if (ev.data && ev.data.size) { chunks.push(ev.data); } };
                mediaRecorder.onstop = async ()=>{
                    cancelAnimationFrame(rafId);
                    // Prefer the recorder-reported type if present
                    const effectiveMime = (mediaRecorder && mediaRecorder.mimeType) ? mediaRecorder.mimeType : (chosenMime || 'audio/webm');
                    const blob = new Blob(chunks,{type: effectiveMime});
                    const ab = await blob.arrayBuffer();
                    // Try to decode in-browser and re-encode to WAV for maximum compatibility
                    let wavBuffer = null;
                    try {
                        const ac = new (window.AudioContext||window.webkitAudioContext)();
                        const decoded = await ac.decodeAudioData(ab.slice(0));
                        wavBuffer = encodeWAV(decoded);
                    } catch(e) {
                        wavBuffer = null;
                    }
                    if (wavBuffer) {
                        const wbytes = new Uint8Array(wavBuffer);
                        let wbin=''; for(let i=0;i<wbytes.length;i++) wbin += String.fromCharCode(wbytes[i]);
                        const wb64 = btoa(wbin);
                        applyPayload({
                            b64: wb64,
                            mime: 'audio/wav',
                            size: wbytes.length,
                            filename: 'vocalbrand-recording.wav',
                            ext: 'wav',
                            sent: false,
                        });
                    } else {
                        // Fallback to original blob path
                        const bytes = new Uint8Array(ab);
                        let binary=''; for(let i=0;i<bytes.length;i++) binary += String.fromCharCode(bytes[i]);
                        const b64 = btoa(binary);
                        applyPayload({
                            b64,
                            mime: effectiveMime,
                            size: bytes.length,
                            sent: false,
                        });
                    }
                };
                mediaRecorder.start(); startedAt = performance.now(); log('Recording...');
                startBtn.disabled=true; stopBtn.disabled=false; meter();
            }catch(err){ log('Error: '+err.message); }
        };
        stopBtn.onclick=()=>{ if(mediaRecorder && mediaRecorder.state!=='inactive') mediaRecorder.stop(); startBtn.disabled=false; stopBtn.disabled=true; log('Processing...'); };

        // When user explicitly confirms, send payload to Streamlit and trigger rerun
        container.addEventListener('click', (e)=>{
            const t = e.target && e.target.closest ? e.target.closest('#vb_use_btn') : null;
            if (!t) return;
            if (!pendingPayload || !pendingPayload.b64) { log('No recording to use yet.'); return; }
            sendPayload('manual');
        }, {capture:true});
        postReady(); postHeight();
        window.addEventListener('message', (event)=>{
            try {
                if (!event || !event.data) return;
                if (event.origin && event.origin !== window.location.origin) return;
                const data = event.data;
                if (typeof data !== 'object' || data === null) return;
                if (data.source === 'vocalbrand' && data.type === 'VB_PRO_INGESTED') {
                    pendingPayload = null;
                    try { sessionStorage.removeItem(STORAGE_KEY); } catch(_e) {}
                    revokeUrl();
                    log('Recording locked in ✅');
                }
            } catch(_e) {}
        });
        const restored = loadPayload();
        if (restored) {
            applyPayload(restored, {forceRetry: true});
        }
    }
    init();
})();
</script>
    """
        # Capture value posted back from the HTML component (via postMessage streamlit:setComponentValue)
        pro_component_val = st.components.v1.html(
            js_template.replace("__FALLBACK_ID__", fallback_id),
            height=420,
            scrolling=False,
        )
        pro_val = None  # Removed caption and textarea - no white artifacts
        last_hash_key = "last_fallback_b64_hash"
        # Prefer direct component value; fallback to hidden textarea if needed
        b64_from_component: Optional[str] = None
        mime_from_component: Optional[str] = None
        if isinstance(pro_component_val, dict) and pro_component_val.get("b64"):
            try:
                size = int(pro_component_val.get("size") or 0)
            except Exception:
                size = 0
            # basic sanity: accept if > 1KB
            if size > 1024:
                b64_from_component = str(pro_component_val["b64"])  # plain base64 without data URL prefix
                if pro_component_val.get("mime"):
                    mime_from_component = str(pro_component_val["mime"]).strip()
        if b64_from_component:
            # Compose a robust data URL using the provided MIME when available
            if mime_from_component:
                pro_val = f"data:{mime_from_component};base64," + b64_from_component
            else:
                pro_val = "data:audio/webm;base64," + b64_from_component
        if pro_val:
            try:
                # Accept data URL or plain base64
                b64 = pro_val
                if b64.startswith("data:"):
                    b64 = b64.split(",", 1)[1]
                current_hash = hashlib.sha1(b64.encode("utf-8")).hexdigest()
                auto_needed = st.session_state.get(last_hash_key) != current_hash
                
                # 🎯 SURGICAL FIX: Preserve audio bytes BEFORE processing
                if auto_needed:
                    try:
                        # Detect MIME from data URL (if present)
                        inferred_format = None
                        if pro_val.startswith("data:"):
                            try:
                                header = pro_val.split(",",1)[0]  # data:audio/<mime>;base64
                                if ";base64" in header:
                                    header = header.split(";",1)[0]
                                if header.startswith("data:"):
                                    header = header[len("data:"):]
                                # header now like "audio/webm" or "audio/mp4" etc
                                if "/" in header:
                                    inferred_format = header.split("/",1)[1]
                            except Exception:
                                inferred_format = None
                        raw_blob = base64.b64decode(b64)
                        from pydub import AudioSegment  # type: ignore
                        # Map common mimetypes to pydub formats
                        fmt = (inferred_format or "webm").lower()
                        if fmt in ("mp4","mpg4","m4a"):
                            fmt = "mp4"
                        elif fmt in ("aac",):
                            fmt = "aac"
                        elif fmt in ("mpeg","mp3"):
                            fmt = "mp3"
                        elif fmt in ("ogg",):
                            fmt = "ogg"
                        elif fmt in ("wav",):
                            fmt = "wav"
                        else:
                            fmt = "webm"
                        seg = AudioSegment.from_file(BytesIO(raw_blob), format=fmt)
                        wav_buf = BytesIO()
                        seg.export(wav_buf, format="wav")
                        wav_bytes = wav_buf.getvalue()
                        # STORE IN SESSION STATE FIRST - survives reruns
                        st.session_state["pro_recorder_audio_preview"] = wav_bytes
                        # Auto-ingest just like the native recorder so flow continues without extra clicks
                        meta = _ingest_audio_bytes(wav_bytes, source="pro_recorder", filename="recording.wav")
                        _render_audio_feedback(meta, wav_bytes)
                        st.session_state[last_hash_key] = current_hash
                        st.session_state["pro_ingested_hash"] = current_hash
                        st.success("Recording Locked In ✅", icon="✅")
                        # Also guide the user to the upload area (covers the case when they don't press the green button)
                        st.session_state["show_guidance_message"] = True
                        st.session_state["scroll_to_upload"] = True
                        # Refresh the UI so the top-level guidance banner is shown immediately
                        st.rerun()
                        st.markdown(
                            """
                            <script>
                            (function(){
                                try { window.sessionStorage && window.sessionStorage.removeItem('vb_pro_payload_v1'); } catch (_e) {}
                                try {
                                    const frames = window.frames || [];
                                    for (let i = 0; i < frames.length; i++) {
                                        try { frames[i].postMessage({source:'vocalbrand', type:'VB_PRO_INGESTED'}, '*'); } catch (_err) {}
                                    }
                                } catch (_e) {}
                            })();
                            </script>
                            """,
                            unsafe_allow_html=True,
                        )
                    except Exception as e:
                        st.warning(f"Pro Recorder decode failed: {str(e)[:220]}")
                
                # Show persistent audio player if we have bytes
                if "pro_recorder_audio_preview" in st.session_state:
                    preview_bytes = st.session_state["pro_recorder_audio_preview"]
                    st.markdown("### 🎵 Your Recording")
                    st.audio(preview_bytes, format="audio/wav")
                    # Helpful nudge if progression stalls for any reason
                    st.info(
                        "If the next step doesn't appear after clicking \"Use This Recording\", simply upload the downloaded file using the box below to continue.",
                        icon="ℹ️",
                    )
                    
                # 🌟 ULTRA SUPREME: Ultra prominent action buttons guaranteed visible
                st.markdown("<div class='mt-1'></div>", unsafe_allow_html=True)
                st.markdown("<hr class='my-0.5' style='border-width:2px;'/>", unsafe_allow_html=True)
                
                # Ensure audio player has clean styling
                if "pro_recorder_audio_preview" in st.session_state:
                    st.markdown('''
                    <style>
                    audio {
                        width: 100% !important;
                        border-radius: 8px !important;
                        margin: 0.5rem 0 !important;
                    }
                    </style>
                    ''', unsafe_allow_html=True)
                
                # CRITICAL: Professional button with guaranteed styling
                st.markdown('''
                <style>
                /* Ensure button visibility */
                .recorder-button {
                    background: linear-gradient(135deg, #3182CE 0%, #2C5282 100%);
                    color: white;
                    padding: 12px 24px;
                    font-weight: 600;
                    border-radius: 8px;
                    text-align: center;
                    margin: 1rem 0;
                    cursor: pointer;
                    box-shadow: 0 4px 6px rgba(49, 130, 206, 0.25);
                    transition: all 0.2s ease;
                }
                .recorder-button:hover {
                    box-shadow: 0 6px 8px rgba(49, 130, 206, 0.4);
                    transform: translateY(-2px);
                }
                </style>
                <div class="recorder-button" onclick="document.getElementById('use_recording_pro_btn').click()">
                    🔒 USE THIS RECORDING
                </div>
                ''', unsafe_allow_html=True)
                
                # Hidden button that will be clicked by the div above
                force = st.button("USE THIS RECORDING", key="use_recording_pro_btn", type="primary")
                
                if force:
                    if "pro_recorder_audio_preview" in st.session_state:
                        wav_bytes = st.session_state["pro_recorder_audio_preview"]
                        meta = _ingest_audio_bytes(wav_bytes, source="pro_recorder", filename="recording.wav")
                        _render_audio_feedback(meta, wav_bytes)
                        st.success("Recording Locked In ✅", icon="✅")
                        
                        # Clear preview after use
                        del st.session_state["pro_recorder_audio_preview"]
                        st.session_state["pro_ingested_hash"] = current_hash
                        # 🌟 ULTRA SUPREME: Triple guarantee of flow continuation
                        st.session_state["force_continue_flow"] = True
                        st.session_state["completed_recording"] = True
                        # 🎯 ELEGANT SOLUTION: Store flag to show guidance message after rerun
                        st.session_state["show_guidance_message"] = True
                        # 🔑 CRITICAL: Set flow_state to 'processing' to trigger Step 2
                        st.session_state["flow_state"] = "processing"
                        st.rerun()  # 🔑 CRITICAL: Force flow continuation
                        st.markdown(
                            """
                            <script>
                            (function(){
                                try { window.sessionStorage && window.sessionStorage.removeItem('vb_pro_payload_v1'); } catch (_e) {}
                                try {
                                    const frames = window.frames || [];
                                    for (let i = 0; i < frames.length; i++) {
                                        try { frames[i].postMessage({source:'vocalbrand', type:'VB_PRO_INGESTED'}, '*'); } catch (_err) {}
                                    }
                                } catch (_e) {}
                            })();
                            </script>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.error("No recording found. Please record again.")
            except Exception as e:  # noqa: BLE001
                msg = str(e)
                if len(msg) > 220:
                    msg = msg[:220] + "…"
                st.warning(f"Pro Recorder decode failed: {msg}")
        # Show upload option alongside Pro Recorder (no early return - allow cloning section)
        render_file_upload_fallback()
        # 🎯 CRITICAL FIX: Don't return early! Let cloning section render if audio is ready
        # Skip rendering native recorders below since Pro Recorder is active
        return  # But return AFTER rendering upload, before native recorders
    
    # Prefer st_audiorec if available; it returns raw wav bytes directly
    raw_bytes: Optional[bytes] = None
    
    # 💡 Elegant browser compatibility notice
    st.info(
        "💡 **Audio recording tips:**\n\n"
        "• If the recording button doesn't respond, **refresh the page** or **open in a different browser** (Chrome/Edge recommended).\n\n"
        "• Some in-app browsers (TikTok, Instagram, Facebook) may have microphone restrictions—try opening this page in your device's default browser for best results.",
        icon="ℹ️"
    )
    
    if st_audiorec is not None:
        with st.spinner("Ready. Click microphone to start/stop"):
            wav_data = st_audiorec()  # returns bytes or None
        if wav_data:
            raw_bytes = wav_data
    elif audiorecorder is not None:
        audio = audiorecorder(
            "🎙️ Start recording",
            "⏹️ Stop recording",
            key="native_recorder_component",
        )
        if audio and len(audio) > 0:
            buffer = BytesIO()
            audio.export(buffer, format="wav")
            raw_bytes = buffer.getvalue()
    elif mic_recorder is not None:
        # mic_recorder returns a dict with 'bytes' (wav) when finished
        st.caption("Alternative recorder active (mic_recorder)")
        rec = mic_recorder(start_prompt="🎙️ Start", stop_prompt="⏹️ Stop", just_once=True, use_container_width=True, key="mr_fallback")
        if isinstance(rec, dict) and rec.get("bytes"):
            raw_bytes = rec["bytes"]

    if raw_bytes:
        meta = _ingest_audio_bytes(raw_bytes, source="native_recorder")
        _render_audio_feedback(meta, raw_bytes)
    render_file_upload_fallback()


def _validate_audio(audio_data: bytes) -> bool:
    """Validate audio data for cloning requirements."""
    try:
        if not audio_data:
            return False
            
        # Convert to AudioSegment for analysis
        from pydub import AudioSegment
        audio = AudioSegment.from_file(BytesIO(audio_data))
        
        # Check duration (30-60 seconds recommended)
        duration_ms = len(audio)
        if duration_ms < 10000:  # Minimum 10 seconds
            st.warning("⚠️ Audio is too short. Recommended duration is 30-60 seconds.")
            return False
            
        # Check volume levels
        if audio.dBFS < -35:
            st.warning("⚠️ Audio volume is too low. Please record in a quieter environment.")
            return False
            
        # Check sample rate
        if audio.frame_rate < 16000:
            st.warning("⚠️ Audio quality is too low. Please use a better microphone.")
            return False
            
        return True
        
    except Exception as e:
        st.error(f"Audio validation failed: {str(e)}")
        return False

def _trim_silence(audio_data: bytes, min_silence_len: int = 500, silence_thresh: int = -40) -> bytes:
    """Trim silence from the beginning and end of the audio."""
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(BytesIO(audio_data))
        
        # Trim silence
        trimmed = audio.strip_silence(
            silence_len=min_silence_len,
            silence_thresh=silence_thresh,
            padding=100
        )
        
        # Convert back to bytes
        buffer = BytesIO()
        trimmed.export(buffer, format="wav")
        return buffer.getvalue()
        
    except Exception as e:
        st.warning(f"Failed to trim silence: {str(e)}")
        return audio_data

def _start_cloning_process(audio_data: bytes, voice_label: str) -> None:
    """Start the voice cloning process with proper error handling."""
    try:
        with st.spinner("🔄 Cloning your voice..."):
            # Prepare audio data
            buf = BytesIO(audio_data)
            buf.name = "voice_sample.wav"
            
            # Start cloning
            result = engine.clone_voice(buf, voice_label.strip() or "VocalBrand Voice")
            
            if result.get("success") and result.get("voice_id"):
                # Update session state
                st.session_state.clone_voice_id = result.get("voice_id")
                st.session_state.clone_voice_label = voice_label
                st.session_state.clone_status = result.get("message", "")
                st.session_state.clone_timestamp = datetime.utcnow().isoformat()
                
                # Update history
                history = st.session_state.get("clone_history", [])
                history.append({
                    "voice_id": result.get("voice_id"),
                    "label": voice_label,
                    "provider": result.get("provider"),
                    "message": result.get("message"),
                    "at": st.session_state.clone_timestamp
                })
                st.session_state.clone_history = history[-15:]  # Keep last 15 entries
                
                # Show success
                st.success(f"✨ Voice cloned successfully! Voice ID: {result.get('voice_id')}")
                st.session_state.flow_state = "complete"
                
            else:
                error_msg = result.get("message", "Voice cloning failed")
                error_detail = result.get("error_detail", "")
                st.error(f"❌ **Voice Cloning Failed**\n\n{error_msg}")
                if error_detail:
                    with st.expander("🔍 Technical Details"):
                        st.code(error_detail)
                st.session_state.flow_state = "ready"
                
    except Exception as e:
        st.error(f"❌ An error occurred during cloning: {str(e)}")
        st.session_state.flow_state = "ready"

def _render_audio_feedback(meta: Dict[str, Any], raw_bytes: bytes) -> None:
    """Render audio feedback with waveform visualization."""
    if meta.get("ok"):
        st.success("Sample captured and validated ✅")
    else:
        st.warning(meta.get("message", "Audio validation warning"))
        
    # Audio stats
    dur = meta.get("duration")
    loud = meta.get("loudness_dbfs")
    qual = meta.get("quality", {})
    if dur is not None:
        st.caption(f"Duration: {dur:.1f}s | Loudness: {loud:.1f} dBFS" if isinstance(loud, (int, float)) else f"Duration: {dur:.1f}s")
    # Post-capture waveform visualization (downsampled)
    try:
        import numpy as np  # type: ignore
        from pydub import AudioSegment  # type: ignore
        seg = AudioSegment.from_file(BytesIO(raw_bytes))
        arr = np.array(seg.get_array_of_samples())
        if seg.channels > 1:
            arr = arr.reshape((-1, seg.channels)).mean(axis=1)
        # Downsample to ~1200 points for light plotting
        target = 1200
        if len(arr) > target:
            step = len(arr) // target
            arr = arr[: target * step]
            arr = arr.reshape(-1, step).mean(axis=1)
        # Normalize to [-1, 1] for cleaner axis
        maxv = float(np.max(np.abs(arr))) or 1.0
        arr = (arr / maxv).astype("float32")
        st.line_chart(arr, height=120)
    except Exception:
        pass
    if os.getenv("DEBUG_LOGGING", "0") == "1":
        with st.expander("Sample diagnostics", expanded=False):
            safe_meta = {k: v for k, v in meta.items() if k not in {"raw_bytes"}}
            st.json(json.loads(json.dumps(safe_meta, default=str)))


def render_clone_section() -> None:
    """Render the world-class voice cloning section."""
    st.markdown("""
        <style>
        .clone-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2); color: white; }
        .clone-title { font-size: 32px; font-weight: 900; margin-bottom: 8px; }
        .clone-subtitle { font-size: 15px; opacity: 0.95; }
        .step-header { font-size: 18px; font-weight: 700; margin: 20px 0 15px 0; color: #1a202c; }
        .preview-box { background: white; padding: 25px; border-radius: 12px; border: 2px solid #667eea; margin: 20px 0; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="clone-header"><div class="clone-title">✨ Voice Cloning</div><div class="clone-subtitle">3-step process to clone your voice</div></div>', unsafe_allow_html=True)
    st.caption("📋 Pro plan: 30 TTS minutes/month")
    
    # Initialize session state
    for key, val in {"flow_state": "initial", "audio_data": None, "audio_meta": None, "clone_voice_label": "My VocalBrand Voice"}.items():
        if key not in st.session_state:
            st.session_state[key] = val
    
    # 💪 Safety net: if audio is staged but flow didn't advance, push to Step 2
    _maybe_force_flow_progression()

    # 🎯 SUPREME FIX: Show guidance message FIRST if user just recorded with green button
    if st.session_state.get("show_guidance_message"):
        st.info(
            "**✨ Next Step - Easy Upload:**\n\n"
            "Your recording has been downloaded to your device. Now simply:\n\n"
            "1️⃣ **Drag & drop** the downloaded audio file below, OR\n"
            "2️⃣ **Click the upload button** to browse and select it\n\n"
            "The drag-and-drop method works seamlessly with all audio formats (WAV, MP3, M4A, AAC) ✅",
            icon="📁"
        )
        # Clear the flag after showing once
        st.session_state["show_guidance_message"] = False
        # If requested, scroll the viewport to the upload box anchor
        if st.session_state.get("scroll_to_upload"):
            st.markdown(
                """
                <script>
                try { window.location.hash = '#vb-upload'; } catch(e) {}
                </script>
                """,
                unsafe_allow_html=True,
            )
            st.session_state["scroll_to_upload"] = False
        # Add small spacing
        st.markdown("---")
    
    # Step 1: Record/Upload
    # 🔑 CRITICAL: Skip Step 1 UI if flow already processing (green button case)
    if st.session_state.flow_state in ["initial"]:
        st.markdown('<div class="step-header">Step 1️⃣: Record or Upload Your Voice</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.checkbox("✂️ Trim silence", key="trim_silence_toggle")
        with col2:
            st.checkbox("⚡ Auto-proceed", key="auto_clone_toggle")

        # Friendly nudge: if browser blocks an automatic event, guide the user immediately
        st.info(
            "If clicking 'Use This Recording' doesn't move to the next step, simply upload the downloaded file using the box below. This works with WAV, MP3, M4A, AAC, OGG, FLAC, AIFF, or WEBM.",
            icon="ℹ️",
        )
        
        audio_data = render_audio_capture_area()
        
        if audio_data is not None:
            if isinstance(audio_data, bytes):
                st.session_state.audio_data = audio_data
                st.session_state.audio_meta = {"ok": True, "filename": "recording.wav", "type": "audio/wav", "source": "recorder"}
                st.session_state.flow_state = "processing"
                st.rerun()
            elif hasattr(audio_data, 'read'):
                try:
                    st.session_state.audio_data = audio_data.read()
                    st.session_state.audio_meta = {"ok": True, "filename": audio_data.name, "type": audio_data.type, "source": "upload"}
                    st.session_state.flow_state = "processing"
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Upload failed: {str(e)}")
                    return
    
    # Step 2: Preview
    if st.session_state.flow_state in ["processing", "ready"]:
        st.markdown('<div class="step-header">Step 2️⃣: Preview & Validate</div>', unsafe_allow_html=True)
        if st.session_state.flow_state == "processing":
            with st.spinner("🔄 Processing..."):
                if st.session_state.get("trim_silence_toggle"):
                    st.session_state.audio_data = _trim_silence(st.session_state.audio_data)
                if _validate_audio(st.session_state.audio_data):
                    st.session_state.flow_state = "ready"
                    st.success("✅ Audio validated!")
                else:
                    st.error("❌ Validation failed")
                    if st.button("🔄 Try Again"):
                        st.session_state.flow_state = "initial"
                        st.session_state.audio_data = None
                        st.rerun()
                    return
        
        if st.session_state.flow_state == "ready":
            st.markdown('<div class="preview-box">', unsafe_allow_html=True)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("**Your Voice Sample**")
                st.audio(st.session_state.audio_data, format="audio/wav")
            with col2:
                st.markdown("**Source**")
                st.metric("", st.session_state.audio_meta.get("source", "unknown").title())
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Step 3: Clone
            st.markdown('<div class="step-header">Step 3️⃣: Create Clone</div>', unsafe_allow_html=True)
            voice_label = st.text_input("Voice name", value=st.session_state.clone_voice_label, placeholder="e.g., Professional Speaker", key="clone_voice_label_input")
            st.session_state.clone_voice_label = voice_label
            
            col1, col2 = st.columns([2, 1])
            with col1:
                if st.button("🚀 Start Cloning", type="primary", use_container_width=True):
                    _start_cloning_process(st.session_state.audio_data, voice_label)
            with col2:
                if st.button("↩️ Discard", use_container_width=True):
                    st.session_state.flow_state = "initial"
                    st.session_state.audio_data = None
                    st.rerun()
    
    # Show completion with option to clone another voice
    if st.session_state.flow_state == "complete":
        st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 12px; color: white; text-align: center; margin: 20px 0;">
                <h2 style="margin: 0 0 10px 0;">🎉 Voice Cloned Successfully!</h2>
                <p style="font-size: 16px; margin: 10px 0;">Your voice is ready to use for text-to-speech generation</p>
            </div>
        """, unsafe_allow_html=True)
        # Fallback guidance in case navigation doesn't auto-switch on some Streamlit versions
        st.info("Next step: open the left Navigation and choose ‘Generate Speech’ to synthesize audio with your new voice.")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("📝 Generate Speech", type="primary", use_container_width=True):
                # Navigate directly to the Generate Speech page by updating the sidebar radio state
                st.session_state["nav_page"] = "Generate Speech"
                st.rerun()
        with col2:
            if st.button("🎙️ Clone Another Voice", use_container_width=True):
                # Reset state to record another voice
                st.session_state.flow_state = "initial"
                st.session_state.audio_data = None
                st.session_state.audio_meta = None
                st.session_state.clone_voice_label = "My VovalBrand Voice"
                st.rerun()


def render_generation_section() -> None:
    st.subheader("Generate speech")
    # Visual-only note (policy, not enforced by code)
    st.caption(
        "Usage policy: Pro includes 30 TTS minutes/month. Additional usage via Minutes Packs (sold by Payment Links)."
    )
    voice_id = st.session_state.get("clone_voice_id", "")
    
    # CRITICAL: Validate voice_id before allowing generation
    if not voice_id:
        st.warning("⚠️ **Clone a voice before generating audio.**\n\nGo to the Voice Cloning section above to record and clone your voice first.")
        return
    
    # CRITICAL: Validate voice_id format (ElevenLabs IDs are alphanumeric, 20-30 chars)
    if len(voice_id) < 15 or not any(c.isdigit() for c in voice_id) or not any(c.isalpha() for c in voice_id):
        st.error(
            f"❌ **Invalid voice ID detected:** `{voice_id}`\n\n"
            "This usually happens when voice cloning failed but wasn't properly handled.\n\n"
            "**Please re-clone your voice using the Voice Cloning section above.**"
        )
        # Clear the invalid voice ID
        st.session_state["clone_voice_id"] = ""
        if st.button("Clear Invalid Voice & Restart"):
            st.session_state["clone_voice_id"] = ""
            st.session_state["clone_status"] = ""
            st.rerun()
        return
    
    st.caption(f"✅ Voice ID: `{voice_id}`")
    voice_label = st.session_state.get("clone_voice_label", "Your Voice")
    if voice_label:
        st.caption(f"Voice: **{voice_label}**")
    with st.expander("Language tips (i)", expanded=False):
        st.markdown(
            "- For English: use the default model and write clean sentences.\n"
            "- For other languages (Portuguese, Spanish, etc.): switch to 'eleven_multilingual_v2'.\n"
            "- Use correct punctuation (commas, periods, question marks) to shape rhythm and prosody.\n"
            "- Provide text with proper diacritics (e.g., Portuguese accents) for better pronunciation.\n"
            "- If pronunciation drifts, re-clone with a sample in the target language and try again."
        )
    prompt = st.text_area("What should this voice say?", height=180, key="tts_prompt")
    col1, col2 = st.columns(2)
    with col1:
        model_id = st.selectbox("Model", [DEFAULT_MODEL_ID, "eleven_multilingual_v2"], index=0)
    with col2:
        output_format = st.selectbox("Output format", [DEFAULT_OUTPUT_FORMAT, "mp3_44100_192", "wav"], index=0)

    # Use database-based counter for free users (persists across sessions/refreshes)
    user_id = st.session_state.get("user_id")
    used_generations = 0
    if user_id and not st.session_state.get("subscription_active"):
        used_generations = get_free_usage(user_id)
    
    disabled = not prompt.strip()
    if not st.session_state.get("subscription_active"):
        st.info(f"Free plan usage: {used_generations}/{FREE_LIMIT} generations")
        if used_generations >= FREE_LIMIT:
            st.error("Free usage limit reached. Upgrade to continue.")
            disabled = True

    if st.button("Generate speech", type="primary", disabled=disabled):
        with st.spinner("Generating with ElevenLabs..."):
            success, audio_buffer, status = engine.text_to_speech(
                prompt.strip(),
                voice_id,
                model_id=model_id,
                output_format=output_format,
            )
        if not success or not audio_buffer:
            st.error(f"Generation failed: {status}")
            return
        audio_bytes = audio_buffer.getvalue()
        st.audio(audio_bytes, format="audio/mpeg" if "mp3" in output_format else "audio/wav")
        st.download_button(
            "Download audio",
            data=audio_bytes,
            file_name=f"vocalbrand_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{'mp3' if 'mp3' in output_format else 'wav'}",
            mime="audio/mpeg" if "mp3" in output_format else "audio/wav",
        )
        
        # Increment persistent usage counter for free users
        if user_id and not st.session_state.get("subscription_active"):
            increment_free_usage(user_id)
        
        history = st.session_state.get("tts_history", [])
        history.append(
            {
                "prompt": prompt.strip()[:180],
                "voice_id": voice_id,
                "status": status,
                "generated_at": datetime.utcnow().isoformat(),
                "format": output_format,
                "bytes": len(audio_bytes),
            }
        )
        st.session_state["tts_history"] = history[-25:]
        st.success("Audio generated and saved to history.")


def render_upgrade_section(container: Any) -> None:
    """Render upgrade section with prominently visible banner - COSMIC FIX."""
    # PROMINENTLY VISIBLE UPGRADE BANNER - COSMIC FIX
    container.markdown(
        """
        <div class="vb-banner vb-banner--upgrade" style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; 
            padding: 20px !important; 
            border-radius: 12px !important; 
            color: white !important; 
            margin-bottom: 20px !important;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2) !important;
            border: none !important;
            display: block !important;
            position: relative !important;
            z-index: 1000 !important;
        ">
            <div class="vb-banner__title" style="font-size: 1.5rem; font-weight: 800; margin-bottom: 8px; color: white;">
                ✨ Upgrade to VocalBrand Pro
            </div>
            <div class="vb-banner__sub" style="font-size: 1rem; opacity: 0.95; color: white;">
                Unlimited generations • Priority processing • Commercial use
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # Feature bullets (kept for clarity/SEO) - styled inline to prevent white artifact boxes
    container.markdown(
        """
        <div style="color:#0f172a; line-height:1.8; margin-bottom:1rem;">
        <strong style="color:#0f172a;">Pro Features:</strong><br>
        • Unlimited voice generations<br>
        • Priority processing<br>
        • Commercial license<br>
        • Advanced voice controls<br>
        • 24/7 premium support
        </div>
        """,
        unsafe_allow_html=True,
    )
    if payment_manager is None:
        container.info("Stripe key missing. Configure STRIPE_API_KEY to enable billing.")
        return
    # Gate behind login
    if not st.session_state.get("user_id"):
        container.info("Log in to start a premium subscription.")
        return
    
    # Main subscription options
    container.markdown("---")
    container.markdown('<div class="vb-section-title">💎 Subscription Plans</div>', unsafe_allow_html=True)
    
    user_ref = f"user_{st.session_state['user_id']}"
    # Ensure annual_link is always defined for later checks
    annual_link: Optional[str] = None
    
    # Monthly subscription (in-app checkout)
    with container.container():
        container.markdown('<div class="vb-section-title" style="font-size:1.15rem;">Monthly Pro</div>', unsafe_allow_html=True)
        container.caption("Unlimited generations, cancel anytime")
        if st.button("€29/mo", key="upgrade_btn_monthly", use_container_width=True):
            url, checkout_id = payment_manager.create_checkout_session(user_ref, plan="monthly")
            st.session_state["latest_checkout_id"] = checkout_id
            st.link_button("Open checkout →", url, type="primary")
        container.markdown("")
    
    # Annual subscription (in-app checkout if price ID configured, otherwise Payment Link)
    if payment_manager.price_id_annual:
        # Use in-app checkout with annual price ID
        with container.container():
            container.markdown('<div class="vb-section-title" style="font-size:1.15rem;">Annual Pro</div>', unsafe_allow_html=True)
            container.caption("Save 17% (€290/year vs €348/year)")
            if st.button("€290/yr", key="upgrade_btn_annual", use_container_width=True):
                url, checkout_id = payment_manager.create_checkout_session(user_ref, plan="annual")
                st.session_state["latest_checkout_id"] = checkout_id
                st.link_button("Open checkout →", url, type="primary")
            container.markdown("")
    else:
        # Fall back to Payment Link if annual price ID not configured
        annual_link = os.getenv("ANNUAL_PAYMENT_LINK")
        if annual_link:
            with container.container():
                container.markdown('<div class="vb-section-title" style="font-size:1.15rem;">Annual Pro</div>', unsafe_allow_html=True)
                container.caption("Save 17% (€290/year vs €348/year)")
                st.link_button("€290/yr →", annual_link, type="primary")
                container.markdown("")
    
    # One-time professional services
    setup_prices = {
        "Setup — Professional": ("€497", SETUP_PRO_PRICE_ID, "60 min"),
        "Setup — Enterprise": ("€997", SETUP_ENT_PRICE_ID, "120 min"),
    }
    visible_setups = [(label, price, price_id, duration) for label, (price, price_id, duration) in setup_prices.items() if price_id]
    
    if visible_setups:
        container.markdown("---")
        container.markdown('<div class="vb-section-title">🚀 Professional Onboarding</div>', unsafe_allow_html=True)
        container.caption("One-time guided setup services for teams and enterprises")
        
        for idx, (label, price, price_id, duration) in enumerate(visible_setups):
            with container.container():
                container.markdown(f'<div class="vb-section-title" style="font-size:1.05rem;">{label}</div>', unsafe_allow_html=True)
                container.caption(f"{duration} guided setup & Q&A")
                if st.button(f"{price} →", key=f"setup_{idx}_{price_id}", type="secondary", use_container_width=True):
                    url, checkout_id = payment_manager.create_checkout_session(user_ref, plan="setup", price_id=price_id, mode="payment")
                    st.session_state["latest_checkout_id"] = checkout_id
                    st.link_button("Open checkout →", url, type="primary")
                container.markdown("")
        # Developer note: if Payment Links are shown but price ID envs are missing, remind to set them
        if os.getenv("DEBUG_LOGGING", "0") == "1":
            missing_envs: List[str] = []
            if any("Professional" in lbl for lbl, _, _, _ in visible_setups) and not (SETUP_PRO_PRICE_ID):
                missing_envs.append("SETUP_PRO_PRICE_ID")
            if any("Enterprise" in lbl for lbl, _, _, _ in visible_setups) and not (SETUP_ENT_PRICE_ID):
                missing_envs.append("SETUP_ENT_PRICE_ID")
            if missing_envs:
                container.caption(
                    "Dev: Set price IDs for automatic entitlements → " + ", ".join(missing_envs)
                )
    
    # Minutes packs for additional usage
    pack_prices = {
        "60 min": ("€89", PACK60_PRICE_ID),
        "300 min": ("€399", PACK300_PRICE_ID),
        "1000 min": ("€1,299", PACK1000_PRICE_ID),
    }
    visible_packs = [(label, price, price_id) for label, (price, price_id) in pack_prices.items() if price_id]
    
    if visible_packs:
        container.markdown("---")
        container.markdown('<div class="vb-section-title">⚡ Additional Minutes Packs</div>', unsafe_allow_html=True)
        container.caption("Premium voice minutes for professional use cases")
        
        for idx, (label, price, price_id) in enumerate(visible_packs):
            with container.container():
                container.markdown(f'<div class="vb-section-title" style="font-size:1.05rem;">Voice Minutes Pack {label}</div>', unsafe_allow_html=True)
                if st.button(f"{price} →", key=f"pack_{idx}_{price_id}", use_container_width=True):
                    url, checkout_id = payment_manager.create_checkout_session(user_ref, plan="pack", price_id=price_id, mode="payment")
                    st.session_state["latest_checkout_id"] = checkout_id
                    st.link_button("Open checkout →", url, type="primary")
                container.markdown("")
        # Developer note for entitlement mapping of packs
        if os.getenv("DEBUG_LOGGING", "0") == "1":
            missing_envs: List[str] = []
            if any(lbl == "60 min" for lbl, _, _ in visible_packs) and not (PACK60_PRICE_ID):
                missing_envs.append("PACK60_PRICE_ID")
            if any(lbl == "300 min" for lbl, _, _ in visible_packs) and not (PACK300_PRICE_ID):
                missing_envs.append("PACK300_PRICE_ID")
            if any(lbl == "1000 min" for lbl, _, _ in visible_packs) and not (PACK1000_PRICE_ID):
                missing_envs.append("PACK1000_PRICE_ID")
            if missing_envs:
                container.caption(
                    "Dev: Set price IDs for automatic entitlements → " + ", ".join(missing_envs)
                )
    
    # Help section
    if visible_setups or visible_packs or annual_link:
        container.markdown("---")
        
        # Critical: explain automatic activation
        container.info(
            "💡 **Automatic Activation:** Credits are added instantly after payment. "
            "All purchases use the same secure checkout flow as Pro subscriptions."
        )
        
        with container.expander("💡 Payment Options FAQ", expanded=False):
            container.markdown(
                """
                **What's included in subscriptions?**
                - Monthly Pro (€29/mo): Unlimited generations, priority processing, commercial license
                - Annual Pro (€290/yr): Same as Monthly, but 17% cheaper (2 months free)
                
                **What are Setup services?**
                - One-time onboarding sessions (not recurring). Video call with our team to help you integrate VocalBrand into your workflow.
                - Professional (€497): 60 min session, best for solo entrepreneurs and small teams
                - Enterprise (€997): 120 min session, best for agencies and larger teams
                
                **What are Minutes Packs?**
                - Additional TTS minutes for billing/accounting purposes.
                - These purchases track usage but don't automatically change in-app quotas while features are locked.
                - For account crediting or custom enterprise pricing, use the Contact page.
                
                **How do I switch between Monthly and Annual?**
                - Cancel your Monthly subscription in Stripe, then purchase Annual via the Payment Link above.
                - Need help with the switch? Visit the Contact page for assistance.
                """
            )
            
            # Add Contact Support button prominently
            if container.button("📧 Contact Support", key="contact_from_faq", use_container_width=True):
                st.session_state["nav_page"] = "Contact"
                safe_rerun()
    
    if st.session_state.get("latest_checkout_id"):
        container.caption(f"Latest checkout: {st.session_state['latest_checkout_id']}")


def render_account_panel() -> None:
    st.sidebar.markdown("## Account")
    if st.session_state.get("user_id"):
        st.sidebar.success(f"Signed in as {st.session_state['user_email']}")
        sub_active = st.session_state.get("subscription_active")
        st.sidebar.markdown(f"**Subscription:** {'Active 💎' if sub_active else 'Free tier'}")
        
        # Show purchased balances
        user_id = st.session_state["user_id"]
        minutes_bal = get_minutes_balance(user_id)
        setup_bal = get_setup_credits(user_id)
        
        if minutes_bal > 0 or setup_bal > 0:
            st.sidebar.markdown("---")
            st.sidebar.markdown("**Your Credits:**")
            if minutes_bal > 0:
                st.sidebar.markdown(f"⚡ Minutes: **{minutes_bal}** min")
            if setup_bal > 0:
                st.sidebar.markdown(f"🚀 Setup credits: **{setup_bal}**")
    
    if st.sidebar.button("Log out", key="logout_btn", use_container_width=True):
        logout()
    else:
        st.sidebar.info("Create an account to unlock cloning and TTS.")
    render_upgrade_section(st.sidebar)
    # Only show system status if DEBUG_LOGGING is explicitly enabled
    if os.getenv("DEBUG_LOGGING", "0") == "1":
        st.sidebar.markdown("---")
        with st.sidebar.expander("System status", expanded=False):
            st.markdown(
                f"- Recorder: {'✅' if HAS_NATIVE_RECORDER else '⚠️'} {RECORDER_STATUS} — {RECORDER_MSG or 'ready'}\n"
                f"- FFmpeg: {FFMPEG_PATH or 'not found'}\n"
                f"- ElevenLabs key: {'configured' if ELEVENLABS_KEY else 'missing'}\n"
                f"- Engine offline: {engine.offline} ({engine.offline_reason})"
            )


def login_section() -> None:
    st.header("Welcome to VocalBrand")
    st.write("Create or log into your account to access cloning and speech generation.")
    tabs = st.tabs(["Sign in", "Create account"])
    with tabs[0]:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Sign in", type="primary")
            if submitted:
                # CRITICAL: Validate inputs before authentication
                email_stripped = (email or "").strip()
                password_stripped = (password or "").strip()
                
                if not email_stripped:
                    st.error("❌ Email is required. Please enter your email address.")
                    return
                
                if not password_stripped:
                    st.error("❌ Password is required. Please enter your password.")
                    return
                
                if len(email_stripped) < 3 or "@" not in email_stripped:
                    st.error("❌ Invalid email format. Please enter a valid email address.")
                    return
                
                if len(password_stripped) < 6:
                    st.error("❌ Password must be at least 6 characters long.")
                    return
                
                ok, uid = authenticate(email_stripped, password_stripped)
                if ok and uid:
                    user = get_user(uid)
                    if user:
                        st.session_state["user_id"] = user["id"]
                        st.session_state["user_email"] = user["email"]
                        st.session_state["subscription_active"] = bool(user.get("subscription_active"))
                        st.success("✅ Signed in successfully.")
                        safe_rerun(0.05)
                        return
                st.error("❌ Invalid credentials. Please check your email and password.")
    with tabs[1]:
        with st.form("register_form"):
            email = st.text_input("Work email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            submitted = st.form_submit_button("Create account", type="primary")
            if submitted:
                # CRITICAL: Validate inputs before registration
                email_stripped = (email or "").strip()
                password_stripped = (password or "").strip()
                
                if not email_stripped:
                    st.error("❌ Email is required. Please enter your email address.")
                    return
                
                if not password_stripped:
                    st.error("❌ Password is required. Please create a password.")
                    return
                
                if len(email_stripped) < 3 or "@" not in email_stripped:
                    st.error("❌ Invalid email format. Please enter a valid email address.")
                    return
                
                if len(password_stripped) < 6:
                    st.error("❌ Password must be at least 6 characters long.")
                    return
                
                ok, message = register_user(email_stripped, password_stripped)
                if ok:
                    st.success("✅ Account created. Sign in using your credentials.")
                else:
                    st.warning(f"⚠️ Registration failed: {message}")


def render_metrics_panel() -> None:
    if os.getenv("DEBUG_LOGGING", "0") != "1":
        return
    with st.expander("Diagnostics", expanded=False):
        st.markdown("#### Hash backend")
        st.json(hash_backend_status())
        st.markdown("#### Recorder status")
        st.json(
            {
                "has_native": HAS_NATIVE_RECORDER,
                "status": RECORDER_STATUS,
                "ffmpeg": FFMPEG_PATH,
                "ffprobe": FFPROBE_PATH,
                "message": RECORDER_MSG,
            }
        )
        st.markdown("#### Recorder bridge history")
        if BRIDGE_STATE.history:
            st.json(BRIDGE_STATE.history[-5:])
        else:
            st.write("No captures yet.")
        if not st.session_state.get("pending_audio_bytes") and BRIDGE_STATE.history:
            if st.button("Adopt last capture (force)"):
                # Try reconstructing using stored meta + (not stored raw bytes, so only meta adoption)
                last = BRIDGE_STATE.history[-1]
                st.warning("Adopted metadata only (raw bytes not cached). Re-record for full pipeline.")
                st.session_state["pending_audio_meta"] = last


def page_onboarding() -> None:
    """Enhanced onboarding with clear value propositions and step-by-step guidance."""
    
    # Hero section with emotional appeal
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 2.5rem; font-weight: 700; 
                   background: linear-gradient(135deg, #1a365d 0%, #d4af37 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   margin-bottom: 1rem;">
            🎙️ Welcome to VocalBrand Supreme
        </h1>
        <p style="font-size: 1.2rem; color: #64748b; max-width: 700px; margin: 0 auto;">
            Transform your voice into a digital asset. Clone once, generate unlimited professional audio in seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick start steps with visual indicators
    st.markdown('<div class="vb-section-title">🚀 Get Started in 4 Simple Steps</div>', unsafe_allow_html=True)
    
    from utils.ui import render_steps
    render_steps(1, 4)  # Show we're on step 1 of 4
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="vb-card" style="text-align: center; min-height: 180px;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎤</div>
            <strong>1. Record Sample</strong>
            <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem;">
                30-60 seconds of clear voice in a quiet space
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="vb-card" style="text-align: center; min-height: 180px;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🧬</div>
            <strong>2. Clone Voice</strong>
            <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem;">
                AI analyzes your voice patterns & creates a unique voice ID
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="vb-card" style="text-align: center; min-height: 180px;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">✍️</div>
            <strong>3. Write Script</strong>
            <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem;">
                Enter any text you want spoken in your voice
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="vb-card" style="text-align: center; min-height: 180px;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎵</div>
            <strong>4. Generate Audio</strong>
            <p style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem;">
                Download professional audio in MP3 or WAV format
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Social proof and trust indicators
    st.markdown('<div class="vb-section-title">💎 Why VocalBrand Supreme?</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        from utils.ui import vb_stat_card
        vb_stat_card("success", "99.9%", "Uptime", "Enterprise-grade reliability")
    
    with col2:
        from utils.ui import vb_stat_card
        vb_stat_card("info", "4", "Premium Voices", "Automatic fallback protection")
    
    with col3:
        from utils.ui import vb_stat_card
        vb_stat_card("brand", "<1.2s", "Average Latency", "Lightning-fast generation")
    
    st.markdown("---")
    
    # Use cases to inspire users
    st.markdown('<div class="vb-section-title">🎯 Perfect For</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Content Creators:**
        - 🎬 YouTube voiceovers
        - 🎙️ Podcast production
        - 📱 Social media content
        - 🎮 Gaming commentary
        
        **Business Professionals:**
        - 📞 IVR & phone systems
        - 📧 Email marketing videos
        - 🎓 Training materials
        - 🔔 Notification systems
        """)
    
    with col2:
        st.markdown("""
        **Agencies & Teams:**
        - 🏢 Client presentations
        - 📊 Demo videos
        - 🌐 Website audio
        - 🎯 Ad campaigns
        
        **Educators & Trainers:**
        - 📚 E-learning courses
        - 🎤 Audiobooks
        - 🧑‍🏫 Lecture recordings
        - 📖 Educational content
        """)
    
    st.markdown("---")
    
    # System metrics in an elegant expander
    with st.expander("📊 System Performance Metrics", expanded=False):
        render_metrics_panel()
    
    # Call to action
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; 
                border-radius: 12px; 
                color: white; 
                text-align: center;
                margin-top: 2rem;">
        <h3 style="margin: 0 0 1rem 0;">Ready to Clone Your Voice? 🚀</h3>
        <p style="margin: 0 0 1rem 0; opacity: 0.95;">
            Head to the <strong>Clone Voice</strong> page to get started, or explore <strong>Generate Speech</strong> to try our demo voices!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick tips section
    st.markdown("---")
    st.markdown("### 💡 Pro Tips for Best Results")
    
    with st.expander("🎤 Recording Quality Tips"):
        st.markdown("""
        **For best voice cloning results:**
        
        ✅ **DO:**
        - Record in a quiet room (no background noise)
        - Speak naturally and clearly
        - Use good quality microphone (built-in is usually fine)
        - Read varied content with different emotions
        - Aim for 60 seconds of audio
        - Maintain consistent volume
        
        ❌ **AVOID:**
        - Recording in noisy environments
        - Speaking too close or too far from mic
        - Monotone reading
        - Audio shorter than 30 seconds
        - Distorted or clipped audio
        - Multiple speakers in the sample
        """)
    
    with st.expander("⚡ Speed & Quality"):
        st.markdown("""
        **Voice Cloning Speed:**
        - Typically completes in 30-45 seconds
        - Processing happens on ElevenLabs servers
        - You'll get a unique voice ID instantly
        
        **Generation Speed:**
        - Most generations: < 2 seconds
        - Average: 1.2 seconds
        - Longer texts may take 3-5 seconds
        - Premium users get priority processing
        """)
    
    with st.expander("💎 Upgrading to Pro"):
        st.markdown("""
        **Free Tier Includes:**
        - 3 test generations to try the system
        - Access to demo voices
        - Basic voice cloning
        
        **Pro Tier Gets You:**
        - ✨ **Unlimited generations**
        - ⚡ Priority processing queue
        - 💼 Commercial license
        - 🎛️ Advanced voice controls
        - 🛟 24/7 premium support
        - 🎯 No rate limits
        
        **Pricing:**
        - Monthly: €29/month (cancel anytime)
        - Annual: €290/year (save 17% - 2 months free!)
        
        👉 Check the sidebar for upgrade options
        """)



def page_clone() -> None:
    render_clone_section()


def page_generate() -> None:
    render_generation_section()
    if st.session_state.get("tts_history"):
        with st.expander("Generation history", expanded=False):
            st.json(st.session_state["tts_history"][::-1][:10])


def page_admin() -> None:
    st.subheader("Admin dashboard")
    st.write("Recent clones")
    st.json(st.session_state.get("clone_history", [])[-10:])
    st.write("Recorder hits", BRIDGE_STATE.hits)
    st.write("Latest bridge payload")
    st.json(BRIDGE_STATE.snapshot())


def page_contact() -> None:
    """Contact form page with enhanced UX."""
    st.title("📧 Contact Us")
    
    # Professional hero section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; 
                border-radius: 12px; 
                color: white; 
                margin-bottom: 2rem;
                text-align: center;">
        <h3 style="margin: 0 0 0.5rem 0;">We're Here to Help! 🚀</h3>
        <p style="margin: 0; opacity: 0.95;">
            Have questions about pricing, features, or need technical support? 
            Our team typically responds within 24 hours.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if email is configured
    if not is_email_configured():
        st.warning("""
        ⚠️ **Contact form is currently being configured.** 
        
        In the meantime, you can reach us through:
        - Our support portal (check your account dashboard)
        - The in-app chat feature
        - Your account manager if you're on a premium plan
        """)
        return
    
    # Contact form with better visual hierarchy
    with st.form("contact_form", clear_on_submit=True):
        st.markdown("### Send us a message")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Your Name *", 
                placeholder="Jane Smith",
                help="How should we address you?"
            )
        
        with col2:
            email = st.text_input(
                "Your Email *", 
                placeholder="jane@company.com",
                help="We'll reply to this address"
            )
        
        # Subject dropdown for better categorization
        subject_options = [
            "General Question",
            "Pricing & Billing",
            "Technical Support",
            "Feature Request",
            "Bug Report",
            "Partnership Inquiry",
            "Other"
        ]
        subject_type = st.selectbox(
            "Subject Category *",
            subject_options,
            help="Help us route your message to the right team"
        )
        
        subject_detail = st.text_input(
            "Subject Details *",
            placeholder="Brief description of your inquiry...",
            help="A short summary helps us respond faster"
        )
        
        message = st.text_area(
            "Your Message *",
            placeholder="Please provide as much detail as possible. For technical issues, include:\n• What you were trying to do\n• What happened instead\n• Any error messages you saw",
            height=200,
            help="The more details you provide, the better we can help"
        )
        
        # Combine subject for email
        full_subject = f"[{subject_type}] {subject_detail}" if subject_detail else subject_type
        
        # Submit button with enhanced styling
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "📨 Send Message", 
                use_container_width=True,
                type="primary"
            )
        
        if submitted:
            # Validate inputs with helpful error messages
            errors = []
            if not name or len(name.strip()) < 2:
                errors.append("Please enter your full name (at least 2 characters)")
            if not email or "@" not in email or "." not in email.split("@")[-1]:
                errors.append("Please enter a valid email address")
            if not subject_detail or len(subject_detail.strip()) < 3:
                errors.append("Please provide a subject (at least 3 characters)")
            if not message or len(message.strip()) < 10:
                errors.append("Please provide a detailed message (at least 10 characters)")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Send email with loading state
                with st.spinner("✨ Sending your message..."):
                    success, result_msg = send_contact_email(
                        name.strip(), 
                        email.strip(), 
                        full_subject, 
                        message.strip()
                    )
                
                if success:
                    st.success(f"""
                    ✅ **Message sent successfully!**
                    
                    {result_msg}
                    
                    📬 You should receive a confirmation email shortly at **{email}**
                    """)
                    st.balloons()
                else:
                    st.error(f"""
                    ❌ **Oops! Something went wrong.**
                    
                    {result_msg}
                    
                    💡 **What to do next:**
                    - Check your internet connection
                    - Try again in a few minutes
                    - If the problem persists, check your account dashboard for alternative contact methods
                    """)
    
    # Info section with visual cards
    st.markdown("---")
    st.markdown("### 💡 What to expect")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="vb-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
            <strong>Fast Response</strong>
            <p style="font-size: 0.9rem; color: #64748b; margin-top: 0.5rem;">
                Usually within 24 hours
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="vb-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💎</div>
            <strong>Priority for Pro</strong>
            <p style="font-size: 0.9rem; color: #64748b; margin-top: 0.5rem;">
                Premium members get priority support
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="vb-card" style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
            <strong>Expert Help</strong>
            <p style="font-size: 0.9rem; color: #64748b; margin-top: 0.5rem;">
                Our team knows VocalBrand inside out
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Common questions quick links
    st.markdown("---")
    st.markdown("### 🔍 Common Questions")
    
    with st.expander("💰 Pricing & Plans"):
        st.markdown("""
        **Monthly Pro (€29/mo):**
        - Unlimited voice generations
        - Priority processing
        - Commercial license
        - Cancel anytime
        
        **Annual Pro (€290/yr):**
        - Everything in Monthly
        - Save 17% (2 months free)
        - Best value for committed users
        
        👉 Visit the Onboarding page to see all payment options
        """)
    
    with st.expander("🎤 Voice Cloning Questions"):
        st.markdown("""
        **How long should my voice sample be?**
        - Minimum: 30 seconds
        - Recommended: 60 seconds
        - Best quality: Clean, clear audio in a quiet environment
        
        **What formats are supported?**
        - Record directly in the browser (recommended)
        - Upload WAV, MP3, or M4A files
        
        **Can I clone multiple voices?**
        - Yes! Each clone gets a unique voice ID
        - Store unlimited voices in your account
        """)
    
    with st.expander("🔧 Technical Support"):
        st.markdown("""
        **For fastest support, include:**
        - What you were trying to do
        - What happened instead
        - Screenshots of any error messages
        - Your browser and operating system
        
        **Common fixes:**
        - Try refreshing the page
        - Check your subscription status
        - Ensure your browser has microphone permissions
        - Clear your browser cache
        """)
    
    with st.expander("💳 Billing Questions"):
        st.markdown("""
        **Subscription Management:**
        - Monthly subscriptions can be cancelled anytime in Stripe
        - Annual subscriptions provide 17% savings
        - All payments are processed securely via Stripe
        
        **Refund Policy:**
        - Contact us within 7 days for refund requests
        - We're happy to work with you on any billing issues
        
        **Need an invoice?**
        - Available for all Pro subscribers
        - Request through this contact form
        """)



def main() -> None:
    inject_css_overrides()
    configure_page()
    init_db()
    ensure_demo_user()
    ensure_session_defaults()
    ensure_voice_reset_on_logout()
    inject_css()
    
    # 🚀 NUCLEAR MOBILE FIXES - CRITICAL
    try:
        inject_mobile_fab_nuclear()
        inject_sidebar_overlap_fix()
    except Exception as e:
        # Silent fail - don't break the app if nuclear fixes fail
        pass
    
    # Inject SEO meta tags for search engine optimization
    try:
        inject_seo_meta()
    except Exception:
        pass
    # If auth failed to import, stop early with a clear diagnostic
    if AUTH_IMPORT_ERROR is not None:
        st.error(
            "Authentication module failed to import. This usually means a conflicting 'auth' package, missing passlib, or stale __pycache__.\n\n"
            f"Root cause: {AUTH_IMPORT_ERROR}\n\n"
            "Troubleshooting:\n"
            "1) Ensure you're launching Streamlit from the project folder containing 'auth.py'.\n"
            "2) Delete any __pycache__ folders.\n"
            "3) Check that no folder or file elsewhere is named 'auth' shadowing this module.\n"
            "4) Install required deps: passlib[bcrypt].\n\n"
            "After fixing, restart the app."
        )
        return
    # Add visual-only, mobile-friendly sidebar opener
    try:
        inject_mobile_nav_helpers()
    except Exception:
        pass
    # Brand the sidebar with logo if available
    try:
        if Path("logo.png").exists():
            st.sidebar.image("logo.png", width="stretch")
            st.sidebar.markdown("---")
    except Exception:
        pass
    # If coming back from Stripe, finalize subscription before rendering panels
    handle_billing_return()
    render_account_panel()

    if not st.session_state.get("user_id"):
        login_section()
        return

    st.title("🎙️ VocalBrand Supreme Console")
    nav_options = ["Onboarding", "Clone Voice", "Generate Speech", "Contact"]
    if st.session_state.get("user_is_admin"):
        nav_options.append("Admin")
    current_page = st.sidebar.radio(
        "Navigation",
        nav_options,
        index=nav_options.index(st.session_state.get("nav_page", "Onboarding")),
    )
    st.session_state["nav_page"] = current_page

    if current_page == "Onboarding":
        page_onboarding()
    elif current_page == "Clone Voice":
        page_clone()
    elif current_page == "Generate Speech":
        page_generate()
    elif current_page == "Contact":
        page_contact()
    elif current_page == "Admin":
        page_admin()


if __name__ == "__main__":
    main()
