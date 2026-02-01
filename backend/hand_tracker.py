"""
Hand Tracker Module for Air Mouse
Provides camera access and hand gesture recognition logic using MediaPipe results.
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional, Any


@dataclass
class HandLandmark:
    """Single hand landmark point."""

    id: int
    x: float  # Normalized 0-1
    y: float  # Normalized 0-1
    pixel_x: int  # Pixel coordinate
    pixel_y: int  # Pixel coordinate


class HandTracker:
    """
    Handles camera capture and interprets MediaPipe hand tracking results.
    Does NOT manage the MediaPipe model instance itself (handled by ModelManager).
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

        # Camera
        self.cap: Optional[cv2.VideoCapture] = None

        # Swipe tracking state
        self.swipe_start_x: int = 0
        self.is_swipe_mode: bool = False

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

    def extract_landmarks(
        self, results: Any, img_shape: Tuple[int, int, int]
    ) -> List[HandLandmark]:
        """
        Extract landmark list from MediaPipe Hands results.

        Args:
            results: MediaPipe Hands results object
            img_shape: (height, width, channels) of image

        Returns:
            List of HandLandmark objects
        """
        h, w, c = img_shape
        landmarks = []

        if not results.multi_hand_landmarks:
            return landmarks

        # Get first hand's landmarks
        hand_landmarks = results.multi_hand_landmarks[0]

        for id, lm in enumerate(hand_landmarks.landmark):
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
        """
        if len(landmarks) == 0:
            self.is_swipe_mode = False
            return "none"

        # Check palm open first (highest priority for swipe mode)
        if self.is_palm_open(landmarks):
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
        wrist = landmarks[0]
        thumb = landmarks[4]
        index = landmarks[8]
        middle_mcp = landmarks[9]  # Middle finger MCP (palm center reference)
        middle = landmarks[12]
        pinky = landmarks[20]

        # Calculate palm size (Wrist to Middle MCP) for dynamic threshold
        palm_size = np.hypot(
            wrist.pixel_x - middle_mcp.pixel_x, wrist.pixel_y - middle_mcp.pixel_y
        )

        # Dynamic thresholds based on hand size
        # Adjust these multipliers to tune sensitivity
        click_threshold = palm_size * 0.35  # ~35% of palm size
        zoom_threshold = palm_size * 0.45  # ~45% of palm size
        double_click_threshold = palm_size * 0.3

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
        if dist_thumb_middle < zoom_threshold:
            return "zoom"

        # Double click check (thumb + pinky)
        if dist_thumb_pinky < double_click_threshold:
            return "double_click"

        # Click/drag gesture (thumb + index close)
        if dist_thumb_index < click_threshold:
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
        """Release camera resources."""
        self.stop_camera()
