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


class MockKDTree:
    """Mock KDTree class for mathutils.kdtree."""

    def __init__(self, size=0):
        self._points = []

    def insert(self, co, index):
        self._points.append((tuple(co), index))

    def balance(self):
        pass

    def find(self, co, filter=None):
        """Returns (co, index, dist) - mock returns None if no points."""
        if not self._points:
            return None, None, float('inf')
        # Simple mock: return first point with distance 0
        return self._points[0][0], self._points[0][1], 0.0

    def find_n(self, co, n):
        """Returns list of (co, index, dist) tuples."""
        return [(p[0], p[1], 0.0) for p in self._points[:n]]

    def find_range(self, co, radius):
        """Returns list of (co, index, dist) tuples within radius."""
        return [(p[0], p[1], 0.0) for p in self._points]


class MockEuler:
    """Mock Euler class for mathutils."""

    def __init__(self, rotation=(0, 0, 0), order='XYZ'):
        if hasattr(rotation, '__iter__'):
            self._rotation = list(rotation)
        else:
            self._rotation = [rotation, rotation, rotation]
        self.order = order

    def __iter__(self):
        return iter(self._rotation)

    def __getitem__(self, idx):
        return self._rotation[idx]

    def __setitem__(self, idx, value):
        self._rotation[idx] = value

    @property
    def x(self):
        return self._rotation[0]

    @property
    def y(self):
        return self._rotation[1]

    @property
    def z(self):
        return self._rotation[2]


mock_mathutils.Euler = MockEuler

# Create mock for mathutils.kdtree submodule
mock_kdtree = MagicMock()
mock_kdtree.KDTree = MockKDTree

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
sys.modules["mathutils.kdtree"] = mock_kdtree


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
