import React from "react";
import { Sparkles, Video, Cpu, ShieldCheck } from "lucide-react";

export const Header: React.FC = () => {
  return (
    <header className="border-b border-slate-800/80 bg-slate-950/60 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/20">
            <Video className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                ViralClip AI
              </span>
              <span className="px-2 py-0.5 text-[10px] uppercase font-bold tracking-wider bg-purple-500/20 text-purple-300 border border-purple-500/30 rounded-full">
                Cloud Engine
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Automatizovaná továrna na YouTube Shorts & TikToky
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="hidden md:inline">FFmpeg & Whisper Cloud Worker:</span>
            <span>Aktivní</span>
          </div>
        </div>
      </div>
    </header>
  );
};

