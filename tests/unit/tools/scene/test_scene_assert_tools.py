from __future__ import annotations

import sys
from unittest.mock import MagicMock

from blender_addon.application.handlers.scene import SceneHandler

from tests.unit.tools.scene.test_scene_measure_tools import _make_box


def test_assert_contact_uses_gap_and_overlap_semantics():
    mock_bpy = sys.modules["bpy"]
    left = _make_box("Left", (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.5, 0.5, 0.5))
    right = _make_box("Right", (1.0, 0.0, 0.0), (2.0, 1.0, 1.0), (1.5, 0.5, 0.5))
    overlap = _make_box("Overlap", (0.5, 0.0, 0.0), (1.5, 1.0, 1.0), (1.0, 0.5, 0.5))
    objects = {"Left": left, "Right": right, "Overlap": overlap}

    mock_bpy.data.objects = MagicMock()
    mock_bpy.data.objects.get.side_effect = objects.get

    handler = SceneHandler()

    touching = handler.assert_contact("Left", "Right", max_gap=0.001)
    rejected_overlap = handler.assert_contact("Left", "Overlap", max_gap=0.001, allow_overlap=False)
    allowed_overlap = handler.assert_contact("Left", "Overlap", max_gap=0.001, allow_overlap=True)

    assert touching["passed"] is True
    assert touching["actual"]["relation"] == "contact"
    assert touching["details"]["measurement_basis"] == "bounding_box"
    assert rejected_overlap["passed"] is False
    assert rejected_overlap["details"]["overlap_rejected"] is True
    assert allowed_overlap["passed"] is True


def test_assert_contact_can_fail_when_mesh_surface_gap_exists_despite_bbox_touching(monkeypatch):
    mock_bpy = sys.modules["bpy"]
    head = _make_box("Head", (-1.0, -1.0, -1.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
    eye = _make_box("Eye", (-0.2, 1.0, -0.2), (0.2, 1.4, 0.2), (0.0, 1.2, 0.0))
    head.type = "MESH"
    eye.type = "MESH"
    mock_bpy.data.objects = MagicMock()
    mock_bpy.data.objects.get.side_effect = {"Head": head, "Eye": eye}.get

    handler = SceneHandler()

    def _fake_mesh_contact(source_obj, target_obj, tolerance, bbox_overlap_volume=0.0):
        return {
            "overlaps": False,
            "gap": 0.051,
            "axis_gap": [0.0, 0.051, 0.0],
            "relation": "separated",
            "nearest_points": {
                "from_object": [0.0, 0.318, 0.0],
                "to_object": [0.0, 0.369, 0.0],
            },
        }

    monkeypatch.setattr(handler, "_measure_mesh_surface_relation", _fake_mesh_contact)

    result = handler.assert_contact("Head", "Eye", max_gap=0.001, allow_overlap=False)

    assert result["passed"] is False
    assert result["actual"]["relation"] == "separated"
    assert result["details"]["measurement_basis"] == "mesh_surface"
    assert result["details"]["bbox_relation"] == "contact"


def test_assert_dimensions_compares_expected_vector_with_tolerance():
    mock_bpy = sys.modules["bpy"]
    cube = _make_box("Cube", (0.0, 0.0, 0.0), (2.1, 2.0, 2.0), (0.0, 0.0, 0.0))
    mock_bpy.data.objects = MagicMock()
    mock_bpy.data.objects.get.side_effect = {"Cube": cube}.get

    handler = SceneHandler()

    failing = handler.assert_dimensions("Cube", [2.0, 2.0, 2.0], tolerance=0.01)
    passing = handler.assert_dimensions("Cube", [2.0, 2.0, 2.0], tolerance=0.11)

    assert failing["passed"] is False
    assert failing["delta"]["x"] == 0.1
    assert failing["details"]["failed_axes"] == ["X"]
    assert passing["passed"] is True


def test_assert_containment_symmetry_and_proportion_cover_spatial_relationships():
    mock_bpy = sys.modules["bpy"]
    inner = _make_box("Inner", (0.2, 0.2, 0.2), (0.8, 0.8, 0.8), (0.5, 0.5, 0.5))
    outer = _make_box("Outer", (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.5, 0.5, 0.5))
    left = _make_box("Left", (-2.5, -1.0, -1.0), (-1.5, 1.0, 1.0), (-2.0, 0.0, 0.0))
    right = _make_box("Right", (1.5, -1.0, -1.0), (2.5, 1.0, 1.0), (2.0, 0.0, 0.0))
    rect = _make_box("Rect", (0.0, 0.0, 0.0), (4.0, 2.0, 1.0), (0.0, 0.0, 0.0))
    objects = {"Inner": inner, "Outer": outer, "Left": left, "Right": right, "Rect": rect}

    mock_bpy.data.objects = MagicMock()
    mock_bpy.data.objects.get.side_effect = objects.get

    handler = SceneHandler()

    containment = handler.assert_containment("Inner", "Outer", min_clearance=0.1, tolerance=0.0001)
    symmetry = handler.assert_symmetry("Left", "Right", axis="X", mirror_coordinate=0.0, tolerance=0.0001)
    single_object_proportion = handler.assert_proportion(
        "Rect",
        axis_a="X",
        axis_b="Y",
        expected_ratio=2.0,
        tolerance=0.0001,
    )

    assert containment["passed"] is True
    assert containment["actual"]["min_clearance"] == 0.2
    assert symmetry["passed"] is True
    assert symmetry["delta"]["mirror_axis"] == 0.0
    assert single_object_proportion["passed"] is True
    assert single_object_proportion["actual"]["ratio"] == 2.0
