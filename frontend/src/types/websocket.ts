/**
 * WebSocket Message Schema for Air Mouse
 * 
 * Defines TypeScript interfaces for all WebSocket communication between
 * Python backend (main.py) and frontend client.
 */

/**
 * HandLandmark - Single hand landmark point from MediaPipe
 * 
 * Maps to Python: lmList = [[id, cx, cy], ...]
 * where id is 0-20 (MediaPipe hand landmark index)
 */
export interface HandLandmark {
  /** MediaPipe landmark index (0-20) */
  id: number;
  /** Normalized x coordinate (0-1) */
  x: number;
  /** Normalized y coordinate (0-1) */
  y: number;
}

/**
 * GestureType - Recognized hand gestures
 * 
 * Maps to Python gesture detection logic in main.py
 */
export type GestureType =
  | 'none'
  | 'click'
  | 'drag'
  | 'zoom'
  | 'swipe_left'
  | 'swipe_right'
  | 'palm_open';

/**
 * HandTrackingMessage - Server to Client message (Active Mode)
 * 
 * Sent by Python backend with hand tracking data and gesture recognition results.
 * Maps to Python: extract_landmarks(), is_palm_open(), gesture detection
 */
export interface HandTrackingMessage {
  /** Message type identifier */
  type: 'hand_data';
  /** Base64 encoded JPEG image */
  image?: string;
  /** Array of hand landmarks (21 points from MediaPipe) */
  landmarks: HandLandmark[];
  /** Detected gesture type */
  gesture: GestureType;
  /** Calculated mouse position on screen */
  mouse_position: {
    x: number;
    y: number;
  };
  /** Whether palm is open (from is_palm_open() function) */
  is_palm_open: boolean;
  /** Frames per second from backend */
  fps: number;
  /** Server timestamp (milliseconds) */
  timestamp: number;
}

/**
 * FaceDataMessage - Server to Client message (Face Analysis Mode)
 * 
 * Sent during Face Scanning/Analysis/Report stages.
 */
export interface FaceDataMessage {
  type: 'face_data';
  /** Base64 encoded JPEG image */
  image?: string;
  /** Current app state on backend */
  state: string;
  /** Distance status */
  status: 'WAIT' | 'PERFECT' | 'TOO_CLOSE' | 'TOO_FAR' | 'BAD_POSE';
  /** Current face width ratio */
  distance_ratio: number;
  /** Target ratio (approx 1m) */
  target_ratio: number;
  /** Analysis results (only available in REPORT state) */
  face_results?: {
    total: number;
    rank: string;
    details: Record<string, { score: number; val: number }>;
  };
  fps: number;
}

/**
 * ConfigMessage - Client to Server configuration message
 * 
 * Sent by frontend to adjust backend parameters
 */
export interface ConfigMessage {
  /** Message type identifier */
  type: 'config';
  /** Smoothing factor (optional, 1-10) */
  smoothing?: number;
  /** Click detection distance threshold (optional, pixels) */
  click_distance?: number;
}

/**
 * ConnectionState - WebSocket connection status
 */
export type ConnectionState =
  | 'disconnected'
  | 'connecting'
  | 'connected'
  | 'error';

/**
 * WebSocket message union type for type-safe message handling
 */
export type WebSocketMessage = HandTrackingMessage | FaceDataMessage | ConfigMessage;
