"""
Root pytest configuration for blender-ai-mcp tests.

This file configures pytest to properly discover and run tests from both:
- tests/unit/ - Unit tests with mocked bpy/bmesh
- tests/e2e/ - End-to-end tests with real Blender (when implemented)

The bpy/bmesh mocks are handled in tests/unit/conftest.py and only apply
to unit tests.
"""
import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (mocked bpy)")
    config.addinivalue_line("markers", "e2e: End-to-end tests (real Blender)")
    config.addinivalue_line("markers", "slow: Slow tests (> 5 seconds)")


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Add 'unit' marker to all tests in unit/ directory
        if "/unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add 'e2e' marker to all tests in e2e/ directory
        if "/e2e/" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
