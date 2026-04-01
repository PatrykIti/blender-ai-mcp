from __future__ import annotations

import sys
from unittest.mock import MagicMock

from blender_addon.application.handlers.scene import SceneHandler


class IdentityMatrix:
    def __matmul__(self, other):
        vector = sys.modules["mathutils"].Vector
        return vector([other[i] for i in range(3)])


def _make_box(name: str, min_corner: tuple[float, float, float], max_corner: tuple[float, float, float], origin):
    vector = sys.modules["mathutils"].Vector
    obj = MagicMock()
    obj.name = name
    obj.bound_box = [
        (min_corner[0], min_corner[1], min_corner[2]),
        (max_corner[0], min_corner[1], min_corner[2]),
        (max_corner[0], max_corner[1], min_corner[2]),
        (min_corner[0], max_corner[1], min_corner[2]),
        (min_corner[0], min_corner[1], max_corner[2]),
        (max_corner[0], min_corner[1], max_corner[2]),
        (max_corner[0], max_corner[1], max_corner[2]),
        (min_corner[0], max_corner[1], max_corner[2]),
    ]
    obj.matrix_world = IdentityMatrix()
    obj.location = vector(origin)
    return obj


def test_measure_distance_and_dimensions_use_structured_truth_values():
    mock_bpy = sys.modules["bpy"]
    cube = _make_box("Cube", (0.0, 0.0, 0.0), (2.0, 4.0, 6.0), (0.0, 0.0, 0.0))
    sphere = _make_box("Sphere", (5.0, 0.0, 0.0), (7.0, 2.0, 2.0), (3.0, 4.0, 0.0))
    objects = {"Cube": cube, "Sphere": sphere}

    mock_bpy.data.objects = MagicMock()
    mock_bpy.data.objects.get.side_effect = objects.get

    handler = SceneHandler()

    distance = handler.measure_distance("Cube", "Sphere", reference="ORIGIN")
    dimensions = handler.measure_dimensions("Cube")

    assert distance["distance"] == 5.0
    assert distance["delta"] == [3.0, 4.0, 0.0]
    assert dimensions["dimensions"] == [2.0, 4.0, 6.0]
    assert dimensions["volume"] == 48.0


def test_measure_gap_alignment_and_overlap_classify_bbox_relationships():
    mock_bpy = sys.modules["bpy"]
    base = _make_box("Base", (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.5, 0.5, 0.5))
    separated = _make_box("Separated", (2.0, 0.0, 0.0), (3.0, 1.0, 1.0), (2.5, 0.5, 0.5))
    overlap = _make_box("Overlap", (0.5, 0.5, 0.5), (1.5, 1.5, 1.5), (1.0, 1.0, 1.0))
    objects = {"Base": base, "Separated": separated, "Overlap": overlap}

    mock_bpy.data.objects = MagicMock()
    mock_bpy.data.objects.get.side_effect = objects.get

    handler = SceneHandler()

    gap = handler.measure_gap("Base", "Separated")
    alignment = handler.measure_alignment("Base", "Separated", axes=["Y", "Z"], reference="CENTER")
    overlap_result = handler.measure_overlap("Base", "Overlap")

    assert gap["gap"] == 1.0
    assert gap["relation"] == "separated"
    assert gap["axis_gap"] == {"x": 1.0, "y": 0.0, "z": 0.0}
    assert alignment["is_aligned"] is True
    assert alignment["aligned_axes"] == ["Y", "Z"]
    assert overlap_result["overlaps"] is True
    assert overlap_result["relation"] == "overlap"
    assert overlap_result["overlap_dimensions"] == [0.5, 0.5, 0.5]
    assert overlap_result["overlap_volume"] == 0.125
