from unittest.mock import MagicMock

import bpy

from blender_addon.application.handlers.curve import CurveHandler


def test_curve_get_data_bezier():
    handler = CurveHandler()

    curve_data = MagicMock()
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 12
    curve_data.resolution_v = 0
    curve_data.render_resolution_u = 64
    curve_data.render_resolution_v = 0
    curve_data.bevel_depth = 0.1
    curve_data.bevel_resolution = 3
    curve_data.extrude = 0.0
    curve_data.fill_mode = "FULL"
    curve_data.use_fill_caps = True
    curve_data.bevel_object = None
    curve_data.taper_object = None

    point = MagicMock()
    point.co = [0.0, 0.0, 0.0]
    point.handle_left = [-1.0, 0.0, 0.0]
    point.handle_right = [1.0, 0.0, 0.0]
    point.handle_left_type = "AUTO"
    point.handle_right_type = "AUTO"
    point.handle_type = "FREE"
    point.radius = 1.0
    point.tilt = 0.0
    point.weight_softbody = 0.5

    spline = MagicMock()
    spline.type = "BEZIER"
    spline.use_cyclic_u = True
    spline.use_cyclic_v = False
    spline.order_u = None
    spline.order_v = None
    spline.resolution_u = 12
    spline.resolution_v = 0
    spline.tilt_interpolation = "LINEAR"
    spline.radius_interpolation = "LINEAR"
    spline.bezier_points = [point]

    curve_data.splines = [spline]

    obj = MagicMock()
    obj.name = "BezierCurve"
    obj.type = "CURVE"
    obj.data = curve_data

    bpy.data.objects = {"BezierCurve": obj}

    result = handler.get_data("BezierCurve")

    assert result["object_name"] == "BezierCurve"
    assert result["splines"][0]["type"] == "BEZIER"
    assert result["splines"][0]["bezier_points"][0]["handle_left_type"] == "AUTO"
