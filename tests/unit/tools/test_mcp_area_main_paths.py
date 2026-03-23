from __future__ import annotations

from unittest.mock import MagicMock


def _direct_route(tool_name, params, direct_executor, prompt=None):
    return direct_executor()


def test_armature_create_main_path_delegates_to_handler(monkeypatch):
    calls = {}

    class Handler:
        def create(self, **kwargs):
            calls["kwargs"] = kwargs
            return "Created armature 'Rig'"

    monkeypatch.setattr("server.adapters.mcp.areas.armature.get_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.armature.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.armature import armature_create

    result = armature_create(MagicMock(), name="Rig", location=[1, 2, 3], bone_name="Root", bone_length=2.0)

    assert result == "Created armature 'Rig'"
    assert calls["kwargs"] == {
        "name": "Rig",
        "location": [1, 2, 3],
        "bone_name": "Root",
        "bone_length": 2.0,
    }


def test_bake_normal_map_main_path_delegates_to_handler(monkeypatch):
    calls = {}

    class Handler:
        def bake_normal_map(self, **kwargs):
            calls["kwargs"] = kwargs
            return "Baked normal map"

    monkeypatch.setattr("server.adapters.mcp.areas.baking.get_baking_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.baking.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.baking import bake_normal_map

    result = bake_normal_map(MagicMock(), object_name="LowPoly", output_path="/tmp/normal.png", resolution=2048)

    assert result == "Baked normal map"
    assert calls["kwargs"]["object_name"] == "LowPoly"
    assert calls["kwargs"]["resolution"] == 2048


def test_curve_create_main_path_delegates_to_handler(monkeypatch):
    calls = {}

    class Handler:
        def create_curve(self, curve_type, location):
            calls["args"] = (curve_type, location)
            return "Created BEZIER curve"

    monkeypatch.setattr("server.adapters.mcp.areas.curve.get_curve_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.curve.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.curve import curve_create

    result = curve_create(MagicMock(), curve_type="BEZIER", location=[0, 1, 2])

    assert result == "Created BEZIER curve"
    assert calls["args"] == ("BEZIER", [0, 1, 2])


def test_lattice_create_parses_string_location_and_delegates(monkeypatch):
    calls = {}

    class Handler:
        def lattice_create(self, **kwargs):
            calls["kwargs"] = kwargs
            return "Created lattice"

    monkeypatch.setattr("server.adapters.mcp.areas.lattice.get_lattice_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.lattice.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.lattice import lattice_create

    result = lattice_create(MagicMock(), name="Cage", location="[1, 2, 3]", points_w=4)

    assert result == "Created lattice"
    assert calls["kwargs"]["location"] == [1.0, 2.0, 3.0]
    assert calls["kwargs"]["points_w"] == 4


def test_modeling_create_primitive_parses_string_vectors_and_delegates(monkeypatch):
    calls = {}

    class Handler:
        def create_primitive(self, primitive_type, radius, size, location, rotation, name):
            calls["args"] = (primitive_type, radius, size, location, rotation, name)
            return "Created Cube named 'Block'"

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_modeling_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.modeling.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.modeling import modeling_create_primitive

    result = modeling_create_primitive(
        MagicMock(),
        primitive_type="Cube",
        location="[1, 2, 3]",
        rotation="[0, 0, 1.57]",
        name="Block",
    )

    assert result == "Created Cube named 'Block'"
    assert calls["args"] == ("Cube", 1.0, 2.0, [1.0, 2.0, 3.0], [0.0, 0.0, 1.57], "Block")


def test_sculpt_auto_main_path_delegates_to_handler(monkeypatch):
    calls = {}

    class Handler:
        def auto_sculpt(self, **kwargs):
            calls["kwargs"] = kwargs
            return "Applied smooth sculpt"

    monkeypatch.setattr("server.adapters.mcp.areas.sculpt.get_sculpt_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.sculpt.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.sculpt import sculpt_auto

    result = sculpt_auto(MagicMock(), operation="smooth", object_name="Head", strength=0.6, iterations=2)

    assert result == "Applied smooth sculpt"
    assert calls["kwargs"]["object_name"] == "Head"
    assert calls["kwargs"]["iterations"] == 2


def test_text_to_mesh_main_path_delegates_to_handler(monkeypatch):
    calls = {}

    class Handler:
        def to_mesh(self, **kwargs):
            calls["kwargs"] = kwargs
            return "Converted text to mesh"

    monkeypatch.setattr("server.adapters.mcp.areas.text.get_text_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.text.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.text import text_to_mesh

    result = text_to_mesh(MagicMock(), object_name="Logo", keep_original=True)

    assert result == "Converted text to mesh"
    assert calls["kwargs"] == {"object_name": "Logo", "keep_original": True}


def test_uv_list_maps_formats_main_path_payload(monkeypatch):
    class Handler:
        def list_maps(self, **kwargs):
            return {
                "object_name": "Wall",
                "uv_map_count": 2,
                "uv_maps": [
                    {
                        "name": "UVMap",
                        "is_active": True,
                        "is_active_render": True,
                        "uv_loop_count": 24,
                        "island_count": 3,
                    },
                    {
                        "name": "Lightmap",
                        "is_active": False,
                        "is_active_render": False,
                        "uv_loop_count": 24,
                    },
                ],
            }

    monkeypatch.setattr("server.adapters.mcp.areas.uv.get_uv_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.uv.ctx_info", lambda ctx, message: None)
    monkeypatch.setattr("server.adapters.mcp.areas.uv.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.uv import uv_list_maps

    result = uv_list_maps(MagicMock(), object_name="Wall", include_island_counts=True)

    assert "Object: Wall" in result
    assert "UV Maps (2):" in result
    assert "UVMap [active, active_render]" in result
    assert "UV loops: 24" in result
    assert "Islands: 3" in result
    assert "Lightmap" in result
