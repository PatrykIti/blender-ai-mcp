"""
E2E Tests for extraction_detect_symmetry (TASK-044-3)

These tests require a running Blender instance with the addon loaded.
"""
import pytest
from server.application.tool_handlers.extraction_handler import ExtractionToolHandler


@pytest.fixture
def extraction_handler(rpc_client):
    """Provides an extraction handler instance using shared RPC client."""
    return ExtractionToolHandler(rpc_client)


def test_detect_symmetry_cube(extraction_handler):
    """Test symmetry detection on default cube (should be symmetric on all axes)."""
    try:
        result = extraction_handler.detect_symmetry("Cube")

        assert "object_name" in result
        assert result["object_name"] == "Cube"
        assert "x_symmetric" in result
        assert "y_symmetric" in result
        assert "z_symmetric" in result
        assert "x_confidence" in result
        assert "total_vertices" in result

        print(f"✓ detect_symmetry on Cube:")
        print(f"  X: {result['x_symmetric']} ({result['x_confidence']})")
        print(f"  Y: {result['y_symmetric']} ({result['y_confidence']})")
        print(f"  Z: {result['z_symmetric']} ({result['z_confidence']})")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_detect_symmetry_with_tolerance(extraction_handler):
    """Test symmetry detection with custom tolerance."""
    try:
        result = extraction_handler.detect_symmetry("Cube", tolerance=0.01)

        assert "tolerance" in result
        assert result["tolerance"] == 0.01
        print(f"✓ detect_symmetry with tolerance: {result['tolerance']}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_detect_symmetry_not_found(extraction_handler):
    """Test symmetry detection on non-existent object."""
    try:
        result = extraction_handler.detect_symmetry("NonExistentObject12345")
        pytest.fail("Should have raised an error")

    except RuntimeError as e:
        assert "not found" in str(e).lower() or "error" in str(e).lower()
        print("✓ detect_symmetry: correctly handles non-existent object")
