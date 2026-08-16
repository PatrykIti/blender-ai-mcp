# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Bounded server-side sampling assistants for analysis and recovery flows."""

from __future__ import annotations

import json
from typing import Any, Sequence, TypeVar, cast

from fastmcp import Context

from server.adapters.mcp.context_utils import ctx_request_id, ctx_sampling_capability
from server.adapters.mcp.contracts.base import MCPContract, to_contract
from server.adapters.mcp.sampling.result_types import (
    AssistantCapabilitySource,
    AssistantPolicy,
    AssistantRunResult,
    InspectionSummaryContract,
    RepairSuggestionContract,
)
from server.adapters.mcp.tasks.task_bridge import is_background_task_context

ResultContractT = TypeVar("ResultContractT", bound=MCPContract)

_ALLOWED_RESPONSIBILITIES = {
    "inspection_summary",
    "repair_suggestion",
    "diagnostic_summary",
    "vision_assist",
}

INSPECTION_SUMMARIZER_POLICY = AssistantPolicy(
    assistant_name="inspection_summarizer",
    responsibility="inspection_summary",
    max_input_chars=14000,
    max_messages=1,
    max_tokens=320,
)

REPAIR_SUGGESTER_POLICY = AssistantPolicy(
    assistant_name="repair_suggester",
    responsibility="repair_suggestion",
    max_input_chars=7000,
    max_messages=1,
    max_tokens=280,
)


def _estimate_message_chars(messages: Sequence[str]) -> int:
    """Estimate the serialized size of the assistant input."""

    return sum(len(message) for message in messages)


def _compact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Trim large paged payloads deterministically before sampling."""

    compact = dict(payload)
    items = compact.get("items")
    if isinstance(items, list) and len(items) > 25:
        compact["items"] = items[:25]
        metadata = compact.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
        metadata = dict(metadata)
        metadata["assistant_truncated_items"] = len(items) - 25
        compact["metadata"] = metadata
    return compact


def _json_payload(payload: dict[str, Any]) -> str:
    """Serialize assistant input payloads deterministically."""

    return json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2)


def _masked_message(policy: AssistantPolicy) -> str:
    """Return the stable masked-error message for a policy."""

    return f"{policy.assistant_name} failed during bounded sampling. Error details were masked."


async def run_typed_assistant(
    ctx: Context,
    *,
    policy: AssistantPolicy,
    messages: Sequence[str],
    system_prompt: str,
    result_type: type[ResultContractT],
    tools: Sequence[Any] | None = None,
) -> AssistantRunResult[ResultContractT]:
    """Run one bounded assistant with typed structured output and fallbacks."""

    budget = policy.to_budget_contract()
    request_id = ctx_request_id(ctx)
    requested_tools = len(tools or ())

    if policy.responsibility not in _ALLOWED_RESPONSIBILITIES:
        return AssistantRunResult(
            status="rejected_by_policy",
            assistant_name=policy.assistant_name,
            message="Assistant responsibility is outside the allowed bounded scope.",
            budget=budget,
            request_id=request_id,
            capability_source="unknown",
            rejection_reason="forbidden_responsibility",
        )

    if not messages:
        return AssistantRunResult(
            status="rejected_by_policy",
            assistant_name=policy.assistant_name,
            message="Assistant input is empty.",
            budget=budget,
            request_id=request_id,
            capability_source="unknown",
            rejection_reason="empty_messages",
        )

    if is_background_task_context(ctx) and not policy.allow_in_background:
        return AssistantRunResult(
            status="rejected_by_policy",
            assistant_name=policy.assistant_name,
            message="Sampling assistants stay bound to foreground MCP requests.",
            budget=budget,
            request_id=request_id,
            capability_source="unknown",
            rejection_reason="background_request_forbidden",
        )

    if len(messages) > policy.max_messages:
        return AssistantRunResult(
            status="rejected_by_policy",
            assistant_name=policy.assistant_name,
            message="Assistant input exceeded the allowed message budget.",
            budget=budget,
            request_id=request_id,
            capability_source="unknown",
            rejection_reason="message_budget_exceeded",
        )

    if requested_tools > policy.tool_budget:
        return AssistantRunResult(
            status="rejected_by_policy",
            assistant_name=policy.assistant_name,
            message="Assistant tool usage exceeded the allowed budget.",
            budget=budget,
            request_id=request_id,
            capability_source="unknown",
            rejection_reason="tool_budget_exceeded",
        )

    if _estimate_message_chars(messages) > policy.max_input_chars:
        return AssistantRunResult(
            status="rejected_by_policy",
            assistant_name=policy.assistant_name,
            message="Assistant input exceeded the allowed character budget.",
            budget=budget,
            request_id=request_id,
            capability_source="unknown",
            rejection_reason="input_budget_exceeded",
        )

    available, capability_source, rejection_reason = ctx_sampling_capability(
        ctx,
        needs_tools=bool(requested_tools),
    )
    if not available:
        resolved_capability_source = cast(
            AssistantCapabilitySource,
            capability_source or "unavailable",
        )
        return AssistantRunResult(
            status="unavailable",
            assistant_name=policy.assistant_name,
            message="Sampling is unavailable on the active MCP request.",
            budget=budget,
            request_id=request_id,
            capability_source=resolved_capability_source,
            rejection_reason=rejection_reason,
        )

    try:
        sampled = await ctx.sample(
            list(messages),
            system_prompt=system_prompt,
            temperature=policy.temperature,
            max_tokens=policy.max_tokens,
            tools=tools,
            result_type=result_type,
            mask_error_details=policy.mask_error_details,
            tool_concurrency=1 if requested_tools else None,
        )
    except Exception as exc:
        error_message = str(exc)
        if "does not support sampling" in error_message:
            return AssistantRunResult(
                status="unavailable",
                assistant_name=policy.assistant_name,
                message="Sampling is unavailable on the active MCP request.",
                budget=budget,
                request_id=request_id,
                capability_source="unavailable",
                rejection_reason="sampling_capability_missing",
            )

        resolved_capability_source = cast(
            AssistantCapabilitySource,
            capability_source or "unknown",
        )
        return AssistantRunResult(
            status="masked_error",
            assistant_name=policy.assistant_name,
            message=_masked_message(policy) if policy.mask_error_details else error_message,
            budget=budget,
            request_id=request_id,
            capability_source=resolved_capability_source,
            rejection_reason="sampling_execution_failed",
        )

    resolved_capability_source = cast(
        AssistantCapabilitySource,
        capability_source or "unknown",
    )
    return AssistantRunResult(
        status="success",
        assistant_name=policy.assistant_name,
        message=f"{policy.assistant_name} completed.",
        budget=budget,
        request_id=request_id,
        capability_source=resolved_capability_source,
        result=to_contract(result_type, sampled.result),
    )


async def run_inspection_summary_assistant(
    ctx: Context,
    *,
    action: str,
    object_name: str | None,
    payload: dict[str, Any],
) -> AssistantRunResult[InspectionSummaryContract]:
    """Summarize an inspection contract without becoming the truth authority."""

    compact_payload = _compact_payload(payload)
    assistant_input = {
        "action": action,
        "object_name": object_name,
        "payload": compact_payload,
        "boundary_rules": {
            "truth_source": "inspection_contract",
            "no_new_scene_truth": True,
            "no_destructive_planning": True,
        },
    }
    system_prompt = (
        "You are a bounded Blender inspection summarizer. "
        "Summarize only the supplied inspection contract. "
        "Do not invent scene state, do not claim verification beyond the payload, "
        "and do not propose destructive modeling plans."
    )
    message = f"Produce a compact structured summary for this inspection payload.\n{_json_payload(assistant_input)}"
    return await run_typed_assistant(
        ctx,
        policy=INSPECTION_SUMMARIZER_POLICY,
        messages=(message,),
        system_prompt=system_prompt,
        result_type=InspectionSummaryContract,
    )


async def run_repair_suggestion_assistant(
    ctx: Context,
    *,
    diagnostics: dict[str, Any],
) -> AssistantRunResult[RepairSuggestionContract]:
    """Draft bounded next-step repair guidance from router/runtime diagnostics."""

    assistant_input = {
        "diagnostics": diagnostics,
        "boundary_rules": {
            "truth_source": "router_diagnostics",
            "inspection_required_for_scene_truth": True,
            "must_not_replace_router_policy": True,
            "must_not_execute_actions": True,
        },
    }
    system_prompt = (
        "You are a bounded Blender repair suggester. "
        "Use only the provided diagnostics to draft safe next actions. "
        "Do not claim that a Blender result is correct unless diagnostics say so, "
        "and escalate to inspection when scene truth is uncertain."
    )
    message = (
        f"Draft structured repair guidance for this router/runtime diagnostic state.\n{_json_payload(assistant_input)}"
    )
    return await run_typed_assistant(
        ctx,
        policy=REPAIR_SUGGESTER_POLICY,
        messages=(message,),
        system_prompt=system_prompt,
        result_type=RepairSuggestionContract,
    )


__all__ = [
    "INSPECTION_SUMMARIZER_POLICY",
    "REPAIR_SUGGESTER_POLICY",
    "run_inspection_summary_assistant",
    "run_repair_suggestion_assistant",
    "run_typed_assistant",
]
