"""Utilities for working with FastMCP Context from sync tool functions.

FastMCP's Context methods like `ctx.info()` are async and must be awaited.
Most tools in this repo are implemented as sync functions, so we need a safe
bridge that avoids "coroutine was never awaited" warnings.
"""

from __future__ import annotations

import asyncio

import anyio
from fastmcp import Context


def ctx_info(ctx: Context, message: str) -> None:
    """Best-effort INFO message to the connected MCP client.

    Works from both:
    - async event loop thread (schedule with create_task)
    - AnyIO worker thread (use anyio.from_thread.run)
    """
    # If we're in the async event loop thread, schedule a task.
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None:
        coro = ctx.info(message)
        try:
            loop.create_task(coro)
        except Exception:
            coro.close()
        return

    # If we're in a worker thread managed by AnyIO, bridge to the event loop.
    try:
        anyio.from_thread.run(ctx.info, message)
    except Exception:
        # Best-effort: never fail a tool call because of client logging.
        return

