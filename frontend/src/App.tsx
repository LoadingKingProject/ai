import React, { useState, useEffect } from 'react';
import { AppStage } from './types';
import { INTRO_VIDEO_URL, CALIBRATION_DURATION_MS, SUCCESS_MESSAGE_DURATION_MS, WEBSOCKET_URL } from './constants';
import { VideoBackground } from './components/VideoBackground';
import { WebcamFeed } from './components/WebcamFeed';
import { HUDOverlay } from './components/HUDOverlay';
import { HandLandmarks } from './components/HandLandmarks';
import { useWebSocket } from './hooks/useWebSocket';

const App: React.FC = () => {
  const [stage, setStage] = useState<AppStage>(AppStage.BOOT_SEQUENCE);
  
  // WebSocket connection for hand tracking
  const { 
    connectionState, 
    landmarks, 
    gesture, 
    connect, 
    disconnect 
  } = useWebSocket(WEBSOCKET_URL);

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

  // Auto-connect to WebSocket when entering ACTIVE_MODE
  useEffect(() => {
    if (stage === AppStage.ACTIVE_MODE && connectionState === 'disconnected') {
      connect();
    }
    
    // Cleanup on unmount
    return () => {
      if (connectionState === 'connected') {
        disconnect();
      }
    };
  }, [stage, connectionState, connect, disconnect]);

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

      {/* LAYER 2: Hand Landmarks Overlay (only in ACTIVE_MODE) */}
      {stage === AppStage.ACTIVE_MODE && (
        <HandLandmarks landmarks={landmarks} />
      )}

      {/* LAYER 3: UI Overlay */}
      {stage !== AppStage.BOOT_SEQUENCE && (
        <div className="absolute inset-0 animate-in fade-in duration-1000">
           <HUDOverlay 
             stage={stage} 
             connectionState={connectionState}
             gesture={gesture}
             onReconnect={connect}
           />
        </div>
      )}
      
      {/* Optional: Skip button for development/demo purposes */}
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
