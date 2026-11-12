import os
import uuid
import asyncio
import logging
from typing import Dict, Any, List, Optional, Literal
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from services.downloader import VideoDownloader
from services.transcriber import AudioTranscriber
from services.analyzer import ViralAnalyzer
from services.voiceover import ElevenLabsVoiceover
from services.reframer import SmartFaceReframer
from services.subtitles import SubtitleGenerator
from services.broll_manager import BrollManager
from services.video_engine import VideoEngine

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("viralclip.main")

# Directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.getenv("TEMP_DIR", os.path.join(BASE_DIR, "temp"))
OUTPUTS_DIR = os.getenv("OUTPUTS_DIR", os.path.join(BASE_DIR, "outputs"))
BROLL_DIR = os.path.join(BASE_DIR, "assets", "broll")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(BROLL_DIR, exist_ok=True)

app = FastAPI(
    title="ViralClip AI Cloud Engine",
    description="Automated AI Cloud Pipeline for YouTube Shorts and TikTok generation (Client Mode & Monetization Mode)",
    version="1.0.0"
)

# CORS configuration
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount outputs for direct streaming and downloads
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")

# In-memory Job State Database
jobs_db: Dict[str, Dict[str, Any]] = {}

# Pydantic Schemas
class JobRequest(BaseModel):
    youtube_url: str = Field(..., description="Target YouTube Video URL")
    mode: Literal["client", "aggressive_monetization"] = Field(
        default="client",
        description="Mode 1: 'client' (Clean Cut) vs Mode 2: 'aggressive_monetization' (Anti-Content ID / Reused Content Bypass)"
    )
    theme_prompt: Optional[str] = Field(
        default="",
        description="Target theme or focus (e.g. 'Funniest moments', 'Deep philosophical insights')"
    )
    watermark_text: Optional[str] = Field(
        default=None,
        description="Branding watermark (e.g. '@creator_handle') for Client Mode"
    )
    broll_type: Optional[str] = Field(
        default="minecraft",
        description="B-roll style for Mode 2: 'minecraft', 'gta', or 'satisfying'"
    )
    voice_id: Optional[str] = Field(
        default="pNInz6obpgDQGcFmaJgB",
        description="ElevenLabs Voice ID (Adam, Rachel, etc.)"
    )
    min_virality_score: Optional[float] = Field(
        default=8.0,
        ge=1.0,
        le=10.0,
        description="Minimum viral score threshold"
    )
    max_clips: Optional[int] = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum clips to generate"
    )

class ClipResponse(BaseModel):
    clip_id: str
    title: str
    description: str
    hashtags: List[str]
    virality_score: float
    virality_reason: str
    duration: float
    start_time: float
    end_time: float
    video_url: str
    download_url: str
    mode: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal["queued", "downloading", "transcribing", "analyzing", "rendering", "completed", "failed"]
    progress: int
    current_step: str
    error_message: Optional[str] = None
    clips: List[ClipResponse] = []


def run_pipeline(job_id: str, request: JobRequest):
    """Orchestrates the end-to-end processing pipeline in the background."""
    try:
        jobs_db[job_id]["status"] = "downloading"
        jobs_db[job_id]["progress"] = 10
        jobs_db[job_id]["current_step"] = "Stahuji zvuk z YouTube pro Whisper AI..."

        downloader = VideoDownloader(output_dir=TEMP_DIR)
        transcriber = AudioTranscriber()
        analyzer = ViralAnalyzer()
        reframer = SmartFaceReframer()
        sub_gen = SubtitleGenerator(output_dir=TEMP_DIR)
        broll_mgr = BrollManager(broll_dir=BROLL_DIR)
        video_engine = VideoEngine(output_dir=OUTPUTS_DIR)
        voiceover = ElevenLabsVoiceover()

        # Step 1: Download audio
        base_name = f"{job_id}"
        audio_file = downloader.download_audio_for_transcription(request.youtube_url, base_name)

        # Step 2: Transcribe with Whisper
        jobs_db[job_id]["status"] = "transcribing"
        jobs_db[job_id]["progress"] = 30
        jobs_db[job_id]["current_step"] = "Přepisuji mluvené slovo a časové značky (OpenAI Whisper)..."

        transcript = transcriber.transcribe_with_word_timestamps(audio_file)

        # Step 3: LLM Virality Analysis
        jobs_db[job_id]["status"] = "analyzing"
        jobs_db[job_id]["progress"] = 50
        jobs_db[job_id]["current_step"] = f"Hledám nejvirálnější úseky (Skóre 8+/10) přes GPT-4o..."

        clips_metadata = analyzer.analyze_transcript(
            transcript_data=transcript,
            mode=request.mode,
            theme_focus=request.theme_prompt or "",
            min_score=request.min_virality_score or 8.0,
            max_clips=request.max_clips or 3
        )

        if not clips_metadata:
            raise ValueError("Žádný úsek videa nedosáhl požadovaného skóre virality 8+/10.")

        # Step 4: Render Clips
        jobs_db[job_id]["status"] = "rendering"
        rendered_clips = []
        total_clips = len(clips_metadata)

        for idx, clip in enumerate(clips_metadata):
            step_pct = 50 + int((idx / total_clips) * 45)
            jobs_db[job_id]["progress"] = step_pct
            jobs_db[job_id]["current_step"] = f"Renderuji klip {idx + 1} z {total_clips} ({request.mode})..."

            clip_start = clip["start_time"]
            clip_end = clip["end_time"]
            clip_duration = clip_end - clip_start
            clip_id_str = f"{job_id}_clip_{idx + 1}"

            # Download raw video segment
            raw_video = downloader.download_video_segment(
                url=request.youtube_url,
                start_time=clip_start,
                end_time=clip_end,
                base_filename=clip_id_str
            )

            # Generate Karaoke Subtitles
            sub_file = os.path.join(TEMP_DIR, f"{clip_id_str}_sub.ass")
            sub_gen.generate_karaoke_ass(
                words=clip.get("words", []),
                clip_start=clip_start,
                output_file=sub_file
            )

            final_mp4_name = f"{clip_id_str}_final.mp4"

            if request.mode == "client":
                # Mode 1: Client Clean Cut with Auto-Reframe
                crop_info = reframer.analyze_crop_coordinates(raw_video)
                crop_filter = reframer.get_ffmpeg_crop_filter(crop_info)

                final_path = video_engine.render_client_mode(
                    raw_video_path=raw_video,
                    ass_subtitles_path=sub_file,
                    output_filename=final_mp4_name,
                    crop_filter=crop_filter,
                    watermark_text=request.watermark_text
                )
            else:
                # Mode 2: Aggressive Monetization Transformation
                # Generate AI voiceover
                vo_file = os.path.join(TEMP_DIR, f"{clip_id_str}_voice.mp3")
                commentary_script = clip.get("commentary_script", {})
                voiceover.generate_commentary_audio(
                    commentary_script=commentary_script,
                    output_path=vo_file,
                    voice_id=request.voice_id or "pNInz6obpgDQGcFmaJgB"
                )

                # Get B-roll footage
                broll_file = broll_mgr.get_or_create_broll(
                    broll_type=request.broll_type or "minecraft",
                    duration=clip_duration + 5
                )

                final_path = video_engine.render_aggressive_monetization_mode(
                    raw_video_path=raw_video,
                    broll_video_path=broll_file,
                    voiceover_audio_path=vo_file,
                    ass_subtitles_path=sub_file,
                    output_filename=final_mp4_name,
                    reaction_badge_text="EXKLUZIVNÍ ROZBOR / REAKCE"
                )

            # Register output
            video_url = f"/outputs/{final_mp4_name}"
            rendered_clips.append(
                ClipResponse(
                    clip_id=clip_id_str,
                    title=clip.get("title", f"Viral Moment #{idx + 1}"),
                    description=clip.get("description", ""),
                    hashtags=clip.get("hashtags", ["#shorts", "#viral"]),
                    virality_score=clip.get("virality_score", 9.0),
                    virality_reason=clip.get("virality_reason", "Vysoký virální náboj a rychlé tempo."),
                    duration=round(clip_duration, 1),
                    start_time=clip_start,
                    end_time=clip_end,
                    video_url=video_url,
                    download_url=f"/api/clips/{clip_id_str}/download",
                    mode=request.mode
                )
            )

        # Mark finished
        jobs_db[job_id]["status"] = "completed"
        jobs_db[job_id]["progress"] = 100
        jobs_db[job_id]["current_step"] = "Hotovo! Všechny klipy jsou připraveny ke stažení."
        jobs_db[job_id]["clips"] = [c.model_dump() for c in rendered_clips]

    except Exception as e:
        logger.exception(f"Error in pipeline job {job_id}: {str(e)}")
        jobs_db[job_id]["status"] = "failed"
        jobs_db[job_id]["error_message"] = str(e)
        jobs_db[job_id]["current_step"] = "Chyba při zpracování videa."


# API Endpoints
@app.post("/api/jobs", response_model=Dict[str, str])
def create_job(request: JobRequest, background_tasks: BackgroundTasks):
    """Start video conversion pipeline in cloud background worker."""
    job_id = str(uuid.uuid4())[:8]
    jobs_db[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "current_step": "Úloha zařazena do fronty...",
        "error_message": None,
        "clips": []
    }

    background_tasks.add_task(run_pipeline, job_id, request)
    return {"job_id": job_id, "status": "queued"}


@app.get("/api/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str):
    """Retrieve live status, progress percentage, and generated clips for a job."""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job ID not found")
    data = jobs_db[job_id]
    return JobStatusResponse(**data)


@app.get("/api/clips/{clip_id}/download")
def download_clip(clip_id: str):
    """Direct MP4 file download endpoint."""
    filename = f"{clip_id}_final.mp4"
    filepath = os.path.join(OUTPUTS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Requested clip file not found")
    return FileResponse(
        filepath,
        media_type="video/mp4",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/api/health")
def healthcheck():
    """Service health check."""
    return {"status": "ok", "service": "viralclip-backend", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
