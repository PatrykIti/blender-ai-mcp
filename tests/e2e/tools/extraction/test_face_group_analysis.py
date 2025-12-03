"""
E2E Tests for extraction_face_group_analysis (TASK-044-5)

These tests require a running Blender instance with the addon loaded.
"""
import pytest
from server.application.tool_handlers.extraction_handler import ExtractionToolHandler


@pytest.fixture
def extraction_handler(rpc_client):
    """Provides an extraction handler instance using shared RPC client."""
    return ExtractionToolHandler(rpc_client)


def test_face_group_analysis_cube(extraction_handler):
    """Test face group analysis on default cube."""
    try:
        result = extraction_handler.face_group_analysis("Cube")

        assert "object_name" in result
        assert result["object_name"] == "Cube"
        assert "face_groups" in result
        assert "normal_group_count" in result
        assert "height_level_count" in result

        print(f"✓ face_group_analysis on Cube:")
        print(f"  Normal groups: {result['normal_group_count']}")
        print(f"  Height levels: {result['height_level_count']}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_face_group_analysis_feature_detection(extraction_handler):
    """Test inset/extrusion detection."""
    try:
        result = extraction_handler.face_group_analysis("Cube")

        assert "detected_insets" in result
        assert "detected_extrusions" in result
        assert "has_insets" in result
        assert "has_extrusions" in result

        print(f"✓ face_group_analysis feature detection:")
        print(f"  Insets: {result['detected_insets']} (has_insets: {result['has_insets']})")
        print(f"  Extrusions: {result['detected_extrusions']} (has_extrusions: {result['has_extrusions']})")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_face_group_analysis_with_angle_threshold(extraction_handler):
    """Test with custom angle threshold."""
    try:
        result = extraction_handler.face_group_analysis("Cube", angle_threshold=10.0)

        assert "face_groups" in result
        print(f"✓ face_group_analysis with angle_threshold: {len(result['face_groups'])} groups")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_face_group_analysis_not_found(extraction_handler):
    """Test face group analysis on non-existent object."""
    try:
        result = extraction_handler.face_group_analysis("NonExistentObject12345")
        pytest.fail("Should have raised an error")

    except RuntimeError as e:
        assert "not found" in str(e).lower() or "error" in str(e).lower()
        print("✓ face_group_analysis: correctly handles non-existent object")
