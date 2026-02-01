import React, { useRef, useState } from 'react';
import { Power } from 'lucide-react';

interface VideoBackgroundProps {
  src: string;
  onEnded: () => void;
  className?: string;
}

export const VideoBackground: React.FC<VideoBackgroundProps> = ({ src, onEnded, className = '' }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [hasStarted, setHasStarted] = useState(false);

  const handleStart = () => {
    if (videoRef.current) {
      videoRef.current.muted = false; // Unmute
      videoRef.current.play()
        .then(() => setHasStarted(true))
        .catch(e => console.error("Playback failed:", e));
    }
  };

  return (
    <div className={`fixed inset-0 z-50 bg-black ${className}`}>
      {/* Video Element */}
      <video
        ref={videoRef}
        src={src}
        className={`w-full h-full object-cover transition-opacity duration-1000 ${hasStarted ? 'opacity-100' : 'opacity-30'}`}
        onEnded={onEnded}
        playsInline
        // Preload but don't auto-play until clicked
        preload="auto"
      />

      {/* Start Button Overlay */}
      {!hasStarted && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/60 backdrop-blur-sm z-50">
          
          {/* Decorative Elements */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] border border-cyan-500/20 rounded-lg pointer-events-none"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[520px] h-[320px] border-x border-cyan-500/10 rounded-lg pointer-events-none"></div>

          <button
            onClick={handleStart}
            className="group relative px-8 py-4 bg-transparent border-2 border-cyan-500 text-cyan-400 font-mono-tech tracking-[0.2em] text-xl font-bold uppercase transition-all duration-300 hover:bg-cyan-500 hover:text-black hover:shadow-[0_0_30px_rgba(6,182,212,0.6)] active:scale-95"
          >
            <span className="flex items-center gap-3">
              <Power className="w-6 h-6 animate-pulse" />
              SYNCHRONIZE INTERFACE
            </span>
            
            {/* Corner Accents */}
            <div className="absolute top-0 left-0 w-2 h-2 bg-cyan-500 -translate-x-1/2 -translate-y-1/2 transition-all group-hover:w-full group-hover:h-full group-hover:opacity-0"></div>
            <div className="absolute bottom-0 right-0 w-2 h-2 bg-cyan-500 translate-x-1/2 translate-y-1/2 transition-all group-hover:w-full group-hover:h-full group-hover:opacity-0"></div>
          </button>

          <div className="mt-6 text-cyan-500/50 font-mono-tech text-xs tracking-widest animate-pulse">
            SYSTEM STANDBY // AWAITING INPUT
          </div>
        </div>
      )}
    </div>
  );
};
