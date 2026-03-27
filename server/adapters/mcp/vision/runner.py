# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Bounded runtime runner for optional local/external vision assistance."""

from __future__ import annotations

import json
from typing import cast

from fastmcp import Context

from server.adapters.mcp.context_utils import ctx_request_id
from server.adapters.mcp.contracts.base import to_contract
from server.adapters.mcp.sampling.result_types import (
    AssistantCapabilitySource,
    AssistantPolicy,
    AssistantRunResult,
    VisionAssistContract,
)
from server.adapters.mcp.tasks.task_bridge import is_background_task_context

from .backend import VisionBackendUnavailableError, VisionRequest
from .runtime import LazyVisionBackendResolver

VISION_ASSIST_POLICY = AssistantPolicy(
    assistant_name="vision_assist",
    responsibility="vision_assist",
    max_input_chars=12000,
    max_messages=1,
    max_tokens=400,
)


def _estimate_request_chars(request: VisionRequest) -> int:
    payload = {
        "goal": request.goal,
        "target_object": request.target_object,
        "prompt_hint": request.prompt_hint,
        "truth_summary": request.truth_summary,
        "metadata": request.metadata,
        "images": [
            {
                "role": image.role,
                "label": image.label,
                "path": image.path,
            }
            for image in request.images
        ],
    }
    return len(json.dumps(payload, ensure_ascii=True, sort_keys=True))


async def run_vision_assist(
    ctx: Context,
    *,
    request: VisionRequest,
    resolver: LazyVisionBackendResolver,
) -> AssistantRunResult[VisionAssistContract]:
    """Run one bounded vision assist request against the configured backend."""

    budget = VISION_ASSIST_POLICY.to_budget_contract()
    request_id = ctx_request_id(ctx)
    runtime = resolver.runtime_config

    if is_background_task_context(ctx):
        return AssistantRunResult(
            status="rejected_by_policy",
            assistant_name=VISION_ASSIST_POLICY.assistant_name,
            message="Vision assistance stays bound to foreground MCP requests.",
            budget=budget,
            request_id=request_id,
            capability_source="unknown",
            rejection_reason="background_request_forbidden",
        )

    if len(request.images) == 0:
        return AssistantRunResult(
            status="rejected_by_policy",
            assistant_name=VISION_ASSIST_POLICY.assistant_name,
            message="Vision request requires at least one image.",
            budget=budget,
            request_id=request_id,
            capability_source="unknown",
            rejection_reason="empty_images",
        )

    if len(request.images) > runtime.max_images:
        return AssistantRunResult(
            status="rejected_by_policy",
            assistant_name=VISION_ASSIST_POLICY.assistant_name,
            message="Vision request exceeded the image budget.",
            budget=budget,
            request_id=request_id,
            capability_source="unknown",
            rejection_reason="image_budget_exceeded",
        )

    if _estimate_request_chars(request) > VISION_ASSIST_POLICY.max_input_chars:
        return AssistantRunResult(
            status="rejected_by_policy",
            assistant_name=VISION_ASSIST_POLICY.assistant_name,
            message="Vision request exceeded the allowed input character budget.",
            budget=budget,
            request_id=request_id,
            capability_source="unknown",
            rejection_reason="input_budget_exceeded",
        )

    try:
        backend = resolver.resolve_default()
    except VisionBackendUnavailableError as exc:
        return AssistantRunResult(
            status="unavailable",
            assistant_name=VISION_ASSIST_POLICY.assistant_name,
            message="Vision backend is unavailable on the active runtime.",
            budget=budget,
            request_id=request_id,
            capability_source="unavailable",
            rejection_reason=str(exc),
        )

    capability_source = cast(
        AssistantCapabilitySource,
        "local_runtime" if backend.backend_kind in {"transformers_local", "mlx_local"} else "external_runtime",
    )

    try:
        payload = await backend.analyze(request)
    except VisionBackendUnavailableError as exc:
        return AssistantRunResult(
            status="unavailable",
            assistant_name=VISION_ASSIST_POLICY.assistant_name,
            message="Vision backend is unavailable on the active runtime.",
            budget=budget,
            request_id=request_id,
            capability_source=capability_source,
            rejection_reason=str(exc),
        )
    except Exception as exc:  # pragma: no cover - defensive normalization
        return AssistantRunResult(
            status="masked_error",
            assistant_name=VISION_ASSIST_POLICY.assistant_name,
            message="vision_assist failed during bounded execution. Error details were masked.",
            budget=budget,
            request_id=request_id,
            capability_source=capability_source,
            rejection_reason=str(exc),
        )

    return AssistantRunResult(
        status="success",
        assistant_name=VISION_ASSIST_POLICY.assistant_name,
        message="vision_assist completed.",
        budget=budget,
        request_id=request_id,
        capability_source=capability_source,
        result=to_contract(VisionAssistContract, payload),
    )
