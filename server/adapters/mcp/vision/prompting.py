# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Prompt-building helpers for bounded vision backends."""

from __future__ import annotations

import json

from .backend import VisionRequest

_EXPECTED_KEYS = (
    "goal_summary",
    "reference_match_summary",
    "visible_changes",
    "likely_issues",
    "recommended_checks",
    "confidence",
    "captures_used",
)


def _local_output_template(request: VisionRequest) -> str:
    labels = [image.label or image.role for image in request.images]
    template = {
        "goal_summary": "One short sentence about whether the after images move toward the goal/reference.",
        "reference_match_summary": None,
        "visible_changes": [],
        "likely_issues": [],
        "recommended_checks": [],
        "confidence": None,
        "captures_used": labels,
    }
    return json.dumps(template, ensure_ascii=True, indent=2)


def build_vision_system_prompt(*, backend_kind: str) -> str:
    """Return the bounded system prompt, tuned slightly by backend family."""

    shared = (
        "You are a bounded vision assistant for Blender modeling.\n\n"
        "You are not the truth source. Use images only to interpret visible change and compare against the goal/reference.\n"
        "Do not claim geometric correctness from images alone. Recommend deterministic follow-up checks when correctness matters.\n\n"
        "Return exactly one JSON object with keys:\n"
        "- goal_summary: string\n"
        "- reference_match_summary: string or null\n"
        "- visible_changes: string[]\n"
        '- likely_issues: [{"category": string, "summary": string, "severity": "high"|"medium"|"low"}]\n'
        '- recommended_checks: [{"tool_name": string, "reason": string, "priority": "high"|"normal"}]\n'
        "- confidence: number or null\n"
        "- captures_used: string[]\n"
    )
    if backend_kind in {"transformers_local", "mlx_local"}:
        return (
            shared
            + "\n"
            + "Do not explain the JSON. Do not echo the input payload. "
            + "Do not wrap the result in markdown unless unavoidable. "
            + "If signal is weak, still return the required JSON shape with conservative values.\n"
        )
    return shared


def build_vision_payload_text(request: VisionRequest) -> str:
    """Serialize the bounded vision input payload."""

    payload = {
        "goal": request.goal,
        "target_object": request.target_object,
        "prompt_hint": request.prompt_hint,
        "truth_summary": request.truth_summary,
        "metadata": request.metadata,
        "images": [{"role": image.role, "label": image.label} for image in request.images],
    }
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2)


def build_local_vision_payload_text(request: VisionRequest) -> str:
    """Return a shorter local-model-oriented payload to reduce echoing."""

    image_lines = [
        f"- {image.role}: {image.label or image.role}"
        for image in request.images
    ]
    truth_summary = request.truth_summary or {}
    truth_lines = []
    if isinstance(truth_summary, dict):
        for key, value in truth_summary.items():
            truth_lines.append(f"- {key}: {value}")

    parts = [
        "TASK:",
        "Compare before/after images against the goal and any references.",
        "",
        f"GOAL: {request.goal}",
        f"TARGET_OBJECT: {request.target_object or 'none'}",
        f"PROMPT_HINT: {request.prompt_hint or 'none'}",
        "IMAGES:",
        *image_lines,
    ]
    if truth_lines:
        parts.extend(["TRUTH_SUMMARY:", *truth_lines])
    parts.extend(
        [
            "",
            "Return exactly one JSON object with the required keys only.",
            "If you can provide only one useful sentence, put it in goal_summary.",
            "Do not repeat the input payload.",
            "Do not invent alternate top-level keys like comparison, summary, analysis, before, after, or reference.",
            "If uncertain, keep fields conservative but present.",
            "OUTPUT_TEMPLATE:",
            _local_output_template(request),
        ]
    )
    return "\n".join(parts)


def expected_json_keys() -> tuple[str, ...]:
    """Expose the canonical required JSON keys for tests and parse repair."""

    return _EXPECTED_KEYS
