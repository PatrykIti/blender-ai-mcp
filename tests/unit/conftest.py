"""
Pytest configuration for managing bpy and bmesh mocks across all tests.

This ensures that bpy is properly mocked before any test imports blender modules,
and that mocks are reset between tests for proper isolation.
"""
import sys
from unittest.mock import MagicMock
import pytest


# Create global mocks for bpy, bmesh, and mathutils
mock_bpy = MagicMock()
mock_bmesh = MagicMock()
mock_mathutils = MagicMock()


class MockVector:
    """Mock Vector class for mathutils."""

    def __init__(self, coords=(0, 0, 0)):
        if hasattr(coords, '__iter__'):
            self._coords = list(coords)
        else:
            self._coords = [coords, coords, coords]

    def __iter__(self):
        return iter(self._coords)

    def __add__(self, other):
        if isinstance(other, MockVector):
            return MockVector([a + b for a, b in zip(self._coords, other._coords)])
        return MockVector([c + other for c in self._coords])

    def __sub__(self, other):
        if isinstance(other, MockVector):
            return MockVector([a - b for a, b in zip(self._coords, other._coords)])
        return MockVector([c - other for c in self._coords])

    def __getitem__(self, idx):
        return self._coords[idx]

    def __setitem__(self, idx, value):
        self._coords[idx] = value

    @property
    def x(self):
        return self._coords[0]

    @property
    def y(self):
        return self._coords[1]

    @property
    def z(self):
        return self._coords[2]


mock_mathutils.Vector = MockVector

# Configure mock bpy structure
mock_bpy.ops = MagicMock()
mock_bpy.data = MagicMock()
mock_bpy.context = MagicMock()
mock_bpy.types = MagicMock()

# Inject mocks into sys.modules BEFORE any imports
# This runs at module load time, before test collection
sys.modules["bpy"] = mock_bpy
sys.modules["bmesh"] = mock_bmesh
sys.modules["mathutils"] = mock_mathutils


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


@pytest.fixture
def mathutils():
    """Provide access to the mock mathutils module in tests."""
    return mock_mathutils
