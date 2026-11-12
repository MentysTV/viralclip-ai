"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { ModeSelector, PipelineMode } from "@/components/ModeSelector";
import { StatusTracker } from "@/components/StatusTracker";
import { ClipCard, ClipData } from "@/components/ClipCard";
import {
  Link as LinkIcon,
  Sparkles,
  Sliders,
  PlaySquare,
  ShieldAlert,
  Gamepad2,
  Mic2,
  CheckCircle,
  HelpCircle
} from "lucide-react";

export default function Dashboard() {
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [mode, setMode] = useState<PipelineMode>("client");
  const [themePrompt, setThemePrompt] = useState("");
  const [watermarkText, setWatermarkText] = useState("@creator_channel");
  const [brollType, setBrollType] = useState("minecraft");
  const [voiceId, setVoiceId] = useState("pNInz6obpgDQGcFmaJgB"); // Adam
  const [minScore, setMinScore] = useState(8.0);
  const [maxClips, setMaxClips] = useState(3);

  // Job states
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<
    "idle" | "queued" | "downloading" | "transcribing" | "analyzing" | "rendering" | "completed" | "failed"
  >("idle");
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [clips, setClips] = useState<ClipData[]>([]);

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Polling job status
  useEffect(() => {
    if (!activeJobId || jobStatus === "completed" || jobStatus === "failed") {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${apiBaseUrl}/api/jobs/${activeJobId}`);
        if (!res.ok) throw new Error("Chyba při komunikaci s backendem");
        const data = await res.json();

        setJobStatus(data.status);
        setProgress(data.progress);
        setCurrentStep(data.current_step);
        if (data.error_message) setErrorMessage(data.error_message);

        if (data.status === "completed" && data.clips) {
          setClips(data.clips);
          setIsSubmitting(false);
        } else if (data.status === "failed") {
          setIsSubmitting(false);
        }
      } catch (err: any) {
        console.error("Polling error:", err);
      }
    }, 2500);

    return () => clearInterval(interval);
  }, [activeJobId, jobStatus, apiBaseUrl]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!youtubeUrl.trim()) return;

    setIsSubmitting(true);
    setErrorMessage(null);
    setClips([]);
    setJobStatus("queued");
    setProgress(5);
    setCurrentStep("Odesílám požadavek do cloudu...");

    try {
      const payload = {
        youtube_url: youtubeUrl.trim(),
        mode: mode,
        theme_prompt: themePrompt.trim(),
        watermark_text: mode === "client" ? watermarkText.trim() : null,
        broll_type: mode === "aggressive_monetization" ? brollType : null,
        voice_id: mode === "aggressive_monetization" ? voiceId : null,
        min_virality_score: Number(minScore),
        max_clips: Number(maxClips),
      };

      const res = await fetch(`${apiBaseUrl}/api/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || "Server odmítl požadavek");
      }

      const data = await res.json();
      setActiveJobId(data.job_id);
    } catch (err: any) {
      console.error(err);
      setJobStatus("failed");
      setErrorMessage(err.message || "Nepodařilo se zahájit pipeline");
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero Title */}
        <div className="text-center space-y-3 pt-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Cloud Video Pipeline 2026</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-white">
            YouTube URL na <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">Virální Shorts & TikToky</span>
          </h1>
          <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto">
            Plně automatické zpracování v cloudu bez nutnosti lokálního výkonu. Zvolte režim pro klienta nebo agresivní transformaci pro monetizaci.
          </p>
        </div>

        {/* Mode Selector */}
        <div className="space-y-2">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Krok 1: Výběr pracovního režimu
          </label>
          <ModeSelector currentMode={mode} onSelectMode={setMode} />
        </div>

        {/* Main Input Form */}
        <form onSubmit={handleSubmit} className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-700/60 shadow-xl space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center justify-between">
              <span>Krok 2: Zadejte YouTube URL</span>
              <span className="text-slate-400 font-normal">Podporuje podcasty, rozhovory, streamy</span>
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                <LinkIcon className="w-5 h-5" />
              </div>
              <input
                type="url"
                required
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="w-full pl-11 pr-4 py-3.5 bg-slate-900/90 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm font-medium transition"
              />
            </div>
          </div>

          {/* Theme / Custom Focus Input */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center justify-between">
              <span>Krok 3: Téma / Dodatečné instrukce pro AI</span>
              <span className="text-xs text-purple-400 font-normal">Volitelné</span>
            </label>
            <input
              type="text"
              value={themePrompt}
              onChange={(e) => setThemePrompt(e.target.value)}
              placeholder="např. 'Vyber nejvtipnější hlášky a spory', 'Zaměř se na moment, kde mluví o penězích'"
              className="w-full px-4 py-3 bg-slate-900/90 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm transition"
            />
          </div>

          {/* Dynamic Settings depending on Mode */}
          {mode === "client" ? (
            <div className="p-4 rounded-xl bg-cyan-950/20 border border-cyan-500/30 space-y-4">
              <div className="flex items-center space-x-2 text-cyan-300 font-bold text-xs uppercase tracking-wide">
                <Sliders className="w-4 h-4" />
                <span>Nastavení pro klientský střih</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-slate-300 font-medium mb-1">
                    Vodoznak / Branding tvůrce (@handle):
                  </label>
                  <input
                    type="text"
                    value={watermarkText}
                    onChange={(e) => setWatermarkText(e.target.value)}
                    placeholder="@moj_kanal"
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-300 font-medium mb-1">
                    Minimální skóre virality (1-10):
                  </label>
                  <div className="flex items-center space-x-3">
                    <input
                      type="range"
                      min="7"
                      max="10"
                      step="0.5"
                      value={minScore}
                      onChange={(e) => setMinScore(parseFloat(e.target.value))}
                      className="w-full accent-cyan-400"
                    />
                    <span className="text-xs font-bold text-cyan-400 shrink-0">{minScore} / 10</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-500/30 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 text-purple-300 font-bold text-xs uppercase tracking-wide">
                  <ShieldAlert className="w-4 h-4" />
                  <span>Anti-Content ID & Fair Use Modifikátory</span>
                </div>
                <span className="text-[11px] text-amber-400 font-semibold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                  Rychlost 1.02x & Audio Ducking Aktivní
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {/* B-roll Picker */}
                <div>
                  <label className="block text-xs text-slate-300 font-medium mb-1 flex items-center space-x-1">
                    <Gamepad2 className="w-3.5 h-3.5 text-purple-400" />
                    <span>Split-Screen B-roll:</span>
                  </label>
                  <select
                    value={brollType}
                    onChange={(e) => setBrollType(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs focus:ring-1 focus:ring-purple-500"
                  >
                    <option value="minecraft">Minecraft Parkour</option>
                    <option value="gta">GTA V Mega Ramp Stunt</option>
                    <option value="satisfying">Satisfying Sand / ASMR</option>
                  </select>
                </div>

                {/* Voice Picker */}
                <div>
                  <label className="block text-xs text-slate-300 font-medium mb-1 flex items-center space-x-1">
                    <Mic2 className="w-3.5 h-3.5 text-purple-400" />
                    <span>ElevenLabs Hlas:</span>
                  </label>
                  <select
                    value={voiceId}
                    onChange={(e) => setVoiceId(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs focus:ring-1 focus:ring-purple-500"
                  >
                    <option value="pNInz6obpgDQGcFmaJgB">Adam (Hluboký, Dramatický)</option>
                    <option value="21m00Tcm4TlvDq8ikWAM">Rachel (Energická, Čistá)</option>
                    <option value="ErXwobaYiN019PkySvjV">Antoni (Dynamický vypravěč)</option>
                  </select>
                </div>

                {/* Max clips */}
                <div>
                  <label className="block text-xs text-slate-300 font-medium mb-1">
                    Počet klipů k exportu:
                  </label>
                  <select
                    value={maxClips}
                    onChange={(e) => setMaxClips(parseInt(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs"
                  >
                    <option value="1">1 nejlepší klip</option>
                    <option value="2">2 klipy</option>
                    <option value="3">3 klipy (Doporučeno)</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Submit Action Button */}
          <button
            type="submit"
            disabled={isSubmitting || !youtubeUrl}
            className={`w-full py-4 px-6 rounded-xl font-black text-base flex items-center justify-center space-x-2 shadow-xl transition-all duration-300 ${
              isSubmitting || !youtubeUrl
                ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                : "bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white shadow-purple-600/30 hover:shadow-purple-600/50 transform active:scale-[0.99]"
            }`}
          >
            <Sparkles className="w-5 h-5" />
            <span>
              {isSubmitting
                ? "Zpracovávám v cloudu..."
                : mode === "client"
                ? "Spustit Auto-Reframe & Karaoke Střih"
                : "Spustit Agresivní Transformaci & Monetizaci"}
            </span>
          </button>
        </form>

        {/* Live Status Tracker */}
        {jobStatus !== "idle" && (
          <StatusTracker
            status={jobStatus}
            progress={progress}
            currentStep={currentStep}
            errorMessage={errorMessage}
            mode={mode}
          />
        )}

        {/* Generated Clips Showcase */}
        {clips.length > 0 && (
          <div className="space-y-6 pt-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h2 className="text-xl sm:text-2xl font-black text-white flex items-center space-x-2">
                  <span>Vygenerované Klipy</span>
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    {clips.length} hotové
                  </span>
                </h2>
                <p className="text-xs text-slate-400">
                  Videa jsou připravena pro okamžité publikování na YouTube Shorts, TikTok a Instagram Reels.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-6">
              {clips.map((clip) => (
                <ClipCard key={clip.clip_id} clip={clip} apiBaseUrl={apiBaseUrl} />
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/80 py-6 mt-12 text-center text-xs text-slate-500">
        <p>ViralClip AI Cloud Engine &copy; 2026. Běží plně na serverech bez nutnosti lokálního GPU.</p>
      </footer>
    </div>
  );
}

