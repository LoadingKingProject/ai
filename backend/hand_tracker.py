"""
Hand Tracker Module for Air Mouse
Provides MediaPipe Tasks-based hand tracking and gesture recognition.
"""

import cv2
import numpy as np
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional

import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    HandLandmarkerResult,
    RunningMode,
)


# Model URL and path
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
MODEL_DIR = Path(__file__).parent / "models"
MODEL_PATH = MODEL_DIR / "hand_landmarker.task"


@dataclass
class HandLandmark:
    """Single hand landmark point."""

    id: int
    x: float  # Normalized 0-1
    y: float  # Normalized 0-1
    pixel_x: int  # Pixel coordinate
    pixel_y: int  # Pixel coordinate


def download_model() -> Path:
    """Download the hand landmarker model if not present."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    if not MODEL_PATH.exists():
        print(f"Downloading hand landmarker model to {MODEL_PATH}...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded successfully.")

    return MODEL_PATH


class HandTracker:
    """
    MediaPipe Tasks-based hand tracking with gesture recognition.

    Provides methods to:
    - Process camera frames for hand detection
    - Extract hand landmarks
    - Detect gestures (palm open, click, drag, zoom, swipe)
    """

    # Default configuration
    DEFAULT_CAM_WIDTH = 640
    DEFAULT_CAM_HEIGHT = 480
    DEFAULT_CLICK_DIST = 30
    DEFAULT_ZOOM_DIST = 40
    DEFAULT_DOUBLE_CLICK_DIST = 30
    DEFAULT_SWIPE_THRESHOLD = 50

    def __init__(
        self,
        cam_id: int = 0,
        cam_width: int = DEFAULT_CAM_WIDTH,
        cam_height: int = DEFAULT_CAM_HEIGHT,
        click_dist: int = DEFAULT_CLICK_DIST,
        zoom_dist: int = DEFAULT_ZOOM_DIST,
        double_click_dist: int = DEFAULT_DOUBLE_CLICK_DIST,
        swipe_threshold: int = DEFAULT_SWIPE_THRESHOLD,
    ):
        self.cam_id = cam_id
        self.cam_width = cam_width
        self.cam_height = cam_height
        self.click_dist = click_dist
        self.zoom_dist = zoom_dist
        self.double_click_dist = double_click_dist
        self.swipe_threshold = swipe_threshold

        # Download model if needed
        model_path = download_model()

        # MediaPipe Tasks initialization
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.7,
            min_tracking_confidence=0.7,
            running_mode=RunningMode.IMAGE,
        )
        self.hand_landmarker = HandLandmarker.create_from_options(options)

        # Camera
        self.cap: Optional[cv2.VideoCapture] = None

        # Swipe tracking state
        self.swipe_start_x: int = 0
        self.is_swipe_mode: bool = False

        # Latest result
        self.latest_result: Optional[HandLandmarkerResult] = None

    def start_camera(self) -> bool:
        """Initialize and start camera capture."""
        self.cap = cv2.VideoCapture(self.cam_id)
        if not self.cap.isOpened():
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)
        return True

    def stop_camera(self) -> None:
        """Release camera resources."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a frame from camera, flip horizontally."""
        if self.cap is None:
            return False, None

        success, frame = self.cap.read()
        if not success:
            return False, None

        # Flip horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        return True, frame

    def process_frame(self, frame: np.ndarray) -> Optional[HandLandmarkerResult]:
        """
        Process a frame with MediaPipe Tasks HandLandmarker.

        Returns HandLandmarkerResult or None if no hand detected.
        """
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        # Detect hand landmarks
        result = self.hand_landmarker.detect(mp_image)
        self.latest_result = result

        return result

    def extract_landmarks(
        self, result: HandLandmarkerResult, img_shape: Tuple[int, int, int]
    ) -> List[HandLandmark]:
        """
        Extract landmark list from HandLandmarkerResult.

        Args:
            result: HandLandmarkerResult from process_frame
            img_shape: (height, width, channels) of image

        Returns:
            List of HandLandmark objects with both normalized and pixel coords
        """
        h, w, c = img_shape
        landmarks = []

        if not result.hand_landmarks:
            return landmarks

        # Get first hand's landmarks
        hand_landmarks = result.hand_landmarks[0]

        for id, lm in enumerate(hand_landmarks):
            cx, cy = int(lm.x * w), int(lm.y * h)
            landmarks.append(
                HandLandmark(
                    id=id,
                    x=lm.x,  # Normalized 0-1
                    y=lm.y,  # Normalized 0-1
                    pixel_x=cx,
                    pixel_y=cy,
                )
            )

        return landmarks

    def is_palm_open(self, landmarks: List[HandLandmark]) -> bool:
        """
        Check if palm is open (all 4 fingers extended).

        Checks if fingertips (8, 12, 16, 20) are above their PIP joints
        (6, 10, 14, 18) in screen coordinates.
        """
        if len(landmarks) == 0:
            return False

        fingers_extended = []
        # Check index, middle, ring, pinky fingers
        for tip_id in [8, 12, 16, 20]:
            pip_id = tip_id - 2
            # Tip is above PIP when y coordinate is smaller (screen coords)
            if landmarks[tip_id].pixel_y < landmarks[pip_id].pixel_y:
                fingers_extended.append(1)
            else:
                fingers_extended.append(0)

        # All 4 fingers must be extended
        return sum(fingers_extended) == 4

    def detect_gesture(
        self,
        landmarks: List[HandLandmark],
        is_dragging: bool = False,
    ) -> str:
        """
        Detect gesture from landmarks.

        Returns one of: 'none', 'click', 'drag', 'zoom', 'swipe_left',
                        'swipe_right', 'palm_open'
        """
        if len(landmarks) == 0:
            self.is_swipe_mode = False
            return "none"

        # Check palm open first (highest priority for swipe mode)
        if self.is_palm_open(landmarks):
            # Track swipe gesture
            x_center = landmarks[9].pixel_x  # Palm center

            if not self.is_swipe_mode:
                self.swipe_start_x = x_center
                self.is_swipe_mode = True
                return "palm_open"
            else:
                diff = x_center - self.swipe_start_x

                if diff > self.swipe_threshold:
                    self.is_swipe_mode = False
                    return "swipe_right"
                elif diff < -self.swipe_threshold:
                    self.is_swipe_mode = False
                    return "swipe_left"

                return "palm_open"

        # Not palm open - reset swipe mode
        self.is_swipe_mode = False

        # Get key landmark positions
        thumb = landmarks[4]
        index = landmarks[8]
        middle = landmarks[12]
        pinky = landmarks[20]

        # Calculate distances
        dist_thumb_middle = np.hypot(
            thumb.pixel_x - middle.pixel_x, thumb.pixel_y - middle.pixel_y
        )
        dist_thumb_pinky = np.hypot(
            thumb.pixel_x - pinky.pixel_x, thumb.pixel_y - pinky.pixel_y
        )
        dist_thumb_index = np.hypot(
            thumb.pixel_x - index.pixel_x, thumb.pixel_y - index.pixel_y
        )

        # Zoom gesture (thumb + middle close)
        if dist_thumb_middle < self.zoom_dist:
            return "zoom"

        # Double click gesture would be detected by caller based on timing
        # Here we just detect thumb-pinky proximity (but return 'click' since
        # double-click is timing-based)
        if dist_thumb_pinky < self.double_click_dist:
            return "click"

        # Click/drag gesture (thumb + index close)
        if dist_thumb_index < self.click_dist:
            if is_dragging:
                return "drag"
            return "click"

        return "none"

    def get_index_finger_position(
        self, landmarks: List[HandLandmark]
    ) -> Tuple[int, int]:
        """Get index finger tip position in pixels."""
        if len(landmarks) == 0:
            return 0, 0
        return landmarks[8].pixel_x, landmarks[8].pixel_y

    def close(self) -> None:
        """Release all resources."""
        self.stop_camera()
        if self.hand_landmarker:
            self.hand_landmarker.close()
