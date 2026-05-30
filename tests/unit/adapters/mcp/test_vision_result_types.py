"""Tests for bounded vision-assist result contracts."""

from __future__ import annotations

from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantRunResult,
    VisionAssistContract,
    VisionCapabilitySummaryContract,
    VisionPacketStatusContract,
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
            correction_focus=["Head/body ratio", "Ear thickness"],
            likely_issues=[],
            next_corrections=["Thicken the ears slightly and reduce the head/body ratio."],
            recommended_checks=[],
            packet_guidance=VisionPacketStatusContract(
                packet_status="ready",
                status_reason=None,
                ranking_recommendation="rank",
            ),
            capability_summary=VisionCapabilitySummaryContract(
                model_id="Qwen/Qwen3-VL-4B-Instruct",
                capability_source="fallback_registry",
                context_length=128_000,
                max_completion_tokens=8_192,
                input_modalities=["image", "text"],
                output_modalities=["text"],
                supported_parameters=["max_tokens", "response_format"],
                requested_max_tokens=4_096,
                request_mode="json_object",
                response_healing_enabled=True,
            ),
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
    assert contract.result.correction_focus == ["Head/body ratio", "Ear thickness"]
    assert contract.result.packet_guidance is not None
    assert contract.result.packet_guidance.packet_status == "ready"
    assert contract.result.packet_guidance.ranking_recommendation == "rank"
    assert contract.result.capability_summary is not None
    assert contract.result.capability_summary.model_id == "Qwen/Qwen3-VL-4B-Instruct"
    assert contract.result.capability_summary.capability_source == "fallback_registry"
    assert contract.result.capability_summary.context_length == 128_000
    assert contract.result.capability_summary.max_completion_tokens == 8_192
    assert contract.result.capability_summary.input_modalities == ["image", "text"]
    assert contract.result.capability_summary.output_modalities == ["text"]
    assert contract.result.capability_summary.supported_parameters == ["max_tokens", "response_format"]
    assert contract.result.capability_summary.requested_max_tokens == 4_096
    assert contract.result.capability_summary.request_mode == "json_object"
    assert contract.result.capability_summary.response_healing_enabled is True
    assert contract.result.boundary_policy is not None
    assert contract.result.boundary_policy.not_truth_source is True


def test_vision_assist_contract_fields_carry_descriptions():
    fields = VisionAssistContract.model_fields
    # The near-synonymous compare lists and the scalar summaries must each be
    # self-describing so the orchestrating LLM can disambiguate them by schema.
    for name in (
        "goal_summary",
        "reference_match_summary",
        "visible_changes",
        "shape_mismatches",
        "proportion_mismatches",
        "correction_focus",
        "next_corrections",
        "recommended_checks",
        "likely_issues",
        "confidence",
    ):
        description = fields[name].description
        assert description, f"{name} is missing a Field description"

    # Confidence must be marked non-authoritative inline.
    confidence_description = (fields["confidence"].description or "").lower()
    assert "non-authoritative" in confidence_description
    assert "not" in confidence_description


def test_vision_assist_contract_descriptions_do_not_change_defaults():
    # Descriptions are additive metadata: the empty-list / None defaults are
    # unchanged so existing serialized payloads stay valid.
    contract = VisionAssistContract(goal_summary="ok", visible_changes=[])
    assert contract.shape_mismatches == []
    assert contract.proportion_mismatches == []
    assert contract.recommended_checks == []
    assert contract.confidence is None
    assert contract.boundary_policy.not_truth_source is True
