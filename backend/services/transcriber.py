import os
import logging
from typing import Dict, Any, List
from openai import OpenAI

logger = logging.getLogger(__name__)

class AudioTranscriber:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for Whisper transcription.")
        self.client = OpenAI(api_key=self.api_key)

    def transcribe_with_word_timestamps(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio using OpenAI Whisper API with exact word-level timestamps.
        Returns verbose JSON with segments and individual words.
        """
        logger.info(f"Submitting audio file to Whisper API: {audio_file_path}")
        
        file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
        if file_size_mb > 25:
            raise ValueError(f"Audio file is {file_size_mb:.1f}MB, exceeds OpenAI Whisper 25MB limit.")

        with open(audio_file_path, "rb") as audio_file:
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"]
            )

        # Response contains text, segments, and words
        data = response.to_dict()
        
        words: List[Dict[str, Any]] = []
        if "words" in data and data["words"]:
            for w in data["words"]:
                words.append({
                    "word": w.get("word", "").strip(),
                    "start": round(float(w.get("start", 0.0)), 2),
                    "end": round(float(w.get("end", 0.0)), 2)
                })

        segments: List[Dict[str, Any]] = []
        if "segments" in data and data["segments"]:
            for s in data["segments"]:
                segments.append({
                    "id": s.get("id"),
                    "start": round(float(s.get("start", 0.0)), 2),
                    "end": round(float(s.get("end", 0.0)), 2),
                    "text": s.get("text", "").strip()
                })

        result = {
            "full_text": data.get("text", ""),
            "duration": data.get("duration", 0.0),
            "language": data.get("language", "cs"),
            "words": words,
            "segments": segments
        }
        
        logger.info(f"Transcription complete: {len(words)} words, {len(segments)} segments identified.")
        return result

