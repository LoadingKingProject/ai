import React, { useEffect, useState } from 'react';
import { AppStage } from '../types';
import type { ConnectionState, GestureType } from '../types/websocket';
import { Scan, Zap, CheckCircle2, Lock, Crosshair, Aperture, Wifi, WifiOff, Hand, Move, ZoomIn, ArrowLeft, ArrowRight, MousePointer } from 'lucide-react';

interface HUDOverlayProps {
  stage: AppStage;
  connectionState?: ConnectionState;
  gesture?: GestureType;
  onReconnect?: () => void;
}

/**
 * Get display text and icon for current gesture
 */
const getGestureDisplay = (gesture: GestureType | undefined) => {
  switch (gesture) {
    case 'click':
      return { text: 'CLICK DETECTED', icon: MousePointer };
    case 'drag':
      return { text: 'DRAG MODE', icon: Move };
    case 'zoom':
      return { text: 'ZOOM MODE', icon: ZoomIn };
    case 'swipe_left':
      return { text: 'SWIPE ←', icon: ArrowLeft };
    case 'swipe_right':
      return { text: 'SWIPE →', icon: ArrowRight };
    case 'palm_open':
      return { text: 'PALM OPEN - SWIPE READY', icon: Hand };
    default:
      return null;
  }
};

export const HUDOverlay: React.FC<HUDOverlayProps> = ({ 
  stage, 
  connectionState = 'disconnected' as ConnectionState,
  gesture = 'none' as GestureType,
  onReconnect 
}) => {
  const [randomCode, setRandomCode] = useState("0000");
  const [coords, setCoords] = useState({ x: 0, y: 0 });

  // Simulate changing data
  useEffect(() => {
    const interval = setInterval(() => {
      setRandomCode(Math.floor(Math.random() * 9999).toString().padStart(4, '0'));
      setCoords({ 
        x: Math.floor(Math.random() * 100), 
        y: Math.floor(Math.random() * 100) 
      });
    }, 100);
    return () => clearInterval(interval);
  }, []);

  const isCalibrating = stage === AppStage.CALIBRATING;
  const isComplete = stage === AppStage.CALIBRATION_COMPLETE;
  const isActive = stage === AppStage.ACTIVE_MODE;

  // Get backend connection status display
  const getConnectionDisplay = () => {
    switch (connectionState) {
      case 'connected':
        return { text: 'BACKEND: CONNECTED', color: 'text-emerald-400', dotColor: 'bg-emerald-500', Icon: Wifi };
      case 'connecting':
        return { text: 'CONNECTING...', color: 'text-yellow-400', dotColor: 'bg-yellow-500', Icon: Wifi };
      case 'error':
        return { text: 'BACKEND: ERROR', color: 'text-red-400', dotColor: 'bg-red-500', Icon: WifiOff };
      default:
        return { text: 'BACKEND: OFFLINE', color: 'text-red-400', dotColor: 'bg-red-500', Icon: WifiOff };
    }
  };

  const connectionDisplay = getConnectionDisplay();
  const gestureDisplay = getGestureDisplay(gesture);

  return (
    <div className="absolute inset-0 z-30 pointer-events-none select-none p-4 md:p-8 flex flex-col justify-between overflow-hidden">
      
      {/* --- BACKGROUND GRID (Subtle Tech Texture) --- */}
      <div className="absolute inset-0 opacity-10" 
           style={{ backgroundImage: 'linear-gradient(rgba(0, 255, 255, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 255, 0.1) 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
      </div>

      {/* --- TOP HEADER --- */}
      <div className="flex justify-between items-start z-10">
        {/* Top Left Block */}
        <div className="flex flex-col gap-1 border-l-2 border-cyan-500/50 pl-4">
          <div className="flex items-center gap-2 text-cyan-400">
            <Aperture className="w-5 h-5 animate-spin-slow duration-[10s]" />
            <span className="font-mono-tech text-sm tracking-[0.3em] font-bold">VISION OS</span>
          </div>
          <div className="text-[10px] font-mono-tech text-cyan-600 tracking-widest">
            SYS.VER 4.2.0 // BUILD {randomCode}
          </div>
        </div>

        {/* Top Center Decor */}
        <div className="hidden md:flex flex-col items-center opacity-50">
          <div className="w-32 h-1 bg-gradient-to-r from-transparent via-cyan-500 to-transparent"></div>
          <div className="text-[9px] text-cyan-300 font-mono-tech mt-1 tracking-[0.5em]">TARGETING SYSTEM</div>
        </div>

        {/* Top Right Block */}
        <div className="text-right border-r-2 border-emerald-500/50 pr-4">
          {/* Network Status */}
          <div className="font-mono-tech text-xs text-emerald-400 tracking-widest flex items-center justify-end gap-2">
            <span>NET: CONNECTED</span>
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
          </div>
          <div className="font-mono-tech text-[10px] text-emerald-600/80 mt-1">
            LAT: {coords.x}.{randomCode} / LON: {coords.y}.{randomCode}
          </div>
          
          {/* Backend Connection Status */}
          <div className={`font-mono-tech text-xs tracking-widest flex items-center justify-end gap-2 mt-2 ${connectionDisplay.color}`}>
            <connectionDisplay.Icon className="w-3 h-3" />
            <span>{connectionDisplay.text}</span>
            <div className={`w-2 h-2 rounded-full ${connectionDisplay.dotColor} ${connectionState === 'connecting' ? 'animate-pulse' : ''}`}></div>
          </div>
          
          {/* Reconnect Button */}
          {connectionState === 'disconnected' && onReconnect && (
            <button 
              onClick={onReconnect}
              className="mt-2 text-xs text-cyan-400 hover:text-cyan-300 pointer-events-auto font-mono-tech tracking-widest border border-cyan-500/30 px-2 py-1 rounded hover:bg-cyan-500/10 transition-colors"
            >
              [RECONNECT]
            </button>
          )}
        </div>
      </div>

      {/* --- CENTER AREA (State Dependent) --- */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex flex-col items-center justify-center w-full max-w-2xl text-center z-20">
        
        {/* Calibration / Loading UI */}
        {(isCalibrating || isComplete) && (
          <div className="relative flex items-center justify-center">
            {/* Outer Rotating Ring */}
            <div className={`absolute border border-dashed border-cyan-500/20 rounded-full w-[350px] h-[350px] transition-all duration-1000 ${isComplete ? 'scale-110 opacity-0' : 'animate-[spin_10s_linear_infinite]'}`}></div>
            
            {/* Inner HUD Circle */}
            <div className={`w-64 h-64 border-2 rounded-full flex items-center justify-center relative backdrop-blur-sm bg-black/10 transition-all duration-500 ${isComplete ? 'border-emerald-500/80 shadow-[0_0_50px_rgba(16,185,129,0.3)]' : 'border-cyan-500/40'}`}>
               
               {/* Scanning Line */}
               {!isComplete && (
                 <div className="absolute w-full h-1 bg-cyan-400/50 shadow-[0_0_15px_rgba(34,211,238,0.8)] animate-[scan_2s_ease-in-out_infinite] top-0"></div>
               )}

               <div className="flex flex-col items-center">
                  {isCalibrating && (
                    <>
                      <Scan className="w-10 h-10 text-cyan-400 mb-4 animate-pulse" />
                      <h1 className="text-2xl md:text-3xl font-bold tracking-[0.2em] text-white drop-shadow-lg">
                        CALIBRATING
                      </h1>
                      <div className="flex items-center gap-1 mt-2">
                         <div className="w-1 h-1 bg-cyan-400 rounded-full animate-bounce"></div>
                         <div className="w-1 h-1 bg-cyan-400 rounded-full animate-bounce delay-100"></div>
                         <div className="w-1 h-1 bg-cyan-400 rounded-full animate-bounce delay-200"></div>
                      </div>
                      <p className="mt-2 text-cyan-400/80 font-mono-tech text-xs tracking-widest">
                        BIOMETRIC SCAN IN PROGRESS
                      </p>
                    </>
                  )}

                  {isComplete && (
                    <>
                      <CheckCircle2 className="w-14 h-14 text-emerald-400 mb-4 animate-in zoom-in duration-300" />
                      <h1 className="text-2xl md:text-3xl font-bold tracking-[0.2em] text-emerald-100 drop-shadow-[0_0_15px_rgba(52,211,153,1)]">
                        ACCESS GRANTED
                      </h1>
                      <p className="mt-2 text-emerald-400/80 font-mono-tech text-xs tracking-widest">
                        USER IDENTITY CONFIRMED
                      </p>
                    </>
                  )}
               </div>
            </div>
          </div>
        )}
      </div>

      {/* --- BOTTOM FOOTER --- */}
      <div className="flex justify-between items-end z-10">
        {/* Bottom Left Status */}
        <div className="flex flex-col gap-2">
           {/* Gesture Display - Show when active and gesture detected */}
           {isActive && gestureDisplay && (
             <div className="flex items-center gap-3 text-cyan-400 animate-in slide-in-from-left-4 duration-300 mb-2">
               <div className="p-2 border border-cyan-500/30 bg-cyan-900/10 rounded">
                 <gestureDisplay.icon className="w-5 h-5" />
               </div>
               <div>
                 <div className="font-bold tracking-[0.15em] text-md text-white drop-shadow-md">
                   {gestureDisplay.text}
                 </div>
               </div>
             </div>
           )}
           
           {/* Default Active State */}
           {isActive && (
             <div className="flex items-center gap-3 text-emerald-400 animate-in slide-in-from-left-4 duration-700">
               <div className="p-2 border border-emerald-500/30 bg-emerald-900/10 rounded">
                 <Zap className="w-6 h-6" fill="currentColor" />
               </div>
               <div>
                 <div className="font-bold tracking-[0.15em] text-lg text-white drop-shadow-md">
                   GESTURE ACTIVE
                 </div>
                 <div className="text-[10px] font-mono-tech text-emerald-500/70 tracking-widest">
                   HAND TRACKING ENABLED
                 </div>
               </div>
             </div>
           )}
           {!isActive && (
              <div className="flex items-center gap-2 text-amber-500/60">
                <Lock className="w-4 h-4" />
                <span className="font-mono-tech text-xs tracking-widest">SYSTEM LOCKED</span>
              </div>
           )}
        </div>

        {/* Bottom Right Decoration */}
        <div className="flex items-end gap-4 opacity-60">
           <div className="hidden md:block w-32 h-8 border-b border-r border-slate-600 relative">
              <div className="absolute bottom-0 right-0 w-2 h-2 bg-slate-500"></div>
           </div>
           <div className="font-mono-tech text-xs text-slate-500 tracking-widest">
             8X-9214-A
           </div>
        </div>
      </div>

      {/* --- DECORATIVE OVERLAY ELEMENTS --- */}
      {/* Corner Brackets */}
      <div className="absolute top-6 left-6 w-8 h-8 border-t-2 border-l-2 border-cyan-500/30 rounded-tl-none"></div>
      <div className="absolute top-6 right-6 w-8 h-8 border-t-2 border-r-2 border-cyan-500/30 rounded-tr-none"></div>
      <div className="absolute bottom-6 left-6 w-8 h-8 border-b-2 border-l-2 border-cyan-500/30 rounded-bl-none"></div>
      <div className="absolute bottom-6 right-6 w-8 h-8 border-b-2 border-r-2 border-cyan-500/30 rounded-br-none"></div>
      
      {/* Crosshair Center (Subtle) */}
      {isActive && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 opacity-20 pointer-events-none">
          <Crosshair className="w-96 h-96 text-white stroke-[0.5]" />
        </div>
      )}
    </div>
  );
};
