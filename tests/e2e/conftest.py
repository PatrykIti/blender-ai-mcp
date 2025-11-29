"""
E2E test configuration for blender-ai-mcp.

This conftest provides fixtures for running tests against a real Blender instance.

To run E2E tests:
    BLENDER_PATH=/path/to/blender pytest tests/e2e/ -v

Prerequisites:
- Blender installed and accessible
- blender_addon properly configured

Note: E2E tests are not yet implemented. See TASK-028 for implementation plan.
"""
import os
import pytest

# Skip all E2E tests if Blender is not available
BLENDER_PATH = os.environ.get("BLENDER_PATH", "blender")


def pytest_collection_modifyitems(config, items):
    """Skip E2E tests if Blender is not available."""
    import shutil

    if not shutil.which(BLENDER_PATH):
        skip_marker = pytest.mark.skip(reason="Blender not found. Set BLENDER_PATH env var.")
        for item in items:
            if "/e2e/" in str(item.fspath):
                item.add_marker(skip_marker)


# Placeholder fixtures - to be implemented in TASK-028

# @pytest.fixture(scope="session")
# def blender_process():
#     """Start Blender with addon loaded for entire test session."""
#     pass

# @pytest.fixture
# def rpc_client(blender_process):
#     """Provide RPC client connected to test Blender instance."""
#     pass

# @pytest.fixture
# def clean_scene(rpc_client):
#     """Ensure clean scene before each test."""
#     pass
