"""Blender-backed E2E tests for macro_finish_form."""

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


def test_macro_finish_form_rounded_housing_adds_bevel_and_subsurf(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    target_name = "FinishHousing"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=target_name, size=2.0, location=[0, 0, 0])

        result = macro_handler.finish_form(
            target_object=target_name,
            preset="rounded_housing",
            bevel_width=0.03,
            bevel_segments=3,
            subsurf_levels=2,
        )

        assert result["status"] == "success"
        assert result["macro_name"] == "macro_finish_form"

        modifiers = scene_handler.inspect_modifiers(target_name)
        object_entry = next(item for item in modifiers["objects"] if item["name"] == target_name)
        modifier_types = [item["type"] for item in object_entry["modifiers"]]

        assert "BEVEL" in modifier_types
        assert "SUBSURF" in modifier_types
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)


def test_macro_finish_form_shell_thicken_adds_solidify(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    target_name = "FinishShell"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=target_name, size=2.0, location=[0, 0, 0])

        result = macro_handler.finish_form(
            target_object=target_name,
            preset="shell_thicken",
            thickness=0.08,
            solidify_offset=-1.0,
        )

        assert result["status"] == "success"

        modifiers = scene_handler.inspect_modifiers(target_name)
        object_entry = next(item for item in modifiers["objects"] if item["name"] == target_name)
        solidify = next(item for item in object_entry["modifiers"] if item["type"] == "SOLIDIFY")

        assert solidify["thickness"] == pytest.approx(0.08, abs=1e-4)
        assert solidify["offset"] == pytest.approx(-1.0, abs=1e-4)
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)


def test_macro_finish_form_invalid_panel_override_raises(
    clean_scene,
    modeling_handler,
    macro_handler,
):
    target_name = "FinishPanel"

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=target_name, size=2.0, location=[0, 0, 0])

        with pytest.raises(ValueError, match="thickness override"):
            macro_handler.finish_form(
                target_object=target_name,
                preset="panel_finish",
                thickness=0.05,
            )
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)
