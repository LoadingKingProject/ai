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
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum
from contextlib import asynccontextmanager

# Ensure backend directory is in path for imports
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import cv2

from model_manager import ModelManager
from hand_tracker import HandLandmark
from mouse_controller import MouseController
from face_analyzer import FaceAnalyzer


# Configuration
CAM_ID = 0
CAM_WIDTH = 640
CAM_HEIGHT = 480
SMOOTHING = 10
FRAME_REDUCTION = 100
CLICK_COOLDOWN = 0.5
SWIPE_COOLDOWN = 1.0
TARGET_FPS = 30


class GlobalState(Enum):
    WAITING_FACE = "WAITING_FACE"  # Face detection & distance check
    ANALYZING = "ANALYZING"  # Countdown & ratio analysis
    REPORT = "REPORT"  # Show result & wait for approval
    ACTIVE = "ACTIVE"  # Hand tracking & mouse control


class AirMouseServer:
    """
    Air Mouse server managing camera capture and WebSocket connections.

    Runs camera processing in a background thread and broadcasts
    hand tracking data to connected WebSocket clients.
    """

    def __init__(self):
        self.model_manager = ModelManager()
        self.mouse_controller: Optional[MouseController] = None
        self.face_analyzer = FaceAnalyzer()

        self.running = False
        self.capture_thread: Optional[threading.Thread] = None

        # State management
        self.state = GlobalState.WAITING_FACE
        self.state_lock = threading.Lock()

        # Latest tracking data (thread-safe via GIL for simple reads)
        self.latest_data: Optional[Dict[str, Any]] = None
        self.data_lock = threading.Lock()

        # FPS calculation
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0.0

        # Timing variables
        self.last_click_time = 0.0
        self.last_swipe_time = 0.0
        self.analysis_start_time = 0.0

        # Face analysis results
        self.face_results = None
        self.face_status = "WAIT"
        self.distance_ratio = 0.0

        # Camera source wrapper
        self.camera_source = None

    def start(self) -> bool:
        """Initialize and start camera capture thread."""
        # Initialize MouseController
        self.mouse_controller = MouseController(
            cam_width=CAM_WIDTH,
            cam_height=CAM_HEIGHT,
            frame_reduction=FRAME_REDUCTION,
            smoothing=SMOOTHING,
        )

        # Start with Face Mesh model
        if not self.model_manager.load_face_mesh():
            print("Failed to load Face Mesh model")
            return False

        from hand_tracker import HandTracker

        self.camera_source = HandTracker(CAM_ID, CAM_WIDTH, CAM_HEIGHT)

        if not self.camera_source.start_camera():
            print("Failed to open camera")
            return False

        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()

        print(f"Server started: {CAM_WIDTH}x{CAM_HEIGHT}")
        return True

    def stop(self) -> None:
        """Stop camera capture and cleanup."""
        self.running = False

        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)

        if self.camera_source:
            self.camera_source.close()

        # Unload all models
        self.model_manager.unload_face_mesh()
        self.model_manager.unload_hands()

        if self.mouse_controller:
            self.mouse_controller.release_all()
            self.mouse_controller = None

        print("Server stopped")

    def set_state(self, new_state: GlobalState):
        """Thread-safe state transition."""
        with self.state_lock:
            print(f"State transition: {self.state.value} -> {new_state.value}")

            # Handle model switching based on state
            if new_state == GlobalState.ACTIVE:
                # Transition to Hand Tracking
                self.model_manager.load_hands()
            elif new_state in [GlobalState.WAITING_FACE, GlobalState.ANALYZING]:
                # Transition to Face Mesh (if not already)
                self.model_manager.load_face_mesh()

            self.state = new_state

    def _encode_frame(self, frame):
        """Encode frame to base64 string for streaming."""
        try:
            # Compress frame to reduce bandwidth (quality 70)
            _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            return base64.b64encode(buffer).decode("utf-8")
        except Exception as e:
            print(f"Frame encoding error: {e}")
            return None

    def _capture_loop(self) -> None:
        """Main capture loop running in background thread."""
        frame_interval = 1.0 / TARGET_FPS

        while self.running:
            loop_start = time.time()

            # Read frame
            success, frame = self.camera_source.read_frame()
            if not success or frame is None:
                continue

            # Process based on current state
            with self.state_lock:
                current_state = self.state

            if current_state == GlobalState.ACTIVE:
                self._process_hand_tracking(frame)
            else:
                self._process_face_analysis(frame, current_state)

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

    def _process_face_analysis(self, frame, state):
        """Process frame using Face Mesh."""
        face_mesh = self.model_manager.get_face_mesh()
        if not face_mesh:
            return

        # Encode frame for streaming
        image_base64 = self._encode_frame(frame)

        # MediaPipe requires RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        try:
            results = face_mesh.process(rgb_frame)
        except Exception as e:
            print(f"Face Mesh process error: {e}")
            return

        h, w, _ = frame.shape
        data = {
            "type": "face_data",
            "image": image_base64,
            "state": state.value,
            "status": "WAIT",
            "distance_ratio": 0.0,
            "target_ratio": self.face_analyzer.TARGET_RATIO,
            "face_results": self.face_results,
            "fps": round(self.current_fps, 1),
        }

        if results and results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            # Check distance and pose
            status, ratio, _ = self.face_analyzer.check_precision_distance(
                landmarks, w, h
            )
            self.face_status = status
            self.distance_ratio = ratio

            data["status"] = status
            data["distance_ratio"] = ratio

            # Logic for state transitions
            if state == GlobalState.WAITING_FACE:
                if status == "PERFECT":
                    if self.analysis_start_time == 0:
                        self.analysis_start_time = time.time()

                    # If perfect for 3 seconds -> ANALYZING -> REPORT
                    if time.time() - self.analysis_start_time > 3.0:
                        self.set_state(GlobalState.ANALYZING)
                        # Perform analysis once
                        self.face_results = self.face_analyzer.analyze_ratio(
                            landmarks, w, h
                        )
                        data["face_results"] = self.face_results
                        self.set_state(GlobalState.REPORT)
                else:
                    self.analysis_start_time = 0

        # Update latest data
        with self.data_lock:
            self.latest_data = data

    def _process_hand_tracking(self, frame):
        """Process frame using Hand Tracking."""
        hands = self.model_manager.get_hands()
        if not hands:
            return

        # Encode frame for streaming
        image_base64 = self._encode_frame(frame)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        try:
            results = hands.process(rgb_frame)
        except Exception as e:
            print(f"Hand tracking error: {e}")
            return

        # Build tracking data
        current_time = time.time()

        data = {
            "type": "hand_data",
            "image": image_base64,
            "state": GlobalState.ACTIVE.value,
            "landmarks": [],
            "gesture": "none",
            "mouse_position": {"x": 0, "y": 0},
            "is_palm_open": False,
            "fps": round(self.current_fps, 1),
            "timestamp": int(current_time * 1000),
        }

        if results.multi_hand_landmarks:
            # We can re-use camera_source.extract_landmarks
            landmarks = self.camera_source.extract_landmarks(results, frame.shape)

            if landmarks:
                data["landmarks"] = [
                    {"id": lm.id, "x": lm.x, "y": lm.y} for lm in landmarks
                ]
                data["is_palm_open"] = self.camera_source.is_palm_open(landmarks)

                gesture = self.camera_source.detect_gesture(
                    landmarks, self.mouse_controller.is_dragging
                )

                gesture = self._handle_gesture(gesture, landmarks, current_time)
                data["gesture"] = gesture

                mx, my = self.mouse_controller.get_current_position()
                data["mouse_position"] = {"x": round(mx, 1), "y": round(my, 1)}

        with self.data_lock:
            self.latest_data = data

    def _handle_gesture(
        self, gesture: str, landmarks: List[HandLandmark], current_time: float
    ) -> str:
        """Handle gesture actions (mouse control)."""
        if gesture == "palm_open":
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
            middle = landmarks[12]
            self.mouse_controller.mouse_up()
            self.mouse_controller.handle_zoom(middle.pixel_y)
            return "zoom"

        self.mouse_controller.reset_zoom()

        if gesture == "click" or gesture == "drag":
            index_x, index_y = self.camera_source.get_index_finger_position(landmarks)
            self.mouse_controller.move_to(index_x, index_y)
            self.mouse_controller.mouse_down()
            return "drag"

        if gesture == "double_click":
            index_x, index_y = self.camera_source.get_index_finger_position(landmarks)
            self.mouse_controller.move_to(index_x, index_y)
            self.mouse_controller.double_click()
            return "double_click"

        if gesture == "none":
            index_x, index_y = self.camera_source.get_index_finger_position(landmarks)
            self.mouse_controller.move_to(index_x, index_y)
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
    if not server.start():
        print("Warning: Camera failed to start.")
    yield
    server.stop()


# FastAPI app
app = FastAPI(
    title="Air Mouse Backend",
    description="WebSocket server for face analysis and hand tracking",
    version="1.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ApprovalRequest(BaseModel):
    approved: bool


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/approve")
async def approve_face_analysis(request: ApprovalRequest):
    """Endpoint to handle approval or retry."""
    if request.approved:
        server.set_state(GlobalState.ACTIVE)
        return {"status": "success", "message": "Switched to Active Mode"}
    else:
        # Retry logic: Reset to WAITING_FACE
        server.face_results = None
        server.analysis_start_time = 0
        server.set_state(GlobalState.WAITING_FACE)
        return {"status": "success", "message": "Retrying Face Analysis"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket client connected")

    try:
        while True:
            data = server.get_latest_data()
            if data:
                await websocket.send_json(data)
            else:
                # Keep alive packet
                await websocket.send_json(
                    {"type": "ping", "timestamp": int(time.time() * 1000)}
                )

            await asyncio.sleep(1 / TARGET_FPS)

    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if server.mouse_controller:
            server.mouse_controller.release_all()


if __name__ == "__main__":
    print("Starting Air Mouse Backend...")
    print("Press Ctrl+C to stop")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
