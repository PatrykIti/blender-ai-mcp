# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Background-task bridge for task-capable FastMCP tool entrypoints."""

from __future__ import annotations

import asyncio
import logging
import time
from concurrent.futures import TimeoutError as FuturesTimeoutError
from threading import Event
from typing import Any, Callable, TypeVar

from fastmcp import Context

from server.adapters.mcp.tasks.job_registry import (
    get_background_job_registry,
    is_terminal_background_job_status,
)
from server.adapters.mcp.tasks.result_store import get_background_result_store
from server.adapters.mcp.timeout_policy import MCPTimeoutPolicy, build_timeout_policy
from server.infrastructure.config import get_config
from server.infrastructure.di import get_rpc_client

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _monotonic_now() -> float:
    """Wrapper around monotonic time to keep timeout tests local to this module."""

    return time.monotonic()


def _get_timeout_policy(ctx: Context) -> MCPTimeoutPolicy:
    """Return the active timeout policy for the running server surface."""

    try:
        policy = getattr(ctx.fastmcp, "_bam_timeout_policy", None)
    except Exception:
        policy = None

    if isinstance(policy, MCPTimeoutPolicy):
        return policy

    config = get_config()
    return build_timeout_policy(
        tool_timeout_seconds=config.MCP_TOOL_TIMEOUT_SECONDS,
        task_timeout_seconds=config.MCP_TASK_TIMEOUT_SECONDS,
        rpc_timeout_seconds=config.RPC_TIMEOUT_SECONDS,
        addon_execution_timeout_seconds=config.ADDON_EXECUTION_TIMEOUT_SECONDS,
    )


def is_background_task_context(ctx: Context) -> bool:
    """Return True when the current tool execution is running as an MCP task."""

    try:
        is_background_task = getattr(ctx, "is_background_task", False)
        task_id = getattr(ctx, "task_id", None)
        return is_background_task is True and isinstance(task_id, str) and bool(task_id)
    except Exception:
        return False


async def _report_background_progress(
    ctx: Context,
    *,
    task_id: str,
    tool_name: str,
    current: float,
    total: float | None = None,
    message: str | None = None,
    status: str | None = None,
) -> None:
    """Update internal registry state and best-effort MCP progress notifications."""

    registry = get_background_job_registry()
    existing = registry.get(task_id)
    if existing is not None and is_terminal_background_job_status(existing.status):
        if status != existing.status:
            return
    registry.update_progress(
        task_id,
        current=current,
        total=total,
        message=message,
        status=status,
    )

    try:
        await ctx.report_progress(progress=current, total=total, message=message)
    except Exception as exc:
        logger.debug("Skipping MCP progress notification for %s/%s: %s", tool_name, task_id, exc)


async def run_rpc_background_job(
    ctx: Context,
    *,
    tool_name: str,
    rpc_cmd: str,
    rpc_args: dict[str, Any],
    foreground_executor: Callable[[], T],
    result_formatter: Callable[[Any], T],
    start_message: str,
    completion_message: str,
    poll_interval_seconds: float = 0.25,
) -> T:
    """Run an adopted Blender-backed operation in foreground or task mode."""

    if not is_background_task_context(ctx):
        return foreground_executor()

    task_id = str(ctx.task_id)
    policy = _get_timeout_policy(ctx)
    registry = get_background_job_registry()
    result_store = get_background_result_store()
    rpc_client = get_rpc_client()

    registry.register(task_id=task_id, tool_name=tool_name, backend_kind="addon_job")
    await _report_background_progress(
        ctx,
        task_id=task_id,
        tool_name=tool_name,
        current=0,
        total=1,
        message=start_message,
        status="queued",
    )

    launch_response = await asyncio.to_thread(
        rpc_client.launch_background_job,
        rpc_cmd,
        rpc_args,
        timeout_seconds=policy.task_timeout_seconds,
    )
    if launch_response.status == "error":
        error = launch_response.error or f"Failed to launch background job for {tool_name}"
        registry.mark_failed(task_id, error)
        raise RuntimeError(error)

    launch_result = launch_response.result if isinstance(launch_response.result, dict) else {}
    addon_job_id = str(launch_result.get("job_id") or "")
    if not addon_job_id:
        error = f"Background launch for {tool_name} did not return a job_id"
        registry.mark_failed(task_id, error)
        raise RuntimeError(error)

    registry.bind_backend_job(task_id, addon_job_id)
    poll_deadline = _monotonic_now() + float(policy.task_timeout_seconds)

    try:
        while True:
            if _monotonic_now() >= poll_deadline:
                error = (
                    f"Background job {addon_job_id} for {tool_name} exceeded MCP_TASK_TIMEOUT_SECONDS="
                    f"{policy.task_timeout_seconds}"
                )
                try:
                    cancel_response = await asyncio.to_thread(
                        rpc_client.cancel_background_job,
                        addon_job_id,
                    )
                    cancel_error = cancel_response.error if cancel_response.status == "error" else None
                except Exception:
                    cancel_error = None
                registry.mark_failed(task_id, cancel_error or error)
                raise RuntimeError(cancel_error or error)

            poll_response = await asyncio.to_thread(rpc_client.get_background_job_status, addon_job_id)
            if poll_response.status == "error":
                error = poll_response.error or f"Polling failed for background job {addon_job_id}"
                registry.mark_failed(task_id, error)
                raise RuntimeError(error)

            snapshot = poll_response.result if isinstance(poll_response.result, dict) else {}
            status = str(snapshot.get("status") or "unknown")
            current = float(snapshot.get("progress_current", 0))
            total_raw = snapshot.get("progress_total")
            total = float(total_raw) if isinstance(total_raw, (int, float)) else None
            message = snapshot.get("status_message")

            await _report_background_progress(
                ctx,
                task_id=task_id,
                tool_name=tool_name,
                current=current,
                total=total,
                message=message,
                status=status,
            )

            if status == "completed":
                collect_response = await asyncio.to_thread(
                    rpc_client.collect_background_job_result,
                    addon_job_id,
                )
                if collect_response.status == "error":
                    error = collect_response.error or f"Result collection failed for background job {addon_job_id}"
                    registry.mark_failed(task_id, error)
                    raise RuntimeError(error)

                collect_result = collect_response.result if isinstance(collect_response.result, dict) else {}
                payload = collect_result.get("result", collect_result)
                try:
                    formatted_result = result_formatter(payload)
                    result_record = result_store.put(
                        task_id=task_id,
                        tool_name=tool_name,
                        payload=formatted_result,
                    )
                except Exception as exc:
                    error = str(exc) or f"Result formatting failed for background job {addon_job_id}"
                    registry.mark_failed(task_id, error)
                    raise
                registry.mark_completed(task_id, result_ref=result_record.result_ref)
                await _report_background_progress(
                    ctx,
                    task_id=task_id,
                    tool_name=tool_name,
                    current=total or current or 1,
                    total=total or current or 1,
                    message=completion_message,
                    status="completed",
                )
                return formatted_result

            if status == "failed":
                error = str(snapshot.get("error") or f"Background job {addon_job_id} failed")
                registry.mark_failed(task_id, error)
                raise RuntimeError(error)

            if status == "cancelled":
                error = str(snapshot.get("error") or f"Background job {addon_job_id} cancelled")
                registry.mark_cancelled(task_id, error=error)
                raise asyncio.CancelledError(error)

            await asyncio.sleep(poll_interval_seconds)
    except asyncio.CancelledError:
        cancel_response = await asyncio.to_thread(
            rpc_client.cancel_background_job,
            addon_job_id,
        )
        cancel_error = cancel_response.error if cancel_response.status == "error" else None
        registry.mark_cancelled(
            task_id,
            error=cancel_error or f"Task {task_id} cancelled while waiting for Blender job {addon_job_id}",
        )
        raise


async def run_local_background_operation(
    ctx: Context,
    *,
    tool_name: str,
    foreground_executor: Callable[[], T],
    background_executor: Callable[[Callable[[float, float | None, str | None], None], Callable[[], bool]], T],
    result_formatter: Callable[[Any], T],
    start_message: str,
    completion_message: str,
) -> T:
    """Run a server-local heavy operation in task mode with shared bookkeeping."""

    if not is_background_task_context(ctx):
        return foreground_executor()

    task_id = str(ctx.task_id)
    policy = _get_timeout_policy(ctx)
    registry = get_background_job_registry()
    result_store = get_background_result_store()
    registry.register(task_id=task_id, tool_name=tool_name, backend_kind="server_local")

    await _report_background_progress(
        ctx,
        task_id=task_id,
        tool_name=tool_name,
        current=0,
        total=1,
        message=start_message,
        status="queued",
    )

    loop = asyncio.get_running_loop()
    cancellation_flag = Event()

    def progress_callback(current: float, total: float | None = None, message: str | None = None) -> None:
        if cancellation_flag.is_set() or registry.is_terminal(task_id):
            return
        try:
            future = asyncio.run_coroutine_threadsafe(
                _report_background_progress(
                    ctx,
                    task_id=task_id,
                    tool_name=tool_name,
                    current=current,
                    total=total,
                    message=message,
                    status="running",
                ),
                loop,
            )
        except RuntimeError:
            return
        try:
            future.result(timeout=1.0)
        except FuturesTimeoutError:
            future.cancel()
        except Exception:
            return

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(
                background_executor,
                progress_callback,
                cancellation_flag.is_set,
            ),
            timeout=policy.task_timeout_seconds,
        )
    except asyncio.TimeoutError as exc:
        cancellation_flag.set()
        error = (
            f"Local background operation for {tool_name} exceeded MCP_TASK_TIMEOUT_SECONDS="
            f"{policy.task_timeout_seconds}"
        )
        registry.mark_failed(task_id, error)
        raise RuntimeError(error) from exc
    except asyncio.CancelledError:
        cancellation_flag.set()
        registry.mark_cancelled(task_id, error=f"Task {task_id} cancelled during local background execution")
        raise
    except Exception as exc:
        cancellation_flag.set()
        error = str(exc) or f"Local background execution failed for {tool_name}"
        registry.mark_failed(task_id, error)
        raise

    if isinstance(result, dict) and result.get("status") == "cancelled":
        registry.mark_cancelled(task_id, error=str(result.get("message") or "Background operation cancelled"))
        raise asyncio.CancelledError(str(result.get("message") or "Background operation cancelled"))

    try:
        formatted_result = result_formatter(result)
    except Exception as exc:
        error = str(exc) or f"Local background result formatting failed for {tool_name}"
        registry.mark_failed(task_id, error)
        raise
    result_record = result_store.put(
        task_id=task_id,
        tool_name=tool_name,
        payload=formatted_result,
    )
    registry.mark_completed(task_id, result_ref=result_record.result_ref)
    await _report_background_progress(
        ctx,
        task_id=task_id,
        tool_name=tool_name,
        current=1,
        total=1,
        message=completion_message,
        status="completed",
    )
    return formatted_result
