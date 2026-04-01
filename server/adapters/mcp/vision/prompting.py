# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Prompt-building helpers for bounded vision backends."""

from __future__ import annotations

import json

from .backend import VisionRequest

_EXPECTED_KEYS = (
    "goal_summary",
    "reference_match_summary",
    "visible_changes",
    "shape_mismatches",
    "proportion_mismatches",
    "correction_focus",
    "likely_issues",
    "next_corrections",
    "recommended_checks",
    "confidence",
    "captures_used",
)

_REFERENCE_GUIDED_CHECKPOINT_MODES = (
    "comparison_mode=checkpoint_vs_reference",
    "comparison_mode=current_view_checkpoint",
    "comparison_mode=stage_checkpoint_vs_reference",
)


def _is_reference_guided_checkpoint(request: VisionRequest) -> bool:
    prompt_hint = (request.prompt_hint or "").lower()
    has_reference = any(image.role == "reference" for image in request.images)
    return has_reference and any(mode in prompt_hint for mode in _REFERENCE_GUIDED_CHECKPOINT_MODES)


def _local_output_template(request: VisionRequest) -> str:
    labels = [image.label or image.role for image in request.images]
    template = {
        "goal_summary": "One short sentence about whether the after images move toward the goal/reference.",
        "reference_match_summary": None,
        "visible_changes": [],
        "shape_mismatches": [],
        "proportion_mismatches": [],
        "correction_focus": [],
        "likely_issues": [],
        "next_corrections": [],
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
        "- shape_mismatches: string[]\n"
        "- proportion_mismatches: string[]\n"
        "- correction_focus: string[]\n"
        '- likely_issues: [{"category": string, "summary": string, "severity": "high"|"medium"|"low"}]\n'
        "- next_corrections: string[]\n"
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
            + "If there is a visible before/after difference, visible_changes must contain 1-3 short concrete visual items. "
            + "Leave visible_changes empty only when there is truly no visible change. "
            + "Do not use visible_changes for unchanged facts from truth_summary such as same dimensions, same center, or same volume. "
            + "Use shape_mismatches only for visible form/silhouette problems. "
            + "Use proportion_mismatches only for visible size/ratio relationship problems. "
            + "Use correction_focus for the 1-3 highest-priority mismatch targets to fix next. "
            + "Use next_corrections for 1-3 bounded next-step corrections only when they are visually justified. "
            + "Do not present next_corrections as proof that the fix is safe or correct; deterministic checks still decide correctness. "
            + "Leave likely_issues and recommended_checks empty unless there is a specific visible risk or a clearly valuable deterministic follow-up check. "
            + "For easy smoke or obvious progression cases, avoid filler likely_issues and avoid generic follow-up checks. "
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

    image_lines = [f"- {image.role}: {image.label or image.role}" for image in request.images]
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
    reference_guided_checkpoint = _is_reference_guided_checkpoint(request)
    parts.extend(
        [
            "",
            "Return exactly one JSON object with the required keys only.",
            "If you can provide only one useful sentence, put it in goal_summary.",
            "If the after image(s) visibly changed, also populate visible_changes with 1-3 short concrete visual observations.",
            "Do not use visible_changes for unchanged truth_summary facts such as same dimensions, same center, or same volume.",
            "Use shape_mismatches only for visible form/silhouette problems.",
            "Use proportion_mismatches only for visible size/ratio problems.",
            "Use correction_focus for the 1-3 highest-priority mismatch targets to fix next.",
            "Use next_corrections for 1-3 bounded next-step fixes only when they are visually justified.",
            "Do not present next_corrections as proof that the fix is safe or correct; deterministic checks still decide correctness.",
            "Leave likely_issues and recommended_checks empty unless you have a specific visual reason to add them.",
            "For easy smoke or obvious progression cases, avoid filler likely_issues and avoid generic follow-up checks.",
            "Do not repeat the input payload.",
            "Do not invent alternate top-level keys like comparison, summary, analysis, before, after, or reference.",
            "If uncertain, keep fields conservative but present.",
            "OUTPUT_TEMPLATE:",
            _local_output_template(request),
        ]
    )
    if reference_guided_checkpoint:
        parts.extend(
            [
                "Because this is a reference-guided checkpoint comparison:",
                "- populate reference_match_summary if the references meaningfully inform the comparison",
                "- prefer concrete silhouette/proportion mismatches over generic praise",
                "- correction_focus should rank the most important fixes first",
                "- next_corrections should stay tightly aligned with the mismatches you listed",
            ]
        )
    return "\n".join(parts)


def expected_json_keys() -> tuple[str, ...]:
    """Expose the canonical required JSON keys for tests and parse repair."""

    return _EXPECTED_KEYS


def build_vision_response_json_schema() -> dict[str, object]:
    """Return a provider-agnostic JSON Schema for bounded vision responses."""

    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "goal_summary": {"type": "string"},
            "reference_match_summary": {"type": ["string", "null"]},
            "visible_changes": {"type": "array", "items": {"type": "string"}},
            "shape_mismatches": {"type": "array", "items": {"type": "string"}},
            "proportion_mismatches": {"type": "array", "items": {"type": "string"}},
            "correction_focus": {"type": "array", "items": {"type": "string"}},
            "likely_issues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "category": {"type": "string"},
                        "summary": {"type": "string"},
                        "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                    },
                    "required": ["category", "summary"],
                },
            },
            "next_corrections": {"type": "array", "items": {"type": "string"}},
            "recommended_checks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "tool_name": {"type": "string"},
                        "reason": {"type": "string"},
                        "priority": {"type": "string", "enum": ["high", "normal"]},
                    },
                    "required": ["tool_name", "reason"],
                },
            },
            "confidence": {"type": ["number", "null"]},
            "captures_used": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["goal_summary", "visible_changes", "captures_used"],
    }
