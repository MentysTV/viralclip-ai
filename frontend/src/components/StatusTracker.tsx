import React from "react";
import { Loader2, CheckCircle2, AlertCircle, FileVideo, Mic, BrainCircuit, Sparkles, Layers } from "lucide-react";

interface StatusTrackerProps {
  status: "queued" | "downloading" | "transcribing" | "analyzing" | "rendering" | "completed" | "failed";
  progress: number;
  currentStep: string;
  errorMessage?: string | null;
  mode: string;
}

export const StatusTracker: React.FC<StatusTrackerProps> = ({
  status,
  progress,
  currentStep,
  errorMessage,
  mode,
}) => {
  const steps = [
    { id: "downloading", label: "Stahování audia z YouTube", icon: FileVideo },
    { id: "transcribing", label: "Whisper AI synchronizace slov", icon: Mic },
    { id: "analyzing", label: "GPT-4o virální analýza (8+/10)", icon: BrainCircuit },
    {
      id: "rendering",
      label: mode === "client" ? "Auto-reframe & Karaoke střih" : "Anti-Content ID & ElevenLabs Rozbor",
      icon: Sparkles,
    },
  ];

  const getStepStatus = (stepId: string) => {
    if (status === "failed") return "error";
    if (status === "completed") return "done";

    const order = ["downloading", "transcribing", "analyzing", "rendering", "completed"];
    const currentIndex = order.indexOf(status);
    const stepIndex = order.indexOf(stepId);

    if (currentIndex > stepIndex) return "done";
    if (currentIndex === stepIndex) return "active";
    return "pending";
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-700/60 shadow-xl my-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          {status === "completed" ? (
            <CheckCircle2 className="w-6 h-6 text-emerald-400" />
          ) : status === "failed" ? (
            <AlertCircle className="w-6 h-6 text-rose-500" />
          ) : (
            <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
          )}
          <div>
            <h3 className="font-bold text-sm sm:text-base text-white">
              {status === "completed"
                ? "Zpracování úspěšně dokončeno!"
                : status === "failed"
                ? "Chyba při zpracování videa"
                : "Automatická cloudová pipeline pracuje..."}
            </h3>
            <p className="text-xs text-slate-400">{currentStep}</p>
          </div>
        </div>
        <div className="text-right">
          <span className="text-lg font-black text-purple-400">{progress}%</span>
        </div>
      </div>

      {/* Animated progress bar */}
      <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden mb-6">
        <div
          className={`h-2.5 rounded-full transition-all duration-500 ${
            status === "failed"
              ? "bg-rose-500"
              : status === "completed"
              ? "bg-emerald-500"
              : "bg-gradient-to-r from-purple-500 via-indigo-500 to-cyan-400"
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Step indicators */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {steps.map((st) => {
          const state = getStepStatus(st.id);
          const Icon = st.icon;

          return (
            <div
              key={st.id}
              className={`flex items-center space-x-2.5 p-2.5 rounded-xl border text-xs transition-all ${
                state === "done"
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                  : state === "active"
                  ? "bg-purple-500/10 border-purple-500/50 text-purple-300 ring-1 ring-purple-500/30"
                  : "bg-slate-900/40 border-slate-800/80 text-slate-500"
              }`}
            >
              <div
                className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                  state === "done"
                    ? "bg-emerald-500/20 text-emerald-400"
                    : state === "active"
                    ? "bg-purple-500/20 text-purple-400"
                    : "bg-slate-800 text-slate-600"
                }`}
              >
                {state === "active" ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Icon className="w-4 h-4" />
                )}
              </div>
              <span className="font-medium truncate">{st.label}</span>
            </div>
          );
        })}
      </div>

      {errorMessage && (
        <div className="mt-4 p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-300 text-xs flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
};

