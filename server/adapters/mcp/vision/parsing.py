# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Parsing and repair helpers for bounded vision backend outputs."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from .backend import VisionRequest
from .config import VisionContractProfile
from .prompting import (
    _is_reference_classification_request,
    _is_reference_packet_compare_request,
    _is_reference_understanding_request,
    expected_json_keys,
    resolve_vision_contract_profile,
)
from .reference_gates import derive_tail_profile_gate_proposals

_SUMMARY_ALIASES = ("comparison", "summary", "analysis", "description", "result")
_VISIBLE_CHANGES_ALIASES = ("changes", "visible_differences", "differences")
_SHAPE_MISMATCHES_ALIASES = ("shape_mismatches", "form_mismatches", "silhouette_mismatches")
_PROPORTION_MISMATCHES_ALIASES = ("proportion_mismatches", "ratio_mismatches", "size_mismatches")
_CORRECTION_FOCUS_ALIASES = ("correction_focus", "priority_mismatches", "priority_fixes", "focus_areas")
_LIKELY_ISSUES_ALIASES = ("issues", "problems", "risks")
_NEXT_CORRECTIONS_ALIASES = ("next_corrections", "suggested_corrections", "corrections")
_RECOMMENDED_CHECKS_ALIASES = ("checks", "follow_up_checks", "deterministic_checks", "recommended_tools")
_CANONICAL_CHECK_TOOL_MAP: dict[str, str] = {
    "inspect_scene": "scene_inspect",
    "check_alignment": "scene_measure_alignment",
    "measure_alignment": "scene_measure_alignment",
    "measure_gap": "scene_measure_gap",
    "measure_overlap": "scene_measure_overlap",
    "assert_contact": "scene_assert_contact",
    "assert_symmetry": "scene_assert_symmetry",
    "assert_proportion": "scene_assert_proportion",
    "assert_dimensions": "scene_assert_dimensions",
    "compare_ortho_views": "scene_get_viewport",
    "viewport_check": "scene_get_viewport",
    "check_viewport": "scene_get_viewport",
}
_CANONICAL_CHECK_TOOLS: set[str] = {
    "scene_inspect",
    "scene_get_viewport",
    "scene_get_bounding_box",
    "scene_measure_dimensions",
    "scene_measure_gap",
    "scene_measure_alignment",
    "scene_measure_overlap",
    "scene_assert_contact",
    "scene_assert_dimensions",
    "scene_assert_containment",
    "scene_assert_symmetry",
    "scene_assert_proportion",
}
_LABEL_MAP_KEYS = {"before", "after", "reference"}
_VISIBLE_CHANGE_GOAL_SUMMARY_HINTS = (
    "the after image shows",
    "the after images show",
    "after image shows",
    "after images show",
)
_REFERENCE_GUIDED_CHECKPOINT_HINTS = (
    "comparison_mode=checkpoint_vs_reference",
    "comparison_mode=current_view_checkpoint",
    "comparison_mode=stage_checkpoint_vs_reference",
)
_UNHELPFUL_CORRECTION_SNIPPETS = (
    "same dimensions",
    "same center",
    "same volume",
    "center unchanged",
    "volume unchanged",
    "bounding box unchanged",
)
_PACKET_CLEAN_HINTS = (
    "looks visually clean",
    "visually acceptable",
    "no dominant",
    "no clear mismatch",
    "matches the reference",
    "match the reference",
    "aligned with the reference",
    "no correction needed",
)
_REFERENCE_UNDERSTANDING_STYLE_VALUES = {
    "low_poly_faceted",
    "hard_surface",
    "smooth_organic",
    "architectural_mass",
    "dental_surface",
    "unknown",
}
_REFERENCE_UNDERSTANDING_CATEGORY_VALUES = {
    "creature",
    "hard_surface",
    "architectural_mass",
    "dental_surface",
    "organic_form",
    "unknown",
}
_REFERENCE_UNDERSTANDING_CONSTRUCTION_PATH_VALUES = {
    "low_poly_facet",
    "hard_surface",
    "organic_sculpt",
    "creature_blockout",
    "dental_surface",
    "architectural_mass",
    "unknown",
}
_REFERENCE_UNDERSTANDING_FINISH_POLICY_VALUES = {
    "preserve_facets",
    "inspect_first",
    "bounded_local_detail",
    "unknown",
}
_REFERENCE_UNDERSTANDING_FAMILY_VALUES = {"macro", "modeling_mesh", "sculpt_region", "inspect_only"}
_REFERENCE_UNDERSTANDING_GUIDED_FAMILY_VALUES = {
    "spatial_context",
    "reference_context",
    "primary_masses",
    "secondary_parts",
    "attachment_alignment",
    "checkpoint_iterate",
    "inspect_validate",
    "finish",
    "utility",
}
_REFERENCE_UNDERSTANDING_FAMILY_ALIASES = {
    "mesh_edit": "modeling_mesh",
    "material_finish": "inspect_only",
}
_REFERENCE_UNDERSTANDING_GUIDED_FAMILY_ALIASES = {
    "mesh_edit": "secondary_parts",
    "material_finish": "finish",
}
_REFERENCE_UNDERSTANDING_SOURCE_CLASS_VALUES = {
    "reference_image",
    "style_cue",
    "part_cue",
    "construction_hint",
    "gate_seed",
}
_REFERENCE_UNDERSTANDING_VIEW_VALUES = {"front", "side", "top", "back", "three_quarter", "detail", "unknown"}
_REFERENCE_UNDERSTANDING_SEGMENTATION_ARTIFACT_VALUES = {"mask", "crop", "box"}
_REFERENCE_UNDERSTANDING_SCULPT_POLICY_VALUES = {"hidden", "local_detail_only", "allowed_or_primary"}
_REFERENCE_UNDERSTANDING_ATTACHMENT_RELATION_VALUES = {
    "segment_attachment",
    "seated_attachment",
    "embedded_attachment",
    "support_contact",
    "symmetry_pair",
    "unknown",
}


def _labels_for(request: VisionRequest) -> list[str]:
    return [image.label or image.role for image in request.images]


def unwrap_json_text(text: str) -> str:
    """Remove one full-document fenced code block when present."""

    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return stripped


def extract_json_object_candidate(text: str) -> str | None:
    """Extract the widest JSON-object-like substring from text when possible."""

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return text[start : end + 1]


def _json_container_shape(text: str, parsed_from: str) -> str:
    stripped = text.strip()
    unwrapped = unwrap_json_text(text)
    if stripped.startswith("```") and parsed_from == unwrapped:
        return "fenced_json"
    if parsed_from == stripped:
        return "json"
    return "embedded_json"


def _looks_like_input_echo(parsed: dict[str, Any]) -> bool:
    return {"goal", "images", "metadata"} <= set(parsed.keys()) and "goal_summary" not in parsed


def _looks_like_label_map(parsed: dict[str, Any]) -> bool:
    keys = set(parsed.keys())
    return bool(keys) and keys <= _LABEL_MAP_KEYS


def _repair_echo_payload(parsed: dict[str, Any], request: VisionRequest) -> dict[str, Any]:
    labels = _labels_for(request)
    return {
        "goal_summary": "Model echoed the request payload instead of producing visual analysis.",
        "reference_match_summary": None,
        "visible_changes": [],
        "shape_mismatches": [],
        "proportion_mismatches": [],
        "correction_focus": [],
        "likely_issues": [
            {
                "category": "backend_output",
                "summary": "Model returned an input-echo response instead of bounded visual analysis.",
                "severity": "medium",
            }
        ],
        "next_corrections": [],
        "recommended_checks": [],
        "confidence": 0.0,
        "captures_used": labels,
        "analysis_unusable": True,
    }


def _repair_label_map_payload(parsed: dict[str, Any], request: VisionRequest) -> dict[str, Any]:
    labels = _labels_for(request)
    return {
        "goal_summary": "Model returned capture labels instead of visual analysis.",
        "reference_match_summary": None,
        "visible_changes": [],
        "shape_mismatches": [],
        "proportion_mismatches": [],
        "correction_focus": [],
        "likely_issues": [
            {
                "category": "backend_output",
                "summary": "Model returned image-label mapping instead of bounded visual analysis.",
                "severity": "medium",
            }
        ],
        "next_corrections": [],
        "recommended_checks": [],
        "confidence": 0.0,
        "captures_used": labels,
        "analysis_unusable": True,
    }


def _repair_unrecognized_payload(parsed: dict[str, Any], request: VisionRequest) -> dict[str, Any]:
    labels = _labels_for(request)
    keys = ", ".join(sorted(str(key) for key in parsed.keys())) or "none"
    return {
        "goal_summary": "Model returned JSON, but not in the required vision-assist contract shape.",
        "reference_match_summary": None,
        "visible_changes": [],
        "shape_mismatches": [],
        "proportion_mismatches": [],
        "correction_focus": [],
        "likely_issues": [
            {
                "category": "backend_output",
                "summary": f"Model returned unsupported JSON keys: {keys}.",
                "severity": "medium",
            }
        ],
        "next_corrections": [],
        "recommended_checks": [],
        "confidence": 0.0,
        "captures_used": labels,
        "analysis_unusable": True,
    }


def _first_string(parsed: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = parsed.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _coerce_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _dedupe_string_list(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _prune_unhelpful_correction_items(items: list[str]) -> list[str]:
    pruned: list[str] = []
    for item in items:
        normalized = item.strip().lower()
        if any(snippet in normalized for snippet in _UNHELPFUL_CORRECTION_SNIPPETS):
            continue
        pruned.append(item)
    return pruned


def _looks_clean_packet_text(*values: str | None) -> bool:
    normalized = " | ".join(str(value or "").strip().lower() for value in values if str(value or "").strip())
    return bool(normalized) and any(hint in normalized for hint in _PACKET_CLEAN_HINTS)


def _bounded_string_list(items: list[str], *, max_items: int = 3, prune_unhelpful: bool = False) -> list[str]:
    bounded, _omitted = _bounded_string_list_counted(items, max_items=max_items, prune_unhelpful=prune_unhelpful)
    return bounded


def _bounded_string_list_counted(
    items: list[str], *, max_items: int = 3, prune_unhelpful: bool = False
) -> tuple[list[str], int]:
    """Return the bounded list plus the number of items dropped by the cap."""

    deduped = _dedupe_string_list(items)
    if prune_unhelpful:
        deduped = _prune_unhelpful_correction_items(deduped)
    bounded = deduped[:max_items]
    return bounded, max(0, len(deduped) - len(bounded))


def _clamp_unit_interval(value: Any) -> float | None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    return max(0.0, min(1.0, float(value)))


def _coerce_findings_list(value: Any, *, max_items: int = 8) -> list[dict[str, Any]]:
    """Coerce model-provided structured findings into the typed finding shape.

    Defensive and lossless-on-failure: drops malformed entries, clamps confidence
    to [0,1], keeps magnitude_ratio as a non-negative proportional ratio, and
    normalizes axis/direction to the allowed enums (or None). Advisory only.
    """

    if not isinstance(value, list):
        return []
    axes = {"x", "y", "z", "none"}
    directions = {"increase", "decrease", "none"}
    findings: list[dict[str, Any]] = []
    for raw in value:
        if not isinstance(raw, dict):
            continue
        finding_text = raw.get("finding")
        if not isinstance(finding_text, str) or not finding_text.strip():
            continue

        def _opt_str(key: str) -> str | None:
            candidate = raw.get(key)
            return candidate.strip() if isinstance(candidate, str) and candidate.strip() else None

        axis = _opt_str("axis")
        axis = axis.lower() if axis and axis.lower() in axes else None
        direction = _opt_str("direction")
        direction = direction.lower() if direction and direction.lower() in directions else None
        magnitude = raw.get("magnitude_ratio")
        magnitude_ratio = (
            float(magnitude) if isinstance(magnitude, (int, float)) and not isinstance(magnitude, bool) else None
        )
        if magnitude_ratio is not None and magnitude_ratio < 0:
            magnitude_ratio = None
        findings.append(
            {
                "finding": finding_text.strip(),
                "view_id": _opt_str("view_id"),
                "target_label": _opt_str("target_label"),
                "axis": axis,
                "direction": direction,
                "magnitude_ratio": magnitude_ratio,
                "reference_id": _opt_str("reference_id"),
                "confidence": _clamp_unit_interval(raw.get("confidence")),
            }
        )
        if len(findings) >= max_items:
            break
    return findings


def _first_nonempty_value(parsed: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = parsed.get(key)
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        if isinstance(value, list) and not value:
            continue
        return value
    return None


def _is_reference_guided_checkpoint(request: VisionRequest) -> bool:
    prompt_hint = (request.prompt_hint or "").lower()
    has_reference = any(image.role == "reference" for image in request.images)
    return has_reference and any(hint in prompt_hint for hint in _REFERENCE_GUIDED_CHECKPOINT_HINTS)


def _uses_google_family_compare_contract(
    *,
    vision_contract_profile: VisionContractProfile | None = None,
    provider_name: str | None = None,
    request: VisionRequest | None = None,
) -> bool:
    resolved_profile = resolve_vision_contract_profile(
        vision_contract_profile=vision_contract_profile,
        provider_name=provider_name,
    )
    return (
        resolved_profile == "google_family_compare" and request is not None and _is_reference_guided_checkpoint(request)
    )


def _coerce_issue_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    issues: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            issues.append(
                {
                    "category": "reported_issue",
                    "summary": item.strip(),
                    "severity": "medium",
                }
            )
            continue
        if not isinstance(item, dict):
            continue
        summary = item.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            continue
        severity = str(item.get("severity") or "medium").lower()
        if severity not in {"high", "medium", "low"}:
            severity = "medium"
        issues.append(
            {
                "category": str(item.get("category") or "reported_issue"),
                "summary": summary.strip(),
                "severity": severity,
            }
        )
    return issues


def _dedupe_issue_list(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[dict[str, Any]] = []
    for item in issues:
        summary = str(item.get("summary") or "").strip()
        category = str(item.get("category") or "reported_issue")
        severity = str(item.get("severity") or "medium")
        key = (category.lower(), summary.lower(), severity.lower())
        if not summary or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _coerce_check_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    checks: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            continue
        if not isinstance(item, dict):
            continue
        tool_name = str(item.get("tool_name") or "").strip()
        reason = item.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            continue
        priority = str(item.get("priority") or "normal").lower()
        if priority not in {"high", "normal"}:
            priority = "normal"
        canonical_tool_name = _canonicalize_check_tool_name(tool_name)
        if canonical_tool_name is None:
            continue
        checks.append(
            {
                "tool_name": canonical_tool_name,
                "reason": reason.strip(),
                "priority": priority,
            }
        )
    return checks


def _canonicalize_check_tool_name(tool_name: str) -> str | None:
    normalized = tool_name.strip()
    if not normalized:
        return None
    lowered = normalized.lower()
    canonical = _CANONICAL_CHECK_TOOL_MAP.get(lowered, normalized)
    return canonical if canonical in _CANONICAL_CHECK_TOOLS else None


def _dedupe_check_list(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[dict[str, Any]] = []
    for item in checks:
        reason = str(item.get("reason") or "").strip()
        tool_name = str(item.get("tool_name") or "follow_up_check")
        priority = str(item.get("priority") or "normal")
        key = (tool_name.lower(), reason.lower(), priority.lower())
        if not reason or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _reference_understanding_defaults_for_path(path: str) -> tuple[str, list[str], list[str], str]:
    if path == "low_poly_facet":
        return (
            "modeling_mesh",
            ["macro", "modeling_mesh", "inspect_only"],
            ["reference_context", "primary_masses", "secondary_parts", "inspect_validate"],
            "preserve_facets",
        )
    if path == "hard_surface":
        return (
            "modeling_mesh",
            ["macro", "modeling_mesh", "inspect_only"],
            ["reference_context", "primary_masses", "secondary_parts", "inspect_validate"],
            "inspect_first",
        )
    if path == "organic_sculpt":
        return (
            "sculpt_region",
            ["macro", "modeling_mesh", "sculpt_region", "inspect_only"],
            ["reference_context", "primary_masses", "secondary_parts", "inspect_validate", "finish"],
            "bounded_local_detail",
        )
    if path == "creature_blockout":
        return (
            "macro",
            ["macro", "modeling_mesh", "inspect_only"],
            ["reference_context", "primary_masses", "secondary_parts", "inspect_validate"],
            "inspect_first",
        )
    if path == "dental_surface":
        return (
            "inspect_only",
            ["inspect_only", "modeling_mesh"],
            ["reference_context", "inspect_validate"],
            "inspect_first",
        )
    if path == "architectural_mass":
        return (
            "modeling_mesh",
            ["macro", "modeling_mesh", "inspect_only"],
            ["reference_context", "primary_masses", "secondary_parts", "inspect_validate"],
            "inspect_first",
        )
    return ("inspect_only", ["inspect_only"], ["reference_context", "inspect_validate"], "unknown")


def _normalize_reference_family(value: Any, *, fallback: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in _REFERENCE_UNDERSTANDING_FAMILY_ALIASES:
        normalized = _REFERENCE_UNDERSTANDING_FAMILY_ALIASES[normalized]
    if normalized in _REFERENCE_UNDERSTANDING_FAMILY_VALUES:
        return normalized
    return fallback


def _normalize_reference_family_list(value: Any, *, fallback: list[str]) -> list[str]:
    if not isinstance(value, list):
        return list(fallback)
    families: list[str] = []
    for item in value:
        normalized = _normalize_reference_family(item, fallback="")
        if normalized and normalized not in families:
            families.append(normalized)
    return families or list(fallback)


def _normalize_reference_guided_family_list(value: Any, *, fallback: list[str]) -> list[str]:
    if not isinstance(value, list):
        return list(fallback)
    guided_families: list[str] = []
    for item in value:
        normalized = str(item or "").strip().lower()
        if normalized in _REFERENCE_UNDERSTANDING_GUIDED_FAMILY_ALIASES:
            normalized = _REFERENCE_UNDERSTANDING_GUIDED_FAMILY_ALIASES[normalized]
        if normalized in _REFERENCE_UNDERSTANDING_GUIDED_FAMILY_VALUES and normalized not in guided_families:
            guided_families.append(normalized)
    return guided_families or list(fallback)


def _normalize_reference_understanding_subject(parsed: dict[str, Any]) -> dict[str, Any]:
    subject = parsed.get("subject")
    if not isinstance(subject, dict):
        subject = {"label": str(parsed.get("subject_label") or parsed.get("goal_summary") or "").strip()}
    label = str(subject.get("label") or parsed.get("subject_label") or "").strip() or "unknown subject"
    category = str(subject.get("category") or "unknown").strip().lower()
    if category not in _REFERENCE_UNDERSTANDING_CATEGORY_VALUES:
        category = "unknown"
    confidence = subject.get("confidence")
    if not isinstance(confidence, (int, float)):
        confidence = None
    uncertainty_notes = _coerce_string_list(subject.get("uncertainty_notes"))
    return {
        "label": label,
        "category": category,
        "confidence": confidence,
        "uncertainty_notes": uncertainty_notes,
    }


def _normalize_reference_understanding_style(parsed: dict[str, Any]) -> dict[str, Any]:
    raw_style = parsed.get("style")
    if isinstance(raw_style, dict):
        style_label = str(raw_style.get("style_label") or raw_style.get("label") or "unknown").strip().lower()
        confidence = raw_style.get("confidence")
        notes = _coerce_string_list(raw_style.get("notes"))
    else:
        style_label = str(raw_style or parsed.get("style_label") or "unknown").strip().lower()
        confidence = parsed.get("style_confidence")
        notes = _coerce_string_list(parsed.get("style_notes"))
    if style_label not in _REFERENCE_UNDERSTANDING_STYLE_VALUES:
        style_label = "unknown"
    if not isinstance(confidence, (int, float)):
        confidence = None
    return {
        "style_label": style_label,
        "confidence": confidence,
        "notes": notes,
    }


def _normalize_creature_reference_target_label(
    target_label: str,
    *,
    part_label: str,
) -> str:
    normalized = target_label.strip().lower().replace(" ", "_")
    if not normalized:
        return normalized
    target_tokens = {token for token in re.split(r"[^a-z0-9]+", normalized) if token}
    part_tokens = {token for token in re.split(r"[^a-z0-9]+", part_label.strip().lower()) if token}
    combined_tokens = target_tokens | part_tokens

    def _looks_generic(tokens: set[str], *, allowed: set[str]) -> bool:
        return bool(tokens) and tokens <= allowed

    if normalized in {"body", "body_core", "body_mass", "torso", "torso_mass"} or _looks_generic(
        combined_tokens,
        allowed={"body", "core", "mass", "torso", "main"},
    ):
        return "body_core"
    if normalized in {"head", "head_mass", "head_core"} or _looks_generic(
        combined_tokens,
        allowed={"head", "mass", "core"},
    ):
        return "head_mass"
    if normalized in {"tail", "tail_mass", "tail_core"} or _looks_generic(
        combined_tokens,
        allowed={"tail", "mass", "core", "silhouette", "profile"},
    ):
        return "tail_mass"
    if normalized in {"snout", "snout_mass", "muzzle", "nose"} or _looks_generic(
        combined_tokens,
        allowed={"snout", "mass", "muzzle", "nose", "core"},
    ):
        return "snout_mass"
    if normalized in {"ear", "ears", "ear_pair", "earpair"} or _looks_generic(
        combined_tokens,
        allowed={"ear", "ears", "pair", "silhouette"},
    ):
        return "ear_pair"
    if normalized in {"eye", "eyes", "eye_pair", "eyepair"} or _looks_generic(
        combined_tokens,
        allowed={"eye", "eyes", "pair", "visible", "readable"},
    ):
        return "eye_pair"
    if normalized in {
        "foreleg",
        "forelegs",
        "front_leg",
        "front_legs",
        "frontleg",
        "frontlegs",
        "forelimb",
        "forelimbs",
        "foreleg_pair",
        "forelegpair",
    } or _looks_generic(
        combined_tokens,
        allowed={
            "foreleg",
            "forelegs",
            "front",
            "frontleg",
            "frontlegs",
            "forelimb",
            "forelimbs",
            "legs",
            "leg",
            "pair",
        },
    ):
        return "foreleg_pair"
    if normalized in {
        "hindleg",
        "hindlegs",
        "back_leg",
        "back_legs",
        "backleg",
        "backlegs",
        "rear_leg",
        "rear_legs",
        "hindlimb",
        "hindlimbs",
        "hindleg_pair",
        "hindlegpair",
    } or _looks_generic(
        combined_tokens,
        allowed={
            "hindleg",
            "hindlegs",
            "back",
            "backleg",
            "backlegs",
            "rear",
            "rearleg",
            "rearlegs",
            "hindlimb",
            "hindlimbs",
            "legs",
            "leg",
            "pair",
        },
    ):
        return "hindleg_pair"
    return normalized


def _normalize_reference_part_target_label(
    target_label: str,
    *,
    part_label: str,
    subject_category: str,
) -> str:
    normalized = target_label.strip().lower().replace(" ", "_")
    if subject_category == "creature":
        return _normalize_creature_reference_target_label(
            normalized,
            part_label=part_label,
        )
    return normalized


def _normalize_reference_role_candidate(
    value: Any,
    *,
    subject_category: str,
) -> str | None:
    label = str(value or "").strip()
    if not label:
        return None
    normalized = _normalize_reference_part_target_label(
        label,
        part_label=label,
        subject_category=subject_category,
    )
    return normalized or None


def _normalize_reference_role_candidate_list(
    value: Any,
    *,
    subject_category: str,
    max_items: int = 5,
) -> list[str]:
    items: list[str] = []
    for raw_item in _coerce_string_list(value):
        normalized = _normalize_reference_role_candidate(
            raw_item,
            subject_category=subject_category,
        )
        if normalized and normalized not in items:
            items.append(normalized)
    return items[:max_items]


def _normalize_reference_understanding_parts(
    parsed: dict[str, Any],
    *,
    subject_category: str,
) -> list[dict[str, Any]]:
    value = parsed.get("required_parts")
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for index, raw_item in enumerate(value, start=1):
        if isinstance(raw_item, str) and raw_item.strip():
            label = raw_item.strip()
            items.append(
                {
                    "part_label": label,
                    "target_label": _normalize_reference_part_target_label(
                        label,
                        part_label=label,
                        subject_category=subject_category,
                    ),
                    "construction_hint": None,
                    "priority": "normal",
                    "source_reference_ids": [],
                }
            )
            continue
        if not isinstance(raw_item, dict):
            continue
        label = str(raw_item.get("part_label") or raw_item.get("label") or "").strip()
        if not label:
            continue
        priority = str(raw_item.get("priority") or "normal").strip().lower()
        if priority not in {"high", "normal"}:
            priority = "normal"
        raw_target_label = str(raw_item.get("target_label") or "").strip() or label.lower().replace(" ", "_")
        target_label = _normalize_reference_part_target_label(
            raw_target_label,
            part_label=label,
            subject_category=subject_category,
        )
        items.append(
            {
                "part_label": label,
                "target_label": target_label,
                "construction_hint": _truncate_text_value(raw_item.get("construction_hint")),
                "priority": priority,
                "source_reference_ids": _coerce_string_list(raw_item.get("source_reference_ids")),
            }
        )
    return items[:5]


def _normalize_reference_understanding_views(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    value = parsed.get("views")
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for raw_item in value:
        if not isinstance(raw_item, dict):
            continue
        view_id = str(raw_item.get("view_id") or raw_item.get("label") or "unknown").strip().lower()
        if view_id not in _REFERENCE_UNDERSTANDING_VIEW_VALUES:
            view_id = "unknown"
        confidence = raw_item.get("confidence")
        if not isinstance(confidence, (int, float)):
            confidence = None
        items.append(
            {
                "view_id": view_id,
                "detected": bool(raw_item.get("detected", view_id != "unknown")),
                "confidence": confidence,
                "reference_ids": _coerce_string_list(raw_item.get("reference_ids")),
                "key_features": _bounded_string_list(_coerce_string_list(raw_item.get("key_features")), max_items=6),
            }
        )
    return items[:6]


def _truncate_text_value(value: Any, *, limit: int = 240) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip().replace("\n", " ")
    if not text:
        return None
    return text[:limit]


def _normalize_reference_understanding_strategy(parsed: dict[str, Any]) -> dict[str, Any]:
    strategy = parsed.get("construction_strategy")
    if not isinstance(strategy, dict):
        strategy = {}
    raw_path = str(strategy.get("construction_path") or parsed.get("construction_path") or "unknown").strip().lower()
    if raw_path not in _REFERENCE_UNDERSTANDING_CONSTRUCTION_PATH_VALUES:
        raw_path = "unknown"
    fallback_primary, fallback_allowed, fallback_guided, fallback_finish = _reference_understanding_defaults_for_path(
        raw_path
    )
    primary_family = _normalize_reference_family(strategy.get("primary_family"), fallback=fallback_primary)
    allowed_families = _normalize_reference_family_list(
        strategy.get("allowed_families"),
        fallback=fallback_allowed,
    )
    finish_policy = str(strategy.get("finish_policy") or fallback_finish).strip().lower()
    if finish_policy not in _REFERENCE_UNDERSTANDING_FINISH_POLICY_VALUES:
        finish_policy = fallback_finish
    return {
        "construction_path": raw_path,
        "primary_family": primary_family,
        "allowed_families": allowed_families,
        "stage_sequence": _coerce_string_list(strategy.get("stage_sequence")),
        "finish_policy": finish_policy,
        "_fallback_guided_families": fallback_guided,
    }


def _normalize_reference_understanding_hints(parsed: dict[str, Any], *, strategy: dict[str, Any]) -> dict[str, Any]:
    hints = parsed.get("router_handoff_hints")
    if not isinstance(hints, dict):
        hints = {}
    fallback_guided = list(strategy.get("_fallback_guided_families") or ["reference_context", "inspect_validate"])
    preferred_family = _normalize_reference_family(hints.get("preferred_family"), fallback=strategy["primary_family"])
    allowed_guided_families = _normalize_reference_guided_family_list(
        hints.get("allowed_guided_families"),
        fallback=fallback_guided,
    )
    sculpt_policy = str(hints.get("sculpt_policy") or "").strip().lower()
    if sculpt_policy not in _REFERENCE_UNDERSTANDING_SCULPT_POLICY_VALUES:
        construction_path = strategy["construction_path"]
        if construction_path == "organic_sculpt":
            sculpt_policy = "allowed_or_primary"
        elif construction_path == "creature_blockout":
            sculpt_policy = "local_detail_only"
        else:
            sculpt_policy = "hidden"
    return {
        "preferred_family": preferred_family,
        "allowed_guided_families": allowed_guided_families,
        "sculpt_policy": sculpt_policy,
    }


def _normalize_reference_understanding_mass_recipe(
    parsed: dict[str, Any],
    *,
    subject_category: str,
) -> list[dict[str, Any]]:
    value = parsed.get("mass_recipe")
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for raw_item in value:
        if not isinstance(raw_item, dict):
            continue
        raw_target = str(raw_item.get("target_label") or raw_item.get("part_label") or "").strip()
        if not raw_target:
            continue
        target_label = _normalize_reference_part_target_label(
            raw_target,
            part_label=raw_target,
            subject_category=subject_category,
        )
        items.append(
            {
                "target_label": target_label,
                "geometry_family": _truncate_text_value(raw_item.get("geometry_family"), limit=80),
                "construction_hint": _truncate_text_value(raw_item.get("construction_hint")),
                "anchor_role_candidates": _normalize_reference_role_candidate_list(
                    raw_item.get("anchor_role_candidates") or raw_item.get("anchor_object_candidates"),
                    subject_category=subject_category,
                ),
                "support_surface_candidates": _bounded_string_list(
                    _coerce_string_list(raw_item.get("support_surface_candidates")),
                    max_items=5,
                ),
                "contact_expectations": _bounded_string_list(
                    _coerce_string_list(raw_item.get("contact_expectations")),
                    max_items=5,
                ),
                "source_reference_ids": _coerce_string_list(raw_item.get("source_reference_ids")),
            }
        )
    return items[:8]


def _normalize_reference_understanding_attachment_plan(
    parsed: dict[str, Any],
    *,
    subject_category: str,
) -> list[dict[str, Any]]:
    value = parsed.get("attachment_plan")
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for raw_item in value:
        if not isinstance(raw_item, dict):
            continue
        raw_target = str(raw_item.get("target_label") or raw_item.get("part_label") or "").strip()
        if not raw_target:
            continue
        target_label = _normalize_reference_part_target_label(
            raw_target,
            part_label=raw_target,
            subject_category=subject_category,
        )
        required_relation = str(raw_item.get("required_relation") or "unknown").strip().lower()
        if required_relation not in _REFERENCE_UNDERSTANDING_ATTACHMENT_RELATION_VALUES:
            required_relation = "unknown"
        items.append(
            {
                "target_label": target_label,
                "anchor_role_candidates": _normalize_reference_role_candidate_list(
                    raw_item.get("anchor_role_candidates") or raw_item.get("anchor_object_candidates"),
                    subject_category=subject_category,
                ),
                "required_relation": required_relation,
                "support_surface_candidates": _bounded_string_list(
                    _coerce_string_list(raw_item.get("support_surface_candidates")),
                    max_items=5,
                ),
                "contact_expectations": _bounded_string_list(
                    _coerce_string_list(raw_item.get("contact_expectations")),
                    max_items=5,
                ),
                "notes": _bounded_string_list(_coerce_string_list(raw_item.get("notes")), max_items=5),
            }
        )
    return items[:8]


def _normalize_reference_understanding_contact_expectations(
    parsed: dict[str, Any],
    *,
    subject_category: str,
) -> list[dict[str, Any]]:
    value = parsed.get("contact_expectations")
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for raw_item in value:
        if not isinstance(raw_item, dict):
            continue
        raw_target = str(raw_item.get("target_label") or raw_item.get("part_label") or "").strip()
        if not raw_target:
            continue
        target_label = _normalize_reference_part_target_label(
            raw_target,
            part_label=raw_target,
            subject_category=subject_category,
        )
        items.append(
            {
                "target_label": target_label,
                "expected_contacts": _bounded_string_list(
                    _coerce_string_list(raw_item.get("expected_contacts")),
                    max_items=5,
                ),
                "avoid_contacts": _bounded_string_list(
                    _coerce_string_list(raw_item.get("avoid_contacts")),
                    max_items=5,
                ),
                "notes": _bounded_string_list(_coerce_string_list(raw_item.get("notes")), max_items=5),
            }
        )
    return items[:8]


def _normalize_reference_understanding_shape_profile_hints(
    parsed: dict[str, Any],
    *,
    subject_category: str,
) -> list[dict[str, Any]]:
    value = parsed.get("shape_profile_hints")
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for raw_item in value:
        if not isinstance(raw_item, dict):
            continue
        raw_target = str(raw_item.get("target_label") or raw_item.get("part_label") or "").strip()
        summary = _truncate_text_value(raw_item.get("summary"))
        if not raw_target or summary is None:
            continue
        target_label = _normalize_reference_part_target_label(
            raw_target,
            part_label=raw_target,
            subject_category=subject_category,
        )
        items.append(
            {
                "target_label": target_label,
                "summary": summary,
                "reference_id": str(raw_item.get("reference_id") or "").strip() or None,
            }
        )
    return items[:8]


def _normalize_reference_understanding_silhouette_landmarks(
    parsed: dict[str, Any],
    *,
    subject_category: str,
) -> list[dict[str, Any]]:
    value = parsed.get("silhouette_landmarks")
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for index, raw_item in enumerate(value, start=1):
        if not isinstance(raw_item, dict):
            continue
        summary = _truncate_text_value(raw_item.get("summary"))
        if summary is None:
            continue
        raw_target = str(raw_item.get("target_label") or raw_item.get("part_label") or "").strip()
        target_label = (
            _normalize_reference_part_target_label(
                raw_target,
                part_label=raw_target,
                subject_category=subject_category,
            )
            if raw_target
            else None
        )
        view_id = str(raw_item.get("view_id") or "unknown").strip().lower()
        if view_id not in _REFERENCE_UNDERSTANDING_VIEW_VALUES:
            view_id = "unknown"
        items.append(
            {
                "landmark_id": str(raw_item.get("landmark_id") or f"landmark_{index}").strip(),
                "target_label": target_label,
                "view_id": view_id,
                "summary": summary,
            }
        )
    return items[:8]


def _normalize_reference_gate_proposals(
    parsed: dict[str, Any],
    *,
    parts: list[dict[str, Any]],
    subject_category: str,
) -> list[dict[str, Any]]:
    value = parsed.get("gate_proposals")
    proposals: list[dict[str, Any]] = []
    if isinstance(value, list):
        for raw_item in value:
            if not isinstance(raw_item, dict):
                continue
            normalized: dict[str, Any] = {}
            for key in (
                "gate_id",
                "gate_type",
                "label",
                "target_kind",
                "target_label",
                "target_object",
                "required",
                "priority",
                "status",
                "rationale",
                "allow_embedded_intersection",
                "allow_alignment_drift",
            ):
                if key in raw_item:
                    normalized[key] = raw_item.get(key)
            if normalized.get("target_label"):
                normalized["target_label"] = _normalize_reference_part_target_label(
                    str(normalized["target_label"]),
                    part_label=str(raw_item.get("label") or raw_item.get("part_label") or normalized["target_label"]),
                    subject_category=subject_category,
                )
            if "target_objects" in raw_item and isinstance(raw_item.get("target_objects"), list):
                normalized["target_objects"] = [
                    str(item).strip() for item in raw_item["target_objects"] if str(item).strip()
                ]
            families = _normalize_reference_guided_family_list(
                raw_item.get("allowed_correction_families"),
                fallback=[],
            )
            if families:
                normalized["allowed_correction_families"] = families
            evidence_requirements = raw_item.get("evidence_requirements")
            if isinstance(evidence_requirements, list):
                normalized["evidence_requirements"] = [
                    {"evidence_kind": item, "required": True} if isinstance(item, str) else item
                    for item in evidence_requirements
                ]
            if normalized.get("gate_type"):
                proposals.append(normalized)
    if proposals:
        return proposals[:8]

    derived: list[dict[str, Any]] = []
    for item in parts[:6]:
        derived.append(
            {
                "gate_type": "required_part",
                "label": f"{item['part_label']} is represented",
                "target_kind": "reference_part",
                "target_label": item["target_label"],
                "priority": item["priority"],
                "rationale": item.get("construction_hint"),
            }
        )
    derived.extend(derive_tail_profile_gate_proposals(parts))
    return derived[:8]


def _normalize_reference_visual_evidence_refs(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    value = parsed.get("visual_evidence_refs")
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for index, raw_item in enumerate(value, start=1):
        if not isinstance(raw_item, dict):
            continue
        source_class = str(raw_item.get("source_class") or "reference_image").strip().lower()
        if source_class not in _REFERENCE_UNDERSTANDING_SOURCE_CLASS_VALUES:
            source_class = "reference_image"
        summary = str(raw_item.get("summary") or "").strip()
        if not summary:
            continue
        items.append(
            {
                "evidence_id": str(raw_item.get("evidence_id") or f"evidence_{index}").strip(),
                "source_class": source_class,
                "summary": summary,
                "reference_id": str(raw_item.get("reference_id") or "").strip() or None,
            }
        )
    return items[:12]


def _normalize_reference_verification_requirements(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    value = parsed.get("verification_requirements")
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for raw_item in value:
        if isinstance(raw_item, str):
            continue
        if not isinstance(raw_item, dict):
            continue
        tool_name = _canonicalize_check_tool_name(str(raw_item.get("tool_name") or "").strip())
        reason = str(raw_item.get("reason") or "").strip()
        if tool_name is None or not reason:
            continue
        priority = str(raw_item.get("priority") or "normal").strip().lower()
        if priority not in {"high", "normal"}:
            priority = "normal"
        items.append({"tool_name": tool_name, "reason": reason, "priority": priority})
    return items[:5]


def _normalize_reference_classification_scores(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    value = parsed.get("classification_scores")
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for raw_item in value:
        if not isinstance(raw_item, dict):
            continue
        label = str(raw_item.get("label") or "").strip()
        score = raw_item.get("score")
        if not label or not isinstance(score, (int, float)):
            continue
        normalized_score = float(score)
        if not 0.0 <= normalized_score <= 1.0:
            continue
        items.append({"label": label, "score": normalized_score})
    items.sort(key=lambda item: item["score"], reverse=True)
    return items[:5]


def _normalize_reference_classification_payload(parsed: dict[str, Any]) -> dict[str, Any]:
    scores = _normalize_reference_classification_scores(parsed)
    if scores:
        return {"classification_scores": scores}
    return {"classification_scores": []}


def _normalize_reference_segmentation_artifacts(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    value = parsed.get("segmentation_artifacts")
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for index, raw_item in enumerate(value, start=1):
        if not isinstance(raw_item, dict):
            continue
        artifact_kind = str(raw_item.get("artifact_kind") or "mask").strip().lower()
        if artifact_kind not in _REFERENCE_UNDERSTANDING_SEGMENTATION_ARTIFACT_VALUES:
            artifact_kind = "mask"
        items.append(
            {
                "artifact_id": str(raw_item.get("artifact_id") or f"artifact_{index}").strip(),
                "artifact_kind": artifact_kind,
                "reference_id": str(raw_item.get("reference_id") or "").strip() or None,
                "summary": _truncate_text_value(raw_item.get("summary")),
            }
        )
    return items[:8]


def _build_reference_understanding_id(request: VisionRequest) -> str:
    reference_ids = [str(item).strip() for item in request.metadata.get("reference_ids") or [] if str(item).strip()]
    basis = "|".join([request.goal.strip().lower(), *reference_ids]) or request.goal.strip().lower()
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:10]
    return f"understanding_{digest}"


def _normalize_reference_understanding_payload(parsed: dict[str, Any], request: VisionRequest) -> dict[str, Any]:
    subject = _normalize_reference_understanding_subject(parsed)
    strategy = _normalize_reference_understanding_strategy(parsed)
    parts = _normalize_reference_understanding_parts(
        parsed,
        subject_category=subject["category"],
    )
    views = _normalize_reference_understanding_views(parsed)
    return {
        "status": "available",
        "understanding_id": _build_reference_understanding_id(request),
        "goal": request.goal,
        "reference_ids": [
            str(item).strip() for item in request.metadata.get("reference_ids") or [] if str(item).strip()
        ],
        "subject": subject,
        "style": _normalize_reference_understanding_style(parsed),
        "views": views,
        "required_parts": parts,
        "mass_recipe": _normalize_reference_understanding_mass_recipe(
            parsed,
            subject_category=subject["category"],
        ),
        "attachment_plan": _normalize_reference_understanding_attachment_plan(
            parsed,
            subject_category=subject["category"],
        ),
        "contact_expectations": _normalize_reference_understanding_contact_expectations(
            parsed,
            subject_category=subject["category"],
        ),
        "shape_profile_hints": _normalize_reference_understanding_shape_profile_hints(
            parsed,
            subject_category=subject["category"],
        ),
        "silhouette_landmarks": _normalize_reference_understanding_silhouette_landmarks(
            parsed,
            subject_category=subject["category"],
        ),
        "part_order": _normalize_reference_role_candidate_list(
            parsed.get("part_order"),
            subject_category=subject["category"],
            max_items=8,
        ),
        "must_seat_before_next_stage": _normalize_reference_role_candidate_list(
            parsed.get("must_seat_before_next_stage"),
            subject_category=subject["category"],
            max_items=8,
        ),
        "non_goals": _bounded_string_list(_coerce_string_list(parsed.get("non_goals")), max_items=8),
        "construction_strategy": {key: value for key, value in strategy.items() if not key.startswith("_")},
        "router_handoff_hints": _normalize_reference_understanding_hints(parsed, strategy=strategy),
        "gate_proposals": _normalize_reference_gate_proposals(
            parsed,
            parts=parts,
            subject_category=subject["category"],
        ),
        "visual_evidence_refs": _normalize_reference_visual_evidence_refs(parsed),
        "verification_requirements": _normalize_reference_verification_requirements(parsed),
        "boundary_policy": {
            "advisory_only": True,
            "not_truth_source": True,
            "may_unlock_tools": False,
            "may_pass_gates": False,
            "may_propose_gates": True,
        },
    }


def _normalize_payload(parsed: dict[str, Any], request: VisionRequest) -> dict[str, Any]:
    labels = _labels_for(request)
    goal_summary = _first_string(parsed, ("goal_summary", *_SUMMARY_ALIASES)) or ""
    reference_match_summary = _first_string(parsed, ("reference_match_summary", "reference_summary", "reference_match"))
    visible_changes = _coerce_string_list(parsed.get("visible_changes"))
    if not visible_changes:
        visible_changes = _coerce_string_list(_first_nonempty_value(parsed, _VISIBLE_CHANGES_ALIASES))
    if not visible_changes and goal_summary:
        goal_summary_lower = goal_summary.lower()
        if any(hint in goal_summary_lower for hint in _VISIBLE_CHANGE_GOAL_SUMMARY_HINTS):
            visible_changes = [goal_summary]
    omitted_total = 0
    visible_changes, _omitted = _bounded_string_list_counted(visible_changes)
    omitted_total += _omitted
    shape_mismatches, _omitted = _bounded_string_list_counted(
        _coerce_string_list(_first_nonempty_value(parsed, _SHAPE_MISMATCHES_ALIASES)),
        prune_unhelpful=True,
    )
    omitted_total += _omitted
    proportion_mismatches, _omitted = _bounded_string_list_counted(
        _coerce_string_list(_first_nonempty_value(parsed, _PROPORTION_MISMATCHES_ALIASES)),
        prune_unhelpful=True,
    )
    omitted_total += _omitted
    correction_focus, _omitted = _bounded_string_list_counted(
        _coerce_string_list(_first_nonempty_value(parsed, _CORRECTION_FOCUS_ALIASES)),
        prune_unhelpful=True,
    )
    omitted_total += _omitted

    likely_issues = _coerce_issue_list(parsed.get("likely_issues"))
    if not likely_issues:
        for alias in _LIKELY_ISSUES_ALIASES:
            likely_issues = _coerce_issue_list(parsed.get(alias))
            if likely_issues:
                break
    likely_issues = _dedupe_issue_list(likely_issues)

    recommended_checks = _coerce_check_list(parsed.get("recommended_checks"))
    if not recommended_checks:
        for alias in _RECOMMENDED_CHECKS_ALIASES:
            recommended_checks = _coerce_check_list(parsed.get(alias))
            if recommended_checks:
                break
    recommended_checks = _dedupe_check_list(recommended_checks)
    next_corrections, _omitted = _bounded_string_list_counted(
        _coerce_string_list(_first_nonempty_value(parsed, _NEXT_CORRECTIONS_ALIASES)),
        prune_unhelpful=True,
    )
    omitted_total += _omitted
    if not correction_focus and _is_reference_guided_checkpoint(request):
        correction_focus = _bounded_string_list(
            [*shape_mismatches, *proportion_mismatches, *next_corrections],
            prune_unhelpful=True,
        )

    confidence = parsed.get("confidence")
    if not isinstance(confidence, (int, float)) and confidence is not None:
        confidence = None

    packet_guidance = None
    if _is_reference_packet_compare_request(request):
        raw_packet_guidance = parsed.get("packet_guidance")
        if not isinstance(raw_packet_guidance, dict):
            raw_packet_guidance = {}
        packet_status = (
            str(raw_packet_guidance.get("packet_status") or parsed.get("packet_status") or "").strip().lower()
        )
        if packet_status not in {"ready", "clean", "low_information", "blocked"}:
            if correction_focus or shape_mismatches or proportion_mismatches or next_corrections:
                packet_status = "ready"
            elif _looks_clean_packet_text(goal_summary, reference_match_summary):
                packet_status = "clean"
            else:
                packet_status = "low_information"

        ranking_recommendation = (
            str(raw_packet_guidance.get("ranking_recommendation") or parsed.get("ranking_recommendation") or "")
            .strip()
            .lower()
        )
        if ranking_recommendation not in {"rank", "skip_clean", "skip_low_information", "skip_blocked"}:
            ranking_recommendation = {
                "ready": "rank",
                "clean": "skip_clean",
                "low_information": "skip_low_information",
                "blocked": "skip_blocked",
            }[packet_status]

        status_reason = _first_string(
            raw_packet_guidance,
            ("status_reason",),
        ) or _first_string(parsed, ("status_reason",))
        if status_reason is None:
            status_reason = {
                "ready": None,
                "clean": "Packet appears visually acceptable without a ranking pass.",
                "low_information": "Packet did not provide enough bounded visual signal for confident ranking.",
                "blocked": "Packet-local evidence was insufficient or missing for safe interpretation.",
            }[packet_status]
        packet_guidance = {
            "packet_status": packet_status,
            "status_reason": status_reason,
            "ranking_recommendation": ranking_recommendation,
        }

    return {
        "goal_summary": goal_summary,
        "reference_match_summary": reference_match_summary,
        "visible_changes": visible_changes,
        "shape_mismatches": shape_mismatches,
        "proportion_mismatches": proportion_mismatches,
        "correction_focus": correction_focus,
        "likely_issues": likely_issues,
        "next_corrections": next_corrections,
        "recommended_checks": recommended_checks,
        "findings": _coerce_findings_list(parsed.get("findings")),
        "packet_guidance": packet_guidance,
        "confidence": confidence,
        "captures_used": list(parsed.get("captures_used") or labels),
        "evidence_truncated": omitted_total > 0,
        "omitted_count": omitted_total,
        "analysis_unusable": False,
    }


def _has_contract_signal(parsed: dict[str, Any]) -> bool:
    expected = set(expected_json_keys())
    aliases = set(
        _SUMMARY_ALIASES
        + _VISIBLE_CHANGES_ALIASES
        + _SHAPE_MISMATCHES_ALIASES
        + _PROPORTION_MISMATCHES_ALIASES
        + _CORRECTION_FOCUS_ALIASES
        + _LIKELY_ISSUES_ALIASES
        + _NEXT_CORRECTIONS_ALIASES
        + _RECOMMENDED_CHECKS_ALIASES
    )
    return bool(set(parsed.keys()) & (expected | aliases))


def _has_contract_signal_for(
    parsed: dict[str, Any],
    *,
    vision_contract_profile: VisionContractProfile | None = None,
    request: VisionRequest | None = None,
    provider_name: str | None = None,
) -> bool:
    expected = set(
        expected_json_keys(
            vision_contract_profile=vision_contract_profile,
            provider_name=provider_name,
            request=request,
        )
    )
    aliases = set(
        _SUMMARY_ALIASES
        + _VISIBLE_CHANGES_ALIASES
        + _SHAPE_MISMATCHES_ALIASES
        + _PROPORTION_MISMATCHES_ALIASES
        + _CORRECTION_FOCUS_ALIASES
        + _LIKELY_ISSUES_ALIASES
        + _NEXT_CORRECTIONS_ALIASES
        + _RECOMMENDED_CHECKS_ALIASES
    )
    return bool(set(parsed.keys()) & (expected | aliases))


def _payload_shape_for(
    parsed: dict[str, Any],
    *,
    vision_contract_profile: VisionContractProfile | None = None,
    request: VisionRequest | None = None,
    provider_name: str | None = None,
) -> str:
    if _looks_like_input_echo(parsed):
        return "input_echo"
    if _looks_like_label_map(parsed):
        return "label_map"
    if any(
        key in parsed
        for key in expected_json_keys(
            vision_contract_profile=vision_contract_profile,
            provider_name=provider_name,
            request=request,
        )
    ):
        return "contract"
    if any(key in parsed for key in _SUMMARY_ALIASES):
        return "summary_alias"
    if _has_contract_signal_for(
        parsed,
        vision_contract_profile=vision_contract_profile,
        request=request,
        provider_name=provider_name,
    ):
        return "alias_contract"
    return "unsupported_json"


def _balance_json_delimiters(text: str) -> str | None:
    stack: list[str] = []
    in_string = False
    escaped = False
    for char in text:
        if escaped:
            escaped = False
            continue
        if in_string and char == "\\":
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            stack.append("}")
        elif char == "[":
            stack.append("]")
        elif char in {"}", "]"}:
            if not stack or char != stack[-1]:
                return None
            stack.pop()
    if in_string:
        return None
    return text + "".join(reversed(stack))


def _repair_gemini_compare_json_candidate(text: str) -> str | None:
    candidate = unwrap_json_text(text).strip()
    start = candidate.find("{")
    if start == -1:
        return None
    candidate = candidate[start:]
    candidate = re.sub(r",(\s*[}\]])", r"\1", candidate)
    candidate = re.sub(r",\s*$", "", candidate)
    balanced_candidate = _balance_json_delimiters(candidate)
    if balanced_candidate is None:
        return None
    json.loads(balanced_candidate)
    return balanced_candidate


def _payload_shape(parsed: dict[str, Any]) -> str:
    if _looks_like_input_echo(parsed):
        return "input_echo"
    if _looks_like_label_map(parsed):
        return "label_map"
    if any(key in parsed for key in expected_json_keys()):
        return "contract"
    if any(key in parsed for key in _SUMMARY_ALIASES):
        return "summary_alias"
    if _has_contract_signal(parsed):
        return "alias_contract"
    return "unsupported_json"


def _reject_unknown_contract_keys(
    parsed: dict[str, Any],
    *,
    allowed_keys: set[str],
    contract_name: str,
) -> None:
    unknown_keys = sorted(str(key) for key in parsed.keys() if str(key) not in allowed_keys)
    if unknown_keys:
        joined = ", ".join(unknown_keys)
        raise ValueError(f"{contract_name} output included unsupported top-level fields: {joined}")


def _reject_missing_contract_keys(
    parsed: dict[str, Any],
    *,
    required_keys: set[str],
    contract_name: str,
) -> None:
    missing_keys = sorted(str(key) for key in required_keys if str(key) not in parsed)
    if missing_keys:
        joined = ", ".join(missing_keys)
        raise ValueError(f"{contract_name} output omitted required top-level fields: {joined}")


def _reject_unexpected_dict_keys(
    payload: dict[str, Any],
    *,
    expected_keys: set[str],
    contract_name: str,
) -> None:
    extra = sorted(key for key in payload.keys() if key not in expected_keys)
    if extra:
        joined = ", ".join(extra)
        raise ValueError(f"{contract_name} output included unsupported nested fields: {joined}")


def _require_str_list(value: Any, *, contract_name: str, field_name: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{contract_name} output included malformed nested section: {field_name}")
    return value


def _validate_reference_understanding_contract_shape(parsed: dict[str, Any]) -> None:
    subject = parsed.get("subject")
    if not isinstance(subject, dict):
        raise ValueError("Reference-understanding output included malformed nested section: subject")
    _reject_unexpected_dict_keys(
        {str(key): value for key, value in subject.items()},
        expected_keys={"label", "category", "confidence", "uncertainty_notes"},
        contract_name="Reference-understanding",
    )
    if not isinstance(subject.get("label"), str):
        raise ValueError("Reference-understanding output included malformed nested section: subject.label")
    if (
        not isinstance(subject.get("category"), str)
        or subject.get("category") not in _REFERENCE_UNDERSTANDING_CATEGORY_VALUES
    ):
        raise ValueError("Reference-understanding output included malformed nested section: subject.category")
    if subject.get("confidence") is not None and not isinstance(subject.get("confidence"), (int, float)):
        raise ValueError("Reference-understanding output included malformed nested section: subject.confidence")
    _require_str_list(
        subject.get("uncertainty_notes"),
        contract_name="Reference-understanding",
        field_name="subject.uncertainty_notes",
    )

    style = parsed.get("style")
    if not isinstance(style, dict):
        raise ValueError("Reference-understanding output included malformed nested section: style")
    _reject_unexpected_dict_keys(
        {str(key): value for key, value in style.items()},
        expected_keys={"style_label", "confidence", "notes"},
        contract_name="Reference-understanding",
    )
    if (
        not isinstance(style.get("style_label"), str)
        or style.get("style_label") not in _REFERENCE_UNDERSTANDING_STYLE_VALUES
    ):
        raise ValueError("Reference-understanding output included malformed nested section: style.style_label")
    if style.get("confidence") is not None and not isinstance(style.get("confidence"), (int, float)):
        raise ValueError("Reference-understanding output included malformed nested section: style.confidence")
    _require_str_list(style.get("notes"), contract_name="Reference-understanding", field_name="style.notes")

    views = parsed.get("views")
    if not isinstance(views, list):
        raise ValueError("Reference-understanding output included malformed nested section: views")
    for item in views:
        if not isinstance(item, dict):
            raise ValueError("Reference-understanding output included malformed nested section: views")
        _reject_unexpected_dict_keys(
            {str(key): value for key, value in item.items()},
            expected_keys={"view_id", "detected", "confidence", "reference_ids", "key_features"},
            contract_name="Reference-understanding",
        )
        if (
            not isinstance(item.get("view_id"), str)
            or item.get("view_id") not in _REFERENCE_UNDERSTANDING_VIEW_VALUES
            or not isinstance(item.get("detected"), bool)
        ):
            raise ValueError("Reference-understanding output included malformed nested section: views")
        if item.get("confidence") is not None and not isinstance(item.get("confidence"), (int, float)):
            raise ValueError("Reference-understanding output included malformed nested section: views.confidence")
        _require_str_list(
            item.get("reference_ids"), contract_name="Reference-understanding", field_name="views.reference_ids"
        )
        _require_str_list(
            item.get("key_features"), contract_name="Reference-understanding", field_name="views.key_features"
        )

    parts = parsed.get("required_parts")
    if not isinstance(parts, list):
        raise ValueError("Reference-understanding output included malformed nested section: required_parts")
    for item in parts:
        if not isinstance(item, dict):
            raise ValueError("Reference-understanding output included malformed nested section: required_parts")
        _reject_unexpected_dict_keys(
            {str(key): value for key, value in item.items()},
            expected_keys={"part_label", "target_label", "construction_hint", "priority", "source_reference_ids"},
            contract_name="Reference-understanding",
        )
        if not isinstance(item.get("part_label"), str):
            raise ValueError(
                "Reference-understanding output included malformed nested section: required_parts.part_label"
            )
        if item.get("target_label") is not None and not isinstance(item.get("target_label"), str):
            raise ValueError(
                "Reference-understanding output included malformed nested section: required_parts.target_label"
            )
        if item.get("construction_hint") is not None and not isinstance(item.get("construction_hint"), str):
            raise ValueError(
                "Reference-understanding output included malformed nested section: required_parts.construction_hint"
            )
        if item.get("priority") not in {"high", "normal"}:
            raise ValueError(
                "Reference-understanding output included malformed nested section: required_parts.priority"
            )
        _require_str_list(
            item.get("source_reference_ids"),
            contract_name="Reference-understanding",
            field_name="required_parts.source_reference_ids",
        )

    mass_recipe = parsed.get("mass_recipe")
    if not isinstance(mass_recipe, list):
        raise ValueError("Reference-understanding output included malformed nested section: mass_recipe")
    for item in mass_recipe:
        if not isinstance(item, dict):
            raise ValueError("Reference-understanding output included malformed nested section: mass_recipe")
        _reject_unexpected_dict_keys(
            {str(key): value for key, value in item.items()},
            expected_keys={
                "target_label",
                "geometry_family",
                "construction_hint",
                "anchor_role_candidates",
                "anchor_object_candidates",
                "support_surface_candidates",
                "contact_expectations",
                "source_reference_ids",
            },
            contract_name="Reference-understanding",
        )
        if not isinstance(item.get("target_label"), str):
            raise ValueError(
                "Reference-understanding output included malformed nested section: mass_recipe.target_label"
            )
        if item.get("geometry_family") is not None and not isinstance(item.get("geometry_family"), str):
            raise ValueError(
                "Reference-understanding output included malformed nested section: mass_recipe.geometry_family"
            )
        if item.get("construction_hint") is not None and not isinstance(item.get("construction_hint"), str):
            raise ValueError(
                "Reference-understanding output included malformed nested section: mass_recipe.construction_hint"
            )
        _require_str_list(
            item.get("anchor_role_candidates")
            if "anchor_role_candidates" in item
            else item.get("anchor_object_candidates"),
            contract_name="Reference-understanding",
            field_name="mass_recipe.anchor_role_candidates",
        )
        _require_str_list(
            item.get("support_surface_candidates"),
            contract_name="Reference-understanding",
            field_name="mass_recipe.support_surface_candidates",
        )
        _require_str_list(
            item.get("contact_expectations"),
            contract_name="Reference-understanding",
            field_name="mass_recipe.contact_expectations",
        )
        _require_str_list(
            item.get("source_reference_ids"),
            contract_name="Reference-understanding",
            field_name="mass_recipe.source_reference_ids",
        )

    attachment_plan = parsed.get("attachment_plan")
    if not isinstance(attachment_plan, list):
        raise ValueError("Reference-understanding output included malformed nested section: attachment_plan")
    for item in attachment_plan:
        if not isinstance(item, dict):
            raise ValueError("Reference-understanding output included malformed nested section: attachment_plan")
        _reject_unexpected_dict_keys(
            {str(key): value for key, value in item.items()},
            expected_keys={
                "target_label",
                "anchor_role_candidates",
                "anchor_object_candidates",
                "required_relation",
                "support_surface_candidates",
                "contact_expectations",
                "notes",
            },
            contract_name="Reference-understanding",
        )
        if not isinstance(item.get("target_label"), str):
            raise ValueError(
                "Reference-understanding output included malformed nested section: attachment_plan.target_label"
            )
        if (
            not isinstance(item.get("required_relation"), str)
            or item.get("required_relation") not in _REFERENCE_UNDERSTANDING_ATTACHMENT_RELATION_VALUES
        ):
            raise ValueError(
                "Reference-understanding output included malformed nested section: attachment_plan.required_relation"
            )
        _require_str_list(
            item.get("anchor_role_candidates")
            if "anchor_role_candidates" in item
            else item.get("anchor_object_candidates"),
            contract_name="Reference-understanding",
            field_name="attachment_plan.anchor_role_candidates",
        )
        _require_str_list(
            item.get("support_surface_candidates"),
            contract_name="Reference-understanding",
            field_name="attachment_plan.support_surface_candidates",
        )
        _require_str_list(
            item.get("contact_expectations"),
            contract_name="Reference-understanding",
            field_name="attachment_plan.contact_expectations",
        )
        _require_str_list(
            item.get("notes"),
            contract_name="Reference-understanding",
            field_name="attachment_plan.notes",
        )

    contact_expectations = parsed.get("contact_expectations")
    if not isinstance(contact_expectations, list):
        raise ValueError("Reference-understanding output included malformed nested section: contact_expectations")
    for item in contact_expectations:
        if not isinstance(item, dict):
            raise ValueError("Reference-understanding output included malformed nested section: contact_expectations")
        _reject_unexpected_dict_keys(
            {str(key): value for key, value in item.items()},
            expected_keys={"target_label", "expected_contacts", "avoid_contacts", "notes"},
            contract_name="Reference-understanding",
        )
        if not isinstance(item.get("target_label"), str):
            raise ValueError(
                "Reference-understanding output included malformed nested section: contact_expectations.target_label"
            )
        _require_str_list(
            item.get("expected_contacts"),
            contract_name="Reference-understanding",
            field_name="contact_expectations.expected_contacts",
        )
        _require_str_list(
            item.get("avoid_contacts"),
            contract_name="Reference-understanding",
            field_name="contact_expectations.avoid_contacts",
        )
        _require_str_list(
            item.get("notes"),
            contract_name="Reference-understanding",
            field_name="contact_expectations.notes",
        )

    shape_profile_hints = parsed.get("shape_profile_hints")
    if not isinstance(shape_profile_hints, list):
        raise ValueError("Reference-understanding output included malformed nested section: shape_profile_hints")
    for item in shape_profile_hints:
        if not isinstance(item, dict):
            raise ValueError("Reference-understanding output included malformed nested section: shape_profile_hints")
        _reject_unexpected_dict_keys(
            {str(key): value for key, value in item.items()},
            expected_keys={"target_label", "summary", "reference_id"},
            contract_name="Reference-understanding",
        )
        if not isinstance(item.get("target_label"), str) or not isinstance(item.get("summary"), str):
            raise ValueError("Reference-understanding output included malformed nested section: shape_profile_hints")
        if item.get("reference_id") is not None and not isinstance(item.get("reference_id"), str):
            raise ValueError(
                "Reference-understanding output included malformed nested section: shape_profile_hints.reference_id"
            )

    silhouette_landmarks = parsed.get("silhouette_landmarks")
    if not isinstance(silhouette_landmarks, list):
        raise ValueError("Reference-understanding output included malformed nested section: silhouette_landmarks")
    for item in silhouette_landmarks:
        if not isinstance(item, dict):
            raise ValueError("Reference-understanding output included malformed nested section: silhouette_landmarks")
        _reject_unexpected_dict_keys(
            {str(key): value for key, value in item.items()},
            expected_keys={"landmark_id", "target_label", "view_id", "summary"},
            contract_name="Reference-understanding",
        )
        if not isinstance(item.get("landmark_id"), str) or not isinstance(item.get("summary"), str):
            raise ValueError("Reference-understanding output included malformed nested section: silhouette_landmarks")
        if item.get("target_label") is not None and not isinstance(item.get("target_label"), str):
            raise ValueError(
                "Reference-understanding output included malformed nested section: silhouette_landmarks.target_label"
            )
        if not isinstance(item.get("view_id"), str) or item.get("view_id") not in _REFERENCE_UNDERSTANDING_VIEW_VALUES:
            raise ValueError(
                "Reference-understanding output included malformed nested section: silhouette_landmarks.view_id"
            )

    _require_str_list(parsed.get("part_order"), contract_name="Reference-understanding", field_name="part_order")
    _require_str_list(
        parsed.get("must_seat_before_next_stage"),
        contract_name="Reference-understanding",
        field_name="must_seat_before_next_stage",
    )

    _require_str_list(parsed.get("non_goals"), contract_name="Reference-understanding", field_name="non_goals")

    strategy = parsed.get("construction_strategy")
    if not isinstance(strategy, dict):
        raise ValueError("Reference-understanding output included malformed nested section: construction_strategy")
    _reject_unexpected_dict_keys(
        {str(key): value for key, value in strategy.items()},
        expected_keys={"construction_path", "primary_family", "allowed_families", "stage_sequence", "finish_policy"},
        contract_name="Reference-understanding",
    )
    if (
        not isinstance(strategy.get("construction_path"), str)
        or strategy.get("construction_path") not in _REFERENCE_UNDERSTANDING_CONSTRUCTION_PATH_VALUES
        or not isinstance(strategy.get("primary_family"), str)
        or strategy.get("primary_family") not in _REFERENCE_UNDERSTANDING_FAMILY_VALUES
    ):
        raise ValueError("Reference-understanding output included malformed nested section: construction_strategy")
    allowed_families = _require_str_list(
        strategy.get("allowed_families"),
        contract_name="Reference-understanding",
        field_name="construction_strategy.allowed_families",
    )
    if any(item not in _REFERENCE_UNDERSTANDING_FAMILY_VALUES for item in allowed_families):
        raise ValueError(
            "Reference-understanding output included malformed nested section: construction_strategy.allowed_families"
        )
    _require_str_list(
        strategy.get("stage_sequence"),
        contract_name="Reference-understanding",
        field_name="construction_strategy.stage_sequence",
    )
    if (
        not isinstance(strategy.get("finish_policy"), str)
        or strategy.get("finish_policy") not in _REFERENCE_UNDERSTANDING_FINISH_POLICY_VALUES
    ):
        raise ValueError(
            "Reference-understanding output included malformed nested section: construction_strategy.finish_policy"
        )

    hints = parsed.get("router_handoff_hints")
    if not isinstance(hints, dict):
        raise ValueError("Reference-understanding output included malformed nested section: router_handoff_hints")
    _reject_unexpected_dict_keys(
        {str(key): value for key, value in hints.items()},
        expected_keys={"preferred_family", "allowed_guided_families", "sculpt_policy"},
        contract_name="Reference-understanding",
    )
    if (
        not isinstance(hints.get("preferred_family"), str)
        or hints.get("preferred_family") not in _REFERENCE_UNDERSTANDING_FAMILY_VALUES
        or not isinstance(hints.get("sculpt_policy"), str)
        or hints.get("sculpt_policy") not in _REFERENCE_UNDERSTANDING_SCULPT_POLICY_VALUES
    ):
        raise ValueError("Reference-understanding output included malformed nested section: router_handoff_hints")
    allowed_guided_families = _require_str_list(
        hints.get("allowed_guided_families"),
        contract_name="Reference-understanding",
        field_name="router_handoff_hints.allowed_guided_families",
    )
    if any(item not in _REFERENCE_UNDERSTANDING_GUIDED_FAMILY_VALUES for item in allowed_guided_families):
        raise ValueError(
            "Reference-understanding output included malformed nested section: router_handoff_hints.allowed_guided_families"
        )

    for field_name in ("gate_proposals", "visual_evidence_refs", "verification_requirements"):
        value = parsed.get(field_name)
        if not isinstance(value, list):
            raise ValueError(f"Reference-understanding output included malformed nested section: {field_name}")
    for item in parsed.get("visual_evidence_refs", []):
        if not isinstance(item, dict):
            raise ValueError("Reference-understanding output included malformed nested section: visual_evidence_refs")
        _reject_unexpected_dict_keys(
            {str(key): value for key, value in item.items()},
            expected_keys={"evidence_id", "source_class", "summary", "reference_id"},
            contract_name="Reference-understanding",
        )
        if not isinstance(item.get("evidence_id"), str):
            raise ValueError("Reference-understanding output included malformed nested section: visual_evidence_refs")
        if (
            not isinstance(item.get("source_class"), str)
            or item.get("source_class") not in _REFERENCE_UNDERSTANDING_SOURCE_CLASS_VALUES
        ):
            raise ValueError(
                "Reference-understanding output included malformed nested section: visual_evidence_refs.source_class"
            )
        if not isinstance(item.get("summary"), str):
            raise ValueError(
                "Reference-understanding output included malformed nested section: visual_evidence_refs.summary"
            )
        if item.get("reference_id") is not None and not isinstance(item.get("reference_id"), str):
            raise ValueError(
                "Reference-understanding output included malformed nested section: visual_evidence_refs.reference_id"
            )
    for item in parsed.get("verification_requirements", []):
        if not isinstance(item, dict):
            raise ValueError(
                "Reference-understanding output included malformed nested section: verification_requirements"
            )
        _reject_unexpected_dict_keys(
            {str(key): value for key, value in item.items()},
            expected_keys={"tool_name", "reason", "priority"},
            contract_name="Reference-understanding",
        )
        if not isinstance(item.get("tool_name"), str) or not isinstance(item.get("reason"), str):
            raise ValueError(
                "Reference-understanding output included malformed nested section: verification_requirements"
            )
        if item.get("priority") not in {"high", "normal"}:
            raise ValueError(
                "Reference-understanding output included malformed nested section: verification_requirements.priority"
            )


def _validate_reference_classification_contract_shape(parsed: dict[str, Any]) -> None:
    scores = parsed.get("classification_scores")
    if not isinstance(scores, list):
        raise ValueError("Reference-classification output included malformed nested section: classification_scores")
    if not 1 <= len(scores) <= 5:
        raise ValueError("Reference-classification output did not match the required contract shape.")
    for item in scores:
        if not isinstance(item, dict):
            raise ValueError("Reference-classification output included malformed nested section: classification_scores")
        _reject_unexpected_dict_keys(
            {str(key): value for key, value in item.items()},
            expected_keys={"label", "score"},
            contract_name="Reference-classification",
        )
        score = item.get("score")
        if (
            not isinstance(item.get("label"), str)
            or not isinstance(score, (int, float))
            or not 0.0 <= float(score) <= 1.0
        ):
            raise ValueError("Reference-classification output included malformed nested section: classification_scores")


def _reject_malformed_reference_understanding_contract(parsed: dict[str, Any]) -> None:
    expected_shapes: dict[str, type] = {
        "subject": dict,
        "style": dict,
        "views": list,
        "required_parts": list,
        "mass_recipe": list,
        "attachment_plan": list,
        "contact_expectations": list,
        "shape_profile_hints": list,
        "silhouette_landmarks": list,
        "part_order": list,
        "must_seat_before_next_stage": list,
        "non_goals": list,
        "construction_strategy": dict,
        "router_handoff_hints": dict,
        "gate_proposals": list,
        "visual_evidence_refs": list,
        "verification_requirements": list,
    }
    malformed = [
        key
        for key, expected_type in expected_shapes.items()
        if key in parsed and not isinstance(parsed[key], expected_type)
    ]
    if malformed:
        joined = ", ".join(sorted(malformed))
        raise ValueError(f"Reference-understanding output included malformed top-level sections: {joined}")


def diagnose_vision_output_text(
    text: str,
    *,
    vision_contract_profile: VisionContractProfile | None = None,
    request: VisionRequest | None = None,
    provider_name: str | None = None,
) -> dict[str, Any]:
    """Classify one raw backend output before contract normalization."""

    resolved_contract_profile = resolve_vision_contract_profile(
        vision_contract_profile=vision_contract_profile,
        provider_name=provider_name,
    )
    stripped = text.strip()
    preview = stripped[:280]
    candidates = [unwrap_json_text(text)]
    extracted = extract_json_object_candidate(candidates[0])
    if extracted and extracted not in candidates:
        candidates.append(extracted)

    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            if _uses_google_family_compare_contract(
                vision_contract_profile=resolved_contract_profile,
                provider_name=provider_name,
                request=request,
            ):
                try:
                    repaired_candidate = _repair_gemini_compare_json_candidate(candidate)
                except json.JSONDecodeError:
                    repaired_candidate = None
                if repaired_candidate is not None:
                    payload = json.loads(repaired_candidate)
                    if isinstance(payload, dict):
                        keys = sorted(str(key) for key in payload.keys())
                        return {
                            "container_shape": _json_container_shape(text, repaired_candidate),
                            "payload_shape": _payload_shape_for(
                                payload,
                                vision_contract_profile=resolved_contract_profile,
                                request=request,
                                provider_name=provider_name,
                            ),
                            "top_level_keys": keys,
                            "vision_contract_profile": resolved_contract_profile,
                            "raw_preview": preview,
                        }
            continue
        if isinstance(payload, dict):
            keys = sorted(str(key) for key in payload.keys())
            return {
                "container_shape": _json_container_shape(text, candidate),
                "payload_shape": _payload_shape_for(
                    payload,
                    vision_contract_profile=resolved_contract_profile,
                    request=request,
                    provider_name=provider_name,
                ),
                "top_level_keys": keys,
                "vision_contract_profile": resolved_contract_profile,
                "raw_preview": preview,
            }

    return {
        "container_shape": "prose",
        "payload_shape": "no_json",
        "top_level_keys": [],
        "vision_contract_profile": resolved_contract_profile,
        "raw_preview": preview,
    }


def parse_vision_output_text(
    text: str,
    request: VisionRequest,
    *,
    vision_contract_profile: VisionContractProfile | None = None,
    provider_name: str | None = None,
) -> dict[str, Any]:
    """Parse and minimally repair backend output into bounded vision payload fields."""

    resolved_contract_profile = resolve_vision_contract_profile(
        vision_contract_profile=vision_contract_profile,
        provider_name=provider_name,
    )
    candidates = [unwrap_json_text(text)]
    extracted = extract_json_object_candidate(candidates[0])
    if extracted and extracted not in candidates:
        candidates.append(extracted)

    parsed: dict[str, Any] | None = None
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            if _uses_google_family_compare_contract(
                vision_contract_profile=resolved_contract_profile,
                provider_name=provider_name,
                request=request,
            ):
                try:
                    repaired_candidate = _repair_gemini_compare_json_candidate(candidate)
                except json.JSONDecodeError:
                    repaired_candidate = None
                if repaired_candidate is not None:
                    payload = json.loads(repaired_candidate)
                    if isinstance(payload, dict):
                        parsed = payload
                        break
            continue
        if isinstance(payload, dict):
            parsed = payload
            break

    if parsed is None:
        raise json.JSONDecodeError("No JSON object found", text, 0)

    if _is_reference_classification_request(request):
        if _looks_like_input_echo(parsed) or _looks_like_label_map(parsed):
            raise ValueError(
                "Reference-classification output echoed the input instead of returning the required contract."
            )
        _reject_unknown_contract_keys(
            parsed,
            allowed_keys={"classification_scores"},
            contract_name="Reference-classification",
        )
        _reject_missing_contract_keys(
            parsed,
            required_keys={"classification_scores"},
            contract_name="Reference-classification",
        )
        _validate_reference_classification_contract_shape(parsed)
        normalized = _normalize_reference_classification_payload(parsed)
        if not normalized["classification_scores"]:
            raise ValueError("Reference-classification output did not match the required contract shape.")
        return normalized

    if _is_reference_understanding_request(request):
        if _looks_like_input_echo(parsed) or _looks_like_label_map(parsed):
            raise ValueError(
                "Reference-understanding output echoed the input instead of returning the required contract."
            )
        if not _has_contract_signal_for(
            parsed,
            vision_contract_profile=resolved_contract_profile,
            request=request,
            provider_name=provider_name,
        ):
            raise ValueError("Reference-understanding output did not match the required contract shape.")
        _reject_unknown_contract_keys(
            parsed,
            allowed_keys=set(
                expected_json_keys(
                    vision_contract_profile=resolved_contract_profile,
                    provider_name=provider_name,
                    request=request,
                )
            ),
            contract_name="Reference-understanding",
        )
        _reject_missing_contract_keys(
            parsed,
            required_keys=set(
                expected_json_keys(
                    vision_contract_profile=resolved_contract_profile,
                    provider_name=provider_name,
                    request=request,
                )
            ),
            contract_name="Reference-understanding",
        )
        _validate_reference_understanding_contract_shape(parsed)
        return _normalize_reference_understanding_payload(parsed, request)

    if _looks_like_input_echo(parsed):
        return _repair_echo_payload(parsed, request)

    if _looks_like_label_map(parsed):
        return _repair_label_map_payload(parsed, request)

    if not _has_contract_signal_for(
        parsed,
        vision_contract_profile=resolved_contract_profile,
        request=request,
        provider_name=provider_name,
    ):
        return _repair_unrecognized_payload(parsed, request)

    return _normalize_payload(parsed, request)
