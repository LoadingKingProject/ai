import React, { useEffect, useState, useRef } from 'react';
import { Trophy, CheckCircle, RefreshCcw, ShieldCheck, ShieldAlert } from 'lucide-react';

interface FaceReportOverlayProps {
  results: {
    total: number;
    rank: string;
    details: Record<string, { score: number; val: number }>;
  };
  onApprove: () => void;
  onRetry: () => void;
}

export const FaceReportOverlay: React.FC<FaceReportOverlayProps> = ({ results, onApprove, onRetry }) => {
  const { total, rank, details } = results;
  
  // States: 'checking' -> 'success' | 'failed'
  const [status, setStatus] = useState<'checking' | 'success' | 'failed'>('checking');
  
  // Audio refs
  const successAudio = useRef<HTMLAudioElement | null>(null);
  const failAudio = useRef<HTMLAudioElement | null>(null);

  // Score Threshold
  const PASS_SCORE = 70;

  // Initialize Logic
  useEffect(() => {
    successAudio.current = new Audio('/sounds/success.mp3');
    failAudio.current = new Audio('/sounds/failed.mp3');

    // Initial Check logic
    const checkResult = () => {
      // Always show the score report for 3 seconds first!
      if (total >= PASS_SCORE) {
        setTimeout(handleSuccess, 3000);
      } else {
        setTimeout(handleFail, 3000);
      }
    };

    // Run logic immediately
    checkResult();

    // Master Key Listener (Shift + Enter)
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.shiftKey && e.key === 'Enter') {
        console.log("MASTER KEY ACTIVATED: Forcing Success");
        handleSuccess();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []); // Run once on mount

  const handleSuccess = () => {
    setStatus('success');
    successAudio.current?.play().catch(e => console.log("Audio play error:", e));
    
    // Auto transition after 3s of Success Animation
    setTimeout(() => {
      onApprove();
    }, 3000);
  };

  const handleFail = () => {
    setStatus('failed');
    failAudio.current?.play().catch(e => console.log("Audio play error:", e));
    
    // Auto retry after 3s of Failed Animation
    setTimeout(() => {
      onRetry();
    }, 3000);
  };

  const getRankColor = (r: string) => {
    switch (r) {
      case 'SSS': return 'text-fuchsia-500 shadow-fuchsia-500/50';
      case 'S': return 'text-cyan-400 shadow-cyan-400/50';
      case 'A': return 'text-emerald-400 shadow-emerald-400/50';
      case 'B': return 'text-amber-400 shadow-amber-400/50';
      default: return 'text-red-400 shadow-red-400/50';
    }
  };

  const rankColor = getRankColor(rank);

  // --- RENDER: ACCESS GRANTED (Success) ---
  if (status === 'success') {
    return (
      <div className="absolute inset-0 z-50 bg-black/90 flex flex-col items-center justify-center animate-in fade-in duration-500">
        <div className="relative flex flex-col items-center justify-center">
          {/* Rotating Rings */}
          <div className="absolute w-[500px] h-[500px] border border-emerald-500/30 rounded-full animate-[spin_10s_linear_infinite]"></div>
          <div className="absolute w-[450px] h-[450px] border border-dashed border-emerald-500/20 rounded-full animate-[spin_15s_linear_infinite_reverse]"></div>
          <div className="absolute w-[400px] h-[400px] border-2 border-emerald-500 rounded-full animate-pulse shadow-[0_0_50px_rgba(16,185,129,0.5)]"></div>
          
          <ShieldCheck className="w-24 h-24 text-emerald-400 mb-8 animate-in zoom-in duration-500" />
          
          <h1 className="text-6xl font-black text-white tracking-[0.1em] drop-shadow-[0_0_20px_rgba(16,185,129,0.8)] mb-4 text-center">
            ACCESS GRANTED
          </h1>
          
          <div className="text-emerald-400 font-mono-tech tracking-[0.3em] text-lg animate-pulse">
            BIOMETRIC MATCH CONFIRMED
          </div>

          <div className="mt-8 flex flex-col items-center gap-2">
            <div className="text-zinc-500 font-mono-tech text-xs tracking-widest">
              INITIALIZING AIR MOUSE PROTOCOL...
            </div>
            {/* Loading Bar */}
            <div className="w-64 h-1 bg-zinc-800 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-500 animate-[loading_3s_ease-in-out_forwards]" style={{ width: '100%' }}></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // --- RENDER: ACCESS DENIED (Failed) ---
  if (status === 'failed') {
    return (
      <div className="absolute inset-0 z-50 bg-black/90 flex flex-col items-center justify-center animate-in fade-in duration-500">
        <div className="relative flex flex-col items-center justify-center">
          {/* Pulsing Red Rings */}
          <div className="absolute w-[500px] h-[500px] border border-red-500/30 rounded-full animate-pulse"></div>
          <div className="absolute w-[400px] h-[400px] border-2 border-red-500 rounded-full shadow-[0_0_50px_rgba(239,68,68,0.5)]"></div>
          
          <ShieldAlert className="w-24 h-24 text-red-500 mb-8 animate-bounce" />
          
          <h1 className="text-6xl font-black text-red-500 tracking-[0.1em] drop-shadow-[0_0_20px_rgba(239,68,68,0.8)] mb-4 text-center">
            ACCESS DENIED
          </h1>
          
          <div className="text-red-400 font-mono-tech tracking-[0.3em] text-lg animate-pulse">
            INTRUDER DETECTED
          </div>

          <div className="mt-8 flex flex-col items-center gap-2">
            <div className="text-zinc-500 font-mono-tech text-xs tracking-widest">
              RETRYING SCAN...
            </div>
            <div className="w-64 h-1 bg-zinc-800 rounded-full overflow-hidden">
              <div className="h-full bg-red-500 animate-[loading_3s_ease-in-out_forwards]" style={{ width: '100%' }}></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // --- RENDER: SCORE REPORT (Fallback / Initial - shown for 3s) ---
  return (
    <div className="absolute inset-0 z-40 bg-black/80 backdrop-blur-sm flex flex-col items-center justify-center animate-in fade-in duration-500">
      <div className="bg-zinc-900/90 border border-zinc-700 p-8 rounded-2xl w-full max-w-lg shadow-2xl relative overflow-hidden">
        
        <div className={`absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-transparent via-${rank === 'C' ? 'red-500' : 'emerald-500'} to-transparent opacity-50`}></div>

        <div className="flex flex-col items-center mb-8">
          <Trophy className={`w-12 h-12 mb-2 ${rank === 'C' ? 'text-zinc-500' : 'text-yellow-400'}`} />
          <h2 className="text-2xl font-bold tracking-widest text-white">ANALYSIS REPORT</h2>
        </div>

        <div className="flex items-center justify-center gap-8 mb-8">
          <div className="flex flex-col items-center">
            <span className="text-sm text-zinc-400 tracking-wider">RANK</span>
            <span className={`text-6xl font-black italic tracking-tighter drop-shadow-lg ${rankColor}`}>
              {rank}
            </span>
          </div>
          <div className="w-px h-16 bg-zinc-700"></div>
          <div className="flex flex-col items-center">
            <span className="text-sm text-zinc-400 tracking-wider">SCORE</span>
            <span className="text-5xl font-bold text-white tracking-tight">
              {Math.floor(total)}
            </span>
          </div>
        </div>

        <div className="space-y-4 mb-8">
          {Object.entries(details).map(([key, { score, val }]) => (
            <div key={key} className="flex flex-col gap-1">
              <div className="flex justify-between text-xs text-zinc-400 font-mono-tech">
                <span>{key}</span>
                <span>{score}/100</span>
              </div>
              <div className="w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-1000 ease-out ${
                    score > 90 ? 'bg-cyan-500' : score > 70 ? 'bg-emerald-500' : 'bg-amber-500'
                  }`}
                  style={{ width: `${score}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center text-zinc-500 font-mono-tech text-xs tracking-widest animate-pulse">
          PROCESSING RESULTS...
        </div>

      </div>
    </div>
  );
};
