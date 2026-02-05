"""
NEXUS-ON TTS Service
High-quality Korean Text-to-Speech using Google Cloud TTS

Features:
- Google Cloud TTS API integration (ko-KR-Wavenet-A - Female voice)
- Audio file management (temporary storage)
- Voice configuration (speed, pitch, volume)
- Error handling and fallback

Author: NEXUS-ON Team
Date: 2026-02-04
"""

import os
import logging
import hashlib
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class TTSService:
    """
    High-quality TTS service using Google Cloud Text-to-Speech API.
    
    Supports:
    - Korean female voice (ko-KR-Wavenet-A)
    - Configurable speaking rate, pitch
    - MP3 audio output
    - Temporary file storage
    """
    
    def __init__(self):
        self.enabled = False
        self.client = None
        self.temp_dir = Path(tempfile.gettempdir()) / "nexus_tts"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Initialize Google Cloud TTS client
        try:
            from google.cloud import texttospeech
            self.texttospeech = texttospeech
            
            # Check if credentials are configured
            if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                self.client = texttospeech.TextToSpeechClient()
                self.enabled = True
                logger.info("✅ Google Cloud TTS initialized successfully")
            else:
                logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS not set - TTS disabled")
        except ImportError:
            logger.warning("⚠️ google-cloud-texttospeech not installed - TTS disabled")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Cloud TTS: {e}")
    
    def generate_speech(
        self,
        text: str,
        voice_name: str = "ko-KR-Wavenet-A",
        language_code: str = "ko-KR",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate high-quality TTS audio using Google Cloud TTS.
        
        Args:
            text: Text to synthesize (Korean)
            voice_name: Voice model name (default: ko-KR-Wavenet-A - Female)
            language_code: Language code (default: ko-KR)
            speaking_rate: Speed (0.25 to 4.0, default: 1.0)
            pitch: Pitch (-20.0 to 20.0, default: 0.0)
        
        Returns:
            Dict with keys:
            - audio_path: Path to generated MP3 file
            - duration_ms: Estimated duration in milliseconds
            - text: Original text
            - voice: Voice name used
        """
        if not self.enabled:
            logger.warning("TTS service not enabled - skipping speech generation")
            return None
        
        try:
            # Prepare input
            synthesis_input = self.texttospeech.SynthesisInput(text=text)
            
            # Voice configuration
            voice = self.texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name,
                ssml_gender=self.texttospeech.SsmlVoiceGender.FEMALE
            )
            
            # Audio configuration
            audio_config = self.texttospeech.AudioConfig(
                audio_encoding=self.texttospeech.AudioEncoding.MP3,
                speaking_rate=speaking_rate,
                pitch=pitch,
            )
            
            # Perform TTS request
            logger.info(f"🎤 Generating TTS for text (length: {len(text)}): {text[:50]}...")
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Save audio to temporary file
            audio_hash = hashlib.md5(f"{text}{voice_name}{speaking_rate}{pitch}".encode()).hexdigest()[:12]
            audio_filename = f"tts_{audio_hash}.mp3"
            audio_path = self.temp_dir / audio_filename
            
            with open(audio_path, "wb") as out:
                out.write(response.audio_content)
            
            # Estimate duration (roughly 100ms per character for Korean)
            estimated_duration_ms = int(len(text) * 100 * (1.0 / speaking_rate))
            
            logger.info(f"✅ TTS generated successfully: {audio_path} ({estimated_duration_ms}ms)")
            
            return {
                "audio_path": str(audio_path),
                "audio_url": f"/tts/{audio_filename}",  # URL for serving
                "duration_ms": estimated_duration_ms,
                "text": text,
                "voice": voice_name,
            }
            
        except Exception as e:
            logger.error(f"❌ TTS generation failed: {e}")
            return None
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up old TTS audio files.
        
        Args:
            max_age_hours: Maximum age in hours before deletion
        """
        import time
        
        try:
            now = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for audio_file in self.temp_dir.glob("tts_*.mp3"):
                file_age = now - audio_file.stat().st_mtime
                if file_age > max_age_seconds:
                    audio_file.unlink()
                    logger.debug(f"🗑️ Deleted old TTS file: {audio_file}")
        except Exception as e:
            logger.error(f"❌ Failed to cleanup TTS files: {e}")


# Global TTS service instance
tts_service = TTSService()


# Helper function for easy access
def generate_tts(
    text: str,
    voice_name: str = "ko-KR-Wavenet-A",
    speaking_rate: float = 1.0,
    pitch: float = 0.0,
) -> Optional[Dict[str, Any]]:
    """
    Generate TTS audio (shortcut function).
    
    Args:
        text: Text to synthesize
        voice_name: Voice model (default: ko-KR-Wavenet-A)
        speaking_rate: Speed (default: 1.0)
        pitch: Pitch (default: 0.0)
    
    Returns:
        TTS result dict or None if failed
    """
    return tts_service.generate_speech(text, voice_name, speaking_rate, pitch)
