"""
Mouse Controller Module for Air Mouse
Provides screen coordinate mapping and PyAutoGUI-based mouse control.
"""

import pyautogui
import numpy as np
from typing import Tuple


class MouseController:
    """
    Mouse controller using PyAutoGUI with smoothing.

    Handles:
    - Screen position calculation from camera coordinates
    - Position smoothing for stable cursor movement
    - Mouse actions (move, click, drag, scroll)
    """

    DEFAULT_FRAME_REDUCTION = 100
    DEFAULT_SMOOTHING = 10

    def __init__(
        self,
        cam_width: int = 640,
        cam_height: int = 480,
        frame_reduction: int = DEFAULT_FRAME_REDUCTION,
        smoothing: int = DEFAULT_SMOOTHING,
    ):
        self.cam_width = cam_width
        self.cam_height = cam_height
        self.frame_reduction = frame_reduction
        self.smoothing = smoothing

        # Get screen dimensions
        try:
            self.screen_width, self.screen_height = pyautogui.size()
        except Exception:
            self.screen_width, self.screen_height = 1920, 1080

        # Smoothing state
        self.prev_x: float = 0.0
        self.prev_y: float = 0.0

        # Drag state
        self.is_dragging: bool = False

        # Zoom state
        self.prev_zoom_y: int = 0

        # Disable PyAutoGUI failsafe (edge-of-screen escape)
        pyautogui.FAILSAFE = False

    def calculate_screen_position(
        self,
        x: int,
        y: int,
    ) -> Tuple[float, float]:
        """
        Map camera coordinates to screen coordinates.

        Uses frame_reduction to create a boundary margin and interpolates
        camera position to full screen coordinates.

        Args:
            x: Camera x coordinate (pixels)
            y: Camera y coordinate (pixels)

        Returns:
            (screen_x, screen_y) as floats
        """
        screen_x = np.interp(
            x,
            (self.frame_reduction, self.cam_width - self.frame_reduction),
            (0, self.screen_width),
        )
        screen_y = np.interp(
            y,
            (self.frame_reduction, self.cam_height - self.frame_reduction),
            (0, self.screen_height),
        )
        return float(screen_x), float(screen_y)

    def apply_smoothing(
        self,
        current_x: float,
        current_y: float,
    ) -> Tuple[float, float]:
        """
        Apply smoothing to cursor position for stable movement.

        Uses exponential smoothing: new = prev + (current - prev) / factor

        Args:
            current_x: Target x position
            current_y: Target y position

        Returns:
            (smoothed_x, smoothed_y)
        """
        new_x = self.prev_x + (current_x - self.prev_x) / self.smoothing
        new_y = self.prev_y + (current_y - self.prev_y) / self.smoothing

        self.prev_x = new_x
        self.prev_y = new_y

        return new_x, new_y

    def move_to(self, x: float, y: float) -> Tuple[float, float]:
        """
        Move mouse to position with smoothing.

        Args:
            x: Camera x coordinate
            y: Camera y coordinate

        Returns:
            (actual_x, actual_y) screen position after smoothing
        """
        screen_x, screen_y = self.calculate_screen_position(int(x), int(y))
        smooth_x, smooth_y = self.apply_smoothing(screen_x, screen_y)

        try:
            pyautogui.moveTo(smooth_x, smooth_y)
        except Exception:
            pass

        return smooth_x, smooth_y

    def mouse_down(self) -> None:
        """Press mouse button down (start drag)."""
        if not self.is_dragging:
            pyautogui.mouseDown()
            self.is_dragging = True

    def mouse_up(self) -> None:
        """Release mouse button (end drag)."""
        if self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False

    def click(self) -> None:
        """Perform single click."""
        self.mouse_up()  # Ensure not dragging
        pyautogui.click()

    def double_click(self) -> None:
        """Perform double click."""
        self.mouse_up()  # Ensure not dragging
        pyautogui.doubleClick()

    def scroll(self, amount: int) -> None:
        """
        Scroll with ctrl held (zoom behavior).

        Args:
            amount: Positive for zoom in, negative for zoom out
        """
        self.mouse_up()  # Ensure not dragging
        pyautogui.keyDown("ctrl")
        pyautogui.scroll(amount)
        pyautogui.keyUp("ctrl")

    def handle_zoom(self, current_y: int) -> bool:
        """
        Handle zoom gesture based on vertical movement.

        Args:
            current_y: Current y position of zoom gesture

        Returns:
            True if zoom action was performed
        """
        if self.prev_zoom_y == 0:
            self.prev_zoom_y = current_y
            return False

        diff_y = self.prev_zoom_y - current_y

        if abs(diff_y) > 20:
            if diff_y > 0:
                self.scroll(100)  # Zoom in
            else:
                self.scroll(-100)  # Zoom out
            self.prev_zoom_y = current_y
            return True

        return False

    def reset_zoom(self) -> None:
        """Reset zoom tracking state."""
        self.prev_zoom_y = 0

    def press_key(self, key: str) -> None:
        """Press a keyboard key (for swipe gestures)."""
        self.mouse_up()  # Ensure not dragging
        pyautogui.press(key)

    def get_current_position(self) -> Tuple[float, float]:
        """Get current smoothed mouse position."""
        return self.prev_x, self.prev_y

    def release_all(self) -> None:
        """Release all held inputs (cleanup on disconnect)."""
        self.mouse_up()
        self.reset_zoom()
