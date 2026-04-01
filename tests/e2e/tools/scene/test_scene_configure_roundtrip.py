"""
Blender-backed read/apply/read regression coverage for scene_configure (TASK-118).
"""

from __future__ import annotations

import pytest
from server.application.tool_handlers.scene_handler import SceneToolHandler


@pytest.fixture
def scene_handler(rpc_client):
    """Provides a scene handler instance using shared RPC client."""
    return SceneToolHandler(rpc_client)


def _assert_render_snapshot_equal(actual: dict, expected: dict) -> None:
    assert actual["render_engine"] == expected["render_engine"]
    assert actual["resolution"] == expected["resolution"]
    assert actual["filepath"] == expected["filepath"]
    assert actual["use_file_extension"] == expected["use_file_extension"]
    assert actual["film_transparent"] == expected["film_transparent"]
    assert actual["image_settings"] == expected["image_settings"]
    assert actual["cycles"] == expected["cycles"]


def _assert_color_snapshot_equal(actual: dict, expected: dict) -> None:
    assert actual["display_device"] == expected["display_device"]
    assert actual["view_transform"] == expected["view_transform"]
    assert actual["look"] == expected["look"]
    assert actual["exposure"] == pytest.approx(expected["exposure"], abs=1e-4)
    assert actual["gamma"] == pytest.approx(expected["gamma"], abs=1e-4)
    assert actual["use_curve_mapping"] == expected["use_curve_mapping"]
    assert actual["sequencer_color_space"] == expected["sequencer_color_space"]


def _assert_world_snapshot_equal(actual: dict, expected: dict) -> None:
    assert actual["world_name"] == expected["world_name"]
    assert actual["use_nodes"] == expected["use_nodes"]
    assert actual["node_tree_name"] == expected["node_tree_name"]
    assert actual["node_graph_reference"] == expected["node_graph_reference"]
    assert actual["node_graph_handoff"] == expected["node_graph_handoff"]

    expected_color = expected["color"]
    actual_color = actual["color"]
    if expected_color is None:
        assert actual_color is None
    else:
        assert actual_color == pytest.approx(expected_color, abs=1e-4)

    expected_background = expected["background"]
    actual_background = actual["background"]
    if expected_background is None:
        assert actual_background is None
    else:
        assert actual_background["node_name"] == expected_background["node_name"]
        assert actual_background["strength"] == pytest.approx(expected_background["strength"], abs=1e-4)
        assert actual_background["color"] == pytest.approx(expected_background["color"], abs=1e-4)


def test_scene_configure_render_and_color_management_roundtrip(scene_handler):
    try:
        baseline_render = scene_handler.inspect_render_settings()
        baseline_color = scene_handler.inspect_color_management()

        modified_render = {
            "render_engine": "CYCLES" if baseline_render["render_engine"] != "CYCLES" else "BLENDER_EEVEE_NEXT",
            "resolution": {
                "x": baseline_render["resolution"]["x"],
                "y": baseline_render["resolution"]["y"],
                "percentage": 50 if baseline_render["resolution"]["percentage"] != 50 else 100,
            },
            "film_transparent": not bool(baseline_render["film_transparent"]),
            "cycles": {
                "device": baseline_render["cycles"]["device"] or "CPU",
                "samples": 8 if baseline_render["cycles"]["samples"] != 8 else 16,
                "preview_samples": 4 if baseline_render["cycles"]["preview_samples"] != 4 else 8,
            },
        }
        modified_color = {
            "exposure": float(baseline_color["exposure"]) + 0.5,
            "gamma": float(baseline_color["gamma"]) + 0.1,
            "use_curve_mapping": not bool(baseline_color["use_curve_mapping"]),
        }

        scene_handler.configure_render_settings(modified_render)
        scene_handler.configure_color_management(modified_color)

        changed_render = scene_handler.inspect_render_settings()
        changed_color = scene_handler.inspect_color_management()

        assert changed_render["render_engine"] == modified_render["render_engine"]
        assert changed_render["resolution"]["percentage"] == modified_render["resolution"]["percentage"]
        assert changed_render["film_transparent"] is modified_render["film_transparent"]
        assert changed_render["cycles"]["samples"] == modified_render["cycles"]["samples"]
        assert changed_color["exposure"] == pytest.approx(modified_color["exposure"], abs=1e-4)
        assert changed_color["gamma"] == pytest.approx(modified_color["gamma"], abs=1e-4)
        assert changed_color["use_curve_mapping"] is modified_color["use_curve_mapping"]

        scene_handler.configure_render_settings(baseline_render)
        scene_handler.configure_color_management(baseline_color)

        restored_render = scene_handler.inspect_render_settings()
        restored_color = scene_handler.inspect_color_management()

        _assert_render_snapshot_equal(restored_render, baseline_render)
        _assert_color_snapshot_equal(restored_color, baseline_color)
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
    finally:
        try:
            scene_handler.configure_render_settings(locals().get("baseline_render", {}))
        except Exception:
            pass
        try:
            scene_handler.configure_color_management(locals().get("baseline_color", {}))
        except Exception:
            pass


def test_scene_configure_world_roundtrip(scene_handler):
    try:
        baseline_world = scene_handler.inspect_world()
        if baseline_world["world_name"] is None:
            pytest.skip("Scene has no world assigned")

        modified_world = {
            "world_name": baseline_world["world_name"],
            "use_nodes": True,
            "color": [0.1, 0.2, 0.3],
            "background": {
                "strength": 0.75,
                "color": [0.05, 0.1, 0.15, 1.0],
            },
        }

        scene_handler.configure_world(modified_world)
        changed_world = scene_handler.inspect_world()

        assert changed_world["world_name"] == baseline_world["world_name"]
        assert changed_world["use_nodes"] is True
        assert changed_world["color"] == pytest.approx([0.1, 0.2, 0.3], abs=1e-4)
        assert changed_world["background"]["strength"] == pytest.approx(0.75, abs=1e-4)
        assert changed_world["node_graph_handoff"]["required"] is bool(changed_world["node_tree_name"])

        scene_handler.configure_world(baseline_world)
        restored_world = scene_handler.inspect_world()

        _assert_world_snapshot_equal(restored_world, baseline_world)
    except RuntimeError as e:
        pytest.skip(f"Blender not available: {e}")
    finally:
        try:
            scene_handler.configure_world(locals().get("baseline_world", {}))
        except Exception:
            pass
