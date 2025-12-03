"""
E2E Tests for extraction_edge_loop_analysis (TASK-044-4)

These tests require a running Blender instance with the addon loaded.
"""
import pytest
from server.application.tool_handlers.extraction_handler import ExtractionToolHandler


@pytest.fixture
def extraction_handler(rpc_client):
    """Provides an extraction handler instance using shared RPC client."""
    return ExtractionToolHandler(rpc_client)


def test_edge_loop_analysis_cube(extraction_handler):
    """Test edge loop analysis on default cube."""
    try:
        result = extraction_handler.edge_loop_analysis("Cube")

        assert "object_name" in result
        assert result["object_name"] == "Cube"
        assert "total_edges" in result or "boundary_edges" in result
        assert "parallel_edge_groups" in result
        assert "chamfer_edges" in result
        assert "has_chamfer" in result

        print(f"✓ edge_loop_analysis on Cube:")
        print(f"  Parallel groups: {result.get('parallel_edge_groups', 0)}")
        print(f"  Chamfer edges: {result.get('chamfer_edges', 0)}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_edge_loop_analysis_support_loops(extraction_handler):
    """Test support loop detection."""
    try:
        result = extraction_handler.edge_loop_analysis("Cube")

        assert "support_loop_candidates" in result
        assert "estimated_bevel_segments" in result

        print(f"✓ edge_loop_analysis support loop detection:")
        print(f"  Support loops: {result['support_loop_candidates']}")
        print(f"  Estimated bevel segments: {result['estimated_bevel_segments']}")

    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_edge_loop_analysis_not_found(extraction_handler):
    """Test edge loop analysis on non-existent object."""
    try:
        result = extraction_handler.edge_loop_analysis("NonExistentObject12345")
        pytest.fail("Should have raised an error")

    except RuntimeError as e:
        assert "not found" in str(e).lower() or "error" in str(e).lower()
        print("✓ edge_loop_analysis: correctly handles non-existent object")
