"""Blender-backed E2E tests for macro_adjust_tail_arc."""

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


def test_macro_adjust_tail_arc_repositions_tail_chain_along_arc(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
):
    names = ["TailArc_01", "TailArc_02", "TailArc_03"]

    try:
        for index, name in enumerate(names):
            modeling_handler.create_primitive(primitive_type="CUBE", name=name, size=0.4, location=[float(index), 0.0, 0.0])

        result = macro_handler.adjust_tail_arc(
            segment_objects=names,
            rotation_axis="Y",
            total_angle=60.0,
            direction="positive",
            apply_rotation=True,
        )

        assert result["status"] == "success"
        assert result["macro_name"] == "macro_adjust_tail_arc"
        assert result["objects_modified"] == names[1:]
        assert result["requires_followup"] is True

        tail_02 = scene_handler.get_bounding_box(names[1])
        tail_03 = scene_handler.get_bounding_box(names[2])

        assert tail_02["center"] == pytest.approx([0.866025, 0.0, -0.5], abs=1e-4)
        assert tail_03["center"] == pytest.approx([1.366025, 0.0, -1.366025], abs=1e-4)
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)
