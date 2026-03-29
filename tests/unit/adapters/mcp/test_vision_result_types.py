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
            backend_name="transformers_local",
            model_name="Qwen/Qwen3-VL-4B-Instruct",
            goal_summary="Closer to the rounded housing goal.",
            reference_match_summary="Front silhouette now better matches the reference.",
            visible_changes=["Front face edges appear softer."],
            shape_mismatches=["Ears still look too thin."],
            proportion_mismatches=["Head is still slightly too large relative to the body."],
            likely_issues=[],
            next_corrections=["Thicken the ears slightly and reduce the head/body ratio."],
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
    assert contract.result.backend_name == "transformers_local"
    assert contract.result.model_name == "Qwen/Qwen3-VL-4B-Instruct"
    assert contract.result.shape_mismatches == ["Ears still look too thin."]
    assert contract.result.boundary_policy is not None
    assert contract.result.boundary_policy.not_truth_source is True
