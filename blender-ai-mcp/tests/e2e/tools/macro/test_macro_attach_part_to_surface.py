"""Blender-backed E2E tests for macro_attach_part_to_surface."""

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


def test_macro_attach_part_to_surface_seats_ear_on_head_surface(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    head_name = "AttachHead"
    ear_name = "AttachEar"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=head_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=ear_name, size=1.0, location=[4, 4, 4])
        modeling_handler.transform_object(name=ear_name, scale=[0.2, 0.4, 0.6])

        result = macro_handler.attach_part_to_surface(
            part_object=ear_name,
            surface_object=head_name,
            surface_axis="X",
            surface_side="positive",
            align_mode="center",
            gap=0.0,
        )

        assert result["status"] == "success"
        assert result["macro_name"] == "macro_attach_part_to_surface"
        assert ear_name in result["objects_modified"]
        assert result["requires_followup"] is True

        ear_bbox = scene_handler.get_bounding_box(ear_name)
        gap = scene_handler.measure_gap(ear_name, head_name)
        contact = scene_handler.assert_contact(ear_name, head_name, max_gap=0.001)

        assert ear_bbox["center"] == pytest.approx([1.1, 0.0, 0.0], abs=1e-4)
        assert gap["gap"] == pytest.approx(0.0, abs=1e-4)
        assert gap["relation"] == "contact"
        assert contact["passed"] is True
        assert result["actions_taken"][-1]["details"]["attachment_verdict"] == "seated_contact"
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)


def test_macro_attach_part_to_surface_negative_gap_raises(
    clean_scene,
    modeling_handler,
    macro_handler,
):
    head_name = "AttachErrorHead"
    ear_name = "AttachErrorEar"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=head_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=ear_name, size=1.0, location=[2, 2, 2])

        with pytest.raises(ValueError, match="gap must be >= 0"):
            macro_handler.attach_part_to_surface(
                part_object=ear_name,
                surface_object=head_name,
                surface_axis="X",
                gap=-0.01,
            )
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)


def test_macro_attach_part_to_surface_seats_nose_on_snout_surface(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    snout_name = "AttachSnout"
    nose_name = "AttachNose"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=snout_name, size=1.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=nose_name, size=1.0, location=[4, 4, 4])
        modeling_handler.transform_object(name=snout_name, scale=[0.8, 0.5, 0.4])
        modeling_handler.transform_object(name=nose_name, scale=[0.16, 0.16, 0.16])

        result = macro_handler.attach_part_to_surface(
            part_object=nose_name,
            surface_object=snout_name,
            surface_axis="X",
            surface_side="positive",
            align_mode="center",
            gap=0.0,
        )

        gap = scene_handler.measure_gap(nose_name, snout_name)
        contact = scene_handler.assert_contact(nose_name, snout_name, max_gap=0.001)

        assert result["status"] == "success"
        assert gap["relation"] == "contact"
        assert contact["passed"] is True
        assert result["actions_taken"][-1]["details"]["attachment_verdict"] == "seated_contact"
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)
