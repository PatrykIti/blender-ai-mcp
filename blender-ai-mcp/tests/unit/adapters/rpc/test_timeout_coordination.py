"""Tests for RPC/addon timeout coordination."""

from __future__ import annotations

import json
import queue
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from blender_addon.infrastructure.rpc_server import BlenderRpcServer
from server.adapters.rpc.client import RpcClient


def test_rpc_client_sends_timeout_budget_and_deadline(monkeypatch):
    """RpcClient should propagate addon timeout budget explicitly in the request envelope."""

    captured = {}
    client = RpcClient(
        host="127.0.0.1",
        port=8765,
        rpc_timeout_seconds=45.0,
        addon_execution_timeout_seconds=20.0,
    )
    client.socket = MagicMock()

    def fake_send_msg(sock, msg):
        captured["payload"] = json.loads(msg.decode("utf-8"))

    monkeypatch.setattr("server.adapters.rpc.client.send_msg", fake_send_msg)
    monkeypatch.setattr(
        "server.adapters.rpc.client.recv_msg",
        lambda sock: json.dumps({"request_id": "abc", "status": "ok", "result": {"ok": True}}).encode("utf-8"),
    )

    response = client.send_request("scene.list_objects")

    assert response.status == "ok"
    assert captured["payload"]["timeout_seconds"] == 20.0
    assert isinstance(captured["payload"]["deadline_unix_ms"], int)


def test_rpc_client_normalizes_socket_timeout(monkeypatch):
    """RPC client timeout should surface a stable boundary-specific error."""

    client = RpcClient(host="127.0.0.1", port=8765, rpc_timeout_seconds=12.0, addon_execution_timeout_seconds=10.0)
    client.socket = MagicMock()

    monkeypatch.setattr("server.adapters.rpc.client.send_msg", lambda sock, msg: None)
    monkeypatch.setattr("server.adapters.rpc.client.recv_msg", lambda sock: (_ for _ in ()).throw(TimeoutError()))

    with patch("server.adapters.rpc.client.socket.timeout", TimeoutError):
        response = client.send_request("scene.list_objects")

    assert response.status == "error"
    assert response.error_code == "timeout"
    assert response.error_boundary == "rpc_client"


def test_rpc_server_uses_request_timeout_budget(monkeypatch):
    """Addon RPC server should honor propagated timeout budgets."""

    server = BlenderRpcServer()
    server.command_registry["demo.cmd"] = lambda **kwargs: "ok"

    monkeypatch.setattr(
        "blender_addon.infrastructure.rpc_server.bpy",
        SimpleNamespace(app=SimpleNamespace(timers=SimpleNamespace(register=lambda fn: None))),
    )
    monkeypatch.setattr(queue.Queue, "get", lambda self, timeout=None: (_ for _ in ()).throw(queue.Empty()))

    response = server._process_request(
        {
            "request_id": "req-1",
            "cmd": "demo.cmd",
            "args": {},
            "timeout_seconds": 5.0,
            "deadline_unix_ms": 0,
        }
    )

    assert response["status"] == "error"
    assert response["error_code"] == "timeout"
    assert response["error_boundary"] == "addon_execution"
