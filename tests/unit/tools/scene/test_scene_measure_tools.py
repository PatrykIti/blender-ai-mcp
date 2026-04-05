from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest
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
    assert gap["measurement_basis"] == "bounding_box"
    assert gap["axis_gap"] == {"x": 1.0, "y": 0.0, "z": 0.0}
    assert alignment["is_aligned"] is True
    assert alignment["aligned_axes"] == ["Y", "Z"]
    assert overlap_result["overlaps"] is True
    assert overlap_result["relation"] == "overlap"
    assert overlap_result["measurement_basis"] == "bounding_box"
    assert overlap_result["overlap_dimensions"] == [0.5, 0.5, 0.5]
    assert overlap_result["overlap_volume"] == 0.125


def test_measure_gap_and_overlap_prefer_mesh_surface_semantics_over_bbox_touching(monkeypatch):
    mock_bpy = sys.modules["bpy"]
    head = _make_box("Head", (-1.0, -1.0, -1.0), (1.0, 1.0, 1.0), (0.0, 0.0, 0.0))
    eye = _make_box("Eye", (-0.2, 1.0, -0.2), (0.2, 1.4, 0.2), (0.0, 1.2, 0.0))
    head.type = "MESH"
    eye.type = "MESH"

    mock_bpy.data.objects = MagicMock()
    mock_bpy.data.objects.get.side_effect = {"Head": head, "Eye": eye}.get

    handler = SceneHandler()

    def _fake_mesh_contact(source_obj, target_obj, tolerance, bbox_overlap_volume=0.0):
        assert source_obj.name == "Head"
        assert target_obj.name == "Eye"
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

    gap = handler.measure_gap("Head", "Eye")
    overlap_result = handler.measure_overlap("Head", "Eye")

    assert gap["measurement_basis"] == "mesh_surface"
    assert gap["relation"] == "separated"
    assert gap["bbox_relation"] == "contact"
    assert gap["nearest_points"]["from_object"] == [0.0, 0.318, 0.0]
    assert overlap_result["measurement_basis"] == "mesh_surface"
    assert overlap_result["relation"] == "disjoint"
    assert overlap_result["touching"] is False
    assert overlap_result["bbox_touching"] is True
    assert overlap_result["surface_gap"] == 0.051


def test_measure_gap_preserves_mesh_overlap_semantics_when_bbox_overlap_exists(monkeypatch):
    mock_bpy = sys.modules["bpy"]
    left = _make_box("Left", (0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.5, 0.5, 0.5))
    overlap = _make_box("Overlap", (0.5, 0.0, 0.0), (1.5, 1.0, 1.0), (1.0, 0.5, 0.5))
    left.type = "MESH"
    overlap.type = "MESH"

    mock_bpy.data.objects = MagicMock()
    mock_bpy.data.objects.get.side_effect = {"Left": left, "Overlap": overlap}.get

    handler = SceneHandler()

    def _fake_mesh_contact(source_obj, target_obj, tolerance, bbox_overlap_volume=0.0):
        assert bbox_overlap_volume > 0.0
        return {
            "overlaps": True,
            "gap": 0.0,
            "axis_gap": [0.0, 0.0, 0.0],
            "relation": "overlapping",
            "nearest_points": None,
        }

    monkeypatch.setattr(handler, "_measure_mesh_surface_relation", _fake_mesh_contact)

    gap = handler.measure_gap("Left", "Overlap", tolerance=0.001)

    assert gap["measurement_basis"] == "mesh_surface"
    assert gap["relation"] == "overlapping"
    assert gap["bbox_relation"] == "overlapping"


@pytest.mark.parametrize(
    ("vertices", "triangles"),
    [
        ([], [MagicMock(vertices=(0, 1, 2))]),
        ([MagicMock(co=(0.0, 0.0, 0.0))], []),
    ],
    ids=["empty_vertices", "empty_triangles"],
)
def test_get_evaluated_mesh_data_clears_temp_mesh_on_empty_geometry(vertices, triangles):
    mock_bpy = sys.modules["bpy"]
    mock_bpy.context.evaluated_depsgraph_get.return_value = object()

    obj = MagicMock()
    obj.name = "SparseMesh"
    obj.type = "MESH"

    obj_eval = MagicMock()
    obj_eval.matrix_world = IdentityMatrix()
    obj_eval.to_mesh_clear = MagicMock()
    obj.evaluated_get.return_value = obj_eval

    mesh = MagicMock()
    mesh.vertices = vertices
    mesh.loop_triangles = triangles
    mesh.polygons = []
    obj_eval.to_mesh.return_value = mesh

    handler = SceneHandler()

    result = handler._get_evaluated_mesh_data(obj)

    assert result is None
    obj_eval.to_mesh_clear.assert_called_once_with()
