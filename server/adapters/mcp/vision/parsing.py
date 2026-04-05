# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Parsing and repair helpers for bounded vision backend outputs."""

from __future__ import annotations

import json
import re
from typing import Any

from .backend import VisionRequest
from .config import VisionContractProfile
from .prompting import expected_json_keys, resolve_vision_contract_profile

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


def _bounded_string_list(items: list[str], *, max_items: int = 3, prune_unhelpful: bool = False) -> list[str]:
    deduped = _dedupe_string_list(items)
    if prune_unhelpful:
        deduped = _prune_unhelpful_correction_items(deduped)
    return deduped[:max_items]


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
    visible_changes = _bounded_string_list(visible_changes)
    shape_mismatches = _bounded_string_list(
        _coerce_string_list(_first_nonempty_value(parsed, _SHAPE_MISMATCHES_ALIASES)),
        prune_unhelpful=True,
    )
    proportion_mismatches = _bounded_string_list(
        _coerce_string_list(_first_nonempty_value(parsed, _PROPORTION_MISMATCHES_ALIASES)),
        prune_unhelpful=True,
    )
    correction_focus = _bounded_string_list(
        _coerce_string_list(_first_nonempty_value(parsed, _CORRECTION_FOCUS_ALIASES)),
        prune_unhelpful=True,
    )

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
    next_corrections = _bounded_string_list(
        _coerce_string_list(_first_nonempty_value(parsed, _NEXT_CORRECTIONS_ALIASES)),
        prune_unhelpful=True,
    )
    if not correction_focus and _is_reference_guided_checkpoint(request):
        correction_focus = _bounded_string_list(
            [*shape_mismatches, *proportion_mismatches, *next_corrections],
            prune_unhelpful=True,
        )

    confidence = parsed.get("confidence")
    if not isinstance(confidence, (int, float)) and confidence is not None:
        confidence = None

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
        "confidence": confidence,
        "captures_used": list(parsed.get("captures_used") or labels),
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
