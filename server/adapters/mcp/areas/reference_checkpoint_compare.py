# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Shared checkpoint/reference compare helpers for the reference MCP surface."""

from __future__ import annotations

import mimetypes
from collections.abc import Awaitable, Callable, Sequence
from pathlib import Path
from typing import Any, Literal

from fastmcp import Context

from server.adapters.mcp.contracts.reference import (
    ReferenceCompareCheckpointResponseContract,
    ReferenceImageRecordContract,
    ReferenceViewDiagnosticsHintContract,
)
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.vision import VisionImageInput, VisionRequest

CompareResponseAction = Literal["compare_checkpoint", "compare_current_view"]


def build_compare_response(
    *,
    action: CompareResponseAction,
    checkpoint_path: str,
    checkpoint_label: str | None,
    goal: str | None,
    target_object: str | None,
    target_view: str | None,
    reference_ids: list[str],
    reference_labels: list[str],
    view_diagnostics_hints: list[ReferenceViewDiagnosticsHintContract] | None = None,
    vision_assistant: Any = None,
    message: str | None = None,
    error: str | None = None,
) -> ReferenceCompareCheckpointResponseContract:
    """Build the public compare/checkpoint response envelope."""

    return ReferenceCompareCheckpointResponseContract(
        action=action,
        goal=goal,
        target_object=target_object,
        target_view=target_view,
        checkpoint_path=checkpoint_path,
        checkpoint_label=checkpoint_label,
        reference_count=len(reference_ids),
        reference_ids=reference_ids,
        reference_labels=reference_labels,
        view_diagnostics_hints=view_diagnostics_hints,
        vision_assistant=vision_assistant,
        message=message,
        error=error,
    )


async def run_checkpoint_compare(
    ctx: Context,
    *,
    checkpoint: Path,
    checkpoint_label: str | None,
    target_object: str | None,
    target_view: str | None,
    goal_override: str | None,
    prompt_hint: str | None,
    response_action: CompareResponseAction,
    build_compare_response: Callable[..., ReferenceCompareCheckpointResponseContract],
    get_session_capability_state_async: Callable[[Context], Awaitable[Any]],
    select_reference_records_for_target: Callable[..., tuple[ReferenceImageRecordContract, ...]],
    build_reference_capture_images: Callable[
        [Sequence[ReferenceImageRecordContract | dict[str, Any]]], tuple[VisionCaptureImageContract, ...]
    ],
    run_vision_assist: Callable[..., Awaitable[Any]],
    get_vision_backend_resolver: Callable[[], Any],
    to_vision_assistant_contract: Callable[[Any], Any],
) -> ReferenceCompareCheckpointResponseContract:
    """Run the shared bounded checkpoint compare path."""

    session = await get_session_capability_state_async(ctx)
    goal = goal_override or session.goal
    if not goal:
        return build_compare_response(
            action=response_action,
            checkpoint_path=str(checkpoint),
            checkpoint_label=checkpoint_label,
            goal=None,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error="Set an active goal with router_set_goal(...) before comparing a checkpoint, or pass goal_override.",
        )

    selected_reference_records = select_reference_records_for_target(
        list(session.reference_images or []),
        target_object=target_object,
        target_view=target_view,
    )
    if not selected_reference_records:
        return build_compare_response(
            action=response_action,
            checkpoint_path=str(checkpoint),
            checkpoint_label=checkpoint_label,
            goal=goal,
            target_object=target_object,
            target_view=target_view,
            reference_ids=[],
            reference_labels=[],
            error="No matching reference images are attached for the requested target_object/target_view.",
        )

    reference_images = build_reference_capture_images(selected_reference_records)
    vision_request = VisionRequest(
        goal=goal,
        images=(
            VisionImageInput(
                path=str(checkpoint),
                role="after",
                label=checkpoint_label or checkpoint.name,
                media_type=mimetypes.guess_type(str(checkpoint))[0] or "image/png",
            ),
            *tuple(
                VisionImageInput(
                    path=item.image_path,
                    role="reference",
                    label=item.label,
                    media_type=item.media_type,
                )
                for item in reference_images
            ),
        ),
        target_object=target_object,
        prompt_hint=" | ".join(
            part
            for part in (
                prompt_hint,
                "comparison_mode=checkpoint_vs_reference",
                f"checkpoint_label={checkpoint_label}" if checkpoint_label else None,
                f"target_view={target_view}" if target_view else None,
                *[
                    f"reference[{index}] label={record.label}"
                    for index, record in enumerate(selected_reference_records, start=1)
                    if record.label
                ],
            )
            if part
        )
        or None,
        metadata={
            "source": response_action,
            "checkpoint_path": str(checkpoint),
            "reference_count": len(selected_reference_records),
        },
    )
    outcome = await run_vision_assist(
        ctx,
        request=vision_request,
        resolver=get_vision_backend_resolver(),
    )
    vision_assistant = to_vision_assistant_contract(outcome)
    return build_compare_response(
        action=response_action,
        checkpoint_path=str(checkpoint),
        checkpoint_label=checkpoint_label,
        goal=goal,
        target_object=target_object,
        target_view=target_view,
        reference_ids=[item.reference_id for item in selected_reference_records],
        reference_labels=[item.label or item.reference_id for item in selected_reference_records],
        vision_assistant=vision_assistant,
        message=(
            f"Compared checkpoint '{checkpoint_label or checkpoint.name}' against {len(selected_reference_records)} reference image(s)."
            if outcome.status == "success"
            else "Checkpoint comparison executed but vision assistance did not complete successfully."
        ),
        error=vision_assistant.rejection_reason if vision_assistant.status != "success" else None,
    )
