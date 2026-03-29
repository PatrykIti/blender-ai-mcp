# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Parsing and repair helpers for bounded vision backend outputs."""

from __future__ import annotations

import json
from typing import Any

from .backend import VisionRequest
from .prompting import expected_json_keys

_SUMMARY_ALIASES = ("comparison", "summary", "analysis", "description", "result")
_VISIBLE_CHANGES_ALIASES = ("changes", "visible_differences", "differences")
_LIKELY_ISSUES_ALIASES = ("issues", "problems", "risks")
_RECOMMENDED_CHECKS_ALIASES = ("checks", "follow_up_checks", "deterministic_checks", "recommended_tools")
_LABEL_MAP_KEYS = {"before", "after", "reference"}
_VISIBLE_CHANGE_GOAL_SUMMARY_HINTS = (
    "the after image shows",
    "the after images show",
    "after image shows",
    "after images show",
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
        "likely_issues": [
            {
                "category": "backend_output",
                "summary": "Model returned an input-echo response instead of bounded visual analysis.",
                "severity": "medium",
            }
        ],
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
        "likely_issues": [
            {
                "category": "backend_output",
                "summary": "Model returned image-label mapping instead of bounded visual analysis.",
                "severity": "medium",
            }
        ],
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
        "likely_issues": [
            {
                "category": "backend_output",
                "summary": f"Model returned unsupported JSON keys: {keys}.",
                "severity": "medium",
            }
        ],
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


def _coerce_check_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    checks: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            checks.append(
                {
                    "tool_name": "follow_up_check",
                    "reason": item.strip(),
                    "priority": "normal",
                }
            )
            continue
        if not isinstance(item, dict):
            continue
        tool_name = str(item.get("tool_name") or "follow_up_check")
        reason = item.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            continue
        priority = str(item.get("priority") or "normal").lower()
        if priority not in {"high", "normal"}:
            priority = "normal"
        checks.append(
            {
                "tool_name": tool_name,
                "reason": reason.strip(),
                "priority": priority,
            }
        )
    return checks


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

    likely_issues = _coerce_issue_list(parsed.get("likely_issues"))
    if not likely_issues:
        for alias in _LIKELY_ISSUES_ALIASES:
            likely_issues = _coerce_issue_list(parsed.get(alias))
            if likely_issues:
                break

    recommended_checks = _coerce_check_list(parsed.get("recommended_checks"))
    if not recommended_checks:
        for alias in _RECOMMENDED_CHECKS_ALIASES:
            recommended_checks = _coerce_check_list(parsed.get(alias))
            if recommended_checks:
                break

    confidence = parsed.get("confidence")
    if not isinstance(confidence, (int, float)) and confidence is not None:
        confidence = None

    return {
        "goal_summary": goal_summary,
        "reference_match_summary": reference_match_summary,
        "visible_changes": visible_changes,
        "likely_issues": likely_issues,
        "recommended_checks": recommended_checks,
        "confidence": confidence,
        "captures_used": list(parsed.get("captures_used") or labels),
    }


def _has_contract_signal(parsed: dict[str, Any]) -> bool:
    expected = set(expected_json_keys())
    aliases = set(_SUMMARY_ALIASES + _VISIBLE_CHANGES_ALIASES + _LIKELY_ISSUES_ALIASES + _RECOMMENDED_CHECKS_ALIASES)
    return bool(set(parsed.keys()) & (expected | aliases))


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


def diagnose_vision_output_text(text: str) -> dict[str, Any]:
    """Classify one raw backend output before contract normalization."""

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
            continue
        if isinstance(payload, dict):
            keys = sorted(str(key) for key in payload.keys())
            return {
                "container_shape": _json_container_shape(text, candidate),
                "payload_shape": _payload_shape(payload),
                "top_level_keys": keys,
                "raw_preview": preview,
            }

    return {
        "container_shape": "prose",
        "payload_shape": "no_json",
        "top_level_keys": [],
        "raw_preview": preview,
    }


def parse_vision_output_text(text: str, request: VisionRequest) -> dict[str, Any]:
    """Parse and minimally repair backend output into bounded vision payload fields."""

    candidates = [unwrap_json_text(text)]
    extracted = extract_json_object_candidate(candidates[0])
    if extracted and extracted not in candidates:
        candidates.append(extracted)

    parsed: dict[str, Any] | None = None
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
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

    if not _has_contract_signal(parsed):
        return _repair_unrecognized_payload(parsed, request)

    return _normalize_payload(parsed, request)
