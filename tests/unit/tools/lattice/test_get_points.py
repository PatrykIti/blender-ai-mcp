from unittest.mock import MagicMock

import bpy

from blender_addon.application.handlers.lattice import LatticeHandler


def test_lattice_get_points():
    handler = LatticeHandler()

    lattice_data = MagicMock()
    lattice_data.points_u = 2
    lattice_data.points_v = 2
    lattice_data.points_w = 2
    lattice_data.interpolation_type_u = "KEY_LINEAR"
    lattice_data.interpolation_type_v = "KEY_LINEAR"
    lattice_data.interpolation_type_w = "KEY_LINEAR"

    point_a = MagicMock()
    point_a.co = [0.0, 0.0, 0.0]
    point_a.co_deform = [0.0, 0.0, 0.0]
    point_b = MagicMock()
    point_b.co = [1.0, 0.0, 0.0]
    point_b.co_deform = [1.0, 0.0, 0.0]

    lattice_data.points = [point_a, point_b]

    lattice_obj = MagicMock()
    lattice_obj.name = "Lattice"
    lattice_obj.type = "LATTICE"
    lattice_obj.data = lattice_data

    bpy.data.objects = {"Lattice": lattice_obj}

    result = handler.get_points("Lattice")

    assert result["points_u"] == 2
    assert result["point_count"] == 2
    assert result["points"][1]["co"] == [1.0, 0.0, 0.0]
