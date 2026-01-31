import React, { useRef, useEffect } from 'react';
import type { HandLandmark } from '../types/websocket';

interface HandLandmarksProps {
  landmarks: HandLandmark[];
}

/**
 * HandLandmarks - Canvas overlay component for visualizing hand tracking points
 * 
 * Renders 21 MediaPipe hand landmarks as cyan dots with glow effect.
 * Positioned as an overlay on top of the WebcamFeed component.
 */
export const HandLandmarks: React.FC<HandLandmarksProps> = ({ landmarks }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size to match window
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Don't render if no landmarks
    if (landmarks.length === 0) return;

    // Draw each landmark
    landmarks.forEach((lm) => {
      // Convert normalized (0-1) to canvas pixels
      // Mirror X coordinate to match mirrored video feed
      const x = (1 - lm.x) * canvas.width;
      const y = lm.y * canvas.height;

      // Draw point with glow effect
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = 'cyan';
      ctx.shadowColor = 'cyan';
      ctx.shadowBlur = 10;
      ctx.fill();

      // Reset shadow for next iteration
      ctx.shadowBlur = 0;
    });
  }, [landmarks]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-10 pointer-events-none"
    />
  );
};
