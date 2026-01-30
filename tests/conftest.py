"""
Pytest configuration and shared fixtures for Air Mouse tests.
"""

import pytest


@pytest.fixture
def mock_config():
    """Provide a basic mock configuration for tests."""
    return {
        "debug": True,
        "test_mode": True,
    }
