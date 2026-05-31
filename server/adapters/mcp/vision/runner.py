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
    VisionCapabilitySummaryContract,
)
from server.adapters.mcp.tasks.task_bridge import is_background_task_context

from .backend import VisionBackend, VisionBackendUnavailableError, VisionRequest
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


def _project_runtime_budget(runtime: VisionRuntimeConfig) -> tuple[AssistantPolicy, AssistantBudgetContract]:
    policy = _resolve_vision_assist_policy(runtime)
    return policy, _vision_assist_budget_contract(runtime, policy)


def _bounded_capability_summary(
    runtime: VisionRuntimeConfig,
    backend: VisionBackend,
) -> dict[str, object] | None:
    external = runtime.openai_compatible_external
    if external is None or external.model_capabilities is None:
        return None

    model_capabilities = external.model_capabilities
    payload_summary = getattr(backend, "last_request_policy_summary", None)
    requested_max_tokens = (
        payload_summary.get("requested_max_tokens")
        if isinstance(payload_summary, dict) and isinstance(payload_summary.get("requested_max_tokens"), int)
        else None
    )
    request_mode = (
        str(payload_summary.get("response_format_type"))
        if isinstance(payload_summary, dict) and isinstance(payload_summary.get("response_format_type"), str)
        else None
    )
    response_healing_enabled = None
    if isinstance(payload_summary, dict) and isinstance(payload_summary.get("plugins"), list):
        response_healing_enabled = "response-healing" in payload_summary["plugins"]
    usage_summary = getattr(backend, "last_response_usage_summary", None)
    if not isinstance(usage_summary, dict):
        usage_summary = {}

    prompt_tokens = usage_summary.get("prompt_tokens")
    completion_tokens = usage_summary.get("completion_tokens")
    total_tokens = usage_summary.get("total_tokens")
    finish_reason = usage_summary.get("finish_reason")
    summary = VisionCapabilitySummaryContract(
        model_id=model_capabilities.model_id or runtime.active_model_name,
        capability_source=model_capabilities.capability_source,
        context_length=model_capabilities.context_length,
        max_completion_tokens=model_capabilities.max_completion_tokens,
        input_modalities=list(model_capabilities.input_modalities),
        output_modalities=list(model_capabilities.output_modalities),
        supported_parameters=list(model_capabilities.supported_parameters),
        requested_max_tokens=requested_max_tokens,
        request_mode=request_mode,
        response_healing_enabled=response_healing_enabled,
        prompt_tokens=prompt_tokens if isinstance(prompt_tokens, int) else None,
        completion_tokens=completion_tokens if isinstance(completion_tokens, int) else None,
        total_tokens=total_tokens if isinstance(total_tokens, int) else None,
        finish_reason=str(finish_reason) if finish_reason else None,
    )
    return summary.model_dump(mode="json", exclude_none=True)


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
    policy, budget = _project_runtime_budget(runtime)
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

    try:
        await backend.prepare_for_request(request)
        backend_runtime = backend.runtime_config
        if backend_runtime is not None:
            resolver.update_runtime_config(backend_runtime)
            runtime = resolver.runtime_config
            policy, budget = _project_runtime_budget(runtime)
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
        backend_runtime = backend.runtime_config
        if backend_runtime is not None:
            resolver.update_runtime_config(backend_runtime)
            runtime = resolver.runtime_config
            policy, budget = _project_runtime_budget(runtime)
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
        result=to_contract(
            VisionAssistContract,
            {
                **payload,
                **(
                    {"capability_summary": capability_summary}
                    if (capability_summary := _bounded_capability_summary(runtime, backend)) is not None
                    else {}
                ),
            },
        ),
    )
