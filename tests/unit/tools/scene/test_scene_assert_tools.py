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
    assert rejected_overlap["passed"] is False
    assert rejected_overlap["details"]["overlap_rejected"] is True
    assert allowed_overlap["passed"] is True


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
