"""Tests for RpcClient transport behavior on stdio-safe server paths."""

from __future__ import annotations

import builtins
import socket

import pytest

from server.adapters.rpc.client import RpcClient


class _FailingSocket:
    def __init__(self, exc: Exception):
        self._exc = exc

    def settimeout(self, timeout: float):
        return None

    def connect(self, addr):
        raise self._exc

    def close(self):
        return None


class _DisconnectingSocket:
    def settimeout(self, timeout: float):
        return None

    def sendall(self, data: bytes):
        return None

    def recv(self, n: int) -> bytes:
        return b""

    def close(self):
        return None


def test_rpc_client_connect_failure_does_not_print_to_stdout(monkeypatch, caplog):
    client = RpcClient("127.0.0.1", 8765)

    monkeypatch.setattr(builtins, "print", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("print called")))
    monkeypatch.setattr(
        socket,
        "socket",
        lambda *args, **kwargs: _FailingSocket(OSError("boom")),
    )

    connected = client.connect()

    assert connected is False
    assert "Error connecting to Blender RPC" in caplog.text


def test_rpc_client_disconnect_does_not_print_to_stdout(monkeypatch, caplog):
    client = RpcClient("127.0.0.1", 8765)
    client.socket = _DisconnectingSocket()

    monkeypatch.setattr(builtins, "print", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("print called")))

    response = client.send_request("scene.list_objects", {})

    assert response.status == "error"
    assert response.error_boundary == "rpc_client"
    assert response.error_code == "connection_error"
    assert "Connection lost while talking to Blender RPC" in caplog.text
