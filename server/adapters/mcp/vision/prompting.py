# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Prompt-building helpers for bounded vision backends."""

from __future__ import annotations

import json

from .backend import VisionRequest
from .config import VisionContractProfile

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
_GEMINI_COMPARE_EXPECTED_KEYS = (
    "goal_summary",
    "reference_match_summary",
    "shape_mismatches",
    "proportion_mismatches",
    "correction_focus",
    "next_corrections",
)

_REFERENCE_GUIDED_CHECKPOINT_MODES = (
    "comparison_mode=checkpoint_vs_reference",
    "comparison_mode=current_view_checkpoint",
    "comparison_mode=stage_checkpoint_vs_reference",
)
_DEFAULT_VISION_CONTRACT_PROFILE: VisionContractProfile = "generic_full"


def _is_reference_guided_checkpoint(request: VisionRequest) -> bool:
    prompt_hint = (request.prompt_hint or "").lower()
    has_reference = any(image.role == "reference" for image in request.images)
    return has_reference and any(mode in prompt_hint for mode in _REFERENCE_GUIDED_CHECKPOINT_MODES)


def resolve_vision_contract_profile(
    *,
    vision_contract_profile: VisionContractProfile | None = None,
    provider_name: str | None = None,
) -> VisionContractProfile:
    """Resolve one prompt/parser contract profile with backward-compatible provider fallback."""

    if vision_contract_profile is not None:
        return vision_contract_profile
    if provider_name == "google_ai_studio":
        return "google_family_compare"
    return _DEFAULT_VISION_CONTRACT_PROFILE


def _uses_google_family_compare_contract(
    *,
    vision_contract_profile: VisionContractProfile | None,
    provider_name: str | None,
    request: VisionRequest | None,
) -> bool:
    resolved_profile = resolve_vision_contract_profile(
        vision_contract_profile=vision_contract_profile,
        provider_name=provider_name,
    )
    return (
        resolved_profile == "google_family_compare" and request is not None and _is_reference_guided_checkpoint(request)
    )


def _local_output_template(request: VisionRequest) -> str:
    labels = [image.label or image.role for image in request.images]
    template: dict[str, object] = {
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


def _gemini_compare_output_template() -> str:
    template: dict[str, object] = {
        "goal_summary": "One short sentence about whether the current checkpoint moves toward the goal/reference.",
        "reference_match_summary": None,
        "shape_mismatches": [],
        "proportion_mismatches": [],
        "correction_focus": [],
        "next_corrections": [],
    }
    return json.dumps(template, ensure_ascii=True, indent=2)


def build_vision_system_prompt(
    *,
    backend_kind: str,
    vision_contract_profile: VisionContractProfile | None = None,
    provider_name: str | None = None,
    request: VisionRequest | None = None,
) -> str:
    """Return the bounded system prompt, tuned slightly by backend family."""

    if _uses_google_family_compare_contract(
        vision_contract_profile=vision_contract_profile,
        provider_name=provider_name,
        request=request,
    ):
        return (
            "You are a bounded vision assistant for Blender modeling.\n\n"
            "This request is a reference-guided checkpoint comparison for a Google-family vision contract.\n"
            "You are not the truth source. Use images only to compare the current checkpoint against the goal and references.\n"
            "Do not claim geometric correctness from images alone.\n\n"
            "Return exactly one JSON object with only these keys:\n"
            "- goal_summary: string\n"
            "- reference_match_summary: string or null\n"
            "- shape_mismatches: string[]\n"
            "- proportion_mismatches: string[]\n"
            "- correction_focus: string[]\n"
            "- next_corrections: string[]\n\n"
            "Do not return visible_changes, likely_issues, recommended_checks, confidence, or captures_used.\n"
            "Do not echo the input payload. Do not wrap the result in markdown.\n"
            "Use shape_mismatches only for visible form/silhouette problems.\n"
            "Use proportion_mismatches only for visible size/ratio problems.\n"
            "Use correction_focus for the 1-3 highest-priority mismatch targets to fix next.\n"
            "Use next_corrections for 1-3 bounded next-step fixes that stay tightly aligned with those mismatches.\n"
            "If the signal is weak, keep the arrays conservative but still return the required JSON shape.\n"
        )

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
            + "If you do return recommended_checks, use only canonical MCP tool ids such as scene_measure_gap, scene_measure_overlap, scene_measure_alignment, scene_assert_contact, or scene_get_viewport. "
            + "For easy smoke or obvious progression cases, avoid filler likely_issues and avoid generic follow-up checks. "
            + "If signal is weak, still return the required JSON shape with conservative values.\n"
        )
    return shared


def _build_gemini_compare_payload_text(request: VisionRequest) -> str:
    image_lines = [f"- {image.role}: {image.label or image.role}" for image in request.images]
    truth_summary = request.truth_summary or {}
    truth_lines = []
    if isinstance(truth_summary, dict):
        for key, value in truth_summary.items():
            truth_lines.append(f"- {key}: {value}")

    parts = [
        "TASK:",
        "Compare the current checkpoint images against the active goal and the attached references.",
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
            "Return exactly one JSON object with only these keys:",
            "- goal_summary",
            "- reference_match_summary",
            "- shape_mismatches",
            "- proportion_mismatches",
            "- correction_focus",
            "- next_corrections",
            "Do not return visible_changes, likely_issues, recommended_checks, confidence, or captures_used.",
            "Do not repeat the input payload.",
            "Prefer concrete silhouette/proportion mismatches over generic praise.",
            "correction_focus should rank the most important fixes first.",
            "next_corrections should stay tightly aligned with the mismatches you listed.",
            "OUTPUT_TEMPLATE:",
            _gemini_compare_output_template(),
        ]
    )
    return "\n".join(parts)


def build_vision_payload_text(
    request: VisionRequest,
    *,
    vision_contract_profile: VisionContractProfile | None = None,
    provider_name: str | None = None,
) -> str:
    """Serialize the bounded vision input payload."""

    if _uses_google_family_compare_contract(
        vision_contract_profile=vision_contract_profile,
        provider_name=provider_name,
        request=request,
    ):
        return _build_gemini_compare_payload_text(request)

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
                "- if you recommend deterministic checks, use only canonical MCP tool ids rather than invented labels",
            ]
        )
    return "\n".join(parts)


def expected_json_keys(
    *,
    vision_contract_profile: VisionContractProfile | None = None,
    provider_name: str | None = None,
    request: VisionRequest | None = None,
) -> tuple[str, ...]:
    """Expose the canonical required JSON keys for tests and parse repair."""

    if _uses_google_family_compare_contract(
        vision_contract_profile=vision_contract_profile,
        provider_name=provider_name,
        request=request,
    ):
        return _GEMINI_COMPARE_EXPECTED_KEYS
    return _EXPECTED_KEYS


def build_vision_response_json_schema(
    *,
    vision_contract_profile: VisionContractProfile | None = None,
    provider_name: str | None = None,
    request: VisionRequest | None = None,
) -> dict[str, object]:
    """Return a provider-agnostic JSON Schema for bounded vision responses."""

    if _uses_google_family_compare_contract(
        vision_contract_profile=vision_contract_profile,
        provider_name=provider_name,
        request=request,
    ):
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "goal_summary": {"type": "string"},
                "reference_match_summary": {"type": ["string", "null"]},
                "shape_mismatches": {"type": "array", "items": {"type": "string"}},
                "proportion_mismatches": {"type": "array", "items": {"type": "string"}},
                "correction_focus": {"type": "array", "items": {"type": "string"}},
                "next_corrections": {"type": "array", "items": {"type": "string"}},
            },
            "required": list(_GEMINI_COMPARE_EXPECTED_KEYS),
        }

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
                    "required": ["category", "summary", "severity"],
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
                    "required": ["tool_name", "reason", "priority"],
                },
            },
            "confidence": {"type": ["number", "null"]},
            "captures_used": {"type": "array", "items": {"type": "string"}},
        },
        "required": list(_EXPECTED_KEYS),
    }
