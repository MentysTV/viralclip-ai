import os
import re
import json
import logging
from typing import Dict, Any, Tuple
import yt_dlp

logger = logging.getLogger(__name__)

class VideoDownloader:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def extract_info(self, url: str) -> Dict[str, Any]:
        """Extract metadata without full download."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "id": info.get("id"),
                "title": info.get("title"),
                "duration": info.get("duration", 0),
                "channel": info.get("uploader"),
                "thumbnail": info.get("thumbnail"),
                "webpage_url": info.get("webpage_url", url)
            }

    def download_audio_for_transcription(self, url: str, base_filename: str) -> str:
        """
        Download high-efficiency compressed audio (mp3, mono, 16kHz) for Whisper API.
        This minimizes network payload and fits within Whisper 25MB limits.
        """
        output_path = os.path.join(self.output_dir, f"{base_filename}_audio.mp3")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.output_dir, f"{base_filename}_audio.%(ext)s"),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '64',
            }],
            'postprocessor_args': [
                '-ar', '16000',
                '-ac', '1'
            ],
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Failed to download audio at {output_path}")

        logger.info(f"Audio downloaded for transcription: {output_path} ({os.path.getsize(output_path)} bytes)")
        return output_path

    def download_video_segment(self, url: str, start_time: float, end_time: float, base_filename: str) -> str:
        """
        Download high-quality video for the specified time segment (1080p / 720p).
        Uses yt-dlp section downloader or downloads full and trims cleanly via ffmpeg.
        """
        output_path = os.path.join(self.output_dir, f"{base_filename}_raw.mp4")
        
        # Download targeted quality
        ydl_opts = {
            'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
            # Download section directly to save bandwidth on cloud workers
            'download_ranges': yt_dlp.utils.download_range_func(None, [(start_time, end_time)]),
            'force_keyframes_at_cuts': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(output_path):
            # Fallback if download_ranges fails on specific formats
            logger.warning("Section download failed, attempting standard trimmed download...")
            return self._fallback_download_and_cut(url, start_time, end_time, output_path)

        return output_path

    def _fallback_download_and_cut(self, url: str, start_time: float, end_time: float, output_path: str) -> str:
        temp_full = output_path.replace(".mp4", "_full.mp4")
        ydl_opts = {
            'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': temp_full,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        import subprocess
        duration = end_time - start_time
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_time),
            "-i", temp_full,
            "-t", str(duration),
            "-c:v", "libx264", "-c:a", "aac",
            output_path
        ]
        subprocess.run(cmd, check=True)
        if os.path.exists(temp_full):
            os.remove(temp_full)
        return output_path

