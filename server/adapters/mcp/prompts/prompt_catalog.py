# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Prompt asset inventory and taxonomy for TASK-090."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from server.adapters.mcp.session_phase import SessionPhase, coerce_session_phase

PROMPTS_DIR = Path(__file__).resolve().parents[4] / "_docs" / "_PROMPTS"


@dataclass(frozen=True)
class PromptCatalogEntry:
    """One curated prompt product exposed by the MCP server."""

    name: str
    title: str
    description: str
    source_path: Path | None
    tags: tuple[str, ...]
    operating_mode: str
    audience: str
    phase_tags: tuple[str, ...] = ()
    profile_tags: tuple[str, ...] = ()
    goal_tags: tuple[str, ...] = ()
    recommended: bool = True


_CREATURE_GOAL_HINTS: tuple[str, ...] = (
    "animal",
    "bird",
    "character",
    "creature",
    "ears",
    "face",
    "fox",
    "owl",
    "paw",
    "rabbit",
    "snout",
    "squirrel",
    "tail",
)
_LOW_POLY_GOAL_HINTS: tuple[str, ...] = (
    "blockout",
    "low poly",
    "low-poly",
)
_REFERENCE_GOAL_HINTS: tuple[str, ...] = (
    "front and side",
    "front reference",
    "front/side",
    "matching reference",
    "reference image",
    "reference images",
    "side reference",
)


def _goal_contains_phrase(goal: str, phrase: str) -> bool:
    normalized_phrase = re.escape(phrase.strip().lower())
    return re.search(rf"(?<![a-z0-9]){normalized_phrase}(?![a-z0-9])", goal) is not None


def derive_prompt_goal_tags(
    *,
    goal: str | None,
    guided_handoff: dict[str, object] | None = None,
) -> tuple[str, ...]:
    """Return deterministic recommendation tags derived from explicit session state."""

    normalized_goal = str(goal or "").strip().lower()
    tags: set[str] = set()

    if any(_goal_contains_phrase(normalized_goal, token) for token in _CREATURE_GOAL_HINTS):
        tags.add("goal:creature")
    if any(_goal_contains_phrase(normalized_goal, token) for token in _LOW_POLY_GOAL_HINTS):
        tags.add("goal:low_poly")
    if any(_goal_contains_phrase(normalized_goal, token) for token in _REFERENCE_GOAL_HINTS):
        tags.add("goal:reference_guided")

    recipe_id = str((guided_handoff or {}).get("recipe_id") or "").strip().lower()
    if recipe_id == "low_poly_creature_blockout":
        tags.update({"goal:creature", "goal:low_poly"})

    return tuple(sorted(tags))


PROMPT_CATALOG: tuple[PromptCatalogEntry, ...] = (
    PromptCatalogEntry(
        name="getting_started",
        title="Getting Started",
        description="Onboarding guidance for choosing the right prompt and working mode.",
        source_path=PROMPTS_DIR / "README.md",
        tags=("mode:onboarding", "audience:all"),
        operating_mode="onboarding",
        audience="all",
        phase_tags=("phase:bootstrap", "phase:planning"),
    ),
    PromptCatalogEntry(
        name="workflow_router_first",
        title="Workflow Router First",
        description="Router-first operating guidance for workflow-oriented modeling sessions.",
        source_path=PROMPTS_DIR / "WORKFLOW_ROUTER_FIRST.md",
        tags=("mode:router-first", "audience:guided"),
        operating_mode="router-first",
        audience="guided",
        phase_tags=("phase:planning", "phase:build"),
        profile_tags=("profile:llm-guided",),
    ),
    PromptCatalogEntry(
        name="guided_session_start",
        title="Guided Session Start",
        description="Short fail-safe starter prefix for llm-guided sessions that should avoid hidden-tool and wrong-phase drift.",
        source_path=PROMPTS_DIR / "GUIDED_SESSION_START.md",
        tags=("mode:guided-start", "audience:guided"),
        operating_mode="guided-start",
        audience="guided",
        phase_tags=("phase:bootstrap", "phase:planning", "phase:build"),
        profile_tags=("profile:llm-guided",),
    ),
    PromptCatalogEntry(
        name="manual_tools_no_router",
        title="Manual Tools No Router",
        description="Manual tool-calling guidance for clients or sessions that should avoid the router.",
        source_path=PROMPTS_DIR / "MANUAL_TOOLS_NO_ROUTER.md",
        tags=("mode:manual-tools", "audience:all"),
        operating_mode="manual-tools",
        audience="all",
        phase_tags=("phase:build", "phase:inspect_validate"),
    ),
    PromptCatalogEntry(
        name="demo_low_poly_medieval_well",
        title="Demo Low Poly Medieval Well",
        description="Concrete demo task prompt for a workflow-first low-poly medieval well build.",
        source_path=PROMPTS_DIR / "DEMO_TASK_LOW_POLY_MEDIEVAL_WELL.md",
        tags=("mode:demo", "audience:all"),
        operating_mode="demo",
        audience="all",
        phase_tags=("phase:planning", "phase:build"),
    ),
    PromptCatalogEntry(
        name="demo_generic_modeling",
        title="Demo Generic Modeling",
        description="Generic modeling demo prompt for clients that want a copy/paste-ready task starter.",
        source_path=PROMPTS_DIR / "DEMO_TASK_GENERIC_MODELING.md",
        tags=("mode:demo", "audience:all"),
        operating_mode="demo",
        audience="all",
        phase_tags=("phase:planning", "phase:build"),
    ),
    PromptCatalogEntry(
        name="reference_guided_creature_build",
        title="Reference Guided Creature Build",
        description="Generic creature-build guidance for llm-guided sessions using staged reference checkpoints and bounded compare/iterate loops.",
        source_path=PROMPTS_DIR / "REFERENCE_GUIDED_CREATURE_BUILD.md",
        tags=("mode:guided-reference", "audience:guided", "domain:creature"),
        operating_mode="guided-reference",
        audience="guided",
        phase_tags=("phase:planning", "phase:build"),
        profile_tags=("profile:llm-guided",),
        goal_tags=("goal:creature",),
    ),
    PromptCatalogEntry(
        name="recommended_prompts",
        title="Recommended Prompts",
        description="Dynamic recommendation prompt based on session phase and surface profile.",
        source_path=None,
        tags=("mode:recommendation", "audience:all"),
        operating_mode="recommendation",
        audience="all",
        phase_tags=("phase:bootstrap", "phase:planning", "phase:build", "phase:inspect_validate"),
        recommended=False,
    ),
)


def get_prompt_catalog() -> tuple[PromptCatalogEntry, ...]:
    """Return the canonical prompt catalog."""

    return PROMPT_CATALOG


def get_prompt_catalog_entry(name: str) -> PromptCatalogEntry:
    """Return one prompt catalog entry by stable name."""

    for entry in PROMPT_CATALOG:
        if entry.name == name:
            return entry
    known = ", ".join(sorted(entry.name for entry in PROMPT_CATALOG))
    raise KeyError(f"Unknown prompt asset '{name}'. Expected one of: {known}")


def get_recommended_prompt_entries(
    *,
    surface_profile: str,
    phase: SessionPhase | str,
    goal: str | None = None,
    guided_handoff: dict[str, object] | None = None,
) -> tuple[PromptCatalogEntry, ...]:
    """Return the recommended prompts for one surface profile and session phase."""

    resolved_phase = coerce_session_phase(phase)
    phase_tag = f"phase:{resolved_phase.value}"
    profile_tag = f"profile:{surface_profile}"
    goal_tags = set(
        derive_prompt_goal_tags(
            goal=goal,
            guided_handoff=guided_handoff,
        )
    )

    recommendations: list[tuple[int, int, PromptCatalogEntry]] = []
    for index, entry in enumerate(PROMPT_CATALOG):
        if not entry.recommended:
            continue
        if entry.profile_tags and profile_tag not in entry.profile_tags:
            continue
        if entry.phase_tags and phase_tag not in entry.phase_tags:
            continue
        goal_overlap = len(goal_tags.intersection(entry.goal_tags))
        if entry.goal_tags and goal_overlap == 0:
            continue
        recommendations.append((goal_overlap, index, entry))

    recommendations.sort(key=lambda item: (-item[0], item[1]))
    return tuple(entry for _goal_overlap, _index, entry in recommendations)
