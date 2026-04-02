"""Blender-backed E2E tests for macro_place_supported_pair."""

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


def test_macro_place_supported_pair_places_pair_on_floor(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    support_name = "SupportFloor"
    left_name = "SupportPairLeft"
    right_name = "SupportPairRight"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=support_name, size=1.0, location=[0.0, 0.0, 0.0])
        modeling_handler.transform_object(name=support_name, scale=[3.0, 2.0, 0.1])

        modeling_handler.create_primitive(primitive_type="CUBE", name=left_name, size=1.0, location=[-1.2, 0.0, 0.75])
        modeling_handler.create_primitive(primitive_type="CUBE", name=right_name, size=1.0, location=[1.45, 0.05, 0.9])
        modeling_handler.transform_object(name=left_name, scale=[0.2, 0.3, 0.25])
        modeling_handler.transform_object(name=right_name, scale=[0.2, 0.3, 0.25])

        result = macro_handler.place_supported_pair(
            left_object=left_name,
            right_object=right_name,
            support_object=support_name,
            axis="X",
            mirror_coordinate=0.0,
            support_axis="Z",
            support_side="positive",
            anchor_object="left",
        )

        assert result["status"] == "success"
        assert result["macro_name"] == "macro_place_supported_pair"
        assert left_name in result["objects_modified"]
        assert right_name in result["objects_modified"]
        assert result["requires_followup"] is True

        left_contact = scene_handler.assert_contact(left_name, support_name, max_gap=0.001, allow_overlap=False)
        right_contact = scene_handler.assert_contact(right_name, support_name, max_gap=0.001, allow_overlap=False)
        symmetry = scene_handler.assert_symmetry(
            left_name, right_name, axis="X", mirror_coordinate=0.0, tolerance=0.001
        )
        support_bbox = scene_handler.get_bounding_box(support_name)
        right_bbox = scene_handler.get_bounding_box(right_name)
        expected_right_z = float(support_bbox["max"][2]) + (float(right_bbox["dimensions"][2]) / 2.0)

        assert left_contact["passed"] is True
        assert right_contact["passed"] is True
        assert symmetry["passed"] is True
        assert right_bbox["center"] == pytest.approx([1.2, 0.0, expected_right_z], abs=1e-4)
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)
