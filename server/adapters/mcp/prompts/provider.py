# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""FastMCP prompt provider for TASK-090."""

from __future__ import annotations

from typing import Any, Dict

from fastmcp import Context

from server.adapters.mcp.prompts.prompt_catalog import get_prompt_catalog
from server.adapters.mcp.prompts.rendering import (
    render_prompt_asset,
    render_recommended_prompts,
)
from server.adapters.mcp.session_phase import SessionPhase
from server.adapters.mcp.session_state import get_session_value_async
from server.infrastructure.config import get_config

try:
    from fastmcp.server.providers import LocalProvider
except ImportError:  # pragma: no cover - explicit guard via tests
    LocalProvider = None


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
    ):
        resolved_surface = surface_profile or await get_session_value_async(
            ctx,
            "surface_profile",
            get_config().MCP_SURFACE_PROFILE,
        )
        resolved_phase = session_phase or await get_session_value_async(
            ctx,
            "phase",
            SessionPhase.BOOTSTRAP.value,
        )
        return render_recommended_prompts(
            surface_profile=str(resolved_surface),
            phase=str(resolved_phase),
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
