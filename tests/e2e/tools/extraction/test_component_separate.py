"""
E2E Tests for extraction_component_separate (TASK-044-2)

These tests require a running Blender instance with the addon loaded.
"""
import pytest


def test_component_separate_single_object(extraction_handler, test_cube):
    """Test separating a single solid object (should result in 1 component)."""
    try:
        result = extraction_handler.component_separate(test_cube)

        assert "original_object" in result
        assert "component_count" in result
        assert "components" in result

        print(f"✓ component_separate: {result['component_count']} components created")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "connection" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_component_separate_with_min_vertices(extraction_handler, test_cube):
    """Test component separation with custom min_vertex_count."""
    try:
        result = extraction_handler.component_separate(test_cube, min_vertex_count=8)

        assert "deleted_small_components" in result
        print(f"✓ component_separate with min_vertex_count: {result['deleted_small_components']} small components removed")

    except RuntimeError as e:
        error_msg = str(e).lower()
        if "could not connect" in error_msg or "connection" in error_msg:
            pytest.skip(f"Blender not available: {e}")
        raise


def test_component_separate_not_found(extraction_handler):
    """Test component separate on non-existent object."""
    try:
        result = extraction_handler.component_separate("NonExistentObject12345")
        pytest.fail("Should have raised an error")

    except RuntimeError as e:
        assert "not found" in str(e).lower() or "error" in str(e).lower()
        print("✓ component_separate: correctly handles non-existent object")
