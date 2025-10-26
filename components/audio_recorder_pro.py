"""Advanced audio recorder component with timer and waveform visualization."""

import streamlit as st
import streamlit.components.v1 as components
import base64
import io
import json

def render_audio_recorder_pro() -> bytes:
    """Render an advanced audio recorder with timer and waveform visualization.
    
    Returns:
        bytes: The recorded audio data in WAV format, or None if no recording used
    """
    # Initialize session state for audio storage
    if "vb_recorder_audio_blob" not in st.session_state:
        st.session_state.vb_recorder_audio_blob = None
    if "vb_recorder_use_clicked" not in st.session_state:
        st.session_state.vb_recorder_use_clicked = False
    if "vb_recording_complete" not in st.session_state:
        st.session_state.vb_recording_complete = False
    if "vb_audio_ready_to_process" not in st.session_state:
        st.session_state.vb_audio_ready_to_process = False
    
    recorder_html = """
    <div class="recorder-wrapper">
        <div class="recorder-header">
            <button id="recordButton" class="record-btn">
                <span class="record-icon">🎙️</span>
                <span class="button-text">Start Recording</span>
            </button>
            <div class="timer" id="timer">00:00</div>
        </div>
        <canvas id="visualizer" class="waveform"></canvas>
        <div id="status" class="status"></div>
        <div id="audioPreview"></div>
    </div>
    
    <style>
        .recorder-wrapper {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 10px 0;
        }
        .recorder-header {
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 15px;
        }
        .record-btn {
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 16px;
            transition: all 0.2s;
            font-weight: 600;
        }
        .record-btn:hover {
            background: #1d4ed8;
        }
        .record-btn.recording {
            background: #dc2626;
            animation: pulse 2s infinite;
        }
        .timer {
            font-family: monospace;
            font-size: 24px;
            font-weight: bold;
            background: #f8fafc;
            padding: 8px 16px;
            border-radius: 6px;
            border: 1px solid #e2e8f0;
            min-width: 80px;
            text-align: center;
        }
        .waveform {
            width: 100%;
            height: 100px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            margin: 10px 0;
        }
        .status {
            margin: 10px 0;
            text-align: center;
            color: #64748b;
            font-size: 14px;
            min-height: 20px;
        }
        audio {
            width: 100%;
            margin: 10px 0;
            border-radius: 8px;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.6; }
            100% { opacity: 1; }
        }
    </style>
    
    <script>
        let mediaRecorder;
        let audioChunks = [];
        let startTime;
        let timerInterval;
        let audioContext;
        let analyser;
        let isRecording = false;
        let currentAudioBlob = null;
        
        function updateTimer() {
            const timer = document.getElementById('timer');
            if (!timer || !startTime) return;
            
            const now = Date.now();
            const elapsed = Math.floor((now - startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            timer.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        
        function startVisualization(stream) {
            const canvas = document.getElementById('visualizer');
            if (!canvas) return;
            
            const canvasCtx = canvas.getContext('2d');
            
            if (!audioContext) {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioContext.createAnalyser();
                const source = audioContext.createMediaStreamSource(stream);
                source.connect(analyser);
            }
            
            analyser.fftSize = 2048;
            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            
            function draw() {
                if (!isRecording) return;
                requestAnimationFrame(draw);
                
                analyser.getByteTimeDomainData(dataArray);
                canvasCtx.fillStyle = '#f8fafc';
                canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
                canvasCtx.lineWidth = 2;
                canvasCtx.strokeStyle = '#2563eb';
                canvasCtx.beginPath();
                
                const sliceWidth = canvas.width * 1.0 / bufferLength;
                let x = 0;
                
                for (let i = 0; i < bufferLength; i++) {
                    const v = dataArray[i] / 128.0;
                    const y = v * canvas.height/2;
                    
                    if (i === 0) {
                        canvasCtx.moveTo(x, y);
                    } else {
                        canvasCtx.lineTo(x, y);
                    }
                    x += sliceWidth;
                }
                
                canvasCtx.lineTo(canvas.width, canvas.height/2);
                canvasCtx.stroke();
            }
            
            draw();
        }
        
        function useRecording() {
            if (!currentAudioBlob) {
                alert('No recording available');
                return;
            }
            
            // Download the file for user convenience
            const url = URL.createObjectURL(currentAudioBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'vocalbrand_recording_' + Date.now() + '.wav';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
            console.log('📥 Audio downloaded');
            
            // Store for processing
            const reader = new FileReader();
            reader.onloadend = function() {
                const base64data = reader.result;
                
                try {
                    // Store in localStorage (main)
                    localStorage.setItem('vb_recorded_audio', base64data);
                    localStorage.setItem('vb_recording_ready', '1');
                    
                    // Store in sessionStorage (backup)
                    sessionStorage.setItem('vb_audio_b64', base64data);
                    sessionStorage.setItem('vb_audio_ready', 'true');
                    
                    // Store in window global
                    window.vb_audio_data = base64data;
                    window.vb_audio_ready_flag = true;
                    
                    // Create a hidden div with the audio data as an attribute
                    // This allows Python to potentially read it via the rendered HTML
                    let hiddenDiv = document.getElementById('vb_audio_storage_div');
                    if (!hiddenDiv) {
                        hiddenDiv = document.createElement('div');
                        hiddenDiv.id = 'vb_audio_storage_div';
                        hiddenDiv.style.display = 'none';
                        document.body.appendChild(hiddenDiv);
                    }
                    hiddenDiv.setAttribute('data-audio-b64', base64data);
                    hiddenDiv.setAttribute('data-audio-ready', 'true');
                    
                    console.log('✅ Audio stored in all locations:', base64data.length, 'bytes');
                    
                } catch (e) {
                    console.error('Storage error:', e);
                }
                
                // Update UI
                const statusElement = document.getElementById('status');
                if (statusElement) {
                    statusElement.innerHTML = '✅ Recording saved! Processing...';
                    statusElement.style.color = '#059669';
                    statusElement.style.fontWeight = 'bold';
                }
                
                // CRITICAL: Signal to Python that audio is ready (single hop)
                // Push the actual base64 audio into the URL so Python can decode immediately
                console.log('🔄 Signaling to Python (direct transfer)...');

                try {
                    // Extract base64 payload only
                    let base64Payload = base64data;
                    if (base64data.includes(',')) {
                        base64Payload = base64data.split(',')[1];
                    }
                    // Compute size for logging/display (non-critical)
                    let payloadBytes = 0;
                    try { payloadBytes = atob(base64Payload).length; } catch (e) {}

                    const url = new URL(window.location);
                    url.searchParams.set('vb_audio_b64', base64Payload);
                    url.searchParams.set('vb_audio_bytes', String(payloadBytes));
                    url.searchParams.delete('vb_audio_present');
                    url.searchParams.set('vb_audio_ts', Date.now());
                
                    // Replace history and reload
                    window.history.replaceState({}, '', url);
                    setTimeout(() => window.location.reload(), 50);
                } catch (err) {
                    console.error('URL transfer failed, falling back to presence marker', err);
                    const url = new URL(window.location);
                    url.searchParams.set('vb_audio_present', 'true');
                    url.searchParams.set('vb_audio_ts', Date.now());
                    window.history.replaceState({}, '', url);
                    setTimeout(() => window.location.reload(), 100);
                }
            };
            
            reader.readAsDataURL(currentAudioBlob);
        }
        
        async function toggleRecording() {
            const button = document.getElementById('recordButton');
            const statusElement = document.getElementById('status');
            const previewElement = document.getElementById('audioPreview');
            
            if (!isRecording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        currentAudioBlob = audioBlob;
                        const audioUrl = URL.createObjectURL(audioBlob);
                        
                        previewElement.innerHTML = `
                            <audio controls style="width: 100%; margin: 10px 0;">
                                <source src="${audioUrl}" type="audio/wav">
                            </audio>
                            <button onclick="useRecording()" class="record-btn" style="width: 100%; margin-top: 10px; background: #059669;">
                                ✅ Use This Recording
                            </button>
                        `;
                    };
                    
                    mediaRecorder.start(100);
                    isRecording = true;
                    startTime = Date.now();
                    timerInterval = setInterval(updateTimer, 100);
                    startVisualization(stream);
                    
                    button.classList.add('recording');
                    button.querySelector('.button-text').textContent = 'Stop Recording';
                    statusElement.textContent = '🔴 Recording in progress...';
                    previewElement.innerHTML = '';
                    
                } catch (err) {
                    console.error('Error accessing microphone:', err);
                    statusElement.textContent = '❌ Error: Could not access microphone. Check permissions.';
                }
            } else {
                mediaRecorder.stop();
                isRecording = false;
                clearInterval(timerInterval);
                
                if (audioContext) {
                    audioContext.close();
                    audioContext = null;
                }
                
                button.classList.remove('recording');
                button.querySelector('.button-text').textContent = 'Start New Recording';
                statusElement.textContent = '✅ Recording complete! Click "Use This Recording" below:';
            }
        }
        
        // Initialize the recorder
        document.addEventListener('DOMContentLoaded', () => {
            const button = document.getElementById('recordButton');
            if (button) {
                button.addEventListener('click', toggleRecording);
            }
        });
    </script>
    """
    
    # Render the HTML component
    components.html(recorder_html, height=450)
    
    # Check if audio was retrieved from localStorage by app.py
    audio_data_blob = st.session_state.get("vb_recorder_audio_blob")
    if audio_data_blob:
        st.session_state.vb_recorder_audio_blob = None
        st.session_state.vb_audio_ready_to_process = True
        return audio_data_blob
    
    return None