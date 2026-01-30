import pytest
from main import apply_smoothing


@pytest.mark.unit
def test_smoothing_reduces_sudden_movement():
    """Test that large jumps in position are smoothed out."""
    # Simulate a sudden large movement from (100, 100) to (500, 500)
    current_x, current_y = 500, 500
    prev_x, prev_y = 100, 100
    factor = 5

    new_x, new_y = apply_smoothing(current_x, current_y, prev_x, prev_y, factor)

    # With factor=5, new position should be:
    # new_x = 100 + (500 - 100) / 5 = 100 + 80 = 180
    # new_y = 100 + (500 - 100) / 5 = 100 + 80 = 180
    assert new_x == 180
    assert new_y == 180

    # Verify it's between previous and current (smoothed)
    assert prev_x < new_x < current_x
    assert prev_y < new_y < current_y


@pytest.mark.unit
def test_smoothing_factor_1_immediate():
    """Test that factor=1 produces immediate response (no smoothing)."""
    current_x, current_y = 1920, 1080
    prev_x, prev_y = 960, 540
    factor = 1

    new_x, new_y = apply_smoothing(current_x, current_y, prev_x, prev_y, factor)

    # With factor=1, new position should equal current position
    # new_x = 960 + (1920 - 960) / 1 = 960 + 960 = 1920
    # new_y = 540 + (1080 - 540) / 1 = 540 + 540 = 1080
    assert new_x == current_x
    assert new_y == current_y


@pytest.mark.unit
def test_smoothing_factor_high_slow():
    """Test that high factor produces slow response (heavy smoothing)."""
    current_x, current_y = 1000, 1000
    prev_x, prev_y = 0, 0
    factor = 10

    new_x, new_y = apply_smoothing(current_x, current_y, prev_x, prev_y, factor)

    # With factor=10, new position should be:
    # new_x = 0 + (1000 - 0) / 10 = 100
    # new_y = 0 + (1000 - 0) / 10 = 100
    assert new_x == 100
    assert new_y == 100

    # Verify it's much closer to previous than current (heavy smoothing)
    assert abs(new_x - prev_x) < abs(current_x - prev_x) / 2
    assert abs(new_y - prev_y) < abs(current_y - prev_y) / 2


@pytest.mark.unit
def test_smoothing_same_position():
    """Test that same position produces no change."""
    current_x, current_y = 500, 500
    prev_x, prev_y = 500, 500
    factor = 5

    new_x, new_y = apply_smoothing(current_x, current_y, prev_x, prev_y, factor)

    # When current equals previous, result should be unchanged
    # new_x = 500 + (500 - 500) / 5 = 500 + 0 = 500
    # new_y = 500 + (500 - 500) / 5 = 500 + 0 = 500
    assert new_x == 500
    assert new_y == 500
    assert new_x == current_x
    assert new_y == current_y
