"""Tests for bounded vision output parsing and repair."""

from __future__ import annotations

import json

from server.adapters.mcp.vision.backend import VisionImageInput, VisionRequest
from server.adapters.mcp.vision.parsing import parse_vision_output_text


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

    assert parsed["goal_summary"] == "The after image is closer to the rounded housing target and adds the central cutout."
    assert parsed["visible_changes"] == []
    assert parsed["captures_used"] == ["before_1"]


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
            "issues": ["Top edge still looks flat."],
            "checks": ["Run scene_measure_dimensions for the cutout width."],
        }
    )

    parsed = parse_vision_output_text(text, _request())

    assert parsed["goal_summary"] == "Closer overall."
    assert parsed["visible_changes"] == ["Front is rounder."]
    assert parsed["likely_issues"][0]["summary"] == "Top edge still looks flat."
    assert parsed["recommended_checks"][0]["tool_name"] == "follow_up_check"
