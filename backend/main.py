"""
Air Mouse Backend - FastAPI WebSocket Server

Provides WebSocket endpoint for real-time hand tracking data.
Camera capture runs in a background thread, sending hand tracking
data to connected WebSocket clients.
"""

import asyncio
import sys
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

# Ensure backend directory is in path for imports
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from hand_tracker import HandTracker, HandLandmark
from mouse_controller import MouseController


# Configuration
CAM_ID = 0
CAM_WIDTH = 640
CAM_HEIGHT = 480
SMOOTHING = 10
FRAME_REDUCTION = 100
CLICK_COOLDOWN = 0.5
SWIPE_COOLDOWN = 1.0
TARGET_FPS = 30


class AirMouseServer:
    """
    Air Mouse server managing camera capture and WebSocket connections.

    Runs camera processing in a background thread and broadcasts
    hand tracking data to connected WebSocket clients.
    """

    def __init__(self):
        self.hand_tracker: Optional[HandTracker] = None
        self.mouse_controller: Optional[MouseController] = None

        self.running = False
        self.capture_thread: Optional[threading.Thread] = None

        # Latest tracking data (thread-safe via GIL for simple reads)
        self.latest_data: Optional[Dict[str, Any]] = None
        self.data_lock = threading.Lock()

        # FPS calculation
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0.0

        # Gesture timing
        self.last_click_time = 0.0
        self.last_swipe_time = 0.0

    def start(self) -> bool:
        """Initialize and start camera capture thread."""
        self.hand_tracker = HandTracker(
            cam_id=CAM_ID,
            cam_width=CAM_WIDTH,
            cam_height=CAM_HEIGHT,
        )

        self.mouse_controller = MouseController(
            cam_width=CAM_WIDTH,
            cam_height=CAM_HEIGHT,
            frame_reduction=FRAME_REDUCTION,
            smoothing=SMOOTHING,
        )

        if not self.hand_tracker.start_camera():
            print("Failed to open camera")
            return False

        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()

        print(f"Camera started: {CAM_WIDTH}x{CAM_HEIGHT}")
        return True

    def stop(self) -> None:
        """Stop camera capture and cleanup."""
        self.running = False

        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)

        if self.hand_tracker:
            self.hand_tracker.close()
            self.hand_tracker = None

        if self.mouse_controller:
            self.mouse_controller.release_all()
            self.mouse_controller = None

        print("Camera stopped")

    def _capture_loop(self) -> None:
        """Main capture loop running in background thread."""
        frame_interval = 1.0 / TARGET_FPS

        while self.running and self.hand_tracker:
            loop_start = time.time()

            # Read frame
            success, frame = self.hand_tracker.read_frame()
            if not success or frame is None:
                continue

            # Process frame
            results = self.hand_tracker.process_frame(frame)

            # Build tracking data
            data = self._process_results(results, frame.shape)

            # Store latest data
            with self.data_lock:
                self.latest_data = data

            # FPS calculation
            self.frame_count += 1
            elapsed = time.time() - self.fps_start_time
            if elapsed >= 1.0:
                self.current_fps = self.frame_count / elapsed
                self.frame_count = 0
                self.fps_start_time = time.time()

            # Rate limiting
            processing_time = time.time() - loop_start
            sleep_time = frame_interval - processing_time
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _process_results(self, results, frame_shape) -> Dict[str, Any]:
        """Process MediaPipe results and return tracking data dict."""
        current_time = time.time()

        # Default data when no hand detected
        data = {
            "type": "hand_data",
            "landmarks": [],
            "gesture": "none",
            "mouse_position": {"x": 0, "y": 0},
            "is_palm_open": False,
            "fps": round(self.current_fps, 1),
            "timestamp": int(current_time * 1000),
        }

        # Check if hand detected (new Tasks API uses hand_landmarks)
        if results is None or not results.hand_landmarks:
            return data

        # Extract landmarks using HandTracker method
        landmarks = self.hand_tracker.extract_landmarks(results, frame_shape)

        if len(landmarks) == 0:
            return data

        # Convert landmarks to JSON format (normalized coordinates)
        data["landmarks"] = [{"id": lm.id, "x": lm.x, "y": lm.y} for lm in landmarks]

        # Check palm open
        is_palm_open = self.hand_tracker.is_palm_open(landmarks)
        data["is_palm_open"] = is_palm_open

        # Detect gesture
        gesture = self.hand_tracker.detect_gesture(
            landmarks, self.mouse_controller.is_dragging
        )

        # Handle gesture actions and update gesture string
        gesture = self._handle_gesture(gesture, landmarks, current_time)
        data["gesture"] = gesture

        # Get mouse position
        mouse_x, mouse_y = self.mouse_controller.get_current_position()
        data["mouse_position"] = {"x": round(mouse_x, 1), "y": round(mouse_y, 1)}

        return data

    def _handle_gesture(
        self, gesture: str, landmarks: List[HandLandmark], current_time: float
    ) -> str:
        """
        Handle gesture actions (mouse control) and return final gesture string.
        """
        if gesture == "palm_open":
            # In swipe mode - release drag if active
            self.mouse_controller.mouse_up()
            self.mouse_controller.reset_zoom()
            return "palm_open"

        if gesture == "swipe_right":
            if current_time - self.last_swipe_time > SWIPE_COOLDOWN:
                self.mouse_controller.press_key("right")
                self.last_swipe_time = current_time
                print("Swipe Right -> Next Slide")
            return "swipe_right"

        if gesture == "swipe_left":
            if current_time - self.last_swipe_time > SWIPE_COOLDOWN:
                self.mouse_controller.press_key("left")
                self.last_swipe_time = current_time
                print("Swipe Left -> Prev Slide")
            return "swipe_left"

        if gesture == "zoom":
            # Handle zoom with thumb-middle gesture
            middle = landmarks[12]
            self.mouse_controller.mouse_up()
            self.mouse_controller.handle_zoom(middle.pixel_y)
            return "zoom"

        # Reset zoom when not zooming
        self.mouse_controller.reset_zoom()

        if gesture == "click" or gesture == "drag":
            # Move mouse to index finger position
            index_x, index_y = self.hand_tracker.get_index_finger_position(landmarks)
            self.mouse_controller.move_to(index_x, index_y)

            # Start/continue drag
            self.mouse_controller.mouse_down()
            return "drag"

        if gesture == "none":
            # Normal mouse movement mode - move to index finger
            index_x, index_y = self.hand_tracker.get_index_finger_position(landmarks)
            self.mouse_controller.move_to(index_x, index_y)

            # Release drag if was dragging
            self.mouse_controller.mouse_up()
            return "none"

        return gesture

    def get_latest_data(self) -> Optional[Dict[str, Any]]:
        """Get latest tracking data (thread-safe)."""
        with self.data_lock:
            return self.latest_data.copy() if self.latest_data else None


# Global server instance
server = AirMouseServer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan handler for startup/shutdown."""
    # Startup
    if not server.start():
        print("Warning: Camera failed to start. WebSocket will send empty data.")

    yield

    # Shutdown
    server.stop()


# FastAPI app
app = FastAPI(
    title="Air Mouse Backend",
    description="WebSocket server for hand tracking and mouse control",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/status")
async def status():
    """Get server status with camera and tracking info."""
    return {
        "status": "ok",
        "camera_running": server.running,
        "fps": server.current_fps,
        "has_data": server.latest_data is not None,
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time hand tracking data.

    Sends HandTrackingMessage at ~30fps while connected.
    """
    await websocket.accept()
    print("WebSocket client connected")

    try:
        while True:
            # Get latest tracking data
            data = server.get_latest_data()

            if data:
                await websocket.send_json(data)
            else:
                # Send empty data if camera not ready
                await websocket.send_json(
                    {
                        "type": "hand_data",
                        "landmarks": [],
                        "gesture": "none",
                        "mouse_position": {"x": 0, "y": 0},
                        "is_palm_open": False,
                        "fps": 0,
                        "timestamp": int(time.time() * 1000),
                    }
                )

            # Target 30fps
            await asyncio.sleep(1 / TARGET_FPS)

    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Cleanup: release mouse buttons on disconnect
        if server.mouse_controller:
            server.mouse_controller.release_all()
            print("Mouse released on disconnect")


if __name__ == "__main__":
    print("Starting Air Mouse Backend...")
    print("Press Ctrl+C to stop")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
