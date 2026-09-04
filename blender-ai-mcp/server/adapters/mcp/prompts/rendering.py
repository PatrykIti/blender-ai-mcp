# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Prompt rendering helpers for TASK-090."""

from __future__ import annotations

from typing import Any

from fastmcp.prompts.prompt import Message, PromptResult

from server.adapters.mcp.prompts.prompt_catalog import (
    derive_prompt_goal_tags,
    get_prompt_catalog_entry,
    get_recommended_prompt_entries,
)


def render_prompt_asset(name: str) -> PromptResult:
    """Render one static prompt asset from the catalog."""

    entry = get_prompt_catalog_entry(name)
    if entry.source_path is None:
        raise ValueError(f"Prompt asset '{name}' is dynamic and must be rendered separately.")
    content = entry.source_path.read_text(encoding="utf-8")
    return PromptResult(
        [Message(content)],
        description=entry.description,
        meta={
            "title": entry.title,
            "operating_mode": entry.operating_mode,
            "audience": entry.audience,
            "source_path": str(entry.source_path),
            "tags": list(entry.tags),
        },
    )


def render_recommended_prompts(
    *,
    surface_profile: str,
    phase: str,
    goal: str | None = None,
    guided_handoff: dict[str, Any] | None = None,
    guided_flow_state: dict[str, Any] | None = None,
) -> PromptResult:
    """Render a dynamic recommendation prompt for the current session context."""

    recommendations = get_recommended_prompt_entries(
        surface_profile=surface_profile,
        phase=phase,
        goal=goal,
        guided_handoff=guided_handoff,
    )
    goal_tags = derive_prompt_goal_tags(goal=goal, guided_handoff=guided_handoff)
    lines = [
        f"# Recommended prompts for surface `{surface_profile}` / phase `{phase}`",
        "",
    ]
    flow_required_prompts = [str(name) for name in (guided_flow_state or {}).get("required_prompts") or [] if str(name)]
    flow_preferred_prompts = [
        str(name) for name in (guided_flow_state or {}).get("preferred_prompts") or [] if str(name)
    ]
    current_step = str((guided_flow_state or {}).get("current_step") or "").strip()
    domain_profile = str((guided_flow_state or {}).get("domain_profile") or "").strip()
    if goal:
        lines.append(f"- Active goal: `{goal}`")
        lines.append(
            "- Goal context tags: " + (", ".join(f"`{tag}`" for tag in goal_tags) if goal_tags else "`goal:generic`")
        )
        lines.append("")
    if current_step or domain_profile:
        lines.append(
            "- Guided flow state: "
            + ", ".join(
                part
                for part in (
                    f"domain `{domain_profile}`" if domain_profile else None,
                    f"step `{current_step}`" if current_step else None,
                )
                if part
            )
        )
        lines.append("")
    if flow_required_prompts:
        lines.append("## Required prompt bundle")
        for prompt_name in flow_required_prompts:
            lines.append(f"- `{prompt_name}`")
        lines.append("")
    if flow_preferred_prompts:
        lines.append("## Preferred prompt bundle")
        for prompt_name in flow_preferred_prompts:
            lines.append(f"- `{prompt_name}`")
        lines.append("")
    if not recommendations:
        lines.append("No curated prompt recommendations are available for this phase/profile yet.")
    else:
        lines.append("## Additional curated recommendations")
        for entry in recommendations:
            lines.append(f"- `{entry.name}`: {entry.description}")

    return PromptResult(
        [Message("\n".join(lines))],
        description="Session-aware prompt recommendations",
        meta={
            "surface_profile": surface_profile,
            "phase": phase,
            "goal": goal,
            "goal_tags": list(goal_tags),
            "domain_profile": domain_profile or None,
            "current_step": current_step or None,
            "required_prompt_names": flow_required_prompts,
            "preferred_prompt_names": flow_preferred_prompts,
            "recommended_prompt_names": [entry.name for entry in recommendations],
        },
    )
