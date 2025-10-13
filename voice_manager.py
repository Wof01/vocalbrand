"""ElevenLabs voice management utilities for VocalBrand.

Handles voice cleanup, quota management, and voice lifecycle.
"""
from __future__ import annotations
import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("vocalbrand.voice_manager")

ELEVEN_VOICES_URL = "https://api.elevenlabs.io/v1/voices"
ELEVEN_VOICE_DELETE_URL = "https://api.elevenlabs.io/v1/voices/{voice_id}"


class VoiceManager:
    """Manages ElevenLabs voice quotas and cleanup."""
    
    def __init__(self, api_key: str, *, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout
        self._headers = {"xi-api-key": api_key}
    
    def get_all_voices(self) -> Dict[str, Any]:
        """Get all voices in the account.
        
        Returns:
            Dict with 'voices' list and 'success' bool
        """
        try:
            resp = requests.get(
                ELEVEN_VOICES_URL,
                headers=self._headers,
                timeout=self.timeout
            )
            
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "success": True,
                    "voices": data.get("voices", []),
                    "total": len(data.get("voices", []))
                }
            else:
                return {
                    "success": False,
                    "voices": [],
                    "error": f"API error: {resp.status_code}"
                }
        except Exception as e:
            logger.error(f"Error fetching voices: {e}")
            return {
                "success": False,
                "voices": [],
                "error": str(e)
            }
    
    def get_custom_voices(self) -> List[Dict[str, Any]]:
        """Get only custom (cloned) voices, not pre-made ones.
        
        Returns:
            List of custom voice dicts with: voice_id, name, category, date_unix
        """
        result = self.get_all_voices()
        if not result["success"]:
            return []
        
        # Filter for cloned/generated voices (not pre-made)
        custom_voices = [
            v for v in result["voices"]
            if v.get("category") != "premade"
        ]
        
        return custom_voices
    
    def delete_voice(self, voice_id: str) -> bool:
        """Delete a voice from ElevenLabs account.
        
        Args:
            voice_id: The voice ID to delete
            
        Returns:
            True if successfully deleted, False otherwise
        """
        try:
            resp = requests.delete(
                ELEVEN_VOICE_DELETE_URL.format(voice_id=voice_id),
                headers=self._headers,
                timeout=self.timeout
            )
            
            if resp.status_code == 200:
                logger.info(f"Successfully deleted voice: {voice_id}")
                return True
            else:
                logger.warning(f"Failed to delete voice {voice_id}: {resp.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error deleting voice {voice_id}: {e}")
            return False
    
    def cleanup_oldest_voices(self, keep_count: int = 25) -> Dict[str, Any]:
        """Delete oldest custom voices to free up quota.
        
        Args:
            keep_count: How many voices to keep (delete the rest)
            
        Returns:
            Dict with deletion results
        """
        custom_voices = self.get_custom_voices()
        
        if len(custom_voices) <= keep_count:
            return {
                "success": True,
                "deleted": 0,
                "message": f"Only {len(custom_voices)} voices, no cleanup needed"
            }
        
        # Sort by date (oldest first)
        # ElevenLabs returns date_unix (timestamp)
        sorted_voices = sorted(
            custom_voices,
            key=lambda v: v.get("date_unix", 0)
        )
        
        # Calculate how many to delete
        to_delete_count = len(sorted_voices) - keep_count
        voices_to_delete = sorted_voices[:to_delete_count]
        
        deleted_count = 0
        deleted_ids = []
        failed_ids = []
        
        for voice in voices_to_delete:
            voice_id = voice.get("voice_id")
            voice_name = voice.get("name", "Unknown")
            
            if voice_id:
                if self.delete_voice(voice_id):
                    deleted_count += 1
                    deleted_ids.append({"id": voice_id, "name": voice_name})
                    logger.info(f"Deleted old voice: {voice_name} ({voice_id})")
                else:
                    failed_ids.append({"id": voice_id, "name": voice_name})
        
        return {
            "success": True,
            "deleted": deleted_count,
            "failed": len(failed_ids),
            "deleted_voices": deleted_ids,
            "failed_voices": failed_ids,
            "message": f"Cleaned up {deleted_count} old voices"
        }
    
    def get_quota_info(self) -> Dict[str, Any]:
        """Get current voice quota usage.
        
        Returns:
            Dict with: custom_count, premade_count, total, has_space
        """
        result = self.get_all_voices()
        
        if not result["success"]:
            return {
                "success": False,
                "error": result.get("error"),
                "custom_count": 0,
                "has_space": False
            }
        
        voices = result["voices"]
        custom = [v for v in voices if v.get("category") != "premade"]
        premade = [v for v in voices if v.get("category") == "premade"]
        
        # Most plans have 30 voice limit
        max_voices = 30
        has_space = len(custom) < max_voices
        
        return {
            "success": True,
            "custom_count": len(custom),
            "premade_count": len(premade),
            "total": len(voices),
            "max_voices": max_voices,
            "has_space": has_space,
            "space_remaining": max_voices - len(custom)
        }
    
    def auto_cleanup_if_needed(self, keep_count: int = 25) -> Dict[str, Any]:
        """Automatically clean up if quota is full or nearly full.
        
        Args:
            keep_count: Target number of voices to keep
            
        Returns:
            Dict with cleanup results
        """
        quota = self.get_quota_info()
        
        if not quota["success"]:
            return {
                "success": False,
                "cleaned": False,
                "error": quota.get("error")
            }
        
        custom_count = quota["custom_count"]
        
        # If we have space, no cleanup needed
        if custom_count < keep_count:
            return {
                "success": True,
                "cleaned": False,
                "message": f"Quota OK: {custom_count}/{quota['max_voices']} voices",
                "quota": quota
            }
        
        # Cleanup needed
        logger.warning(f"Voice quota full ({custom_count}/{quota['max_voices']}), initiating cleanup...")
        
        cleanup_result = self.cleanup_oldest_voices(keep_count)
        
        return {
            "success": True,
            "cleaned": True,
            "cleanup_result": cleanup_result,
            "quota_before": quota,
            "message": f"Auto-cleanup: deleted {cleanup_result.get('deleted', 0)} old voices"
        }


def create_voice_manager(api_key: Optional[str] = None) -> Optional[VoiceManager]:
    """Factory function to create VoiceManager instance.
    
    Args:
        api_key: ElevenLabs API key (uses env var if not provided)
        
    Returns:
        VoiceManager instance or None if no API key
    """
    key = api_key or os.getenv("ELEVENLABS_API_KEY")
    
    if not key:
        logger.warning("No ElevenLabs API key provided")
        return None
    
    return VoiceManager(key)
