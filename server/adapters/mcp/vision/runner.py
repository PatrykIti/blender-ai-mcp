# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Bounded runtime runner for optional local/external vision assistance."""

from __future__ import annotations

import json
from dataclasses import replace
from typing import cast

from fastmcp import Context

from server.adapters.mcp.context_utils import ctx_request_id
from server.adapters.mcp.contracts.base import to_contract
from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantCapabilitySource,
    AssistantPolicy,
    AssistantRunResult,
    VisionAssistContract,
)
from server.adapters.mcp.tasks.task_bridge import is_background_task_context

from .backend import VisionBackendUnavailableError, VisionRequest
from .config import (
    VISION_FAIL_SAFE_MAX_IMAGES,
    VISION_FAIL_SAFE_MAX_INPUT_CHARS,
    VISION_FAIL_SAFE_MAX_TOKENS,
    VisionRuntimeConfig,
)
from .runtime import LazyVisionBackendResolver

VISION_ASSIST_POLICY = AssistantPolicy(
    assistant_name="vision_assist",
    responsibility="vision_assist",
    max_input_chars=12000,
    max_messages=1,
    max_tokens=400,
)


def _resolve_vision_assist_policy(runtime: VisionRuntimeConfig) -> AssistantPolicy:
    """Project the runtime-owned input budget onto the bounded runner policy."""

    return replace(
        VISION_ASSIST_POLICY,
        max_input_chars=runtime.effective_max_input_chars,
        max_tokens=runtime.effective_max_tokens,
    )


def _vision_assist_budget_contract(runtime: VisionRuntimeConfig, policy: AssistantPolicy) -> AssistantBudgetContract:
    return policy.to_budget_contract().model_copy(
        update={
            "max_images": runtime.effective_max_images,
            "configured_max_input_chars": runtime.max_input_chars,
            "configured_max_tokens": runtime.max_tokens,
            "configured_max_images": runtime.max_images,
            "effective_max_input_chars": runtime.effective_max_input_chars,
            "effective_max_tokens": runtime.effective_max_tokens,
            "effective_max_images": runtime.effective_max_images,
            "fail_safe_max_input_chars": VISION_FAIL_SAFE_MAX_INPUT_CHARS,
            "fail_safe_max_tokens": VISION_FAIL_SAFE_MAX_TOKENS,
            "fail_safe_max_images": VISION_FAIL_SAFE_MAX_IMAGES,
            "budget_clipped": bool(runtime.budget_clip_fields),
            "budget_clip_fields": list(runtime.budget_clip_fields),
        }
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

    runtime = resolver.runtime_config
    policy = _resolve_vision_assist_policy(runtime)
    budget = _vision_assist_budget_contract(runtime, policy)
    request_id = ctx_request_id(ctx)

    if is_background_task_context(ctx):
        return AssistantRunResult(
            status="rejected_by_policy",
            assistant_name=policy.assistant_name,
            message="Vision assistance stays bound to foreground MCP requests.",
            budget=budget,
            request_id=request_id,
            capability_source="unknown",
            rejection_reason="background_request_forbidden",
        )

    if len(request.images) == 0:
        return AssistantRunResult(
            status="rejected_by_policy",
            assistant_name=policy.assistant_name,
            message="Vision request requires at least one image.",
            budget=budget,
            request_id=request_id,
            capability_source="unknown",
            rejection_reason="empty_images",
        )

    if len(request.images) > runtime.effective_max_images:
        return AssistantRunResult(
            status="rejected_by_policy",
            assistant_name=policy.assistant_name,
            message="Vision request exceeded the image budget.",
            budget=budget,
            request_id=request_id,
            capability_source="unknown",
            rejection_reason="image_budget_exceeded",
        )

    if _estimate_request_chars(request) > policy.max_input_chars:
        return AssistantRunResult(
            status="rejected_by_policy",
            assistant_name=policy.assistant_name,
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
            assistant_name=policy.assistant_name,
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
            assistant_name=policy.assistant_name,
            message="Vision backend is unavailable on the active runtime.",
            budget=budget,
            request_id=request_id,
            capability_source=capability_source,
            rejection_reason=str(exc),
        )
    except Exception as exc:  # pragma: no cover - defensive normalization
        return AssistantRunResult(
            status="masked_error",
            assistant_name=policy.assistant_name,
            message="vision_assist failed during bounded execution. Error details were masked.",
            budget=budget,
            request_id=request_id,
            capability_source=capability_source,
            rejection_reason=str(exc),
        )

    return AssistantRunResult(
        status="success",
        assistant_name=policy.assistant_name,
        message="vision_assist completed.",
        budget=budget,
        request_id=request_id,
        capability_source=capability_source,
        result=to_contract(VisionAssistContract, payload),
    )
