# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Deterministic visibility policy for FastMCP surface profiles and phases."""

from __future__ import annotations

from typing import Any

from server.adapters.mcp.session_phase import SessionPhase, coerce_session_phase
from server.adapters.mcp.visibility.tags import ENTRY_GUIDED, phase_tag


def build_visibility_rules(
    surface_profile: str,
    phase: SessionPhase | str = SessionPhase.BOOTSTRAP,
) -> list[dict[str, Any]]:
    """Build deterministic visibility rules for a profile/phase combination."""

    resolved_phase = coerce_session_phase(phase)

    if surface_profile in {"legacy-flat", "internal-debug", "code-mode-pilot"}:
        return []

    if surface_profile != "llm-guided":
        raise ValueError(f"Unknown visibility surface profile '{surface_profile}'")

    rules: list[dict[str, Any]] = [
        {"enabled": False, "components": {"tool"}, "match_all": True},
        {"enabled": True, "components": {"tool"}, "tags": {ENTRY_GUIDED}},
        {"enabled": True, "components": {"tool"}, "names": {"list_prompts", "get_prompt"}},
        {
            "enabled": True,
            "components": {"prompt"},
            "names": {
                "getting_started",
                "workflow_router_first",
                "manual_tools_no_router",
                "demo_low_poly_medieval_well",
                "demo_generic_modeling",
                "recommended_prompts",
            },
        },
    ]

    if resolved_phase == SessionPhase.BUILD:
        rules.append({"enabled": True, "components": {"tool"}, "tags": {phase_tag(SessionPhase.BUILD)}})
    elif resolved_phase == SessionPhase.INSPECT_VALIDATE:
        rules.append({"enabled": True, "components": {"tool"}, "tags": {phase_tag(SessionPhase.INSPECT_VALIDATE)}})

    return rules
