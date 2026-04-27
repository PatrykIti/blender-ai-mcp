"""Tests for bounded vision output parsing and repair."""

from __future__ import annotations

import json

import pytest
from server.adapters.mcp.vision.backend import VisionImageInput, VisionRequest
from server.adapters.mcp.vision.parsing import diagnose_vision_output_text, parse_vision_output_text


def _request() -> VisionRequest:
    return VisionRequest(
        goal="rounded housing",
        images=(VisionImageInput(path="/tmp/before.png", role="before", label="before_1"),),
        prompt_hint="Return JSON only.",
        truth_summary={"note": "test"},
    )


def test_parse_vision_output_accepts_fenced_json():
    text = """```json
{
  "goal_summary": "Closer to the target.",
  "reference_match_summary": null,
  "visible_changes": ["Front changed."],
  "likely_issues": [],
  "recommended_checks": [],
  "confidence": 0.5,
  "captures_used": ["before_1"]
}
```"""

    parsed = parse_vision_output_text(text, _request())

    assert parsed["goal_summary"] == "Closer to the target."
    assert parsed["captures_used"] == ["before_1"]


def test_parse_vision_output_recovers_json_from_wrapping_prose():
    text = 'Here is the result: {"goal_summary":"ok","reference_match_summary":null,"visible_changes":[],"likely_issues":[],"recommended_checks":[],"confidence":0.2,"captures_used":["before_1"]} Thanks.'

    parsed = parse_vision_output_text(text, _request())

    assert parsed["goal_summary"] == "ok"


def test_parse_vision_output_repairs_input_echo_payload():
    text = json.dumps(
        {
            "goal": "rounded housing",
            "images": [{"role": "before", "label": "before_1"}],
            "metadata": {},
        }
    )

    parsed = parse_vision_output_text(text, _request())

    assert parsed["goal_summary"] == "Model echoed the request payload instead of producing visual analysis."
    assert parsed["confidence"] == 0.0
    assert parsed["likely_issues"][0]["category"] == "backend_output"


def test_parse_vision_output_repairs_summary_alias_payload():
    text = json.dumps(
        {
            "comparison": "The after image is closer to the rounded housing target and adds the central cutout.",
        }
    )

    parsed = parse_vision_output_text(text, _request())

    assert (
        parsed["goal_summary"] == "The after image is closer to the rounded housing target and adds the central cutout."
    )
    assert parsed["visible_changes"] == []
    assert parsed["correction_focus"] == []
    assert parsed["captures_used"] == ["before_1"]


def test_parse_vision_output_backfills_visible_changes_from_goal_summary_when_explicit():
    text = json.dumps(
        {
            "goal_summary": "The after images show the Housing object with rounded edges and a softer front silhouette.",
            "reference_match_summary": None,
            "visible_changes": [],
            "likely_issues": [],
            "recommended_checks": [],
            "confidence": 0.6,
            "captures_used": ["before_1"],
        }
    )

    parsed = parse_vision_output_text(text, _request())

    assert parsed["visible_changes"] == [
        "The after images show the Housing object with rounded edges and a softer front silhouette."
    ]


def test_parse_vision_output_repairs_label_map_payload():
    text = json.dumps(
        {
            "before": "before_1",
            "after": "after_1",
            "reference": "ref_1",
        }
    )

    parsed = parse_vision_output_text(text, _request())

    assert parsed["goal_summary"] == "Model returned capture labels instead of visual analysis."
    assert parsed["confidence"] == 0.0
    assert parsed["likely_issues"][0]["category"] == "backend_output"


def test_parse_vision_output_coerces_alias_lists_and_strings():
    text = json.dumps(
        {
            "summary": "Closer overall.",
            "changes": ["Front is rounder."],
            "shape_mismatches": ["Ears still look too thin."],
            "proportion_mismatches": ["Head is still too large relative to body."],
            "correction_focus": ["Head/body ratio first."],
            "issues": ["Top edge still looks flat."],
            "next_corrections": ["Reduce the head slightly and thicken the ears."],
            "checks": ["Run scene_measure_dimensions for the cutout width."],
        }
    )

    parsed = parse_vision_output_text(text, _request())

    assert parsed["goal_summary"] == "Closer overall."
    assert parsed["visible_changes"] == ["Front is rounder."]
    assert parsed["shape_mismatches"] == ["Ears still look too thin."]
    assert parsed["proportion_mismatches"] == ["Head is still too large relative to body."]
    assert parsed["correction_focus"] == ["Head/body ratio first."]
    assert parsed["likely_issues"][0]["summary"] == "Top edge still looks flat."
    assert parsed["next_corrections"] == ["Reduce the head slightly and thicken the ears."]
    assert parsed["recommended_checks"] == []


def test_parse_vision_output_deduplicates_repeated_lists():
    text = json.dumps(
        {
            "goal_summary": "The after image shows a rounder housing.",
            "reference_match_summary": None,
            "visible_changes": ["Front is rounder.", "Front is rounder."],
            "likely_issues": [
                {"category": "reported_issue", "summary": "Top edge still looks flat.", "severity": "medium"},
                {"category": "reported_issue", "summary": "Top edge still looks flat.", "severity": "medium"},
            ],
            "recommended_checks": [
                {"tool_name": "follow_up_check", "reason": "Run a viewport check.", "priority": "normal"},
                {"tool_name": "follow_up_check", "reason": "Run a viewport check.", "priority": "normal"},
            ],
            "confidence": 0.4,
            "captures_used": ["before_1"],
        }
    )

    parsed = parse_vision_output_text(text, _request())

    assert parsed["visible_changes"] == ["Front is rounder."]
    assert len(parsed["likely_issues"]) == 1
    assert parsed["recommended_checks"] == []


def test_parse_vision_output_canonicalizes_common_check_aliases():
    text = json.dumps(
        {
            "goal_summary": "Closer overall.",
            "visible_changes": [],
            "recommended_checks": [
                {"tool_name": "check_alignment", "reason": "Confirm symmetry after the move.", "priority": "high"},
                {"tool_name": "compare_ortho_views", "reason": "Review front and side framing.", "priority": "normal"},
                {"tool_name": "scene_measure_gap", "reason": "Confirm the remaining separation.", "priority": "high"},
            ],
        }
    )

    parsed = parse_vision_output_text(text, _request())

    assert parsed["recommended_checks"] == [
        {
            "tool_name": "scene_measure_alignment",
            "reason": "Confirm symmetry after the move.",
            "priority": "high",
        },
        {
            "tool_name": "scene_get_viewport",
            "reason": "Review front and side framing.",
            "priority": "normal",
        },
        {
            "tool_name": "scene_measure_gap",
            "reason": "Confirm the remaining separation.",
            "priority": "high",
        },
    ]


def test_parse_vision_output_backfills_correction_focus_for_reference_guided_checkpoint():
    request = VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(
            VisionImageInput(path="/tmp/front.png", role="after", label="target_front_after"),
            VisionImageInput(path="/tmp/ref_front.png", role="reference", label="ref_front"),
        ),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference",
    )
    text = json.dumps(
        {
            "goal_summary": "Closer overall to the squirrel reference.",
            "reference_match_summary": "The front silhouette is closer but still too spherical.",
            "visible_changes": ["The tail arc is more visible from the front."],
            "shape_mismatches": ["Head silhouette is still too spherical."],
            "proportion_mismatches": ["Tail still reads too small relative to the body."],
            "next_corrections": ["Flatten the head silhouette slightly and enlarge the tail arc."],
            "likely_issues": [],
            "recommended_checks": [],
            "confidence": 0.6,
            "captures_used": ["target_front_after", "ref_front"],
        }
    )

    parsed = parse_vision_output_text(text, request)

    assert parsed["correction_focus"] == [
        "Head silhouette is still too spherical.",
        "Tail still reads too small relative to the body.",
        "Flatten the head silhouette slightly and enlarge the tail arc.",
    ]


def test_diagnose_vision_output_classifies_fenced_contract_json():
    text = """```json
{"goal_summary":"ok","reference_match_summary":null,"visible_changes":[],"likely_issues":[],"recommended_checks":[],"confidence":0.2,"captures_used":["before_1"]}
```"""

    diagnostics = diagnose_vision_output_text(text)

    assert diagnostics["container_shape"] == "fenced_json"
    assert diagnostics["payload_shape"] == "contract"


def test_diagnose_vision_output_classifies_summary_alias_json():
    diagnostics = diagnose_vision_output_text('{"comparison":"Closer to the target."}')

    assert diagnostics["container_shape"] == "json"
    assert diagnostics["payload_shape"] == "summary_alias"


def test_diagnose_vision_output_classifies_label_map_json():
    diagnostics = diagnose_vision_output_text('{"before":"b","after":"a","reference":"r"}')

    assert diagnostics["payload_shape"] == "label_map"


def test_diagnose_vision_output_classifies_prose_without_json():
    diagnostics = diagnose_vision_output_text("This is just prose with no JSON at all.")

    assert diagnostics["container_shape"] == "prose"
    assert diagnostics["payload_shape"] == "no_json"


def test_parse_gemini_compare_output_accepts_narrow_contract_and_backfills_defaults():
    request = VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(
            VisionImageInput(path="/tmp/front.png", role="after", label="target_front_after"),
            VisionImageInput(path="/tmp/ref_front.png", role="reference", label="ref_front"),
        ),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference",
    )
    text = json.dumps(
        {
            "goal_summary": "Closer overall to the squirrel reference.",
            "reference_match_summary": "Head shape is closer but still too round.",
            "shape_mismatches": ["Head silhouette is still too spherical."],
            "proportion_mismatches": ["Tail still reads too small relative to the body."],
            "correction_focus": ["Head silhouette", "Tail size"],
            "next_corrections": ["Flatten the head silhouette slightly and enlarge the tail arc."],
        }
    )

    parsed = parse_vision_output_text(
        text,
        request,
        vision_contract_profile="google_family_compare",
        provider_name="openrouter",
    )

    assert parsed["goal_summary"] == "Closer overall to the squirrel reference."
    assert parsed["visible_changes"] == []
    assert parsed["likely_issues"] == []
    assert parsed["recommended_checks"] == []
    assert parsed["captures_used"] == ["target_front_after", "ref_front"]


def test_parse_google_family_compare_output_repairs_truncated_json_on_openrouter():
    request = VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(
            VisionImageInput(path="/tmp/front.png", role="after", label="target_front_after"),
            VisionImageInput(path="/tmp/ref_front.png", role="reference", label="ref_front"),
        ),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference",
    )
    text = (
        '{"goal_summary":"Closer overall.","reference_match_summary":"Head is closer.",'
        '"shape_mismatches":["Head silhouette is still too spherical."],'
        '"proportion_mismatches":["Tail still reads too small relative to the body."],'
        '"correction_focus":["Head silhouette"],'
        '"next_corrections":["Flatten the head silhouette slightly"]'
    )

    parsed = parse_vision_output_text(
        text,
        request,
        vision_contract_profile="google_family_compare",
        provider_name="openrouter",
    )
    diagnostics = diagnose_vision_output_text(
        text,
        vision_contract_profile="google_family_compare",
        request=request,
        provider_name="openrouter",
    )

    assert parsed["goal_summary"] == "Closer overall."
    assert parsed["next_corrections"] == ["Flatten the head silhouette slightly"]
    assert diagnostics["payload_shape"] == "contract"
    assert diagnostics["vision_contract_profile"] == "google_family_compare"


def test_generic_full_contract_profile_does_not_repair_truncated_compare_json():
    request = VisionRequest(
        goal="low poly squirrel",
        target_object="Squirrel",
        images=(
            VisionImageInput(path="/tmp/front.png", role="after", label="target_front_after"),
            VisionImageInput(path="/tmp/ref_front.png", role="reference", label="ref_front"),
        ),
        prompt_hint="comparison_mode=stage_checkpoint_vs_reference",
    )
    text = (
        '{"goal_summary":"Closer overall.","reference_match_summary":"Head is closer.",'
        '"shape_mismatches":["Head silhouette is still too spherical."],'
        '"proportion_mismatches":["Tail still reads too small relative to the body."],'
        '"correction_focus":["Head silhouette"],'
        '"next_corrections":["Flatten the head silhouette slightly"]'
    )

    with pytest.raises(json.JSONDecodeError):
        parse_vision_output_text(
            text,
            request,
            vision_contract_profile="generic_full",
            provider_name="openrouter",
        )
