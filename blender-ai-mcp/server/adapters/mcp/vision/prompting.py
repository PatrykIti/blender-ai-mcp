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
_REFERENCE_UNDERSTANDING_EXPECTED_KEYS = (
    "subject",
    "style",
    "required_parts",
    "non_goals",
    "construction_strategy",
    "router_handoff_hints",
    "gate_proposals",
    "visual_evidence_refs",
    "verification_requirements",
    "classification_scores",
    "segmentation_artifacts",
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


def _is_reference_understanding_request(request: VisionRequest | None) -> bool:
    if request is None:
        return False
    mode = str(request.metadata.get("mode") or "").strip().lower()
    return mode == "reference_understanding"


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


def _reference_understanding_output_template() -> str:
    template: dict[str, object] = {
        "subject": {
            "label": "low poly squirrel",
            "category": "creature",
            "confidence": 0.8,
            "uncertainty_notes": [],
        },
        "style": {
            "style_label": "low_poly_faceted",
            "confidence": 0.8,
            "notes": [],
        },
        "required_parts": [
            {
                "part_label": "body core",
                "target_label": "body_core",
                "construction_hint": "Start with a simple faceted primary mass.",
                "priority": "high",
                "source_reference_ids": [],
            }
        ],
        "non_goals": [],
        "construction_strategy": {
            "construction_path": "low_poly_facet",
            "primary_family": "modeling_mesh",
            "allowed_families": ["macro", "modeling_mesh", "inspect_only"],
            "stage_sequence": ["primary_masses", "secondary_parts", "inspect_validate"],
            "finish_policy": "preserve_facets",
        },
        "router_handoff_hints": {
            "preferred_family": "modeling_mesh",
            "allowed_guided_families": ["reference_context", "primary_masses", "secondary_parts", "inspect_validate"],
            "sculpt_policy": "hidden",
        },
        "gate_proposals": [],
        "visual_evidence_refs": [],
        "verification_requirements": [],
        "classification_scores": [],
        "segmentation_artifacts": [],
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

    if _is_reference_understanding_request(request):
        return (
            "You are a bounded reference-understanding assistant for Blender modeling.\n\n"
            "Interpret only the attached reference images and the build goal.\n"
            "You are advisory only. You are not the truth source, may not unlock tools, and may not mark gates passed.\n"
            "Use only current canonical planner families: macro, modeling_mesh, sculpt_region, inspect_only.\n"
            "Use only current canonical guided families: spatial_context, reference_context, primary_masses, secondary_parts, attachment_alignment, checkpoint_iterate, inspect_validate, finish, utility.\n"
            "Normalize draft aliases: mesh_edit -> modeling_mesh. material_finish is not a canonical family. macro_create_part is historical shorthand, not a current tool. mesh_shade_flat and macro_low_poly_* are future candidates only.\n"
            "Do not return raw Blender code, provider secrets, hidden/internal tools, passed/final-completion status, or a public router strategy tool.\n\n"
            "Return exactly one JSON object with only these keys:\n"
            "- subject\n"
            "- style\n"
            "- required_parts\n"
            "- non_goals\n"
            "- construction_strategy\n"
            "- router_handoff_hints\n"
            "- gate_proposals\n"
            "- visual_evidence_refs\n"
            "- verification_requirements\n"
            "- classification_scores\n"
            "- segmentation_artifacts\n"
        )

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


def _build_reference_understanding_payload_text(request: VisionRequest) -> str:
    image_lines = [f"- {image.role}: {image.label or image.role}" for image in request.images]
    reference_ids = [str(item) for item in request.metadata.get("reference_ids") or []]
    reference_id_lines = [f"- {reference_id}" for reference_id in reference_ids]
    parts = [
        "TASK:",
        "Understand the attached references before any major build decision is made.",
        "",
        f"GOAL: {request.goal}",
        f"TARGET_OBJECT: {request.target_object or 'none'}",
        "REFERENCE_IMAGES:",
        *image_lines,
    ]
    if reference_id_lines:
        parts.extend(["REFERENCE_IDS:", *reference_id_lines])
    parts.extend(
        [
            "",
            "Return exactly one JSON object with only these keys:",
            "- subject",
            "- style",
            "- required_parts",
            "- non_goals",
            "- construction_strategy",
            "- router_handoff_hints",
            "- gate_proposals",
            "- visual_evidence_refs",
            "- verification_requirements",
            "- classification_scores",
            "- segmentation_artifacts",
            "",
            "Rules:",
            "- advisory only: do not claim passed/final-completion truth",
            "- do not unlock tools or invent a public router strategy tool",
            "- use current planner families only: macro, modeling_mesh, sculpt_region, inspect_only",
            "- use current guided families only: spatial_context, reference_context, primary_masses, secondary_parts, attachment_alignment, checkpoint_iterate, inspect_validate, finish, utility",
            "- normalize mesh_edit to modeling_mesh",
            "- do not use material_finish as a canonical family",
            "- treat macro_create_part, mesh_shade_flat, and macro_low_poly_* as historical/future ideas, not current tools",
            "- gate_proposals stay advisory and pending-oriented",
            "- verification_requirements should use canonical MCP tool ids only",
            "OUTPUT_TEMPLATE:",
            _reference_understanding_output_template(),
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

    if _is_reference_understanding_request(request):
        return _build_reference_understanding_payload_text(request)

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

    if _is_reference_understanding_request(request):
        return _build_reference_understanding_payload_text(request)

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

    if _is_reference_understanding_request(request):
        return _REFERENCE_UNDERSTANDING_EXPECTED_KEYS

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

    if _is_reference_understanding_request(request):
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "subject": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "label": {"type": "string"},
                        "category": {
                            "type": "string",
                            "enum": [
                                "creature",
                                "hard_surface",
                                "architectural_mass",
                                "dental_surface",
                                "organic_form",
                                "unknown",
                            ],
                        },
                        "confidence": {"type": ["number", "null"]},
                        "uncertainty_notes": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["label", "category", "confidence", "uncertainty_notes"],
                },
                "style": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "style_label": {
                            "type": "string",
                            "enum": [
                                "low_poly_faceted",
                                "hard_surface",
                                "smooth_organic",
                                "architectural_mass",
                                "dental_surface",
                                "unknown",
                            ],
                        },
                        "confidence": {"type": ["number", "null"]},
                        "notes": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["style_label", "confidence", "notes"],
                },
                "required_parts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "part_label": {"type": "string"},
                            "target_label": {"type": ["string", "null"]},
                            "construction_hint": {"type": ["string", "null"]},
                            "priority": {"type": "string", "enum": ["high", "normal"]},
                            "source_reference_ids": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": [
                            "part_label",
                            "target_label",
                            "construction_hint",
                            "priority",
                            "source_reference_ids",
                        ],
                    },
                },
                "non_goals": {"type": "array", "items": {"type": "string"}},
                "construction_strategy": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "construction_path": {
                            "type": "string",
                            "enum": [
                                "low_poly_facet",
                                "hard_surface",
                                "organic_sculpt",
                                "creature_blockout",
                                "dental_surface",
                                "architectural_mass",
                                "unknown",
                            ],
                        },
                        "primary_family": {
                            "type": "string",
                            "enum": ["macro", "modeling_mesh", "sculpt_region", "inspect_only"],
                        },
                        "allowed_families": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["macro", "modeling_mesh", "sculpt_region", "inspect_only"],
                            },
                        },
                        "stage_sequence": {"type": "array", "items": {"type": "string"}},
                        "finish_policy": {
                            "type": "string",
                            "enum": ["preserve_facets", "inspect_first", "bounded_local_detail", "unknown"],
                        },
                    },
                    "required": [
                        "construction_path",
                        "primary_family",
                        "allowed_families",
                        "stage_sequence",
                        "finish_policy",
                    ],
                },
                "router_handoff_hints": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "preferred_family": {
                            "type": "string",
                            "enum": ["macro", "modeling_mesh", "sculpt_region", "inspect_only"],
                        },
                        "allowed_guided_families": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": [
                                    "spatial_context",
                                    "reference_context",
                                    "primary_masses",
                                    "secondary_parts",
                                    "attachment_alignment",
                                    "checkpoint_iterate",
                                    "inspect_validate",
                                    "finish",
                                    "utility",
                                ],
                            },
                        },
                        "sculpt_policy": {
                            "type": "string",
                            "enum": ["hidden", "local_detail_only", "allowed_or_primary"],
                        },
                    },
                    "required": ["preferred_family", "allowed_guided_families", "sculpt_policy"],
                },
                "gate_proposals": {"type": "array", "items": {"type": "object"}},
                "visual_evidence_refs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "evidence_id": {"type": "string"},
                            "source_class": {
                                "type": "string",
                                "enum": ["reference_image", "style_cue", "part_cue", "construction_hint", "gate_seed"],
                            },
                            "summary": {"type": "string"},
                            "reference_id": {"type": ["string", "null"]},
                        },
                        "required": ["evidence_id", "source_class", "summary", "reference_id"],
                    },
                },
                "verification_requirements": {
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
                "classification_scores": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "label": {"type": "string"},
                            "score": {"type": "number"},
                        },
                        "required": ["label", "score"],
                    },
                },
                "segmentation_artifacts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "artifact_id": {"type": "string"},
                            "artifact_kind": {"type": "string", "enum": ["mask", "crop", "box"]},
                            "reference_id": {"type": ["string", "null"]},
                            "summary": {"type": ["string", "null"]},
                        },
                        "required": ["artifact_id", "artifact_kind", "reference_id", "summary"],
                    },
                },
            },
            "required": list(_REFERENCE_UNDERSTANDING_EXPECTED_KEYS),
        }

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
