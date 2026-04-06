"""Helpers for stdio-backed guided-surface integration tests."""

from __future__ import annotations

import os
import sys
import textwrap
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator

from fastmcp.client import Client
from fastmcp.client.client import CallToolResult
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


def result_payload(result: CallToolResult) -> Any:
    structured = result.structured_content
    if isinstance(structured, dict) and "result" in structured:
        return structured["result"]
    return structured
