# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Canonical visibility tags for FastMCP surface shaping."""

from __future__ import annotations

from server.adapters.mcp.session_phase import SessionPhase

AUDIENCE_LEGACY = "audience:legacy"
AUDIENCE_LLM = "audience:llm"
ENTRY_GUIDED = "entry:guided"


def phase_tag(phase: SessionPhase | str) -> str:
    """Return the canonical phase tag string."""

    value = phase.value if isinstance(phase, SessionPhase) else str(phase)
    return f"phase:{value}"


def capability_phase_tag(*phases: SessionPhase) -> tuple[str, ...]:
    """Return canonical phase tags for one capability."""

    return tuple(phase_tag(phase) for phase in phases)


CAPABILITY_TAGS: dict[str, tuple[str, ...]] = {
    "scene": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        *capability_phase_tag(
            SessionPhase.PLANNING,
            SessionPhase.BUILD,
            SessionPhase.INSPECT_VALIDATE,
        ),
    ),
    "mesh": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        *capability_phase_tag(SessionPhase.BUILD, SessionPhase.INSPECT_VALIDATE),
    ),
    "modeling": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        *capability_phase_tag(SessionPhase.BUILD),
    ),
    "material": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        *capability_phase_tag(SessionPhase.BUILD, SessionPhase.INSPECT_VALIDATE),
    ),
    "uv": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        *capability_phase_tag(SessionPhase.BUILD, SessionPhase.INSPECT_VALIDATE),
    ),
    "collection": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        *capability_phase_tag(SessionPhase.PLANNING, SessionPhase.BUILD),
    ),
    "curve": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        *capability_phase_tag(SessionPhase.BUILD),
    ),
    "lattice": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        *capability_phase_tag(SessionPhase.BUILD),
    ),
    "sculpt": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        *capability_phase_tag(SessionPhase.BUILD),
    ),
    "baking": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        *capability_phase_tag(SessionPhase.INSPECT_VALIDATE),
    ),
    "text": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        *capability_phase_tag(SessionPhase.BUILD),
    ),
    "armature": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        *capability_phase_tag(SessionPhase.BUILD),
    ),
    "system": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        *capability_phase_tag(SessionPhase.INSPECT_VALIDATE),
    ),
    "extraction": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        *capability_phase_tag(SessionPhase.INSPECT_VALIDATE),
    ),
    "router": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        ENTRY_GUIDED,
        *capability_phase_tag(SessionPhase.PLANNING),
    ),
    "workflow_catalog": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        ENTRY_GUIDED,
        *capability_phase_tag(SessionPhase.PLANNING),
    ),
}


def get_capability_tags(capability_id: str) -> tuple[str, ...]:
    """Return canonical tags for a capability manifest entry."""

    return CAPABILITY_TAGS[capability_id]
