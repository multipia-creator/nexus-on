"""
ElevenLabs TTS Service for NEXUS-ON Ceria Character

Features:
- Natural Korean female voices
- Emotional expression support
- Streaming and non-streaming modes
- Free tier: 10,000 characters/month
- Multilingual support

Recommended Korean Voices:
- Rachel (versatile, natural)
- Domi (warm, friendly)
- Bella (calm, professional)
"""

import os
import logging
import hashlib
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    logger.warning("⚠️ elevenlabs package not installed")


class ElevenLabsTTSService:
    """
    ElevenLabs TTS service for high-quality Korean voice synthesis.
    
    Free tier: 10,000 characters/month
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.enabled = bool(self.api_key and ELEVENLABS_AVAILABLE)
        self.temp_dir = Path(tempfile.gettempdir()) / "nexus_tts"
        self.temp_dir.mkdir(exist_ok=True)
        
        if self.enabled:
            self.client = ElevenLabs(api_key=self.api_key)
            logger.info("✅ ElevenLabs TTS initialized successfully")
        else:
            self.client = None
            if not ELEVENLABS_AVAILABLE:
                logger.warning("⚠️ elevenlabs package not installed")
            elif not self.api_key:
                logger.warning("⚠️ ELEVENLABS_API_KEY not set - TTS disabled")
    
    def generate_speech(
        self,
        text: str,
        voice_id: str = "EXAVITQu4vr4xnSDxMaL",  # Rachel (default)
        model: str = "eleven_multilingual_v2",
        speaking_rate: float = 1.0,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
    ) -> Optional[Dict[str, Any]]:
        """
        Generate TTS using ElevenLabs API.
        
        Args:
            text: Text to synthesize
            voice_id: ElevenLabs voice ID (default: Rachel)
            model: Model to use (default: eleven_multilingual_v2)
            speaking_rate: Speed multiplier (0.5 to 2.0)
            stability: Voice stability (0.0 to 1.0)
            similarity_boost: Voice similarity (0.0 to 1.0)
        
        Available Korean-friendly voices:
            - Rachel: EXAVITQu4vr4xnSDxMaL (versatile, natural)
            - Domi: AZnzlk1XvdvUeBnXmlld (warm, friendly)
            - Bella: EXAVITQu4vr4xnSDxMaL (calm, professional)
        
        Returns:
            Dict with audio_path, audio_url, duration_ms, etc.
        """
        if not self.enabled:
            logger.warning("ElevenLabs TTS service not enabled - skipping")
            return None
        
        try:
            # Generate audio using text_to_speech (v2 API)
            logger.info(f"🎤 Generating TTS (ElevenLabs) for: {text[:50]}...")
            
            # Use the text_to_speech.convert method
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id=model,
                voice_settings={
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                }
            )
            
            # Collect audio bytes from generator
            audio_bytes = b"".join(audio_generator)
            
            # Save to file
            audio_hash = hashlib.md5(
                f"{text}{voice_id}{speaking_rate}{stability}".encode()
            ).hexdigest()[:12]
            audio_filename = f"tts_{audio_hash}.mp3"
            audio_path = self.temp_dir / audio_filename
            
            # Write audio to file
            with open(audio_path, "wb") as f:
                f.write(audio_bytes)
            
            # Estimate duration (rough approximation)
            estimated_duration_ms = int(len(text) * 100 * (1.0 / speaking_rate))
            
            logger.info(f"✅ TTS generated: {audio_path} (~{estimated_duration_ms}ms)")
            
            return {
                "audio_path": str(audio_path),
                "audio_url": f"/tts/{audio_filename}",
                "duration_ms": estimated_duration_ms,
                "text": text,
                "voice": voice_id,
                "model": model,
            }
            
        except Exception as e:
            logger.error(f"❌ ElevenLabs TTS generation failed: {e}")
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


# Global instance
elevenlabs_tts_service = ElevenLabsTTSService()


def generate_tts_elevenlabs(
    text: str,
    voice_id: str = "EXAVITQu4vr4xnSDxMaL",  # Rachel
    speaking_rate: float = 1.0,
    stability: float = 0.5,
    similarity_boost: float = 0.75,
) -> Optional[Dict[str, Any]]:
    """
    Generate TTS using ElevenLabs (recommended for Korean).
    
    Args:
        text: Text to synthesize
        voice_id: Voice ID (default: Rachel)
        speaking_rate: Speed (0.5~2.0)
        stability: Voice stability (0.0~1.0)
        similarity_boost: Voice similarity (0.0~1.0)
    """
    return elevenlabs_tts_service.generate_speech(
        text, voice_id, speaking_rate=speaking_rate,
        stability=stability, similarity_boost=similarity_boost
    )


# Voice presets for easy use
VOICE_PRESETS = {
    "rachel": "EXAVITQu4vr4xnSDxMaL",  # Versatile, natural
    "domi": "AZnzlk1XvdvUeBnXmlld",    # Warm, friendly
    "bella": "EXAVITQu4vr4xnSDxMaL",   # Calm, professional (same as Rachel)
}
