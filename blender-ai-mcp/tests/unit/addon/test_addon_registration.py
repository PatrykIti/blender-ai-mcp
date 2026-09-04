from __future__ import annotations

from unittest.mock import ANY, MagicMock


class _DummyHandler:
    def __getattr__(self, _name):
        return lambda *args, **kwargs: None


def test_register_wires_handlers_and_starts_rpc(monkeypatch):
    import blender_addon

    rpc_server = MagicMock()
    fake_bpy = MagicMock()

    monkeypatch.setattr(blender_addon, "bpy", fake_bpy)
    monkeypatch.setattr(blender_addon, "rpc_server", rpc_server)

    for handler_name in [
        "SceneHandler",
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

    rpc_server.register_handler.assert_any_call("scene.list_objects", ANY)
    rpc_server.register_background_handler.assert_any_call("scene.get_viewport", ANY)
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
