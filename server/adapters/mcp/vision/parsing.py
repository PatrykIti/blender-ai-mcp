# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Parsing and repair helpers for bounded vision backend outputs."""

from __future__ import annotations

import json
from typing import Any

from .backend import VisionRequest


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


def _looks_like_input_echo(parsed: dict[str, Any]) -> bool:
    return {"goal", "images", "metadata"} <= set(parsed.keys()) and "goal_summary" not in parsed


def _repair_echo_payload(parsed: dict[str, Any], request: VisionRequest) -> dict[str, Any]:
    labels = [image.label or image.role for image in request.images]
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


def _normalize_payload(parsed: dict[str, Any], request: VisionRequest) -> dict[str, Any]:
    labels = [image.label or image.role for image in request.images]
    return {
        "goal_summary": str(parsed.get("goal_summary") or ""),
        "reference_match_summary": parsed.get("reference_match_summary"),
        "visible_changes": list(parsed.get("visible_changes") or []),
        "likely_issues": list(parsed.get("likely_issues") or []),
        "recommended_checks": list(parsed.get("recommended_checks") or []),
        "confidence": parsed.get("confidence"),
        "captures_used": list(parsed.get("captures_used") or labels),
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

    return _normalize_payload(parsed, request)
