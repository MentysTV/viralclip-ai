import os
import subprocess
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class VideoEngine:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _escape_filter_path(self, path: str) -> str:
        """Escape Windows/Linux paths for FFmpeg filter syntax."""
        p = path.replace("\\", "/")
        # Escape colons for drive letters (e.g. C:/ -> C\\:/)
        p = p.replace(":", r"\:")
        return p

    def render_client_mode(
        self,
        raw_video_path: str,
        ass_subtitles_path: str,
        output_filename: str,
        crop_filter: str,
        watermark_text: Optional[str] = None
    ) -> str:
        """
        REŽIM 1: "PRO KLIENTY / OFICIÁLNÍ TVŮRCE" (Čistý zakázkový střih)
        - Clean 9:16 auto-reframe (1080x1920)
        - 60 fps export, CRF 18 high quality
        - Karaoke dynamic subtitles
        - Optional branding watermark overlay
        """
        final_output_path = os.path.join(self.output_dir, output_filename)
        escaped_sub_path = self._escape_filter_path(ass_subtitles_path)

        filters = []
        # 1. Auto-reframe and scale to 1080x1920 @ 60fps
        filters.append(crop_filter)
        filters.append("fps=60")

        # 2. Watermark overlay (if requested)
        if watermark_text:
            safe_text = watermark_text.replace("'", "").replace(":", "")
            watermark_filter = (
                f"drawtext=text='{safe_text}':fontcolor=white@0.85:fontsize=36:"
                f"x=w-tw-50:y=90:box=1:boxcolor=black@0.45:boxborderw=8"
            )
            filters.append(watermark_filter)

        # 3. Subtitles burn-in
        filters.append(f"ass='{escaped_sub_path}'")

        filter_complex = ",".join(filters)

        cmd = [
            "ffmpeg", "-y",
            "-i", raw_video_path,
            "-vf", filter_complex,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "320k",
            "-ar", "48000",
            final_output_path
        ]

        logger.info(f"Executing Client Mode Render: {' '.join(cmd[:10])}...")
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            error_details = res.stderr.decode("utf-8", errors="ignore")
            logger.error(f"FFmpeg render error: {error_details}")
            raise RuntimeError(f"FFmpeg failed with code {res.returncode}: {error_details[-500:]}")

        logger.info(f"Client Mode Short successfully rendered to: {final_output_path}")
        return final_output_path

    def render_aggressive_monetization_mode(
        self,
        raw_video_path: str,
        broll_video_path: str,
        voiceover_audio_path: Optional[str],
        ass_subtitles_path: str,
        output_filename: str,
        reaction_badge_text: str = "EXKLUZIVNÍ ROZBOR / REAKCE"
    ) -> str:
        """
        REŽIM 2: "AGRESIVNÍ TRANSFORMACE PRO MONETIZACI"
        - Anti-Content ID visual alterations:
          - Speed 1.02x
          - Horizontal flip (mirroring)
          - Color grading (contrast=1.06, saturation=1.14)
          - Split-screen layout (Top: original clip 1080x960, Bottom: dynamic B-roll 1080x960)
          - Reaction border divider & badge
          - Audio ducking (original audio reduced to ~18%, ElevenLabs AI commentary at 100%)
          - 60fps render
        """
        final_output_path = os.path.join(self.output_dir, output_filename)
        escaped_sub_path = self._escape_filter_path(ass_subtitles_path)

        # Filter complex constructing split-screen, visual adjustments, and audio mix
        # [0:v] -> speed 1.02x, scale 1080x960, color grade, hflip
        # [1:v] -> scale 1080x960
        # [0:a] -> speed 1.02x, duck volume to 0.18
        # [2:a] -> voiceover volume 1.0
        
        has_voiceover = voiceover_audio_path and os.path.exists(voiceover_audio_path)

        filter_complex = (
            # 1. Process top video (main speaker)
            "[0:v]setpts=PTS/1.02,"
            "scale=1080:960:force_original_aspect_ratio=increase,"
            "crop=1080:960,"
            "hflip,"
            "eq=contrast=1.06:brightness=0.01:saturation=1.14,"
            "fps=60[top];"
            # 2. Process bottom b-roll
            "[1:v]scale=1080:960:force_original_aspect_ratio=increase,"
            "crop=1080:960,"
            "fps=60[bottom];"
            # 3. Stack vertically into 1080x1920
            "[top][bottom]vstack=inputs=2[stacked];"
            # 4. Reaction divider & badge
            f"[stacked]drawbox=y=956:color=yellow@0.9:width=1080:height=8:t=fill,"
            f"drawtext=text='{reaction_badge_text}':fontcolor=white:fontsize=32:"
            f"x=(w-tw)/2:y=935:box=1:boxcolor=red@0.85:boxborderw=8,"
            f"ass='{escaped_sub_path}'[outv];"
            # 5. Audio ducking and mixing
            "[0:a]atempo=1.02,volume=0.18[ducked_orig];"
        )

        if has_voiceover:
            filter_complex += (
                "[2:a]volume=1.0[voice];"
                "[ducked_orig][voice]amix=inputs=2:duration=first:dropout_transition=2[outa]"
            )
        else:
            filter_complex += "[ducked_orig]volume=1.0[outa]"

        cmd = [
            "ffmpeg", "-y",
            "-i", raw_video_path,
            "-stream_loop", "-1", "-i", broll_video_path,
        ]

        if has_voiceover:
            cmd.extend(["-i", voiceover_audio_path])

        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "[outa]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "19",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "256k",
            "-ar", "48000",
            "-shortest",
            final_output_path
        ])

        logger.info(f"Executing Aggressive Monetization Render: {' '.join(cmd[:12])}...")
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            error_details = res.stderr.decode("utf-8", errors="ignore")
            logger.error(f"FFmpeg aggressive render error: {error_details}")
            raise RuntimeError(f"FFmpeg failed with code {res.returncode}: {error_details[-500:]}")

        logger.info(f"Aggressive Monetization Short successfully rendered to: {final_output_path}")
        return final_output_path

