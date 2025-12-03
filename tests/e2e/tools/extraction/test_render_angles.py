"""
E2E Tests for extraction_render_angles (TASK-044-6)

These tests require a running Blender instance with the addon loaded.
"""
import os
import pytest
from server.application.tool_handlers.extraction_handler import ExtractionToolHandler


@pytest.fixture
def extraction_handler(rpc_client):
    """Provides an extraction handler instance using shared RPC client."""
    return ExtractionToolHandler(rpc_client)


def test_render_angles_single(extraction_handler):
    """Test rendering a single angle."""
    try:
        result = extraction_handler.render_angles(
            "Cube",
            angles=["front"],
            resolution=256,
            output_dir="/tmp/extraction_test"
        )

        assert "object_name" in result
        assert result["object_name"] == "Cube"
        assert "renders" in result
        assert len(result["renders"]) == 1
        assert result["renders"][0]["angle"] == "front"

        print(f"✓ render_angles single: {result['renders'][0]['path']}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_render_angles_multiple(extraction_handler):
    """Test rendering multiple angles."""
    try:
        result = extraction_handler.render_angles(
            "Cube",
            angles=["front", "iso"],
            resolution=256,
            output_dir="/tmp/extraction_test"
        )

        assert len(result["renders"]) == 2
        angles = [r["angle"] for r in result["renders"]]
        assert "front" in angles
        assert "iso" in angles

        print(f"✓ render_angles multiple: {len(result['renders'])} renders")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_render_angles_default_all(extraction_handler):
    """Test rendering with default angles (all 6)."""
    try:
        result = extraction_handler.render_angles(
            "Cube",
            resolution=256,
            output_dir="/tmp/extraction_test"
        )

        # Default should be 6 angles
        assert len(result["renders"]) == 6

        print(f"✓ render_angles all: {len(result['renders'])} renders created")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_render_angles_not_found(extraction_handler):
    """Test render angles on non-existent object."""
    try:
        result = extraction_handler.render_angles("NonExistentObject12345")
        pytest.fail("Should have raised an error")

    except RuntimeError as e:
        assert "not found" in str(e).lower() or "error" in str(e).lower()
        print("✓ render_angles: correctly handles non-existent object")
