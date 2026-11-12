import React from "react";
import { UserCheck, Zap, Scissors, SplitSquareVertical, Flame, Layers, Sparkles, Volume2 } from "lucide-react";

export type PipelineMode = "client" | "aggressive_monetization";

interface ModeSelectorProps {
  currentMode: PipelineMode;
  onSelectMode: (mode: PipelineMode) => void;
}

export const ModeSelector: React.FC<ModeSelectorProps> = ({ currentMode, onSelectMode }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* MODE 1: CLIENT / OFFICIAL CREATORS */}
      <div
        onClick={() => onSelectMode("client")}
        className={`cursor-pointer rounded-2xl p-5 transition-all duration-300 relative border ${
          currentMode === "client"
            ? "bg-slate-900/90 border-cyan-500/80 shadow-lg shadow-cyan-500/10 ring-1 ring-cyan-500/50"
            : "bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-900/60"
        }`}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div
              className={`w-11 h-11 rounded-xl flex items-center justify-center ${
                currentMode === "client"
                  ? "bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/30"
                  : "bg-slate-800 text-slate-400"
              }`}
            >
              <UserCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-base text-white">REŽIM 1: Pro Klienty & Tvůrce</span>
              </div>
              <span className="text-xs text-cyan-400 font-medium">Čistý prémiový zakázkový střih</span>
            </div>
          </div>
          {currentMode === "client" && (
            <span className="px-2 py-0.5 text-[11px] font-semibold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 rounded-full">
              Zvoleno
            </span>
          )}
        </div>

        <p className="mt-3 text-xs text-slate-300 leading-relaxed">
          Určeno pro stříhání vlastních podcastů nebo se svolením tvůrce. Zaměřeno na maximální kvalitu bez zkreslení.
        </p>

        <ul className="mt-4 space-y-2 text-xs text-slate-400 border-t border-slate-800/80 pt-3">
          <li className="flex items-center space-x-2">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
            <span><strong>Precizní auto-reframe 9:16:</strong> Detekce tváře OpenCV/MediaPipe a plynulé centrování</span>
          </li>
          <li className="flex items-center space-x-2">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
            <span><strong>Karaoke titulky:</strong> Synchronizace po slovech přes Whisper API se žlutým zvýrazněním</span>
          </li>
          <li className="flex items-center space-x-2">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
            <span><strong>Branding overlay:</strong> Vložení vodoznaku nebo @sociálních sítí tvůrce</span>
          </li>
          <li className="flex items-center space-x-2">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
            <span><strong>Export ve špičkové kvalitě:</strong> 1080x1920, 60fps, 320kbps audio bez rušení</span>
          </li>
        </ul>
      </div>

      {/* MODE 2: AGGRESSIVE MONETIZATION */}
      <div
        onClick={() => onSelectMode("aggressive_monetization")}
        className={`cursor-pointer rounded-2xl p-5 transition-all duration-300 relative border ${
          currentMode === "aggressive_monetization"
            ? "bg-slate-900/90 border-purple-500/80 shadow-lg shadow-purple-500/10 ring-1 ring-purple-500/50"
            : "bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-900/60"
        }`}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div
              className={`w-11 h-11 rounded-xl flex items-center justify-center ${
                currentMode === "aggressive_monetization"
                  ? "bg-gradient-to-tr from-purple-500 to-pink-500 text-white shadow-md shadow-purple-500/30"
                  : "bg-slate-800 text-slate-400"
              }`}
            >
              <Zap className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-base text-white">REŽIM 2: Agresivní Monetizace</span>
              </div>
              <span className="text-xs text-purple-400 font-medium">Bypass Content ID & Reused Content</span>
            </div>
          </div>
          {currentMode === "aggressive_monetization" && (
            <span className="px-2 py-0.5 text-[11px] font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30 rounded-full">
              Zvoleno
            </span>
          )}
        </div>

        <p className="mt-3 text-xs text-slate-300 leading-relaxed">
          Určeno pro přeměnu cizího obsahu na uznatelný fair-use rozbor. Aplikuje audio/video modifikace a AI komentář.
        </p>

        <ul className="mt-4 space-y-2 text-xs text-slate-400 border-t border-slate-800/80 pt-3">
          <li className="flex items-center space-x-2">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
            <span><strong>Split-Screen Layout:</strong> Nahoře upravený klip, dole Minecraft/GTA parkour podkres</span>
          </li>
          <li className="flex items-center space-x-2">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
            <span><strong>Anti-Content ID ochrana:</strong> 1.02x zrychlení, zrcadlení (hflip) & LUT tónování</span>
          </li>
          <li className="flex items-center space-x-2">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
            <span><strong>AI Hlasový Rozbor (ElevenLabs):</strong> Automatický Hook, Kontext a Rekapitulace</span>
          </li>
          <li className="flex items-center space-x-2">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
            <span><strong>Audio Ducking:</strong> Původní zvuk utlumen na ~18%, do popředí jde komentář</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

