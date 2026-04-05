"""Tests for bounded vision prompt builders."""

from __future__ import annotations

from server.adapters.mcp.vision.backend import VisionImageInput, VisionRequest
from server.adapters.mcp.vision.prompting import (
    build_local_vision_payload_text,
    build_vision_payload_text,
    build_vision_response_json_schema,
    build_vision_system_prompt,
)


def _request() -> VisionRequest:
    return VisionRequest(
        goal="rounded housing",
        target_object="Housing",
        images=(
            VisionImageInput(path="/tmp/before.png", role="before", label="before_1"),
            VisionImageInput(path="/tmp/after.png", role="after", label="after_1"),
            VisionImageInput(path="/tmp/ref.png", role="reference", label="ref_1"),
        ),
        prompt_hint="Return JSON only.",
        truth_summary={"dimensions": [1.0, 2.0, 3.0]},
    )


def test_local_prompt_payload_is_more_compact_and_task_focused():
    text = build_local_vision_payload_text(_request())

    assert "TASK:" in text
    assert "IMAGES:" in text
    assert "- before: before_1" in text
    assert "OUTPUT_TEMPLATE:" in text
    assert '"goal_summary"' in text
    assert '"shape_mismatches"' in text
    assert '"proportion_mismatches"' in text
    assert '"correction_focus"' in text
    assert '"next_corrections"' in text
    assert "If you can provide only one useful sentence, put it in goal_summary." in text
    assert "also populate visible_changes with 1-3 short concrete visual observations" in text
    assert "Leave likely_issues and recommended_checks empty unless you have a specific visual reason" in text
    assert "Do not use visible_changes for unchanged truth_summary facts" in text
    assert "Use shape_mismatches only for visible form/silhouette problems." in text
    assert "Use correction_focus for the 1-3 highest-priority mismatch targets to fix next." in text
    assert "Use next_corrections for 1-3 bounded next-step fixes only when they are visually justified." in text
    assert "avoid filler likely_issues and avoid generic follow-up checks" in text
    assert "Do not invent alternate top-level keys like comparison" in text
    assert "Do not repeat the input payload." in text
    assert '"goal"' not in text


def test_generic_payload_builder_keeps_full_json_structure():
    text = build_vision_payload_text(_request())

    assert '"goal": "rounded housing"' in text
    assert '"prompt_hint": "Return JSON only."' in text


def test_system_prompt_is_stricter_for_local_backends():
    local_prompt = build_vision_system_prompt(backend_kind="mlx_local")
    external_prompt = build_vision_system_prompt(backend_kind="openai_compatible_external")

    assert "Do not echo the input payload" in local_prompt
    assert "visible_changes must contain 1-3 short concrete visual items" in local_prompt
    assert "same dimensions, same center, or same volume" in local_prompt
    assert "shape_mismatches" in local_prompt
    assert "correction_focus" in local_prompt
    assert "next_corrections" in local_prompt
    assert "Do not echo the input payload" not in external_prompt


def test_local_prompt_adds_reference_guided_checkpoint_guidance_when_requested():
    request = VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(
            VisionImageInput(path="/tmp/front.png", role="after", label="target_front_after"),
            VisionImageInput(path="/tmp/ref_front.png", role="reference", label="ref_front"),
        ),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference",
    )

    local_prompt = build_local_vision_payload_text(request)

    assert "Because this is a reference-guided checkpoint comparison:" in local_prompt
    assert "correction_focus should rank the most important fixes first" in local_prompt


def test_google_family_compare_profile_uses_narrow_contract_even_on_openrouter():
    request = VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(
            VisionImageInput(path="/tmp/front.png", role="after", label="target_front_after"),
            VisionImageInput(path="/tmp/ref_front.png", role="reference", label="ref_front"),
        ),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference",
    )

    system_prompt = build_vision_system_prompt(
        backend_kind="openai_compatible_external",
        vision_contract_profile="google_family_compare",
        provider_name="openrouter",
        request=request,
    )
    payload_text = build_vision_payload_text(
        request,
        vision_contract_profile="google_family_compare",
        provider_name="openrouter",
    )
    schema = build_vision_response_json_schema(
        vision_contract_profile="google_family_compare",
        provider_name="openrouter",
        request=request,
    )

    assert "Return exactly one JSON object with only these keys:" in system_prompt
    assert (
        "Do not return visible_changes, likely_issues, recommended_checks, confidence, or captures_used."
        in system_prompt
    )
    assert '"visible_changes"' not in payload_text
    assert '"shape_mismatches"' in payload_text
    assert '"next_corrections"' in payload_text
    assert set(schema["properties"]) == {
        "goal_summary",
        "reference_match_summary",
        "shape_mismatches",
        "proportion_mismatches",
        "correction_focus",
        "next_corrections",
    }


def test_google_family_compare_profile_keeps_full_contract_for_non_checkpoint_requests():
    request = VisionRequest(
        goal="rounded housing",
        target_object="Housing",
        images=(VisionImageInput(path="/tmp/after.png", role="after", label="after_1"),),
        prompt_hint="Return JSON only.",
    )

    system_prompt = build_vision_system_prompt(
        backend_kind="openai_compatible_external",
        vision_contract_profile="google_family_compare",
        provider_name="openrouter",
        request=request,
    )
    payload_text = build_vision_payload_text(
        request,
        vision_contract_profile="google_family_compare",
        provider_name="openrouter",
    )
    schema = build_vision_response_json_schema(
        vision_contract_profile="google_family_compare",
        provider_name="openrouter",
        request=request,
    )

    assert "visible_changes" in system_prompt
    assert '"goal": "rounded housing"' in payload_text
    assert "visible_changes" in schema["properties"]
