import pytest
import numpy as np
from main import detect_click


@pytest.mark.unit
class TestDetectClick:
    """Unit tests for detect_click() function."""

    def test_click_detected_close_fingers(self):
        """Test click detection when fingers are close (distance < threshold)."""
        # Arrange
        x1, y1 = 100, 100  # Index finger
        x2, y2 = 110, 105  # Thumb (close to index)
        threshold = 30

        # Act
        result = detect_click(x1, y1, x2, y2, threshold)

        # Assert
        assert result is True, "Should detect click when distance < threshold"

    def test_click_not_detected_far_fingers(self):
        """Test click not detected when fingers are far (distance > threshold)."""
        # Arrange
        x1, y1 = 100, 100  # Index finger
        x2, y2 = 150, 150  # Thumb (far from index)
        threshold = 30

        # Act
        result = detect_click(x1, y1, x2, y2, threshold)

        # Assert
        assert result is False, "Should not detect click when distance > threshold"

    def test_click_boundary_exact_threshold(self):
        """Test boundary condition: distance == threshold should return False (< not <=)."""
        # Arrange
        x1, y1 = 0, 0
        x2, y2 = 30, 0  # Distance = 30 (exactly at threshold)
        threshold = 30

        # Act
        result = detect_click(x1, y1, x2, y2, threshold)

        # Assert
        assert result is False, (
            "Should not detect click when distance == threshold (uses <, not <=)"
        )

    def test_click_zero_distance(self):
        """Test edge case: fingers overlap (distance = 0)."""
        # Arrange
        x1, y1 = 100, 100
        x2, y2 = 100, 100  # Same position (distance = 0)
        threshold = 30

        # Act
        result = detect_click(x1, y1, x2, y2, threshold)

        # Assert
        assert result is True, "Should detect click when fingers overlap (distance = 0)"

    def test_click_negative_coordinates(self):
        """Test handling of negative coordinates."""
        # Arrange
        x1, y1 = -50, -50
        x2, y2 = -40, -45  # Distance = sqrt(100 + 25) ≈ 11.18
        threshold = 30

        # Act
        result = detect_click(x1, y1, x2, y2, threshold)

        # Assert
        assert result is True, "Should handle negative coordinates correctly"
