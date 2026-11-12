import os
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)

# Default voices on ElevenLabs
VOICE_MAP = {
    "adam": "pNInz6obpgDQGcFmaJgB",      # Deep, authoritative narrative voice
    "rachel": "21m00Tcm4TlvDq8ikWAM",    # Energetic, clear female voice
    "antoni": "ErXwobaYiN019PkySvjV",    # Dynamic storyteller
    "josh": "TxGEqnHWrfWFTfGW9XjX",      # Deep, viral narrator
}

class ElevenLabsVoiceover:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY not found. Synthetic commentary will fall back to local test synthesis.")

    def generate_commentary_audio(
        self,
        commentary_script: Dict[str, str],
        output_path: str,
        voice_id: str = "pNInz6obpgDQGcFmaJgB"
    ) -> str:
        """
        Generate voiceover using ElevenLabs Text-to-Speech API.
        Combines intro hook, middle context, and outro recap.
        """
        intro = commentary_script.get("intro_hook", "")
        middle = commentary_script.get("middle_commentary", "")
        outro = commentary_script.get("outro_recap", "")

        full_speech_text = f"{intro} ... {middle} ... {outro}".strip()
        logger.info(f"Generating ElevenLabs voiceover ({len(full_speech_text)} chars) with voice_id {voice_id}")

        if not self.api_key:
            # Fallback for environments without API key: create silent / synthetic audio via ffmpeg
            logger.warning("No ElevenLabs API key provided. Generating placeholder narration tone.")
            import subprocess
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "sine=frequency=440:duration=5",
                "-c:a", "libmp3lame", "-b:a", "128k",
                output_path
            ]
            subprocess.run(cmd, check=True)
            return output_path

        # Resolve voice alias if provided
        selected_voice = VOICE_MAP.get(voice_id.lower(), voice_id)

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{selected_voice}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        payload = {
            "text": full_speech_text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.50,
                "similarity_boost": 0.75,
                "style": 0.40,
                "use_speaker_boost": True
            }
        }

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code != 200:
            error_msg = f"ElevenLabs API error {response.status_code}: {response.text}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        with open(output_path, "wb") as f:
            f.write(response.content)

        logger.info(f"Voiceover successfully generated and saved to {output_path}")
        return output_path

