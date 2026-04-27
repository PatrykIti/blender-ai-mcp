"""Blender-backed E2E tests for macro_align_part_with_contact."""

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


def test_macro_align_part_with_contact_repairs_small_gap_without_full_replace(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    head_name = "RepairHead"
    ear_name = "RepairEar"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=head_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=ear_name, size=1.0, location=[1.25, 0.0, 0.0])
        modeling_handler.transform_object(name=ear_name, scale=[0.2, 0.4, 0.6])

        result = macro_handler.align_part_with_contact(
            part_object=ear_name,
            reference_object=head_name,
            target_relation="contact",
            align_mode="none",
            max_nudge=0.2,
        )

        assert result["status"] == "success"
        assert result["macro_name"] == "macro_align_part_with_contact"
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


def test_macro_align_part_with_contact_blocks_when_required_nudge_is_too_large(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    head_name = "RepairBlockedHead"
    ear_name = "RepairBlockedEar"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=head_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=ear_name, size=1.0, location=[1.25, 0.0, 0.0])
        modeling_handler.transform_object(name=ear_name, scale=[0.2, 0.4, 0.6])

        before_bbox = scene_handler.get_bounding_box(ear_name)

        result = macro_handler.align_part_with_contact(
            part_object=ear_name,
            reference_object=head_name,
            target_relation="contact",
            align_mode="none",
            max_nudge=0.01,
        )

        after_bbox = scene_handler.get_bounding_box(ear_name)

        assert result["status"] == "blocked"
        assert before_bbox["center"] == pytest.approx(after_bbox["center"], abs=1e-4)
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)


def test_macro_align_part_with_contact_repairs_tail_body_gap_as_attachment(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    body_name = "RepairTailBody"
    tail_name = "RepairTail"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=tail_name, size=1.0, location=[1.35, 0.0, 0.0])
        modeling_handler.transform_object(name=tail_name, scale=[0.6, 0.25, 0.25])

        result = macro_handler.align_part_with_contact(
            part_object=tail_name,
            reference_object=body_name,
            target_relation="contact",
            align_mode="none",
            max_nudge=0.3,
        )

        assert result["status"] == "success"
        assert result["macro_name"] == "macro_align_part_with_contact"
        assert result["actions_taken"][-1]["details"]["attachment_verdict"] == "seated_contact"

        gap = scene_handler.measure_gap(tail_name, body_name)
        contact = scene_handler.assert_contact(tail_name, body_name, max_gap=0.001)

        assert gap["relation"] == "contact"
        assert contact["passed"] is True
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)


def test_macro_align_part_with_contact_repairs_forelimb_body_gap_as_attachment(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    body_name = "RepairForelimbBody"
    forelimb_name = "RepairForelimb"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(
            primitive_type="CUBE", name=forelimb_name, size=1.0, location=[1.0, 0.0, -1.2]
        )
        modeling_handler.transform_object(name=forelimb_name, scale=[0.6, 0.3, 0.3])

        result = macro_handler.align_part_with_contact(
            part_object=forelimb_name,
            reference_object=body_name,
            target_relation="contact",
            align_mode="none",
            max_nudge=0.2,
        )

        gap = scene_handler.measure_gap(forelimb_name, body_name)
        contact = scene_handler.assert_contact(forelimb_name, body_name, max_gap=0.001)

        assert result["status"] == "success"
        assert gap["relation"] == "contact"
        assert contact["passed"] is True
        assert result["actions_taken"][-1]["details"]["attachment_verdict"] == "seated_contact"
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)
