"""Blender-backed E2E tests for macro_cleanup_part_intersections."""

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


def test_macro_cleanup_part_intersections_separates_overlap_to_contact(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    body_name = "OverlapBody"
    horn_name = "OverlapHorn"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.0, location=[0.0, 0.0, 0.0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=horn_name, size=1.0, location=[0.95, 0.0, 1.0])
        modeling_handler.transform_object(name=horn_name, scale=[0.2, 0.4, 0.6])

        result = macro_handler.cleanup_part_intersections(
            part_object=horn_name,
            reference_object=body_name,
            max_push=0.3,
        )

        assert result["status"] == "success"
        assert result["macro_name"] == "macro_cleanup_part_intersections"
        assert horn_name in result["objects_modified"]
        assert result["requires_followup"] is True

        body_bbox = scene_handler.get_bounding_box(body_name)
        horn_bbox = scene_handler.get_bounding_box(horn_name)
        expected_horn_x = float(body_bbox["max"][0]) + (float(horn_bbox["dimensions"][0]) / 2.0)
        overlap = scene_handler.measure_overlap(horn_name, body_name)
        contact = scene_handler.assert_contact(horn_name, body_name, max_gap=0.001, allow_overlap=False)

        assert horn_bbox["center"] == pytest.approx([expected_horn_x, 0.0, 1.0], abs=1e-4)
        assert overlap["overlaps"] is False
        assert contact["passed"] is True
        assert result["actions_taken"][-1]["details"]["attachment_verdict"] == "seated_contact"
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)
