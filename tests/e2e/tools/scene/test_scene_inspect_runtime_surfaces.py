"""
Blender-backed runtime coverage for read-heavy scene inspect surfaces.
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


def test_scene_inspect_runtime_surfaces(scene_handler, modeling_handler):
    object_name = "E2E_Inspect_Surface"

    try:
        _delete_if_present(scene_handler, object_name)
        modeling_handler.create_primitive(
            primitive_type="CUBE",
            name=object_name,
            size=2.0,
            location=[0.0, 0.0, 0.0],
        )
        modeling_handler.add_modifier(
            object_name,
            "BEVEL",
            {
                "width": 0.15,
                "segments": 2,
                "limit_method": "NONE",
            },
        )

        object_report = scene_handler.inspect_object(object_name)
        topology = scene_handler.inspect_mesh_topology(object_name, detailed=True)
        modifiers = scene_handler.inspect_modifiers(object_name)
        constraints = scene_handler.get_constraints(object_name)
        assert object_report["object_name"] == object_name
        assert object_report["type"] == "MESH"
        assert object_report["dimensions"] == pytest.approx([2.0, 2.0, 2.0], abs=1e-4)
        assert any(mod["type"] == "BEVEL" for mod in object_report["modifiers"])
        assert "mesh_stats" in object_report

        assert topology["object_name"] == object_name
        assert topology["vertex_count"] == 8
        assert topology["edge_count"] == 12
        assert topology["face_count"] == 6
        assert topology["triangle_count"] == 0
        assert topology["quad_count"] == 6
        assert topology["ngon_count"] == 0
        assert topology["non_manifold_edges"] == 0

        assert modifiers["object_count"] == 1
        assert modifiers["modifier_count"] == 1
        modifier_entry = modifiers["objects"][0]["modifiers"][0]
        assert modifier_entry["type"] == "BEVEL"
        assert modifier_entry["width"] == pytest.approx(0.15, abs=1e-4)
        assert modifier_entry["segments"] == 2
        assert modifier_entry["limit_method"] == "NONE"

        modifier_data = modeling_handler.get_modifier_data(object_name, modifier_name=modifier_entry["name"])

        assert constraints["object_name"] == object_name
        assert constraints["constraint_count"] == 0
        assert constraints["constraints"] == []
        assert constraints["bone_constraints"] == []

        assert modifier_data["object_name"] == object_name
        assert modifier_data["modifier_count"] == 1
        modifier_payload = modifier_data["modifiers"][0]
        assert modifier_payload["name"] == modifier_entry["name"]
        assert modifier_payload["type"] == "BEVEL"
        assert modifier_payload["properties"]["width"] == pytest.approx(0.15, abs=1e-4)
        assert modifier_payload["properties"]["segments"] == 2
    except RuntimeError as e:
        _skip_only_if_rpc_unavailable(e)
    finally:
        _delete_if_present(scene_handler, object_name)
