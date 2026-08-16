# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Canonical visibility tags and metadata hints for FastMCP surface shaping."""

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
    ),
    "mesh": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
    ),
    "modeling": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
    ),
    "material": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
    ),
    "reference": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        ENTRY_GUIDED,
    ),
    "uv": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
    ),
    "collection": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
    ),
    "curve": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
    ),
    "lattice": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
    ),
    "sculpt": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
    ),
    "baking": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
    ),
    "text": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
    ),
    "armature": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
    ),
    "system": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
    ),
    "extraction": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
    ),
    "router": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        ENTRY_GUIDED,
    ),
    "workflow_catalog": (
        AUDIENCE_LEGACY,
        AUDIENCE_LLM,
        ENTRY_GUIDED,
    ),
}


CAPABILITY_PHASE_HINTS: dict[str, tuple[str, ...]] = {
    "scene": capability_phase_tag(
        SessionPhase.PLANNING,
        SessionPhase.BUILD,
        SessionPhase.INSPECT_VALIDATE,
    ),
    "mesh": capability_phase_tag(SessionPhase.BUILD, SessionPhase.INSPECT_VALIDATE),
    "modeling": capability_phase_tag(SessionPhase.BUILD),
    "material": capability_phase_tag(SessionPhase.BUILD, SessionPhase.INSPECT_VALIDATE),
    "reference": capability_phase_tag(SessionPhase.PLANNING, SessionPhase.BUILD),
    "uv": capability_phase_tag(SessionPhase.BUILD, SessionPhase.INSPECT_VALIDATE),
    "collection": capability_phase_tag(SessionPhase.PLANNING, SessionPhase.BUILD),
    "curve": capability_phase_tag(SessionPhase.BUILD),
    "lattice": capability_phase_tag(SessionPhase.BUILD),
    "sculpt": capability_phase_tag(SessionPhase.BUILD),
    "baking": capability_phase_tag(SessionPhase.INSPECT_VALIDATE),
    "text": capability_phase_tag(SessionPhase.BUILD),
    "armature": capability_phase_tag(SessionPhase.BUILD),
    "system": capability_phase_tag(SessionPhase.INSPECT_VALIDATE),
    "extraction": capability_phase_tag(SessionPhase.INSPECT_VALIDATE),
    "router": capability_phase_tag(SessionPhase.PLANNING),
    "workflow_catalog": capability_phase_tag(SessionPhase.PLANNING),
}


def get_capability_tags(capability_id: str) -> tuple[str, ...]:
    """Return canonical tags for a capability manifest entry."""

    return CAPABILITY_TAGS[capability_id]


def get_capability_phase_hints(capability_id: str) -> tuple[str, ...]:
    """Return metadata-only phase hints for a capability manifest entry."""

    return CAPABILITY_PHASE_HINTS[capability_id]
