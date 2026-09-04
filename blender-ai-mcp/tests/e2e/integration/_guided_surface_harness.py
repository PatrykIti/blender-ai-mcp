"""Helpers for stdio- and streamable-backed guided-surface integration tests."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import tempfile
import textwrap
import time
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import Any, AsyncIterator, Generator

import pytest
from fastmcp.client import Client
from fastmcp.client.client import CallToolResult
from fastmcp.client.transports.http import StreamableHttpTransport
from fastmcp.client.transports.stdio import StdioTransport

REPO_ROOT = Path(__file__).resolve().parents[3]


def base_env(*, extra: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ)
    env.update(
        {
            "PYTHONPATH": str(REPO_ROOT),
            "MCP_SURFACE_PROFILE": "llm-guided",
            "MCP_TRANSPORT_MODE": "stdio",
            "ROUTER_ENABLED": "false",
            "VISION_ENABLED": "false",
            "FASTMCP_SHOW_SERVER_BANNER": "false",
            "PYTHONUNBUFFERED": "1",
        }
    )
    if extra:
        env.update(extra)
    return env


def write_server_script(tmp_path: Path, patch_source: str) -> Path:
    script = tmp_path / "guided_surface_server.py"
    script.write_text(
        textwrap.dedent(
            f"""\
from server.adapters.mcp.server import run

{patch_source}

if __name__ == "__main__":
    run("llm-guided")
"""
        ),
        encoding="utf-8",
    )
    return script


def _free_port() -> int:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            sock.listen(1)
            return int(sock.getsockname()[1])
    except PermissionError as exc:
        pytest.skip(f"Local socket binding is unavailable in this environment: {exc}")


@asynccontextmanager
async def stdio_client(script_path: Path, *, extra_env: dict[str, str] | None = None) -> AsyncIterator[Client]:
    log_path = script_path.with_suffix(".log")
    transport = StdioTransport(
        command=sys.executable,
        args=[str(script_path)],
        env=base_env(extra=extra_env),
        cwd=str(REPO_ROOT),
        keep_alive=False,
        log_file=log_path,
    )
    async with Client(transport, timeout=15, init_timeout=15) as client:
        yield client


@contextmanager
def run_streamable_server(
    script_path: Path,
    *,
    extra_env: dict[str, str] | None = None,
) -> Generator[str, None, None]:
    port = _free_port()
    url = f"http://127.0.0.1:{port}/mcp"
    log_file = tempfile.NamedTemporaryFile(prefix="bam-guided-streamable-", suffix=".log", delete=False)
    log_path = Path(log_file.name)
    log_file.close()
    env = base_env(
        extra={
            "MCP_TRANSPORT_MODE": "streamable",
            "MCP_HTTP_HOST": "127.0.0.1",
            "MCP_HTTP_PORT": str(port),
            "MCP_STREAMABLE_HTTP_PATH": "/mcp",
            **(extra_env or {}),
        }
    )
    process = subprocess.Popen(
        [sys.executable, str(script_path)],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=log_path.open("w"),
        stderr=subprocess.STDOUT,
        text=True,
    )

    async def _probe(server_url: str) -> None:
        transport = StreamableHttpTransport(server_url)
        async with Client(transport, timeout=10, init_timeout=10) as client:
            await client.list_tools()

    try:
        deadline = time.time() + 20
        last_error: Exception | None = None
        while time.time() < deadline:
            try:
                import asyncio

                asyncio.run(_probe(url))
                last_error = None
                break
            except Exception as exc:  # noqa: PERF203 - test-only retry loop
                last_error = exc
                time.sleep(0.25)
        if last_error is not None:
            log_text = log_path.read_text(encoding="utf-8", errors="replace")
            raise AssertionError(
                f"Streamable guided server did not become ready at {url}: {last_error}\n\n--- server log ---\n{log_text}"
            ) from last_error
        yield url
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


@asynccontextmanager
async def streamable_client(url: str) -> AsyncIterator[Client]:
    transport = StreamableHttpTransport(url)
    async with Client(transport, timeout=15, init_timeout=15) as client:
        yield client


def result_payload(result: CallToolResult) -> Any:
    structured = result.structured_content
    if isinstance(structured, dict) and "result" in structured:
        return structured["result"]
    return structured
