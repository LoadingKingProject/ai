import React, { useState, useEffect } from 'react';
import { AppStage } from './types';
import { INTRO_VIDEO_URL, CALIBRATION_DURATION_MS, SUCCESS_MESSAGE_DURATION_MS } from './constants';
import { VideoBackground } from './components/VideoBackground';
import { WebcamFeed } from './components/WebcamFeed';
import { HUDOverlay } from './components/HUDOverlay';

const App: React.FC = () => {
  const [stage, setStage] = useState<AppStage>(AppStage.BOOT_SEQUENCE);

  // Handle Video Completion
  const handleVideoEnded = () => {
    setStage(AppStage.CALIBRATING);
  };

  // Logic to handle state transitions for "Calibration" simulation
  useEffect(() => {
    if (stage === AppStage.CALIBRATING) {
      // 1. Simulate external vision score calculation time
      const calibrationTimer = setTimeout(() => {
        setStage(AppStage.CALIBRATION_COMPLETE);
      }, CALIBRATION_DURATION_MS);

      return () => clearTimeout(calibrationTimer);
    }

    if (stage === AppStage.CALIBRATION_COMPLETE) {
      // 2. Show Success message briefly before activating Gesture Mode
      const successTimer = setTimeout(() => {
        setStage(AppStage.ACTIVE_MODE);
      }, SUCCESS_MESSAGE_DURATION_MS);

      return () => clearTimeout(successTimer);
    }
  }, [stage]);

  return (
    <div className="relative w-screen h-screen bg-black overflow-hidden">
      
      {/* Global CSS Effects */}
      <div className="scanline"></div>
      <div className="vignette"></div>

      {/* LAYER 1: Background Content */}
      {stage === AppStage.BOOT_SEQUENCE ? (
        <VideoBackground 
          src={INTRO_VIDEO_URL} 
          onEnded={handleVideoEnded} 
          className="animate-in fade-in duration-1000"
        />
      ) : (
        <WebcamFeed />
      )}

      {/* LAYER 2: UI Overlay */}
      {/* We only show the HUD if we are NOT in the boot sequence (video playing),
          or you can overlay HUD *over* the video if desired. 
          Here we show it after video starts fading or ends. 
      */}
      {stage !== AppStage.BOOT_SEQUENCE && (
        <div className="absolute inset-0 animate-in fade-in duration-1000">
           <HUDOverlay stage={stage} />
        </div>
      )}
      
      {/* Optional: Skip button for development/demo purposes (hidden in prod feel) */}
      {/* <button 
        onClick={() => setStage(AppStage.CALIBRATING)}
        className="fixed top-2 right-2 z-50 text-xs text-gray-700 opacity-20 hover:opacity-100"
      >
        [DEBUG: SKIP VIDEO]
      </button> */}
    </div>
  );
};

export default App;