import os
import sys
import json
import threading
import subprocess
import shutil
import logging
from typing import Dict, Any, List

# Ensure bundled FFmpeg from imageio-ffmpeg is registered in system PATH
try:
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    std_ffmpeg = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    if not os.path.exists(std_ffmpeg):
        shutil.copyfile(ffmpeg_exe, std_ffmpeg)
    if ffmpeg_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
except Exception as e:
    print(f"Warning setting up FFmpeg: {e}")

# Base application directories
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(APP_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

TEMP_DIR = os.path.join(APP_DIR, "temp")
OUTPUTS_DIR = os.path.join(APP_DIR, "outputs")
BROLL_DIR = os.path.join(BACKEND_DIR, "assets", "broll")
CONFIG_FILE = os.path.join(APP_DIR, "config.json")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(BROLL_DIR, exist_ok=True)

# Import pipeline services
from backend.services.downloader import VideoDownloader
from backend.services.transcriber import AudioTranscriber
from backend.services.analyzer import ViralAnalyzer
from backend.services.voiceover import ElevenLabsVoiceover
from backend.services.reframer import SmartFaceReframer
from backend.services.subtitles import SubtitleGenerator
from backend.services.broll_manager import BrollManager
from backend.services.video_engine import VideoEngine

import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ViralClipDesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ViralClip AI - Generátor YouTube Shorts & TikToků")
        self.geometry("980x860")
        self.minsize(860, 720)

        # Config state
        self.config = self.load_config()
        self.is_processing = False

        # Main Layout
        self.create_ui()

    def load_config(self) -> Dict[str, str]:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
            "elevenlabs_api_key": os.getenv("ELEVENLABS_API_KEY", ""),
            "watermark_text": "@moj_kanal"
        }

    def save_config(self):
        self.config["openai_api_key"] = self.openai_entry.get().strip()
        self.config["elevenlabs_api_key"] = self.elevenlabs_entry.get().strip()
        self.config["watermark_text"] = self.watermark_entry.get().strip()
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)
        self.log("Nastavení a API klíče byly úspěšně uloženy.")

    def create_ui(self):
        # Scrollable container
        self.scroll = ctk.CTkScrollableFrame(self, corner_radius=0)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        title = ctk.CTkLabel(
            header_frame,
            text="🎬 ViralClip AI Desktop Studio",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Automatická tvorba virálních Shorts (9:16) z YouTube odkazů • Běží přímo na tvém PC",
            font=ctk.CTkFont(size=13),
            text_color="#94a3b8"
        )
        subtitle.pack(anchor="w")

        # 1. API Keys Section (Collapsible / Compact Card)
        keys_card = ctk.CTkFrame(self.scroll, corner_radius=12, fg_color="#1e293b", border_width=1, border_color="#334155")
        keys_card.pack(fill="x", pady=(0, 15), padx=5)

        keys_title = ctk.CTkLabel(keys_card, text="🔑 API Klíče (Zadej jednou, uloží se na PC):", font=ctk.CTkFont(size=14, weight="bold"))
        keys_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(12, 8))

        # OpenAI Key
        ctk.CTkLabel(keys_card, text="OpenAI API Key (Whisper + GPT-4o):", font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w", padx=15, pady=4)
        self.openai_entry = ctk.CTkEntry(keys_card, placeholder_text="sk-proj-...", show="•", width=420)
        self.openai_entry.grid(row=1, column=1, sticky="ew", padx=15, pady=4)
        self.openai_entry.insert(0, self.config.get("openai_api_key", ""))

        # ElevenLabs Key
        ctk.CTkLabel(keys_card, text="ElevenLabs API Key (pro AI Hlas v Režimu 2):", font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w", padx=15, pady=4)
        self.elevenlabs_entry = ctk.CTkEntry(keys_card, placeholder_text="xi-api-key-...", show="•", width=420)
        self.elevenlabs_entry.grid(row=2, column=1, sticky="ew", padx=15, pady=4)
        self.elevenlabs_entry.insert(0, self.config.get("elevenlabs_api_key", ""))

        save_keys_btn = ctk.CTkButton(keys_card, text="💾 Uložit klíče", width=120, command=self.save_config)
        save_keys_btn.grid(row=3, column=1, sticky="e", padx=15, pady=(8, 12))
        keys_card.grid_columnconfigure(1, weight=1)

        # 2. Mode Selector Section
        mode_label = ctk.CTkLabel(self.scroll, text="Krok 1: Výběr pracovního režimu", font=ctk.CTkFont(size=14, weight="bold"))
        mode_label.pack(anchor="w", padx=5, pady=(5, 6))

        self.mode_var = ctk.StringVar(value="client")
        self.mode_segmented = ctk.CTkSegmentedButton(
            self.scroll,
            values=["👤 REŽIM 1: Pro Klienty & Tvůrce", "⚡ REŽIM 2: Agresivní Monetizace"],
            command=self.on_mode_change,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.mode_segmented.pack(fill="x", padx=5, pady=(0, 10))
        self.mode_segmented.set("👤 REŽIM 1: Pro Klienty & Tvůrce")

        # Mode description card
        self.mode_desc_card = ctk.CTkFrame(self.scroll, corner_radius=12, fg_color="#0f172a", border_width=1, border_color="#38bdf8")
        self.mode_desc_card.pack(fill="x", padx=5, pady=(0, 15))
        self.mode_desc_text = ctk.CTkLabel(
            self.mode_desc_card,
            text="REŽIM 1 (Klient): Čistý zakázkový střih • Auto-reframe 9:16 (sledování obličeje) • Barevné karaoke titulky • Branding vodoznak • 1080x1920 60fps.",
            font=ctk.CTkFont(size=12),
            text_color="#38bdf8",
            wraplength=800,
            justify="left"
        )
        self.mode_desc_text.pack(padx=15, pady=12, anchor="w")

        # 3. Dynamic Mode Options Frame
        self.options_frame = ctk.CTkFrame(self.scroll, corner_radius=12, fg_color="#1e293b")
        self.options_frame.pack(fill="x", padx=5, pady=(0, 15))
        self.setup_client_options()

        # 4. Input YouTube URL & Theme
        input_card = ctk.CTkFrame(self.scroll, corner_radius=12, fg_color="#1e293b", border_width=1, border_color="#334155")
        input_card.pack(fill="x", padx=5, pady=(0, 15))

        ctk.CTkLabel(input_card, text="Krok 2: YouTube URL videa:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(12, 4))
        self.url_entry = ctk.CTkEntry(input_card, placeholder_text="https://www.youtube.com/watch?v=...", height=38, font=ctk.CTkFont(size=13))
        self.url_entry.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(input_card, text="Krok 3: Téma / Instrukce pro AI (volitelné):", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=15, pady=(0, 4))
        self.theme_entry = ctk.CTkEntry(input_card, placeholder_text="např. 'Hledej nejvtipnější momenty', 'Zaměř se na drama a spory'", height=36)
        self.theme_entry.pack(fill="x", padx=15, pady=(0, 12))

        # Clips count & virality threshold
        sliders_row = ctk.CTkFrame(input_card, fg_color="transparent")
        sliders_row.pack(fill="x", padx=15, pady=(0, 12))

        ctk.CTkLabel(sliders_row, text="Počet klipů:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 10))
        self.clips_combo = ctk.CTkComboBox(sliders_row, values=["1", "2", "3"], width=80)
        self.clips_combo.set("2")
        self.clips_combo.pack(side="left", padx=(0, 30))

        ctk.CTkLabel(sliders_row, text="Minimální skóre virality:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 10))
        self.score_slider = ctk.CTkSlider(sliders_row, from_=7.0, to=10.0, number_of_steps=6, width=160)
        self.score_slider.set(8.0)
        self.score_slider.pack(side="left", padx=(0, 10))
        self.score_val_lbl = ctk.CTkLabel(sliders_row, text="8.0 / 10", font=ctk.CTkFont(size=12, weight="bold"))
        self.score_val_lbl.pack(side="left")
        self.score_slider.configure(command=lambda v: self.score_val_lbl.configure(text=f"{v:.1f} / 10"))

        # 5. Big Action Button
        self.run_btn = ctk.CTkButton(
            self.scroll,
            text="🚀 SPUSTIT AUTOMATICKÝ STŘIH SHORTS",
            height=48,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#7c3aed",
            hover_color="#6d28d9",
            command=self.start_processing
        )
        self.run_btn.pack(fill="x", padx=5, pady=(0, 15))

        # 6. Progress and Status
        self.progress_bar = ctk.CTkProgressBar(self.scroll, height=12)
        self.progress_bar.pack(fill="x", padx=5, pady=(0, 8))
        self.progress_bar.set(0)

        self.status_lbl = ctk.CTkLabel(self.scroll, text="Připraven ke spuštění.", font=ctk.CTkFont(size=13, weight="bold"), text_color="#cbd5e1")
        self.status_lbl.pack(anchor="w", padx=5, pady=(0, 8))

        # 7. Log Window
        self.log_box = ctk.CTkTextbox(self.scroll, height=120, font=ctk.CTkFont(family="Consolas", size=11))
        self.log_box.pack(fill="x", padx=5, pady=(0, 15))
        self.log("ViralClip AI Studio připraveno.")

        # 8. Results Card
        self.results_frame = ctk.CTkFrame(self.scroll, corner_radius=12, fg_color="#0f172a", border_width=1, border_color="#334155")
        self.results_frame.pack(fill="x", padx=5, pady=(0, 15))
        self.results_title = ctk.CTkLabel(self.results_frame, text="Hotové klipy se zobrazí zde:", font=ctk.CTkFont(size=14, weight="bold"))
        self.results_title.pack(anchor="w", padx=15, pady=12)

    def on_mode_change(self, value):
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        if "Klient" in value:
            self.mode_var.set("client")
            self.mode_desc_card.configure(border_color="#38bdf8")
            self.mode_desc_text.configure(
                text="REŽIM 1 (Klient): Čistý zakázkový střih • Auto-reframe 9:16 (sledování obličeje) • Barevné karaoke titulky • Branding vodoznak • 1080x1920 60fps.",
                text_color="#38bdf8"
            )
            self.setup_client_options()
        else:
            self.mode_var.set("aggressive_monetization")
            self.mode_desc_card.configure(border_color="#c084fc")
            self.mode_desc_text.configure(
                text="REŽIM 2 (Monetizace): Bypass Content ID & Reused Content • Split-Screen B-roll • Zrychlení 1.02x • ElevenLabs AI komentář (Hook + Pointa + Rekap) • Audio Ducking na 18% • Reakční rámeček.",
                text_color="#c084fc"
            )
            self.setup_aggressive_options()

    def setup_client_options(self):
        row = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=12)

        ctk.CTkLabel(row, text="Branding vodoznak (@handle):", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 10))
        self.watermark_entry = ctk.CTkEntry(row, width=220)
        self.watermark_entry.insert(0, self.config.get("watermark_text", "@moj_kanal"))
        self.watermark_entry.pack(side="left")

    def setup_aggressive_options(self):
        row = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        row.pack(fill="x", padx=15, pady=12)

        ctk.CTkLabel(row, text="Split-Screen B-roll podkres:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 8))
        self.broll_combo = ctk.CTkComboBox(row, values=["Minecraft Parkour", "GTA V Mega Ramp", "Satisfying Sand"], width=180)
        self.broll_combo.set("Minecraft Parkour")
        self.broll_combo.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(row, text="ElevenLabs Hlas:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 8))
        self.voice_combo = ctk.CTkComboBox(row, values=["Adam (Hluboký)", "Rachel (Energická)", "Antoni (Vypravěč)"], width=160)
        self.voice_combo.set("Adam (Hluboký)")
        self.voice_combo.pack(side="left")

    def log(self, text: str):
        self.log_box.insert("end", f"> {text}\n")
        self.log_box.see("end")

    def update_status(self, text: str, progress: float):
        self.status_lbl.configure(text=text)
        self.progress_bar.set(progress)
        self.log(text)

    def start_processing(self):
        if self.is_processing:
            return

        url = self.url_entry.get().strip()
        if not url:
            self.log("CHYBA: Zadej platné YouTube URL!")
            return

        openai_key = self.openai_entry.get().strip()
        if not openai_key:
            self.log("CHYBA: Zadej OpenAI API klíč (potřebný pro Whisper transkripci a výběr virálních momentů)!")
            return

        self.save_config()

        self.is_processing = True
        self.run_btn.configure(state="disabled", text="ZPRACOVÁVÁM...")
        self.progress_bar.set(0.05)

        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        t = threading.Thread(target=self.run_pipeline_worker, daemon=True)
        t.start()

    def run_pipeline_worker(self):
        try:
            url = self.url_entry.get().strip()
            mode = self.mode_var.get()
            theme = self.theme_entry.get().strip()
            max_clips = int(self.clips_combo.get())
            min_score = float(self.score_slider.get())

            openai_key = self.openai_entry.get().strip()
            eleven_key = self.elevenlabs_entry.get().strip()

            watermark = self.watermark_entry.get().strip() if mode == "client" else None

            # B-roll mapping
            broll_type = "minecraft"
            if mode == "aggressive_monetization":
                sel_broll = self.broll_combo.get()
                if "GTA" in sel_broll:
                    broll_type = "gta"
                elif "Satisfying" in sel_broll:
                    broll_type = "satisfying"

            # Voice ID mapping
            voice_id = "pNInz6obpgDQGcFmaJgB"
            if mode == "aggressive_monetization":
                sel_voice = self.voice_combo.get()
                if "Rachel" in sel_voice:
                    voice_id = "21m00Tcm4TlvDq8ikWAM"
                elif "Antoni" in sel_voice:
                    voice_id = "ErXwobaYiN019PkySvjV"

            self.after(0, lambda: self.update_status("Krok 1/6: Stahuji audio z YouTube pro Whisper AI...", 0.15))
            downloader = VideoDownloader(output_dir=TEMP_DIR)
            job_prefix = f"job_{os.getpid()}"
            audio_path = downloader.download_audio_for_transcription(url, job_prefix)

            self.after(0, lambda: self.update_status("Krok 2/6: Whisper AI transkripce s word-level časovými značkami...", 0.35))
            transcriber = AudioTranscriber(api_key=openai_key)
            transcript = transcriber.transcribe_with_word_timestamps(audio_path)

            self.after(0, lambda: self.update_status(f"Krok 3/6: GPT-4o analyzuje virální úseky (Skóre {min_score}+)...", 0.55))
            analyzer = ViralAnalyzer(api_key=openai_key)
            clips = analyzer.analyze_transcript(
                transcript_data=transcript,
                mode=mode,
                theme_focus=theme,
                min_score=min_score,
                max_clips=max_clips
            )

            if not clips:
                raise ValueError(f"Žádný úsek nedosáhl virálního skóre {min_score}/10. Zkus snížit skóre na 7.5.")

            reframer = SmartFaceReframer()
            sub_gen = SubtitleGenerator(output_dir=TEMP_DIR)
            broll_mgr = BrollManager(broll_dir=BROLL_DIR)
            video_engine = VideoEngine(output_dir=OUTPUTS_DIR)
            voiceover = ElevenLabsVoiceover(api_key=eleven_key)

            completed_clips = []
            total = len(clips)

            for idx, clip in enumerate(clips):
                pct = 0.55 + ((idx + 1) / total) * 0.40
                self.after(0, lambda p=pct, i=idx+1: self.update_status(f"Krok 4/6: Stahuji video segment pro klip {i}/{total}...", p - 0.05))

                clip_id = f"clip_{idx + 1}"
                raw_video = downloader.download_video_segment(
                    url=url,
                    start_time=clip["start_time"],
                    end_time=clip["end_time"],
                    base_filename=f"{job_prefix}_{clip_id}"
                )

                sub_file = os.path.join(TEMP_DIR, f"{job_prefix}_{clip_id}_sub.ass")
                sub_gen.generate_karaoke_ass(
                    words=clip.get("words", []),
                    clip_start=clip["start_time"],
                    output_file=sub_file
                )

                out_filename = f"Short_{clip_id}_{int(clip['virality_score']*10)}.mp4"

                if mode == "client":
                    self.after(0, lambda p=pct, i=idx+1: self.update_status(f"Krok 5/6: Auto-reframe tváře & Karaoke render {i}/{total}...", p))
                    crop_info = reframer.analyze_crop_coordinates(raw_video)
                    crop_filter = reframer.get_ffmpeg_crop_filter(crop_info)
                    final_mp4 = video_engine.render_client_mode(
                        raw_video_path=raw_video,
                        ass_subtitles_path=sub_file,
                        output_filename=out_filename,
                        crop_filter=crop_filter,
                        watermark_text=watermark
                    )
                else:
                    self.after(0, lambda p=pct, i=idx+1: self.update_status(f"Krok 5/6: Generuji ElevenLabs AI hlas & Split-Screen {i}/{total}...", p))
                    vo_file = os.path.join(TEMP_DIR, f"{job_prefix}_{clip_id}_vo.mp3")
                    voiceover.generate_commentary_audio(
                        commentary_script=clip.get("commentary_script", {}),
                        output_path=vo_file,
                        voice_id=voice_id
                    )
                    broll_file = broll_mgr.get_or_create_broll(
                        broll_type=broll_type,
                        duration=(clip["end_time"] - clip["start_time"]) + 5
                    )
                    final_mp4 = video_engine.render_aggressive_monetization_mode(
                        raw_video_path=raw_video,
                        broll_video_path=broll_file,
                        voiceover_audio_path=vo_file,
                        ass_subtitles_path=sub_file,
                        output_filename=out_filename,
                        reaction_badge_text="EXKLUZIVNÍ ROZBOR / REAKCE"
                    )

                clip["final_filepath"] = final_mp4
                completed_clips.append(clip)

            self.after(0, lambda: self.on_pipeline_success(completed_clips))

        except Exception as e:
            err = str(e)
            self.after(0, lambda: self.on_pipeline_error(err))

    def on_pipeline_success(self, clips: List[Dict[str, Any]]):
        self.is_processing = False
        self.run_btn.configure(state="normal", text="🚀 SPUSTIT AUTOMATICKÝ STŘIH SHORTS")
        self.update_status(f"HOTOVO! Vygenerováno {len(clips)} virálních Shorts.", 1.0)

        # Populate Results Frame
        header = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(12, 8))

        ctk.CTkLabel(header, text=f"🎉 Hotové Shorts ({len(clips)} klipů):", font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")

        open_folder_btn = ctk.CTkButton(
            header,
            text="📁 Otevřít složku s videi",
            width=160,
            fg_color="#059669",
            hover_color="#047857",
            command=lambda: os.startfile(OUTPUTS_DIR)
        )
        open_folder_btn.pack(side="right")

        for idx, clip in enumerate(clips):
            card = ctk.CTkFrame(self.results_frame, fg_color="#1e293b", corner_radius=8)
            card.pack(fill="x", padx=15, pady=6)

            # Title row with virality score
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(8, 4))

            score_str = f"🔥 {clip.get('virality_score', 9.0):.1f} / 10"
            ctk.CTkLabel(top_row, text=score_str, font=ctk.CTkFont(size=12, weight="bold"), text_color="#f59e0b").pack(side="left", padx=(0, 10))
            ctk.CTkLabel(top_row, text=f"Délka: {clip.get('duration', 30):.0f}s", font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(side="left")

            play_btn = ctk.CTkButton(
                top_row,
                text="▶ Přehrát video",
                width=110,
                height=26,
                command=lambda p=clip["final_filepath"]: os.startfile(p)
            )
            play_btn.pack(side="right")

            # Clickbait title
            title_row = ctk.CTkFrame(card, fg_color="transparent")
            title_row.pack(fill="x", padx=10, pady=2)
            title_txt = clip.get("title", f"Klip #{idx+1}")
            ctk.CTkLabel(title_row, text=f"Název: {title_txt}", font=ctk.CTkFont(size=12, weight="bold"), wraplength=600, justify="left").pack(side="left")
            copy_t_btn = ctk.CTkButton(
                title_row, text="Kopírovat", width=70, height=22,
                command=lambda t=title_txt: self.copy_to_clipboard(t)
            )
            copy_t_btn.pack(side="right")

            # Hashtags
            tags_str = " ".join(clip.get("hashtags", ["#shorts", "#viral"]))
            tags_row = ctk.CTkFrame(card, fg_color="transparent")
            tags_row.pack(fill="x", padx=10, pady=(2, 8))
            ctk.CTkLabel(tags_row, text=f"Tagy: {tags_str}", font=ctk.CTkFont(size=11), text_color="#a855f7").pack(side="left")
            copy_tag_btn = ctk.CTkButton(
                tags_row, text="Kopírovat tagy", width=95, height=22,
                command=lambda t=tags_str: self.copy_to_clipboard(t)
            )
            copy_tag_btn.pack(side="right")

    def copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.log(f"Zkopírováno do schránky: {text[:40]}...")

    def on_pipeline_error(self, err_msg: str):
        self.is_processing = False
        self.run_btn.configure(state="normal", text="🚀 SPUSTIT AUTOMATICKÝ STŘIH SHORTS")
        self.update_status(f"CHYBA: {err_msg}", 0.0)


if __name__ == "__main__":
    app = ViralClipDesktopApp()
    app.mainloop()
