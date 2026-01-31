import { useState, useEffect, useCallback, useRef } from 'react';
import type {
  HandLandmark,
  GestureType,
  ConnectionState,
  HandTrackingMessage,
  ConfigMessage,
} from '../types/websocket';

interface UseWebSocketReturn {
  connectionState: ConnectionState;
  landmarks: HandLandmark[];
  gesture: GestureType;
  mousePosition: { x: number; y: number };
  fps: number;
  error: string | null;
  connect: () => void;
  disconnect: () => void;
  sendConfig: (config: Omit<ConfigMessage, 'type'>) => void;
}

/**
 * Custom hook for WebSocket connection to Air Mouse backend
 * 
 * Manages WebSocket state, hand tracking data, and gesture recognition.
 * Does NOT auto-connect - call connect() manually.
 */
export const useWebSocket = (url: string): UseWebSocketReturn => {
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [landmarks, setLandmarks] = useState<HandLandmark[]>([]);
  const [gesture, setGesture] = useState<GestureType>('none');
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [fps, setFps] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // Use ref to persist WebSocket instance across renders
  const wsRef = useRef<WebSocket | null>(null);

  /**
   * Establishes WebSocket connection to the server
   */
  const connect = useCallback(() => {
    // Prevent multiple connections
    if (wsRef.current?.readyState === WebSocket.OPEN || 
        wsRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    setConnectionState('connecting');
    setError(null);

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnectionState('connected');
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const message: HandTrackingMessage = JSON.parse(event.data);
        if (message.type === 'hand_data') {
          setLandmarks(message.landmarks);
          setGesture(message.gesture);
          setMousePosition(message.mouse_position);
          setFps(message.fps);
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onerror = () => {
      setConnectionState('error');
      setError('WebSocket connection error');
    };

    ws.onclose = () => {
      setConnectionState('disconnected');
      wsRef.current = null;
    };
  }, [url]);

  /**
   * Manually closes the WebSocket connection
   */
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  /**
   * Sends configuration to the backend
   */
  const sendConfig = useCallback((config: Omit<ConfigMessage, 'type'>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const message: ConfigMessage = {
        type: 'config',
        ...config,
      };
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  // Cleanup on unmount (following WebcamFeed.tsx pattern)
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    connectionState,
    landmarks,
    gesture,
    mousePosition,
    fps,
    error,
    connect,
    disconnect,
    sendConfig,
  };
};
