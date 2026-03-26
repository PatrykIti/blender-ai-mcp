"""Tests for bounded vision-assist result contracts."""

from __future__ import annotations

from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantRunResult,
    VisionAssistContract,
    to_vision_assistant_contract,
)


def test_vision_assistant_contract_wraps_structured_result():
    outcome = AssistantRunResult(
        status="success",
        assistant_name="vision_assist",
        message="vision completed",
        budget=AssistantBudgetContract(
            max_input_chars=16000,
            max_messages=1,
            max_tokens=400,
            tool_budget=0,
        ),
        capability_source="local_runtime",
        result=VisionAssistContract(
            backend_kind="transformers_local",
            model_name="Qwen/Qwen3-VL-4B-Instruct",
            goal_summary="Closer to the rounded housing goal.",
            reference_match_summary="Front silhouette now better matches the reference.",
            visible_changes=["Front face edges appear softer."],
            likely_issues=[],
            recommended_checks=[],
            confidence=0.61,
            captures_used=["front_before", "front_after", "reference_main"],
        ),
    )

    contract = to_vision_assistant_contract(outcome)

    assert contract.status == "success"
    assert contract.capability_source == "local_runtime"
    assert contract.result is not None
    assert contract.result.backend_kind == "transformers_local"
    assert contract.result.model_name == "Qwen/Qwen3-VL-4B-Instruct"
