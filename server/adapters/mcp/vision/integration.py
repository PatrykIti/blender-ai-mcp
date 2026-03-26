# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Integration helpers for attaching bounded vision results to MCP contracts."""

from __future__ import annotations

from fastmcp import Context

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract
from server.adapters.mcp.sampling.result_types import to_vision_assistant_contract
from server.infrastructure.di import get_vision_backend_resolver

from .capture import build_vision_request_from_capture_bundle
from .runner import run_vision_assist


async def maybe_attach_macro_vision(
    ctx: Context,
    report: MacroExecutionReportContract,
) -> MacroExecutionReportContract:
    """Attach bounded vision output to a macro report when a capture bundle exists."""

    if report.capture_bundle is None or report.vision_assistant is not None:
        return report

    request = build_vision_request_from_capture_bundle(
        report.capture_bundle,
        goal=report.intent or report.macro_name,
    )
    outcome = await run_vision_assist(
        ctx,
        request=request,
        resolver=get_vision_backend_resolver(),
    )
    return report.model_copy(update={"vision_assistant": to_vision_assistant_contract(outcome)})
