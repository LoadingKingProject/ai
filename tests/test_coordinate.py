import pytest
import sys
from unittest.mock import MagicMock

# Mock external dependencies before importing main
sys.modules["cv2"] = MagicMock()
sys.modules["mediapipe"] = MagicMock()
sys.modules["pyautogui"] = MagicMock()

import numpy as np
from main import calculate_screen_position


@pytest.mark.unit
class TestCalculateScreenPosition:
    """Unit tests for calculate_screen_position coordinate transformation function."""

    # Test constants matching main.py
    CAM_WIDTH = 640
    CAM_HEIGHT = 480
    FRAME_R = 100
    SCREEN_W = 1920
    SCREEN_H = 1080

    @pytest.mark.unit
    def test_center_mapping(self):
        """Test that webcam center maps to screen center."""
        # Webcam center
        cam_center_x = self.CAM_WIDTH / 2
        cam_center_y = self.CAM_HEIGHT / 2

        screen_x, screen_y = calculate_screen_position(
            cam_center_x,
            cam_center_y,
            self.FRAME_R,
            self.CAM_WIDTH,
            self.CAM_HEIGHT,
            self.SCREEN_W,
            self.SCREEN_H,
        )

        # Screen center
        expected_x = self.SCREEN_W / 2
        expected_y = self.SCREEN_H / 2

        assert abs(screen_x - expected_x) < 1.0, (
            f"Expected x≈{expected_x}, got {screen_x}"
        )
        assert abs(screen_y - expected_y) < 1.0, (
            f"Expected y≈{expected_y}, got {screen_y}"
        )

    @pytest.mark.unit
    def test_edge_mapping_top_left(self):
        """Test that top-left boundary (frame_r, frame_r) maps to (0, 0)."""
        screen_x, screen_y = calculate_screen_position(
            self.FRAME_R,
            self.FRAME_R,
            self.FRAME_R,
            self.CAM_WIDTH,
            self.CAM_HEIGHT,
            self.SCREEN_W,
            self.SCREEN_H,
        )

        assert screen_x == 0, f"Expected x=0, got {screen_x}"
        assert screen_y == 0, f"Expected y=0, got {screen_y}"

    @pytest.mark.unit
    def test_edge_mapping_bottom_right(self):
        """Test that bottom-right boundary maps to (screen_w, screen_h)."""
        screen_x, screen_y = calculate_screen_position(
            self.CAM_WIDTH - self.FRAME_R,
            self.CAM_HEIGHT - self.FRAME_R,
            self.FRAME_R,
            self.CAM_WIDTH,
            self.CAM_HEIGHT,
            self.SCREEN_W,
            self.SCREEN_H,
        )

        assert screen_x == self.SCREEN_W, f"Expected x={self.SCREEN_W}, got {screen_x}"
        assert screen_y == self.SCREEN_H, f"Expected y={self.SCREEN_H}, got {screen_y}"

    @pytest.mark.unit
    def test_frame_restriction(self):
        """Test that FRAME_R margin is applied correctly (linear interpolation bounds)."""
        # Test point at 1/4 of the valid range (between frame_r and cam_w - frame_r)
        # Valid range: frame_r=100 to cam_w-frame_r=540 (width 440)
        # 1/4 point: 100 + 440/4 = 210
        test_x = self.FRAME_R + (self.CAM_WIDTH - 2 * self.FRAME_R) / 4
        test_y = self.FRAME_R + (self.CAM_HEIGHT - 2 * self.FRAME_R) / 4

        screen_x, screen_y = calculate_screen_position(
            test_x,
            test_y,
            self.FRAME_R,
            self.CAM_WIDTH,
            self.CAM_HEIGHT,
            self.SCREEN_W,
            self.SCREEN_H,
        )

        # Expected: 1/4 of screen dimensions
        expected_x = self.SCREEN_W / 4
        expected_y = self.SCREEN_H / 4

        assert abs(screen_x - expected_x) < 1.0, (
            f"Expected x≈{expected_x}, got {screen_x}"
        )
        assert abs(screen_y - expected_y) < 1.0, (
            f"Expected y≈{expected_y}, got {screen_y}"
        )
