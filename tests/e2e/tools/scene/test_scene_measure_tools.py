"""
E2E tests for the first measure/assert scene tools (TASK-116).
"""

import pytest
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


@pytest.fixture
def modeling_handler(rpc_client):
    """Provides a modeling handler instance using shared RPC client."""
    return ModelingToolHandler(rpc_client)


def test_scene_measure_distance_and_gap(scene_handler, modeling_handler):
    left_name = "E2E_Measure_Left"
    right_name = "E2E_Measure_Right"

    try:
        for name in (left_name, right_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass

        modeling_handler.create_primitive(primitive_type="CUBE", name=left_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=right_name, size=2.0, location=[4, 0, 0])

        distance = scene_handler.measure_distance(left_name, right_name, reference="ORIGIN")
        gap = scene_handler.measure_gap(left_name, right_name)

        assert distance["distance"] == pytest.approx(4.0, abs=1e-4)
        assert gap["gap"] == pytest.approx(2.0, abs=1e-4)
        assert gap["relation"] == "separated"
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
    finally:
        for name in (left_name, right_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass


def test_scene_measure_dimensions_alignment_and_overlap(scene_handler, modeling_handler):
    base_name = "E2E_Measure_Base"
    overlap_name = "E2E_Measure_Overlap"

    try:
        for name in (base_name, overlap_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass

        modeling_handler.create_primitive(primitive_type="CUBE", name=base_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=overlap_name, size=2.0, location=[1, 0, 0])

        dimensions = scene_handler.measure_dimensions(base_name)
        alignment = scene_handler.measure_alignment(base_name, overlap_name, axes=["Y", "Z"], reference="CENTER")
        overlap = scene_handler.measure_overlap(base_name, overlap_name)

        assert dimensions["dimensions"] == pytest.approx([2.0, 2.0, 2.0], abs=1e-4)
        assert dimensions["volume"] == pytest.approx(8.0, abs=1e-4)
        assert alignment["is_aligned"] is True
        assert alignment["aligned_axes"] == ["Y", "Z"]
        assert overlap["overlaps"] is True
        assert overlap["relation"] == "overlap"
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
    finally:
        for name in (base_name, overlap_name):
            try:
                scene_handler.delete_object(name)
            except RuntimeError:
                pass
