import React, { useRef, useEffect } from 'react';

interface FaceSniperOverlayProps {
  status: 'WAIT' | 'PERFECT' | 'TOO_CLOSE' | 'TOO_FAR' | 'BAD_POSE';
  distanceRatio: number;
  targetRatio: number;
}

export const FaceSniperOverlay: React.FC<FaceSniperOverlayProps> = ({ 
  status, 
  distanceRatio, 
  targetRatio 
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Responsive Canvas Size
    const updateSize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    updateSize();
    window.addEventListener('resize', updateSize);

    // Drawing Logic
    const draw = () => {
      const w = canvas.width;
      const h = canvas.height;
      const cx = w / 2;
      const cy = h / 2;

      ctx.clearRect(0, 0, w, h);

      // 1. Crosshair
      ctx.strokeStyle = 'rgba(30, 30, 30, 0.5)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(cx, 0);
      ctx.lineTo(cx, h);
      ctx.moveTo(0, cy);
      ctx.lineTo(w, cy);
      ctx.stroke();

      // 2. Gauge Bar Background
      const barW = Math.min(600, w * 0.8);
      const barH = 30;
      const barX = cx - barW / 2;
      const barY = h - 100;

      ctx.fillStyle = 'rgba(40, 40, 40, 0.8)';
      ctx.fillRect(barX, barY, barW, barH);

      // 3. Target Line (Center)
      const targetX = barX + barW / 2;
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(targetX, barY - 10);
      ctx.lineTo(targetX, barY + barH + 10);
      ctx.stroke();

      ctx.fillStyle = '#FFFFFF';
      ctx.font = '12px "Share Tech Mono"';
      ctx.fillText('TARGET (1m)', targetX - 35, barY - 20);

      // 4. Current Position Cursor
      const DISPLAY_RANGE = 0.05; // Sensitivity
      // Invert diff logic because ratio increases as user gets closer (face gets bigger)
      // We want: User Closer -> Ratio Bigger -> Cursor Right (Too Close)
      //          User Farther -> Ratio Smaller -> Cursor Left (Too Far)
      const diff = distanceRatio - targetRatio;
      
      const offset = (diff / DISPLAY_RANGE) * (barW / 2);
      let cursorX = targetX + offset;
      cursorX = Math.max(barX, Math.min(barX + barW, cursorX));

      // 5. Status Styles
      let color = '#FF0000'; // Red (Default/Too Close)
      let msg = '<< MOVE BACK';

      if (status === 'TOO_FAR') {
        color = '#00FFFF'; // Cyan
        msg = 'COME CLOSER >>';
      } else if (status === 'BAD_POSE') {
        color = '#FF00FF'; // Magenta
        msg = 'LOOK STRAIGHT';
      } else if (status === 'PERFECT') {
        color = '#00FF00'; // Green
        msg = 'TARGET LOCKED';

        // Lock-on Effect
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.beginPath();
        // Top bracket
        ctx.moveTo(targetX - 20, barY - 5);
        ctx.lineTo(targetX, barY - 15);
        ctx.lineTo(targetX + 20, barY - 5);
        // Bottom bracket
        ctx.moveTo(targetX - 20, barY + barH + 5);
        ctx.lineTo(targetX, barY + barH + 15);
        ctx.lineTo(targetX + 20, barY + barH + 5);
        ctx.stroke();
      }

      if (status === 'WAIT') {
        msg = 'DETECTING FACE...';
        color = '#AAAAAA';
      }

      // Draw Cursor (Triangle)
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.moveTo(cursorX, barY + barH);
      ctx.lineTo(cursorX - 10, barY + barH + 15);
      ctx.lineTo(cursorX + 10, barY + barH + 15);
      ctx.fill();

      // Draw Message
      ctx.font = 'bold 24px "Share Tech Mono"';
      ctx.textAlign = 'center';
      ctx.fillStyle = color;
      ctx.fillText(msg, cx, h - 140);
    };

    // Animation Loop
    let animationId: number;
    const render = () => {
      draw();
      animationId = requestAnimationFrame(render);
    };
    render();

    return () => {
      window.removeEventListener('resize', updateSize);
      cancelAnimationFrame(animationId);
    };
  }, [status, distanceRatio, targetRatio]);

  return <canvas ref={canvasRef} className="fixed inset-0 z-20 pointer-events-none" />;
};
