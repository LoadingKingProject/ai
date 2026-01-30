import React, { useRef, useEffect } from 'react';

interface VideoBackgroundProps {
  src: string;
  onEnded: () => void;
  className?: string;
}

export const VideoBackground: React.FC<VideoBackgroundProps> = ({ src, onEnded, className = '' }) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.play().catch(e => console.log("Autoplay blocked:", e));
    }
  }, []);

  return (
    <div className={`fixed inset-0 z-10 bg-black ${className}`}>
      <video
        ref={videoRef}
        src={src}
        className="w-full h-full object-cover"
        onEnded={onEnded}
        muted
        playsInline
      />
    </div>
  );
};