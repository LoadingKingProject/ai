import React, { useState, useEffect } from 'react';
import { AppStage } from './types';
import { INTRO_VIDEO_URL, WEBSOCKET_URL } from './constants';
import { VideoBackground } from './components/VideoBackground';
import { WebcamFeed } from './components/WebcamFeed';
import { HUDOverlay } from './components/HUDOverlay';
import { HandLandmarks } from './components/HandLandmarks';
import { FaceSniperOverlay } from './components/FaceSniperOverlay';
import { FaceReportOverlay } from './components/FaceReportOverlay';
import { useWebSocket } from './hooks/useWebSocket';

const App: React.FC = () => {
  const [stage, setStage] = useState<AppStage>(AppStage.BOOT_SEQUENCE);
  
  const { 
    connectionState, 
    landmarks, 
    gesture, 
    faceData,
    currentImage,
    connect, 
    disconnect 
  } = useWebSocket(WEBSOCKET_URL);

  const handleVideoEnded = () => {
    setStage(AppStage.FACE_SCANNING);
    connect();
  };

  useEffect(() => {
    if (faceData) {
      if (faceData.state === 'WAITING_FACE') setStage(AppStage.FACE_SCANNING);
      else if (faceData.state === 'ANALYZING') setStage(AppStage.FACE_ANALYZING);
      else if (faceData.state === 'REPORT') setStage(AppStage.FACE_REPORT);
    }
    else if (landmarks.length > 0) {
      setStage(AppStage.ACTIVE_MODE);
    }
  }, [faceData, landmarks]);

  // Handle Approval (Success)
  const handleApprove = async () => {
    try {
      await fetch('http://localhost:8000/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved: true })
      });
    } catch (err) {
      console.error("Failed to approve:", err);
    }
  };

  // Handle Retry (Failure)
  const handleRetry = async () => {
    try {
      // Signal backend to reset state
      await fetch('http://localhost:8000/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved: false }) // False means Retry
      });
      setStage(AppStage.FACE_SCANNING);
    } catch (err) {
      console.error("Failed to retry:", err);
    }
  };

  return (
    <div className="relative w-screen h-screen bg-black overflow-hidden">
      
      <div className="scanline"></div>
      <div className="vignette"></div>

      {stage === AppStage.BOOT_SEQUENCE ? (
        <VideoBackground 
          src={INTRO_VIDEO_URL} 
          onEnded={handleVideoEnded} 
          className="animate-in fade-in duration-1000"
        />
      ) : (
        <WebcamFeed imageSrc={currentImage} />
      )}

      {(stage === AppStage.FACE_SCANNING || stage === AppStage.FACE_ANALYZING) && faceData && (
        <FaceSniperOverlay 
          status={faceData.status}
          distanceRatio={faceData.distanceRatio}
          targetRatio={faceData.targetRatio}
        />
      )}

      {stage === AppStage.FACE_REPORT && faceData && faceData.faceResults && (
        <FaceReportOverlay 
          results={faceData.faceResults}
          onApprove={handleApprove}
          onRetry={handleRetry}
        />
      )}

      {stage === AppStage.ACTIVE_MODE && (
        <HandLandmarks landmarks={landmarks} />
      )}

      {stage !== AppStage.BOOT_SEQUENCE && (
        <div className="absolute inset-0 animate-in fade-in duration-1000 pointer-events-none">
           <HUDOverlay 
             stage={stage} 
             connectionState={connectionState}
             gesture={gesture}
             onReconnect={connect}
           />
        </div>
      )}
    </div>
  );
};

export default App;
