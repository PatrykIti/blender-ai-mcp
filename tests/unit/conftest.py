"""
Pytest configuration for managing bpy and bmesh mocks across all tests.

This ensures that bpy is properly mocked before any test imports blender modules,
and that mocks are reset between tests for proper isolation.
"""
import sys
from unittest.mock import MagicMock
import pytest


# Create global mocks for bpy and bmesh
mock_bpy = MagicMock()
mock_bmesh = MagicMock()

# Configure mock bpy structure
mock_bpy.ops = MagicMock()
mock_bpy.data = MagicMock()
mock_bpy.context = MagicMock()
mock_bpy.types = MagicMock()

# Inject mocks into sys.modules BEFORE any imports
# This runs at module load time, before test collection
sys.modules["bpy"] = mock_bpy
sys.modules["bmesh"] = mock_bmesh


@pytest.fixture(autouse=True)
def reset_bpy_mocks():
    """
    Automatically reset bpy and bmesh mocks before each test.

    This ensures test isolation while keeping the mocks in sys.modules
    so imports work correctly.
    """
    # Reset before test
    mock_bpy.reset_mock()
    mock_bmesh.reset_mock()

    # Reconfigure essential structure after reset
    mock_bpy.ops = MagicMock()
    mock_bpy.data = MagicMock()
    mock_bpy.context = MagicMock()
    mock_bpy.types = MagicMock()

    yield

    # Could also reset after test if needed, but before is usually sufficient


@pytest.fixture
def bpy():
    """Provide access to the mock bpy module in tests."""
    return mock_bpy


@pytest.fixture
def bmesh():
    """Provide access to the mock bmesh module in tests."""
    return mock_bmesh
