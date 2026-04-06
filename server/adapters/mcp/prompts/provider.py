# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""FastMCP prompt provider for TASK-090."""

from __future__ import annotations

from typing import Any, Dict

from fastmcp import Context

from server.adapters.mcp.prompts.prompt_catalog import get_prompt_catalog
from server.adapters.mcp.prompts.rendering import (
    render_prompt_asset,
    render_recommended_prompts,
)
from server.adapters.mcp.session_capabilities import get_session_capability_state_async
from server.adapters.mcp.session_phase import SessionPhase
from server.infrastructure.config import get_config

LocalProvider: Any = None

try:
    from fastmcp.server.providers import LocalProvider
except ImportError:  # pragma: no cover - explicit guard via tests
    pass


def register_prompt_assets(target: Any) -> Dict[str, Any]:
    """Register curated prompt assets on a FastMCP-compatible provider target."""

    registered: Dict[str, Any] = {}

    for entry in get_prompt_catalog():
        if entry.source_path is None:
            continue

        async def prompt_asset(entry_name: str = entry.name):
            return render_prompt_asset(entry_name)

        registered[entry.name] = target.prompt(
            prompt_asset,
            name=entry.name,
            title=entry.title,
            description=entry.description,
            tags=set(entry.tags),
        )

    async def recommended_prompts(
        ctx: Context,
        surface_profile: str | None = None,
        session_phase: str | None = None,
        session_goal: str | None = None,
    ):
        session_state = await get_session_capability_state_async(ctx)
        resolved_surface = surface_profile or session_state.surface_profile or get_config().MCP_SURFACE_PROFILE
        resolved_phase = session_phase or session_state.phase.value or SessionPhase.BOOTSTRAP.value
        resolved_goal = session_goal if session_goal is not None else session_state.goal
        return render_recommended_prompts(
            surface_profile=str(resolved_surface),
            phase=str(resolved_phase),
            goal=str(resolved_goal) if resolved_goal is not None else None,
            guided_handoff=session_state.guided_handoff,
        )

    registered["recommended_prompts"] = target.prompt(
        recommended_prompts,
        name="recommended_prompts",
        title="Recommended Prompts",
        description="Dynamic prompt recommendations based on surface profile and session phase.",
        tags={"mode:recommendation", "audience:all"},
    )

    return registered


def build_prompt_assets_provider() -> Any:
    """Build the reusable LocalProvider for prompt assets."""

    if LocalProvider is None:
        raise RuntimeError("LocalProvider requires FastMCP >=3.0 in the active environment.")

    provider = LocalProvider()
    register_prompt_assets(provider)
    return provider
