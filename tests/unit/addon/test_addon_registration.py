from __future__ import annotations

from unittest.mock import ANY, MagicMock


class _DummyHandler:
    def __getattr__(self, _name):
        return lambda *args, **kwargs: None


class _SceneHandlerProbeBase:
    last_instance = None

    def __init__(self):
        type(self).last_instance = self


def _assert_bound_method(method, owner, name):
    assert getattr(method, "__self__", None) is owner
    assert getattr(method, "__func__", None) is getattr(type(owner), name)


def test_register_wires_handlers_and_starts_rpc(monkeypatch):
    import blender_addon
    from blender_addon.application.handlers.scene import SceneHandler as RealSceneHandler

    rpc_server = MagicMock()
    fake_bpy = MagicMock()

    monkeypatch.setattr(blender_addon, "bpy", fake_bpy)
    monkeypatch.setattr(blender_addon, "rpc_server", rpc_server)

    class SceneHandlerProbe(_SceneHandlerProbeBase, RealSceneHandler):
        pass

    monkeypatch.setattr(blender_addon, "SceneHandler", SceneHandlerProbe)

    for handler_name in [
        "ModelingHandler",
        "MeshHandler",
        "CollectionHandler",
        "MaterialHandler",
        "UVHandler",
        "CurveHandler",
        "SystemHandler",
        "SculptHandler",
        "BakingHandler",
        "LatticeHandler",
        "ExtractionHandler",
        "TextHandler",
        "ArmatureHandler",
    ]:
        monkeypatch.setattr(blender_addon, handler_name, _DummyHandler)

    blender_addon.register()

    scene_handler = SceneHandlerProbe.last_instance
    assert scene_handler is not None

    expected_scene_methods = {
        "scene.list_objects": "list_objects",
        "scene.delete_object": "delete_object",
        "scene.clean_scene": "clean_scene",
        "scene.duplicate_object": "duplicate_object",
        "scene.set_active_object": "set_active_object",
        "scene.get_mode": "get_mode",
        "scene.list_selection": "list_selection",
        "scene.inspect_object": "inspect_object",
        "scene.snapshot_state": "snapshot_state",
        "scene.inspect_material_slots": "inspect_material_slots",
        "scene.inspect_mesh_topology": "inspect_mesh_topology",
        "scene.inspect_modifiers": "inspect_modifiers",
        "scene.inspect_render_settings": "inspect_render_settings",
        "scene.inspect_color_management": "inspect_color_management",
        "scene.inspect_world": "inspect_world",
        "scene.configure_render_settings": "configure_render_settings",
        "scene.configure_color_management": "configure_color_management",
        "scene.configure_world": "configure_world",
        "scene.get_constraints": "get_constraints",
        "scene.get_viewport": "get_viewport",
        "scene.create_light": "create_light",
        "scene.create_camera": "create_camera",
        "scene.create_empty": "create_empty",
        "scene.set_mode": "set_mode",
        "scene.rename_object": "rename_object",
        "scene.hide_object": "hide_object",
        "scene.show_all_objects": "show_all_objects",
        "scene.isolate_object": "isolate_object",
        "scene.camera_orbit": "camera_orbit",
        "scene.camera_focus": "camera_focus",
        "scene.get_view_state": "get_view_state",
        "scene.restore_view_state": "restore_view_state",
        "scene.set_standard_view": "set_standard_view",
        "scene.get_view_diagnostics": "get_view_diagnostics",
        "scene.get_custom_properties": "get_custom_properties",
        "scene.set_custom_property": "set_custom_property",
        "scene.get_hierarchy": "get_hierarchy",
        "scene.get_bounding_box": "get_bounding_box",
        "scene.get_origin_info": "get_origin_info",
        "scene.measure_distance": "measure_distance",
        "scene.measure_dimensions": "measure_dimensions",
        "scene.measure_gap": "measure_gap",
        "scene.measure_alignment": "measure_alignment",
        "scene.measure_overlap": "measure_overlap",
        "scene.assert_contact": "assert_contact",
        "scene.assert_dimensions": "assert_dimensions",
        "scene.assert_containment": "assert_containment",
        "scene.assert_symmetry": "assert_symmetry",
        "scene.assert_proportion": "assert_proportion",
    }
    registered_scene_handlers = {
        args[0]: args[1]
        for args, _kwargs in rpc_server.register_handler.call_args_list
        if args and args[0].startswith("scene.")
    }

    assert set(registered_scene_handlers) == set(expected_scene_methods)
    for rpc_name, method_name in expected_scene_methods.items():
        _assert_bound_method(registered_scene_handlers[rpc_name], scene_handler, method_name)

    background_handlers = {args[0]: args[1] for args, _kwargs in rpc_server.register_background_handler.call_args_list}
    _assert_bound_method(background_handlers["scene.get_viewport"], scene_handler, "get_viewport")
    rpc_server.register_background_handler.assert_any_call("export.glb", ANY)
    rpc_server.register_background_handler.assert_any_call("extraction.render_angles", ANY)
    rpc_server.start.assert_called_once()


def test_unregister_stops_rpc_server(monkeypatch):
    import blender_addon

    rpc_server = MagicMock()
    monkeypatch.setattr(blender_addon, "bpy", MagicMock())
    monkeypatch.setattr(blender_addon, "rpc_server", rpc_server)

    blender_addon.unregister()

    rpc_server.stop.assert_called_once()


def test_register_in_mock_mode_does_not_start_rpc(monkeypatch, capsys):
    import blender_addon

    rpc_server = MagicMock()
    monkeypatch.setattr(blender_addon, "bpy", None)
    monkeypatch.setattr(blender_addon, "rpc_server", rpc_server)

    blender_addon.register()

    assert "Mock registration" in capsys.readouterr().out
    rpc_server.start.assert_not_called()
