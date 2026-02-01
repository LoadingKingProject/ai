import React from 'react';

interface WebcamFeedProps {
  imageSrc: string | null;
}

export const WebcamFeed: React.FC<WebcamFeedProps> = ({ imageSrc }) => {
  return (
    <div className="fixed inset-0 z-0 overflow-hidden bg-black">
      {imageSrc ? (
        <img
          src={imageSrc}
          alt="Webcam Feed"
          className="w-full h-full object-cover transform scale-x-[-1]"
        />
      ) : (
        <div className="flex items-center justify-center h-full text-red-500 font-mono-tech tracking-widest animate-pulse">
          [ ! ] WAITING FOR VIDEO STREAM
        </div>
      )}
      
      {/* Grid Overlay Effect */}
      <div className="absolute inset-0 pointer-events-none opacity-20"
           style={{
             backgroundImage: 'linear-gradient(rgba(0, 255, 255, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 255, 0.1) 1px, transparent 1px)',
             backgroundSize: '50px 50px'
           }}>
      </div>
    </div>
  );
};
