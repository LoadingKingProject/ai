"""
Unit tests for extract_landmarks() function.

Tests landmark extraction from MediaPipe hand detection results,
including coordinate conversion from normalized (0-1) to pixel coordinates.
"""

import pytest
from unittest.mock import Mock
import sys
import os

# Add parent directory to path for importing main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import extract_landmarks


class MockLandmark:
    """Mock MediaPipe Landmark object with x, y, z coordinates."""

    def __init__(self, x, y, z=0.0):
        self.x = x
        self.y = y
        self.z = z


class MockHandLandmarks:
    """Mock MediaPipe HandLandmarks object containing 21 landmarks."""

    def __init__(self, landmarks=None):
        """Initialize with 21 landmarks (default: evenly distributed)."""
        if landmarks is None:
            # Default: 21 landmarks with normalized coordinates
            self.landmark = [MockLandmark(i / 20, i / 20) for i in range(21)]
        else:
            self.landmark = landmarks


@pytest.fixture
def mock_hand_landmarks():
    """Fixture providing a mock hand landmarks object with 21 landmarks."""
    return MockHandLandmarks()


@pytest.fixture
def mock_hand_landmarks_custom():
    """Fixture providing custom landmark positions for pixel conversion testing."""
    landmarks = [
        MockLandmark(0.5, 0.5),  # Center of image
        MockLandmark(0.0, 0.0),  # Top-left
        MockLandmark(1.0, 1.0),  # Bottom-right
        MockLandmark(0.25, 0.75),  # Custom position
    ]
    # Pad to 21 landmarks
    while len(landmarks) < 21:
        landmarks.append(MockLandmark(0.0, 0.0))
    return MockHandLandmarks(landmarks)


@pytest.mark.unit
def test_extract_21_landmarks(mock_hand_landmarks):
    """Test that extract_landmarks returns exactly 21 landmarks.

    Verifies that the function correctly extracts all 21 hand landmarks
    from MediaPipe hand detection results.
    """
    img_shape = (480, 640, 3)  # height, width, channels

    result = extract_landmarks(mock_hand_landmarks, img_shape)

    # Should return list of 21 landmarks
    assert isinstance(result, list), "Result should be a list"
    assert len(result) == 21, f"Expected 21 landmarks, got {len(result)}"

    # Each landmark should be [id, cx, cy]
    for i, landmark in enumerate(result):
        assert isinstance(landmark, list), f"Landmark {i} should be a list"
        assert len(landmark) == 3, f"Landmark {i} should have 3 elements [id, cx, cy]"
        assert landmark[0] == i, f"Landmark ID should be {i}, got {landmark[0]}"


@pytest.mark.unit
def test_landmark_pixel_conversion(mock_hand_landmarks_custom):
    """Test conversion from normalized (0-1) to pixel coordinates.

    Verifies that normalized coordinates are correctly converted to pixel
    coordinates based on image dimensions.

    Test cases:
    - (0.5, 0.5) in 640x480 image → (320, 240)
    - (0.0, 0.0) in 640x480 image → (0, 0)
    - (1.0, 1.0) in 640x480 image → (640, 480)
    """
    img_shape = (480, 640, 3)  # height=480, width=640
    h, w, c = img_shape

    result = extract_landmarks(mock_hand_landmarks_custom, img_shape)

    # Test case 1: Center (0.5, 0.5) → (320, 240)
    assert result[0][1] == 320, f"Expected x=320, got {result[0][1]}"
    assert result[0][2] == 240, f"Expected y=240, got {result[0][2]}"

    # Test case 2: Top-left (0.0, 0.0) → (0, 0)
    assert result[1][1] == 0, f"Expected x=0, got {result[1][1]}"
    assert result[1][2] == 0, f"Expected y=0, got {result[1][2]}"

    # Test case 3: Bottom-right (1.0, 1.0) → (640, 480)
    assert result[2][1] == 640, f"Expected x=640, got {result[2][1]}"
    assert result[2][2] == 480, f"Expected y=480, got {result[2][2]}"


@pytest.mark.unit
def test_extract_specific_indices(mock_hand_landmarks_custom):
    """Test extraction of specific landmark indices.

    Verifies that specific landmarks (thumb tip at index 4, index finger tip
    at index 8) are correctly extracted with proper coordinate conversion.

    MediaPipe hand landmarks:
    - Index 4: Thumb tip
    - Index 8: Index finger tip
    """
    img_shape = (480, 640, 3)

    result = extract_landmarks(mock_hand_landmarks_custom, img_shape)

    # Verify landmark at index 4 (thumb tip)
    assert result[4][0] == 4, "Landmark ID should be 4"
    assert isinstance(result[4][1], int), "X coordinate should be int"
    assert isinstance(result[4][2], int), "Y coordinate should be int"

    # Verify landmark at index 8 (index finger tip)
    assert result[8][0] == 8, "Landmark ID should be 8"
    assert isinstance(result[8][1], int), "X coordinate should be int"
    assert isinstance(result[8][2], int), "Y coordinate should be int"

    # Both should have valid pixel coordinates (0 <= coord <= dimension)
    assert 0 <= result[4][1] <= 640, f"X coordinate out of bounds: {result[4][1]}"
    assert 0 <= result[4][2] <= 480, f"Y coordinate out of bounds: {result[4][2]}"
    assert 0 <= result[8][1] <= 640, f"X coordinate out of bounds: {result[8][1]}"
    assert 0 <= result[8][2] <= 480, f"Y coordinate out of bounds: {result[8][2]}"
