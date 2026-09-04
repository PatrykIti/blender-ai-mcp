from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest


def _direct_route(**kwargs):
    return kwargs["direct_executor"]()


@pytest.mark.parametrize(
    ("fn_name", "handler_method", "kwargs"),
    [
        ("export_glb", "export_glb", {"filepath": "/tmp/test.glb"}),
        ("export_fbx", "export_fbx", {"filepath": "/tmp/test.fbx"}),
        ("export_obj", "export_obj", {"filepath": "/tmp/test.obj"}),
        ("import_obj", "import_obj", {"filepath": "/tmp/test.obj"}),
        ("import_fbx", "import_fbx", {"filepath": "/tmp/test.fbx"}),
        ("import_glb", "import_glb", {"filepath": "/tmp/test.glb"}),
        ("import_image_as_plane", "import_image_as_plane", {"filepath": "/tmp/test.png"}),
    ],
)
def test_async_system_mcp_wrappers_direct(monkeypatch, fn_name, handler_method, kwargs):
    from server.adapters.mcp.areas import system as system_area

    handler = MagicMock()
    getattr(handler, handler_method).return_value = f"{handler_method} ok"

    monkeypatch.setattr(system_area, "get_system_handler", lambda: handler)
    monkeypatch.setattr(system_area, "ctx_info", lambda ctx, message: None)
    monkeypatch.setattr(system_area, "route_tool_call", _direct_route)
    monkeypatch.setattr(system_area, "is_background_task_context", lambda ctx: False)

    result = asyncio.run(getattr(system_area, fn_name)(MagicMock(), **kwargs))

    assert result == f"{handler_method} ok"
    getattr(handler, handler_method).assert_called_once()


@pytest.mark.parametrize(
    ("fn_name", "expected_rpc_cmd", "kwargs"),
    [
        ("export_glb", "export.glb", {"filepath": "/tmp/test.glb"}),
        ("import_obj", "import.obj", {"filepath": "/tmp/test.obj"}),
        ("import_image_as_plane", "import.image_as_plane", {"filepath": "/tmp/test.png"}),
    ],
)
def test_async_system_mcp_wrappers_background(monkeypatch, fn_name, expected_rpc_cmd, kwargs):
    from server.adapters.mcp.areas import system as system_area

    recorded = {}

    async def fake_run_rpc_background_job(ctx, **job_kwargs):
        recorded.update(job_kwargs)
        return "background ok"

    monkeypatch.setattr(system_area, "is_background_task_context", lambda ctx: True)
    monkeypatch.setattr(system_area, "run_rpc_background_job", fake_run_rpc_background_job)
    monkeypatch.setattr(system_area, "ctx_info", lambda ctx, message: None)

    result = asyncio.run(getattr(system_area, fn_name)(MagicMock(), **kwargs))

    assert result == "background ok"
    assert recorded["rpc_cmd"] == expected_rpc_cmd


@pytest.mark.parametrize(
    ("fn_name", "handler_method", "kwargs", "expected"),
    [
        ("system_set_mode", "set_mode", {"mode": "EDIT", "object_name": "Cube"}, "mode ok"),
        ("system_undo", "undo", {"steps": 2}, "undo ok"),
        ("system_redo", "redo", {"steps": 1}, "redo ok"),
        ("system_save_file", "save_file", {"filepath": "/tmp/test.blend", "compress": True}, "save ok"),
        ("system_new_file", "new_file", {"load_ui": False}, "new ok"),
        ("system_snapshot", "snapshot", {"action": "list", "name": None}, "snapshot ok"),
    ],
)
def test_sync_system_mcp_wrappers(monkeypatch, fn_name, handler_method, kwargs, expected):
    from server.adapters.mcp.areas import system as system_area

    handler = MagicMock()
    getattr(handler, handler_method).return_value = expected

    monkeypatch.setattr(system_area, "get_system_handler", lambda: handler)
    monkeypatch.setattr(system_area, "route_tool_call", _direct_route)

    result = getattr(system_area, fn_name)(MagicMock(), **kwargs)

    assert result == expected
    getattr(handler, handler_method).assert_called_once()
