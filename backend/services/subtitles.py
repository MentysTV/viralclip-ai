import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

ASS_HEADER_TEMPLATE = """[Script Info]
Title: ViralClip AI Dynamic Karaoke Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: KaraokeActive,DejaVu Sans,72,&H0000FFFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,5,2,2,40,40,420,1
Style: KaraokeNormal,DejaVu Sans,68,&H00FFFFFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,5,2,2,40,40,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def format_ass_timestamp(seconds: float) -> str:
    """Format seconds into ASS timestamp: H:MM:SS.cs"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{hrs:d}:{mins:02d}:{secs:02d}.{cs:02d}"

class SubtitleGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_karaoke_ass(
        self,
        words: List[Dict[str, Any]],
        clip_start: float,
        output_file: str,
        highlight_color: str = "&H0000FFFF",  # Bright Yellow in BGR hex
        normal_color: str = "&H00FFFFFF",     # Pure White in BGR hex
        max_words_per_line: int = 4
    ) -> str:
        """
        Generates an ASS subtitle file with rapid-fire word-level karaoke styling.
        Each word in a 3-4 word phrase glows when actively spoken.
        """
        # Adjust word timestamps relative to clip start
        rel_words = []
        for w in words:
            rel_start = max(0.0, w["start"] - clip_start)
            rel_end = max(rel_start + 0.1, w["end"] - clip_start)
            word_str = w["word"].upper().strip()
            if word_str:
                rel_words.append({
                    "word": word_str,
                    "start": rel_start,
                    "end": rel_end
                })

        if not rel_words:
            # Create an empty but valid ASS file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(ASS_HEADER_TEMPLATE)
            return output_file

        # Chunk into groups of 3-4 words for dynamic reading rhythm
        chunks = []
        current_chunk = []
        for w in rel_words:
            current_chunk.append(w)
            if len(current_chunk) >= max_words_per_line:
                chunks.append(current_chunk)
                current_chunk = []
        if current_chunk:
            chunks.append(current_chunk)

        dialogue_lines = []
        for chunk in chunks:
            chunk_start = chunk[0]["start"]
            chunk_end = chunk[-1]["end"]

            # For each word in this chunk, create a sub-event where that specific word is highlighted
            for i, target_word in enumerate(chunk):
                w_start = target_word["start"]
                w_end = target_word["end"]
                start_str = format_ass_timestamp(w_start)
                end_str = format_ass_timestamp(w_end)

                # Assemble line with target word highlighted
                styled_words = []
                for j, w in enumerate(chunk):
                    if j == i:
                        # Active word: Yellow & slightly scaled up
                        styled_words.append(r"{\c" + highlight_color + r"\fscx112\fscy112}" + w["word"] + r"{\fscx100\fscy100}")
                    else:
                        # Inactive words: White
                        styled_words.append(r"{\c" + normal_color + "}" + w["word"])

                text_content = " ".join(styled_words)
                line = f"Dialogue: 0,{start_str},{end_str},KaraokeActive,,0,0,0,,{text_content}"
                dialogue_lines.append(line)

        ass_content = ASS_HEADER_TEMPLATE + "\n".join(dialogue_lines) + "\n"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(ass_content)

        logger.info(f"Karaoke ASS subtitles created with {len(dialogue_lines)} frames at {output_file}")
        return output_file

