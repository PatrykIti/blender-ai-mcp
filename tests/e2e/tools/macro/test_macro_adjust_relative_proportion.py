"""Blender-backed E2E tests for macro_adjust_relative_proportion."""

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


def test_macro_adjust_relative_proportion_repairs_ratio_by_scaling_primary(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    head_name = "ProportionHead"
    body_name = "ProportionBody"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=head_name, size=1.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.0, location=[0, 0, -1.5])

        result = macro_handler.adjust_relative_proportion(
            primary_object=head_name,
            reference_object=body_name,
            expected_ratio=0.4,
            primary_axis="X",
            reference_axis="X",
            scale_target="primary",
            max_scale_delta=0.5,
        )

        assert result["status"] == "success"
        assert result["macro_name"] == "macro_adjust_relative_proportion"
        assert head_name in result["objects_modified"]
        assert result["requires_followup"] is True

        proportion = scene_handler.assert_proportion(
            head_name,
            axis_a="X",
            expected_ratio=0.4,
            reference_object=body_name,
            reference_axis="X",
            tolerance=0.01,
            world_space=True,
        )

        assert proportion["passed"] is True
        assert proportion["actual"]["ratio"] == pytest.approx(0.4, abs=1e-3)
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)


def test_macro_adjust_relative_proportion_blocks_when_scale_delta_too_large(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    head_name = "ProportionBlockedHead"
    body_name = "ProportionBlockedBody"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=head_name, size=1.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.0, location=[0, 0, -1.5])

        before = scene_handler.inspect_object(head_name)

        result = macro_handler.adjust_relative_proportion(
            primary_object=head_name,
            reference_object=body_name,
            expected_ratio=0.2,
            scale_target="primary",
            max_scale_delta=0.1,
        )

        after = scene_handler.inspect_object(head_name)

        assert result["status"] == "blocked"
        assert before["scale"] == pytest.approx(after["scale"], abs=1e-4)
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)
