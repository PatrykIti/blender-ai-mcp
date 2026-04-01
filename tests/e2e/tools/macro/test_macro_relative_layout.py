"""Blender-backed E2E tests for macro_relative_layout."""

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


def test_macro_relative_layout_places_leg_with_contact_under_tabletop(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    table_name = "LayoutTableTop"
    leg_name = "LayoutLeg"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=table_name, size=2.0, location=[0, 0, 1.1])
        modeling_handler.transform_object(name=table_name, scale=[1.0, 0.5, 0.1])

        modeling_handler.create_primitive(primitive_type="CUBE", name=leg_name, size=1.0, location=[3, 3, 3])
        modeling_handler.transform_object(name=leg_name, scale=[0.2, 0.2, 1.0])

        result = macro_handler.relative_layout(
            moving_object=leg_name,
            reference_object=table_name,
            x_mode="min",
            y_mode="max",
            contact_axis="Z",
            contact_side="negative",
            gap=0.0,
            offset=[0.1, -0.05, 0.0],
        )

        assert result["status"] == "success"
        assert result["macro_name"] == "macro_relative_layout"
        assert leg_name in result["objects_modified"]
        assert result["requires_followup"] is True

        leg_bbox = scene_handler.get_bounding_box(leg_name)
        gap = scene_handler.measure_gap(leg_name, table_name)
        contact = scene_handler.assert_contact(leg_name, table_name, max_gap=0.001)

        assert leg_bbox["center"] == pytest.approx([-0.8, 0.35, 0.5], abs=1e-4)
        assert gap["gap"] == pytest.approx(0.0, abs=1e-4)
        assert gap["relation"] == "contact"
        assert contact["passed"] is True
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)


def test_macro_relative_layout_centers_requested_axes(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    base_name = "LayoutBase"
    part_name = "LayoutPart"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=base_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=part_name, size=1.0, location=[4, 4, 4])

        result = macro_handler.relative_layout(
            moving_object=part_name,
            reference_object=base_name,
            x_mode="center",
            y_mode="center",
            z_mode="max",
        )

        assert result["status"] == "success"

        alignment = scene_handler.measure_alignment(part_name, base_name, axes=["X", "Y"], reference="CENTER")
        part_bbox = scene_handler.get_bounding_box(part_name)
        base_bbox = scene_handler.get_bounding_box(base_name)

        assert alignment["is_aligned"] is True
        assert alignment["aligned_axes"] == ["X", "Y"]
        assert part_bbox["center"][0:2] == pytest.approx(base_bbox["center"][0:2], abs=1e-4)
        assert part_bbox["max"][2] == pytest.approx(base_bbox["max"][2], abs=1e-4)
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)


def test_macro_relative_layout_negative_gap_raises(
    clean_scene,
    modeling_handler,
    macro_handler,
):
    table_name = "LayoutErrorBase"
    part_name = "LayoutErrorPart"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=table_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=part_name, size=1.0, location=[2, 2, 2])

        with pytest.raises(ValueError, match="gap must be >= 0"):
            macro_handler.relative_layout(
                moving_object=part_name,
                reference_object=table_name,
                contact_axis="Z",
                gap=-0.01,
            )
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)
