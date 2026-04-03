"""Tests for MCP transport-mode bootstrap wiring."""

from __future__ import annotations

from types import SimpleNamespace

from server.adapters.mcp import server as server_module


class _FakeServer:
    def __init__(self):
        self.calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self._bam_contract_line = "llm-guided-v2"

    def run(self, *args, **kwargs):
        self.calls.append((args, kwargs))


def test_server_run_uses_stdio_transport_mode(monkeypatch):
    fake_server = _FakeServer()

    monkeypatch.setattr(server_module, "build_server", lambda surface_profile=None: fake_server)
    monkeypatch.setattr(server_module, "is_router_enabled", lambda: True)
    monkeypatch.setattr(server_module.signal, "signal", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        server_module,
        "get_config",
        lambda: SimpleNamespace(
            MCP_SURFACE_PROFILE="llm-guided",
            MCP_TRANSPORT_MODE="stdio",
            MCP_HTTP_HOST="127.0.0.1",
            MCP_HTTP_PORT=8000,
            MCP_STREAMABLE_HTTP_PATH="/mcp",
        ),
    )

    server_module.run()

    assert fake_server.calls == [((), {"transport": "stdio"})]


def test_server_run_uses_streamable_http_transport_mode(monkeypatch):
    fake_server = _FakeServer()

    monkeypatch.setattr(server_module, "build_server", lambda surface_profile=None: fake_server)
    monkeypatch.setattr(server_module, "is_router_enabled", lambda: True)
    monkeypatch.setattr(server_module.signal, "signal", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        server_module,
        "get_config",
        lambda: SimpleNamespace(
            MCP_SURFACE_PROFILE="llm-guided",
            MCP_TRANSPORT_MODE="streamable",
            MCP_HTTP_HOST="0.0.0.0",
            MCP_HTTP_PORT=8123,
            MCP_STREAMABLE_HTTP_PATH="/custom-mcp",
        ),
    )

    server_module.run()

    assert fake_server.calls == [
        (
            (),
            {
                "transport": "streamable-http",
                "host": "0.0.0.0",
                "port": 8123,
                "path": "/custom-mcp",
                "stateless_http": False,
            },
        )
    ]
