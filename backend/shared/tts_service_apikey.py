"""
Alternative TTS Service using Google Cloud TTS REST API with API Key
(Fallback when service account JSON is not available)

Features:
- Use Google Cloud TTS REST API directly
- API Key authentication (simpler than service account)
- Same voice quality (ko-KR-Wavenet-A)
- No JSON credentials file needed

Note: This is a fallback option. Service account is still recommended.
"""

import os
import logging
import hashlib
import tempfile
import requests
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class TTSServiceWithAPIKey:
    """
    TTS service using Google Cloud TTS REST API with API Key.
    
    Use this when service account JSON is not available.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_CLOUD_API_KEY")
        self.enabled = bool(self.api_key)
        self.temp_dir = Path(tempfile.gettempdir()) / "nexus_tts"
        self.temp_dir.mkdir(exist_ok=True)
        self.api_url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        
        if self.enabled:
            logger.info("✅ Google Cloud TTS (API Key) initialized successfully")
        else:
            logger.warning("⚠️ GOOGLE_CLOUD_API_KEY not set - TTS disabled")
    
    def generate_speech(
        self,
        text: str,
        voice_name: str = "ko-KR-Wavenet-A",
        language_code: str = "ko-KR",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate TTS using Google Cloud REST API with API Key.
        
        Args:
            text: Text to synthesize
            voice_name: Voice model (default: ko-KR-Wavenet-A)
            language_code: Language code (default: ko-KR)
            speaking_rate: Speed (0.25 to 4.0)
            pitch: Pitch (-20.0 to 20.0)
        
        Returns:
            Dict with audio_path, audio_url, duration_ms, etc.
        """
        if not self.enabled:
            logger.warning("TTS service not enabled - skipping")
            return None
        
        try:
            # Prepare request payload
            payload = {
                "input": {"text": text},
                "voice": {
                    "languageCode": language_code,
                    "name": voice_name,
                    "ssmlGender": "FEMALE"
                },
                "audioConfig": {
                    "audioEncoding": "MP3",
                    "speakingRate": speaking_rate,
                    "pitch": pitch
                }
            }
            
            # Make API request
            logger.info(f"🎤 Generating TTS (API Key) for: {text[:50]}...")
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                json=payload,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"❌ TTS API error: {response.status_code} - {response.text}")
                return None
            
            # Extract audio content (base64 encoded)
            import base64
            result = response.json()
            audio_content = base64.b64decode(result["audioContent"])
            
            # Save to file
            audio_hash = hashlib.md5(f"{text}{voice_name}{speaking_rate}{pitch}".encode()).hexdigest()[:12]
            audio_filename = f"tts_{audio_hash}.mp3"
            audio_path = self.temp_dir / audio_filename
            
            with open(audio_path, "wb") as f:
                f.write(audio_content)
            
            # Estimate duration
            estimated_duration_ms = int(len(text) * 100 * (1.0 / speaking_rate))
            
            logger.info(f"✅ TTS generated: {audio_path} ({estimated_duration_ms}ms)")
            
            return {
                "audio_path": str(audio_path),
                "audio_url": f"/tts/{audio_filename}",
                "duration_ms": estimated_duration_ms,
                "text": text,
                "voice": voice_name,
            }
            
        except Exception as e:
            logger.error(f"❌ TTS generation failed: {e}")
            return None
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Clean up old TTS files."""
        import time
        try:
            now = time.time()
            max_age_seconds = max_age_hours * 3600
            for audio_file in self.temp_dir.glob("tts_*.mp3"):
                if now - audio_file.stat().st_mtime > max_age_seconds:
                    audio_file.unlink()
                    logger.debug(f"🗑️ Deleted old TTS file: {audio_file}")
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")


# Global instance with API Key
tts_service_apikey = TTSServiceWithAPIKey()


def generate_tts_with_apikey(
    text: str,
    voice_name: str = "ko-KR-Wavenet-A",
    speaking_rate: float = 1.0,
    pitch: float = 0.0,
) -> Optional[Dict[str, Any]]:
    """Generate TTS using API Key (fallback)."""
    return tts_service_apikey.generate_speech(text, voice_name, speaking_rate, pitch)
