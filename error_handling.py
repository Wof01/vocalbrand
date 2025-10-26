"""
VocalBrand Supreme Error Handling System
Provides centralized error handling with user-friendly messages and logging
"""
from __future__ import annotations

import logging
import traceback
from typing import Any, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from functools import wraps

import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vocalbrand")

@dataclass
class ErrorInfo:
    message: str
    details: Optional[str] = None
    code: Optional[str] = None
    recovery_hint: Optional[str] = None

class VocalBrandError(Exception):
    """Base exception class for VocalBrand errors"""
    def __init__(
        self, 
        message: str, 
        details: Optional[str] = None,
        code: Optional[str] = None,
        recovery_hint: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.details = details
        self.code = code
        self.recovery_hint = recovery_hint

class AudioProcessingError(VocalBrandError):
    """Raised when audio processing fails"""
    pass

class RecordingError(VocalBrandError):
    """Raised when recording fails"""
    pass

class CloneGenerationError(VocalBrandError):
    """Raised when voice cloning fails"""
    pass

def handle_error(
    error: Union[Exception, VocalBrandError],
    show_details: bool = False
) -> ErrorInfo:
    """Convert any error into user-friendly ErrorInfo"""
    
    if isinstance(error, VocalBrandError):
        return ErrorInfo(
            message=error.message,
            details=error.details if show_details else None,
            code=error.code,
            recovery_hint=error.recovery_hint
        )
    
    # Handle generic exceptions
    return ErrorInfo(
        message="An unexpected error occurred",
        details=str(error) if show_details else None,
        recovery_hint="Please try again or contact support if the issue persists."
    )

def safe_execute(show_details: bool = False):
    """Decorator for safely executing functions with error handling"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_info = handle_error(e, show_details)
                logger.error(f"Error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
                
                if error_info.recovery_hint:
                    st.error(f"{error_info.message}\n\n💡 {error_info.recovery_hint}")
                else:
                    st.error(error_info.message)
                
                if show_details and error_info.details:
                    with st.expander("Technical Details"):
                        st.code(error_info.details)
                
                return None
        return wrapper
    return decorator

# Error message templates
ERROR_MESSAGES = {
    "audio_processing": ErrorInfo(
        message="Could not process audio file",
        recovery_hint="Make sure your file is a valid audio format (WAV, MP3, or M4A)"
    ),
    "recording": ErrorInfo(
        message="Recording failed",
        recovery_hint="Check your microphone permissions and try again"
    ),
    "cloning": ErrorInfo(
        message="Voice cloning failed",
        recovery_hint="Try using a different audio sample with clearer speech"
    ),
    "file_upload": ErrorInfo(
        message="File upload failed",
        recovery_hint="Try uploading a different file"
    ),
    "invalid_format": ErrorInfo(
        message="Invalid file format",
        recovery_hint="Please upload WAV, MP3, or M4A files only"
    )
}