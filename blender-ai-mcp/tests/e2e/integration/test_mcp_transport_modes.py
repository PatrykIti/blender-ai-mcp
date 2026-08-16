"""E2E coverage for MCP transport modes without requiring Blender RPC."""

from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import pytest
from fastmcp.client import Client
from fastmcp.client.transports.http import StreamableHttpTransport
from fastmcp.client.transports.stdio import StdioTransport

REPO_ROOT = Path(__file__).resolve().parents[3]


def _base_env(*, transport_mode: str, extra: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ)
    env.update(
        {
            "PYTHONPATH": str(REPO_ROOT),
            "MCP_SURFACE_PROFILE": "legacy-flat",
            "MCP_TRANSPORT_MODE": transport_mode,
            "ROUTER_ENABLED": "false",
            "VISION_ENABLED": "false",
            "PYTHONUNBUFFERED": "1",
            "FASTMCP_SHOW_SERVER_BANNER": "false",
        }
    )
    if extra:
        env.update(extra)
    return env


def _free_port() -> int:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            sock.listen(1)
            return int(sock.getsockname()[1])
    except PermissionError as exc:
        pytest.skip(f"Local socket binding is unavailable in this environment: {exc}")


async def _call_stage_compare_via_client(client: Client) -> object:
    result = await client.call_tool("reference_compare_stage_checkpoint", {})
    return result.data


async def _fetch_stage_compare_stdio_session_id() -> tuple[str | None, str | None]:
    log_file = tempfile.NamedTemporaryFile(prefix="bam-stdio-", suffix=".log", delete=False)
    log_path = Path(log_file.name)
    log_file.close()
    transport = StdioTransport(
        command=sys.executable,
        args=["-m", "server.main"],
        env=_base_env(transport_mode="stdio"),
        cwd=str(REPO_ROOT),
        keep_alive=False,
        log_file=log_path,
    )
    async with Client(transport, timeout=10, init_timeout=10) as client:
        payload = await _call_stage_compare_via_client(client)
        return getattr(payload, "session_id", None), getattr(payload, "transport", None)


@contextmanager
def _run_streamable_server() -> Generator[str, None, None]:
    port = _free_port()
    url = f"http://127.0.0.1:{port}/mcp"
    log_file = tempfile.NamedTemporaryFile(prefix="bam-streamable-", suffix=".log", delete=False)
    log_path = Path(log_file.name)
    log_file.close()
    process = subprocess.Popen(
        [sys.executable, "-m", "server.main"],
        cwd=str(REPO_ROOT),
        env=_base_env(
            transport_mode="streamable",
            extra={
                "MCP_HTTP_HOST": "127.0.0.1",
                "MCP_HTTP_PORT": str(port),
                "MCP_STREAMABLE_HTTP_PATH": "/mcp",
            },
        ),
        stdout=log_path.open("w"),
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        deadline = time.time() + 20
        last_error: Exception | None = None
        while time.time() < deadline:
            try:
                asyncio.run(_fetch_streamable_session_id(url))
                last_error = None
                break
            except Exception as exc:  # noqa: PERF203 - test-only retry loop
                last_error = exc
                time.sleep(0.25)
        if last_error is not None:
            log_text = log_path.read_text(encoding="utf-8", errors="replace")
            raise AssertionError(
                f"Streamable MCP server did not become ready at {url}: {last_error}\n\n--- server log ---\n{log_text}"
            ) from last_error
        yield url
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


async def _fetch_streamable_session_id(url: str) -> tuple[str | None, str | None]:
    transport = StreamableHttpTransport(url)
    async with Client(transport, timeout=10, init_timeout=10) as client:
        payload = await _call_stage_compare_via_client(client)
        return getattr(payload, "session_id", None), getattr(payload, "transport", None)


@pytest.mark.slow
def test_stdio_transport_e2e_preserves_session_id_within_client_and_changes_on_reconnect():
    first_session_id, first_transport = asyncio.run(_fetch_stage_compare_stdio_session_id())
    second_session_id, second_transport = asyncio.run(_fetch_stage_compare_stdio_session_id())

    assert first_transport == "stdio"
    assert second_transport == "stdio"
    assert first_session_id is not None
    assert second_session_id is not None
    assert first_session_id != second_session_id


@pytest.mark.slow
def test_streamable_transport_e2e_preserves_session_id_within_client_and_changes_on_reconnect():
    with _run_streamable_server() as url:
        first_session_id, first_transport = asyncio.run(_fetch_streamable_session_id(url))
        second_session_id, second_transport = asyncio.run(_fetch_streamable_session_id(url))

    assert first_transport == "streamable-http"
    assert second_transport == "streamable-http"
    assert first_session_id is not None
    assert second_session_id is not None
    assert first_session_id != second_session_id


@pytest.mark.slow
def test_stdio_transport_e2e_keeps_same_session_id_across_calls_in_one_client():
    async def run() -> tuple[str | None, str | None]:
        log_file = tempfile.NamedTemporaryFile(prefix="bam-stdio-", suffix=".log", delete=False)
        log_path = Path(log_file.name)
        log_file.close()
        transport = StdioTransport(
            command=sys.executable,
            args=["-m", "server.main"],
            env=_base_env(transport_mode="stdio"),
            cwd=str(REPO_ROOT),
            keep_alive=False,
            log_file=log_path,
        )
        async with Client(transport, timeout=10, init_timeout=10) as client:
            first = await _call_stage_compare_via_client(client)
            second = await _call_stage_compare_via_client(client)
            return getattr(first, "session_id", None), getattr(second, "session_id", None)

    first_session_id, second_session_id = asyncio.run(run())

    assert first_session_id is not None
    assert first_session_id == second_session_id


@pytest.mark.slow
def test_streamable_transport_e2e_keeps_same_session_id_across_calls_in_one_client():
    async def run(url: str) -> tuple[str | None, str | None]:
        transport = StreamableHttpTransport(url)
        async with Client(transport, timeout=10, init_timeout=10) as client:
            first = await _call_stage_compare_via_client(client)
            second = await _call_stage_compare_via_client(client)
            return getattr(first, "session_id", None), getattr(second, "session_id", None)

    with _run_streamable_server() as url:
        first_session_id, second_session_id = asyncio.run(run(url))

    assert first_session_id is not None
    assert first_session_id == second_session_id
