# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Integration helpers for attaching bounded vision results to MCP contracts."""

from __future__ import annotations

from fastmcp import Context

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract
from server.adapters.mcp.session_capabilities import get_session_capability_state_async
from server.adapters.mcp.sampling.result_types import to_vision_assistant_contract
from server.infrastructure.di import get_vision_backend_resolver

from .capture import (
    build_reference_capture_images,
    build_vision_request_from_capture_bundle,
    select_reference_records_for_target,
)
from .runner import run_vision_assist


async def maybe_attach_macro_vision(
    ctx: Context,
    report: MacroExecutionReportContract,
) -> MacroExecutionReportContract:
    """Attach bounded vision output to a macro report when a capture bundle exists."""

    if report.capture_bundle is None or report.vision_assistant is not None:
        return report

    session = await get_session_capability_state_async(ctx)
    selected_reference_records = select_reference_records_for_target(
        session.reference_images or [],
        target_object=report.capture_bundle.target_object,
    )
    reference_images = build_reference_capture_images(selected_reference_records)
    goal = session.goal or report.intent or report.macro_name
    prompt_hint_parts = [
        f"target_object={report.capture_bundle.target_object}" if report.capture_bundle.target_object else None,
        *[
            f"reference[{index}] label={capture.label}"
            for index, capture in enumerate(reference_images, start=1)
            if capture.label
        ],
        *[
            f"reference_target_view[{index}]={record.target_view}"
            for index, record in enumerate(selected_reference_records, start=1)
            if record.target_view
        ],
    ]
    request = build_vision_request_from_capture_bundle(
        report.capture_bundle,
        goal=goal,
        reference_images=reference_images,
        prompt_hint=" | ".join(part for part in prompt_hint_parts if part) or None,
    )
    outcome = await run_vision_assist(
        ctx,
        request=request,
        resolver=get_vision_backend_resolver(),
    )
    return report.model_copy(update={"vision_assistant": to_vision_assistant_contract(outcome)})
