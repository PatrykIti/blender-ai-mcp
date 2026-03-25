from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from server.adapters.mcp.contracts.scene import SceneInspectResponseContract


def _direct_route(**kwargs):
    return kwargs["direct_executor"]()


def test_scene_list_objects_formats_output(monkeypatch):
    from server.adapters.mcp.areas.scene import scene_list_objects

    handler = MagicMock(unsafe=True)
    handler.list_objects.return_value = [{"name": "Cube"}, {"name": "Light"}]

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: handler)
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)
    monkeypatch.setattr("server.adapters.mcp.areas.scene.route_tool_call", _direct_route)

    result = scene_list_objects(MagicMock())

    assert "Cube" in result
    assert "Light" in result


def test_scene_duplicate_object_parses_translation_and_reports_error(monkeypatch):
    from server.adapters.mcp.areas.scene import scene_duplicate_object

    handler = MagicMock(unsafe=True)
    handler.duplicate_object.return_value = {"name": "Cube.001"}

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: handler)
    monkeypatch.setattr("server.adapters.mcp.areas.scene.route_tool_call", _direct_route)

    result = scene_duplicate_object(MagicMock(), name="Cube", translation="[1, 2, 3]")
    assert "Cube.001" in result
    handler.duplicate_object.assert_called_once_with("Cube", [1.0, 2.0, 3.0])

    error = scene_duplicate_object(MagicMock(), name="Cube", translation="invalid")
    assert "Invalid coordinate format" in error


def test_scene_inspect_supports_multiple_actions(monkeypatch):
    from server.adapters.mcp.areas.scene import scene_inspect

    monkeypatch.setattr("server.adapters.mcp.areas.scene.route_tool_call", _direct_route)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.scene._scene_inspect_object",
        lambda ctx, name: {"object_name": name, "type": "MESH"},
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.scene._scene_inspect_mesh_topology",
        lambda ctx, object_name, detailed: {"vertex_count": 8, "detailed": detailed},
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.scene._scene_inspect_modifiers",
        lambda ctx, object_name, include_disabled: {"modifier_count": 2},
    )

    object_result = asyncio.run(scene_inspect(MagicMock(), action="object", object_name="Cube"))
    topology_result = asyncio.run(scene_inspect(MagicMock(), action="topology", object_name="Cube", detailed=True))
    modifiers_result = asyncio.run(scene_inspect(MagicMock(), action="modifiers"))

    assert isinstance(object_result, SceneInspectResponseContract)
    assert object_result.payload["object_name"] == "Cube"
    assert topology_result.payload["vertex_count"] == 8
    assert modifiers_result.payload["modifier_count"] == 2


def test_scene_create_helpers_handle_parsing_and_errors(monkeypatch):
    from server.adapters.mcp.areas import scene as scene_area

    handler = MagicMock()
    handler.create_light.return_value = "light ok"
    handler.create_camera.return_value = "camera ok"
    handler.create_empty.return_value = "empty ok"

    monkeypatch.setattr(scene_area, "get_scene_handler", lambda: handler)
    monkeypatch.setattr(scene_area, "route_tool_call", _direct_route)

    assert scene_area._scene_create_light(MagicMock(), "SUN", color="[1, 0.5, 0.25]", location="[0,0,3]") == "light ok"
    assert scene_area._scene_create_camera(MagicMock(), "[0,0,5]", "[0,0,0]") == "camera ok"
    assert scene_area._scene_create_empty(MagicMock(), "PLAIN_AXES", location="[1,2,3]") == "empty ok"
    assert "Invalid coordinate format" in scene_area._scene_create_camera(MagicMock(), "invalid", "[0,0,0]")


def test_scene_state_and_utility_wrappers(monkeypatch):
    from server.adapters.mcp.areas import scene as scene_area

    handler = MagicMock(unsafe=True)
    handler.snapshot_state.return_value = {"snapshot": {"object_count": 1}, "hash": "abc12345"}
    handler.rename_object.return_value = "rename ok"
    handler.hide_object.return_value = "hide ok"
    handler.show_all_objects.return_value = "show ok"
    handler.isolate_object.return_value = "isolate ok"
    handler.camera_orbit.return_value = "orbit ok"
    handler.camera_focus.return_value = "focus ok"
    handler.get_custom_properties.return_value = {"properties": {"tag": "hero"}}
    handler.set_custom_property.return_value = "set property ok"
    handler.get_hierarchy.return_value = {"roots": [{"name": "Cube"}]}
    handler.get_bounding_box.return_value = {"min": [0, 0, 0], "max": [1, 1, 1]}
    handler.get_origin_info.return_value = {"origin_world": [0, 0, 0]}
    handler.measure_distance.return_value = {"distance": 2.0, "reference": "ORIGIN"}
    handler.measure_dimensions.return_value = {"dimensions": [1.0, 2.0, 3.0], "volume": 6.0}
    handler.measure_gap.return_value = {"gap": 0.5, "relation": "separated"}
    handler.measure_alignment.return_value = {"is_aligned": True, "aligned_axes": ["Y", "Z"]}
    handler.measure_overlap.return_value = {"overlaps": False, "relation": "disjoint"}
    handler.assert_contact.return_value = {
        "assertion": "scene_assert_contact",
        "passed": True,
        "subject": "Cube",
        "target": "Sphere",
        "actual": {"gap": 0.0, "relation": "contact"},
    }
    handler.assert_dimensions.return_value = {
        "assertion": "scene_assert_dimensions",
        "passed": False,
        "subject": "Cube",
        "actual": {"dimensions": [1.2, 2.0, 3.0]},
        "delta": {"x": 0.2, "y": 0.0, "z": 0.0},
    }

    monkeypatch.setattr(scene_area, "get_scene_handler", lambda: handler)
    monkeypatch.setattr(scene_area, "ctx_info", lambda ctx, message: None)
    monkeypatch.setattr(scene_area, "route_tool_call", _direct_route)

    snapshot = asyncio.run(scene_area.scene_snapshot_state(MagicMock()))
    assert snapshot.hash == "abc12345"

    assert scene_area.scene_rename_object(MagicMock(), "Cube", "Hero") == "rename ok"
    assert scene_area.scene_hide_object(MagicMock(), "Cube") == "hide ok"
    assert scene_area.scene_show_all_objects(MagicMock()) == "show ok"
    assert scene_area.scene_isolate_object(MagicMock(), ["Cube", "Sphere"]) == "isolate ok"
    assert scene_area.scene_camera_orbit(MagicMock()) == "orbit ok"
    assert scene_area.scene_camera_focus(MagicMock(), "Cube") == "focus ok"

    props = scene_area.scene_get_custom_properties(MagicMock(), object_name="Cube")
    assert props.properties["tag"] == "hero"
    assert scene_area.scene_set_custom_property(MagicMock(), "Cube", "tag", "hero") == "set property ok"
    assert asyncio.run(scene_area.scene_get_hierarchy(MagicMock())).payload["roots"][0]["name"] == "Cube"
    assert asyncio.run(scene_area.scene_get_bounding_box(MagicMock(), object_name="Cube")).payload["max"] == [1, 1, 1]
    assert asyncio.run(scene_area.scene_get_origin_info(MagicMock(), object_name="Cube")).payload["origin_world"] == [
        0,
        0,
        0,
    ]
    assert scene_area.scene_measure_distance(MagicMock(), from_object="Cube", to_object="Sphere").payload["distance"] == 2.0
    assert scene_area.scene_measure_dimensions(MagicMock(), object_name="Cube").payload["volume"] == 6.0
    assert scene_area.scene_measure_gap(MagicMock(), from_object="Cube", to_object="Sphere").payload["gap"] == 0.5
    assert (
        scene_area.scene_measure_alignment(MagicMock(), from_object="Cube", to_object="Sphere", axes=["Y", "Z"])
        .payload["is_aligned"]
        is True
    )
    assert (
        scene_area.scene_measure_overlap(MagicMock(), from_object="Cube", to_object="Sphere").payload["relation"]
        == "disjoint"
    )
    assert scene_area.scene_assert_contact(MagicMock(), from_object="Cube", to_object="Sphere").payload.passed is True
    assert (
        scene_area.scene_assert_dimensions(MagicMock(), object_name="Cube", expected_dimensions="[1, 2, 3]")
        .payload.delta["x"]
        == 0.2
    )
