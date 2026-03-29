"""Tests for bounded vision prompt builders."""

from __future__ import annotations

from server.adapters.mcp.vision.backend import VisionImageInput, VisionRequest
from server.adapters.mcp.vision.prompting import (
    build_local_vision_payload_text,
    build_vision_payload_text,
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
    assert "If you can provide only one useful sentence, put it in goal_summary." in text
    assert "also populate visible_changes with 1-3 short concrete visual observations" in text
    assert "Leave likely_issues and recommended_checks empty unless you have a specific visual reason" in text
    assert "Do not use visible_changes for unchanged truth_summary facts" in text
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
    assert "Do not echo the input payload" not in external_prompt
