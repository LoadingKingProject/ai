import { useState, useEffect, useCallback, useRef } from 'react';
import type {
  HandLandmark,
  GestureType,
  ConnectionState,
  WebSocketMessage,
  ConfigMessage,
} from '../types/websocket';

interface FaceData {
  state: string;
  status: 'WAIT' | 'PERFECT' | 'TOO_CLOSE' | 'TOO_FAR' | 'BAD_POSE';
  distanceRatio: number;
  targetRatio: number;
  faceResults?: {
    total: number;
    rank: string;
    details: Record<string, { score: number; val: number }>;
  };
}

interface UseWebSocketReturn {
  connectionState: ConnectionState;
  landmarks: HandLandmark[];
  gesture: GestureType;
  mousePosition: { x: number; y: number };
  faceData: FaceData | null;
  currentImage: string | null;  // Base64 image
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
  const [faceData, setFaceData] = useState<FaceData | null>(null);
  const [currentImage, setCurrentImage] = useState<string | null>(null);
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
        const message: WebSocketMessage = JSON.parse(event.data);
        
        // Handle Image Stream
        if ('image' in message && message.image) {
          setCurrentImage(`data:image/jpeg;base64,${message.image}`);
        }

        if (message.type === 'hand_data') {
          setLandmarks(message.landmarks);
          setGesture(message.gesture);
          setMousePosition(message.mouse_position);
          setFps(message.fps);
          // Clear face data when hand tracking is active
          setFaceData(null);
        } 
        else if (message.type === 'face_data') {
          setFaceData({
            state: message.state,
            status: message.status,
            distanceRatio: message.distance_ratio,
            targetRatio: message.target_ratio,
            faceResults: message.face_results,
          });
          setFps(message.fps);
          // Clear hand data when face analysis is active
          setLandmarks([]);
          setGesture('none');
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
    faceData,
    currentImage,
    fps,
    error,
    connect,
    disconnect,
    sendConfig,
  };
};
