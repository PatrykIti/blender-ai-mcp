# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Prompt rendering helpers for TASK-090."""

from __future__ import annotations

from fastmcp.prompts.prompt import Message, PromptResult

from server.adapters.mcp.prompts.prompt_catalog import (
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
) -> PromptResult:
    """Render a dynamic recommendation prompt for the current session context."""

    recommendations = get_recommended_prompt_entries(
        surface_profile=surface_profile,
        phase=phase,
    )
    lines = [
        f"# Recommended prompts for surface `{surface_profile}` / phase `{phase}`",
        "",
    ]
    if not recommendations:
        lines.append("No curated prompt recommendations are available for this phase/profile yet.")
    else:
        for entry in recommendations:
            lines.append(f"- `{entry.name}`: {entry.description}")

    return PromptResult(
        [Message("\n".join(lines))],
        description="Session-aware prompt recommendations",
        meta={
            "surface_profile": surface_profile,
            "phase": phase,
            "recommended_prompt_names": [entry.name for entry in recommendations],
        },
    )
