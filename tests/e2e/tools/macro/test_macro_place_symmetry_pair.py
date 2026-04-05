"""Blender-backed E2E tests for macro_place_symmetry_pair."""

from __future__ import annotations

import pytest
from server.application.tool_handlers.macro_handler import MacroToolHandler
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler

pytestmark = pytest.mark.e2e


def _skip_if_blender_unavailable(error: RuntimeError) -> None:
    error_msg = str(error).lower()
    if "could not connect" in error_msg or "is blender running" in error_msg:
        pytest.skip(f"Blender not available: {error}")
    raise error


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


def test_macro_place_symmetry_pair_mirrors_right_part_from_left_anchor(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    left_name = "SymPairLeft"
    right_name = "SymPairRight"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=left_name, size=1.0, location=[-1.2, 0.0, 1.0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=right_name, size=1.0, location=[1.45, 0.05, 1.05])
        modeling_handler.transform_object(name=left_name, scale=[0.2, 0.4, 0.6])
        modeling_handler.transform_object(name=right_name, scale=[0.2, 0.4, 0.6])

        result = macro_handler.place_symmetry_pair(
            left_object=left_name,
            right_object=right_name,
            axis="X",
            mirror_coordinate=0.0,
            anchor_object="left",
        )

        assert result["status"] == "success"
        assert result["macro_name"] == "macro_place_symmetry_pair"
        assert right_name in result["objects_modified"]
        assert result["requires_followup"] is True

        symmetry = scene_handler.assert_symmetry(
            left_name, right_name, axis="X", mirror_coordinate=0.0, tolerance=0.001
        )
        right_bbox = scene_handler.get_bounding_box(right_name)

        assert symmetry["passed"] is True
        assert right_bbox["center"] == pytest.approx([1.2, 0.0, 1.0], abs=1e-4)
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)
