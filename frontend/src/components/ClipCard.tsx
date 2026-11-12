import React, { useState } from "react";
import { Download, Copy, Check, Flame, Play, Clock, Share2, Tag, FileText } from "lucide-react";

export interface ClipData {
  clip_id: string;
  title: string;
  description: string;
  hashtags: string[];
  virality_score: number;
  virality_reason: string;
  duration: number;
  start_time: number;
  end_time: number;
  video_url: string;
  download_url: string;
  mode: string;
}

interface ClipCardProps {
  clip: ClipData;
  apiBaseUrl: string;
}

export const ClipCard: React.FC<ClipCardProps> = ({ clip, apiBaseUrl }) => {
  const [copiedTitle, setCopiedTitle] = useState(false);
  const [copiedTags, setCopiedTags] = useState(false);

  // Full video url pointing to backend static server
  const fullVideoSrc = clip.video_url.startsWith("http")
    ? clip.video_url
    : `${apiBaseUrl}${clip.video_url}`;

  const fullDownloadUrl = clip.download_url.startsWith("http")
    ? clip.download_url
    : `${apiBaseUrl}${clip.download_url}`;

  const handleCopyTitle = () => {
    navigator.clipboard.writeText(clip.title);
    setCopiedTitle(true);
    setTimeout(() => setCopiedTitle(false), 2000);
  };

  const handleCopyTags = () => {
    const formatted = `${clip.description}\n\n${clip.hashtags.join(" ")}`;
    navigator.clipboard.writeText(formatted);
    setCopiedTags(true);
    setTimeout(() => setCopiedTags(false), 2000);
  };

  return (
    <div className="glass-panel rounded-2xl overflow-hidden border border-slate-700/60 shadow-xl flex flex-col lg:flex-row transition-all duration-300 hover:border-purple-500/50">
      {/* 9:16 Vertical Video Player Container */}
      <div className="lg:w-80 shrink-0 bg-black flex items-center justify-center p-3 relative">
        <div className="w-full aspect-[9/16] max-h-[520px] rounded-xl overflow-hidden shadow-2xl relative bg-slate-950 border border-slate-800">
          <video
            src={fullVideoSrc}
            controls
            playsInline
            preload="metadata"
            className="w-full h-full object-cover"
          />
          {/* Mode Badge Overlay */}
          <div className="absolute top-2 left-2 pointer-events-none">
            <span
              className={`px-2 py-0.5 text-[10px] font-bold uppercase rounded-md shadow-md ${
                clip.mode === "client"
                  ? "bg-cyan-500/90 text-slate-950"
                  : "bg-purple-600/90 text-white"
              }`}
            >
              {clip.mode === "client" ? "Režim: Klient" : "Režim: Monetizace"}
            </span>
          </div>
        </div>
      </div>

      {/* Metadata, Copy Tools & Actions */}
      <div className="p-6 flex-1 flex flex-col justify-between space-y-4">
        <div>
          {/* Score & Time Badges */}
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1 px-2.5 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-400 text-xs font-black">
                <Flame className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                <span>{clip.virality_score.toFixed(1)} / 10 Virality</span>
              </div>

              <div className="flex items-center space-x-1 px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 text-xs font-semibold">
                <Clock className="w-3 h-3 text-slate-400" />
                <span>{clip.duration}s</span>
              </div>
            </div>

            <span className="text-[11px] text-slate-400">
              Čas ve videu: {Math.floor(clip.start_time / 60)}:{(clip.start_time % 60).toFixed(0).padStart(2, "0")} -{" "}
              {Math.floor(clip.end_time / 60)}:{(clip.end_time % 60).toFixed(0).padStart(2, "0")}
            </span>
          </div>

          {/* AI Virality Reason */}
          <p className="text-xs text-slate-400 italic mb-4 bg-slate-900/50 p-2.5 rounded-lg border border-slate-800">
            "{clip.virality_reason}"
          </p>

          {/* Clickbait Title */}
          <div className="space-y-1 mb-4">
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
              <span>Optimalizovaný Clickbait Název (Vysoké CTR):</span>
              <button
                onClick={handleCopyTitle}
                className="text-purple-400 hover:text-purple-300 flex items-center space-x-1 font-normal text-xs"
              >
                {copiedTitle ? (
                  <>
                    <Check className="w-3 h-3 text-emerald-400" />
                    <span className="text-emerald-400 font-bold">Zkopírováno</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    <span>Kopírovat název</span>
                  </>
                )}
              </button>
            </label>
            <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800 text-sm font-bold text-white select-all">
              {clip.title}
            </div>
          </div>

          {/* Description & Hashtags */}
          <div className="space-y-1">
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
              <span>Popisek a Virální Hashtagy pro algoritmus:</span>
              <button
                onClick={handleCopyTags}
                className="text-purple-400 hover:text-purple-300 flex items-center space-x-1 font-normal text-xs"
              >
                {copiedTags ? (
                  <>
                    <Check className="w-3 h-3 text-emerald-400" />
                    <span className="text-emerald-400 font-bold">Zkopírováno</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    <span>Kopírovat popisek</span>
                  </>
                )}
              </button>
            </label>
            <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800 text-xs text-slate-300 select-all space-y-2">
              <p>{clip.description}</p>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {clip.hashtags.map((tag, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 rounded-md bg-purple-500/10 text-purple-300 font-medium text-[11px]"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Download Action Button */}
        <div className="pt-2">
          <a
            href={fullDownloadUrl}
            target="_blank"
            rel="noopener noreferrer"
            download
            className="w-full py-3 px-4 rounded-xl font-bold text-sm bg-gradient-to-r from-purple-600 via-indigo-600 to-cyan-500 hover:from-purple-500 hover:to-cyan-400 text-white flex items-center justify-center space-x-2 shadow-lg shadow-purple-600/20 transition-all duration-200 transform active:scale-[0.98]"
          >
            <Download className="w-4 h-4" />
            <span>Stáhnout hotové video (1080x1920 MP4)</span>
          </a>
        </div>
      </div>
    </div>
  );
};
