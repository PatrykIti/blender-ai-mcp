"""Coarse router phase hints for FastMCP session adaptation."""

from __future__ import annotations

from typing import Any, Mapping


PLANNING_PHASE_HINT = "planning"
BUILD_PHASE_HINT = "build"
INSPECT_VALIDATE_PHASE_HINT = "inspect_validate"


def derive_phase_hint_from_router_result(result: Mapping[str, Any]) -> str:
    """Map router result state onto the canonical first-pass phase subset."""

    if result.get("inspection_recommended"):
        return INSPECT_VALIDATE_PHASE_HINT

    status = result.get("status")
    if status == "ready":
        return BUILD_PHASE_HINT

    return PLANNING_PHASE_HINT
