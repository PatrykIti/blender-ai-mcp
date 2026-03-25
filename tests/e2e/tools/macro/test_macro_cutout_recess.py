"""Blender-backed E2E tests for macro_cutout_recess."""

from __future__ import annotations

import pytest

from server.application.tool_handlers.macro_handler import MacroToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="session")
def scene_handler(rpc_client):
    return SceneToolHandler(rpc_client)


@pytest.fixture(scope="session")
def modeling_handler(rpc_client):
    return ModelingToolHandler(rpc_client)


@pytest.fixture(scope="session")
def macro_handler(scene_handler, modeling_handler):
    return MacroToolHandler(scene_handler, modeling_handler)


@pytest.fixture
def clean_scene(scene_handler):
    scene_handler.clean_scene(keep_lights_and_cameras=False)
    yield
    scene_handler.clean_scene(keep_lights_and_cameras=False)


def test_macro_cutout_recess_delete_cleanup_roundtrip(clean_scene, scene_handler, modeling_handler, macro_handler):
    target_name = "MacroBody"
    cutter_name = "MacroCutDelete"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=target_name, size=2.0, location=[0, 0, 0])

        baseline_bbox = scene_handler.get_bounding_box(target_name)
        baseline_topology = scene_handler.inspect_mesh_topology(target_name, detailed=False)

        result = macro_handler.cutout_recess(
            target_object=target_name,
            width=0.8,
            height=1.2,
            depth=0.3,
            face="front",
            mode="recess",
            bevel_width=0.02,
            bevel_segments=3,
            cleanup="delete",
            cutter_name=cutter_name,
        )

        assert result["status"] == "success"
        assert result["macro_name"] == "macro_cutout_recess"
        assert target_name in result["objects_modified"]
        assert result["requires_followup"] is True

        objects = {item["name"] for item in scene_handler.list_objects()}
        assert target_name in objects
        assert cutter_name not in objects

        bbox_after = scene_handler.get_bounding_box(target_name)
        topology_after = scene_handler.inspect_mesh_topology(target_name, detailed=False)

        assert bbox_after["dimensions"] == pytest.approx(baseline_bbox["dimensions"], abs=1e-4)
        assert topology_after["face_count"] > baseline_topology["face_count"]
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_macro_cutout_recess_hide_cleanup_keeps_hidden_helper(clean_scene, scene_handler, modeling_handler, macro_handler):
    target_name = "MacroBody"
    cutter_name = "MacroCutHidden"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=target_name, size=2.0, location=[0, 0, 0])

        result = macro_handler.cutout_recess(
            target_object=target_name,
            width=0.6,
            height=0.6,
            depth=0.2,
            face="top",
            mode="cut_through",
            cleanup="hide",
            cutter_name=cutter_name,
        )

        assert result["status"] == "success"

        snapshot = scene_handler.snapshot_state(include_mesh_stats=False, include_materials=False)
        objects = {item["name"]: item for item in snapshot["snapshot"]["objects"]}

        assert cutter_name in objects
        assert objects[cutter_name]["visible"] is False
        assert target_name in objects
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")


def test_macro_cutout_recess_invalid_recess_depth_raises(clean_scene, scene_handler, modeling_handler, macro_handler):
    target_name = "MacroBody"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=target_name, size=2.0, location=[0, 0, 0])

        with pytest.raises(ValueError, match="recess depth"):
            macro_handler.cutout_recess(
                target_object=target_name,
                width=0.8,
                height=0.8,
                depth=2.5,
                face="front",
                mode="recess",
            )
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
