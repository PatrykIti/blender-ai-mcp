"""
Blender-backed runtime coverage for scene context and structural-read surfaces.
"""

from __future__ import annotations

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


def _delete_if_present(scene_handler: SceneToolHandler, object_name: str) -> None:
    try:
        scene_handler.delete_object(object_name)
    except RuntimeError:
        pass


def _skip_only_if_rpc_unavailable(error: RuntimeError) -> None:
    message = str(error).lower()
    if "could not connect" in message or "is blender running" in message:
        pytest.skip(f"Blender not available: {error}")
    raise error


def test_scene_context_runtime_surface(scene_handler, modeling_handler):
    object_name = "E2E_Context_Surface"

    try:
        _delete_if_present(scene_handler, object_name)
        modeling_handler.create_primitive(
            primitive_type="CUBE",
            name=object_name,
            size=2.0,
            location=[3.0, 0.0, 0.0],
        )
        scene_handler.set_active_object(object_name)
        scene_handler.set_mode("OBJECT")

        mode = scene_handler.get_mode()
        selection = scene_handler.list_selection()

        assert mode["mode"] == "OBJECT"
        assert mode["active_object"] == object_name
        assert object_name in mode["selected_object_names"]
        assert mode["selection_count"] >= 1

        assert selection["mode"] == "OBJECT"
        assert object_name in selection["selected_object_names"]
        assert selection["selection_count"] >= 1
        assert selection["edit_mode_vertex_count"] is None
        assert selection["edit_mode_edge_count"] is None
        assert selection["edit_mode_face_count"] is None
    except RuntimeError as e:
        _skip_only_if_rpc_unavailable(e)
    finally:
        _delete_if_present(scene_handler, object_name)


def test_scene_hierarchy_runtime_surface(scene_handler, modeling_handler):
    object_name = "E2E_Hierarchy_Surface"

    try:
        _delete_if_present(scene_handler, object_name)
        modeling_handler.create_primitive(
            primitive_type="CUBE",
            name=object_name,
            size=2.0,
            location=[0.0, 1.0, 0.0],
        )

        object_hierarchy = scene_handler.get_hierarchy(object_name=object_name, include_transforms=True)
        scene_hierarchy = scene_handler.get_hierarchy(include_transforms=False)

        assert object_hierarchy["root"]["name"] == object_name
        assert object_hierarchy["root"]["type"] == "MESH"
        assert object_hierarchy["root"]["children"] == []
        assert object_hierarchy["parent_chain"] == []
        assert len(object_hierarchy["root"]["location"]) == 3
        assert len(object_hierarchy["root"]["rotation"]) == 3
        assert len(object_hierarchy["root"]["scale"]) == 3

        assert scene_hierarchy["root_count"] >= 1
        assert any(node["name"] == object_name for node in scene_hierarchy["hierarchy"])
    except RuntimeError as e:
        _skip_only_if_rpc_unavailable(e)
    finally:
        _delete_if_present(scene_handler, object_name)


def test_scene_bounding_box_and_origin_runtime_surfaces(scene_handler, modeling_handler):
    object_name = "E2E_BBox_Surface"

    try:
        _delete_if_present(scene_handler, object_name)
        modeling_handler.create_primitive(
            primitive_type="CUBE",
            name=object_name,
            size=2.0,
            location=[1.0, 2.0, 3.0],
        )

        bbox = scene_handler.get_bounding_box(object_name, world_space=True)
        origin = scene_handler.get_origin_info(object_name)

        assert bbox["object_name"] == object_name
        assert bbox["world_space"] is True
        assert bbox["dimensions"] == pytest.approx([2.0, 2.0, 2.0], abs=1e-4)
        assert bbox["center"] == pytest.approx([1.0, 2.0, 3.0], abs=1e-4)
        assert len(bbox["corners"]) == 8

        assert origin["object_name"] == object_name
        assert origin["origin_world"] == pytest.approx([1.0, 2.0, 3.0], abs=1e-4)
        assert origin["bbox_center"] == pytest.approx([1.0, 2.0, 3.0], abs=1e-4)
        assert origin["offset_from_center"] == pytest.approx([0.0, 0.0, 0.0], abs=1e-4)
        assert origin["estimated_type"] == "CENTER"
    except RuntimeError as e:
        _skip_only_if_rpc_unavailable(e)
    finally:
        _delete_if_present(scene_handler, object_name)
