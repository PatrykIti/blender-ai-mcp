# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Surface profile selection for FastMCP factory composition."""

from __future__ import annotations

from server.adapters.mcp.providers import (
    build_core_tools_provider,
    build_internal_tools_provider,
    build_router_tools_provider,
    build_workflow_tools_provider,
)
from server.adapters.mcp.settings import SurfaceProfileSettings


SURFACE_PROFILES: dict[str, SurfaceProfileSettings] = {
    "legacy-flat": SurfaceProfileSettings(
        name="legacy-flat",
        server_name="blender-ai-mcp",
        provider_builders=(
            build_core_tools_provider,
            build_router_tools_provider,
            build_workflow_tools_provider,
        ),
        list_page_size=100,
        tasks_enabled=False,
        delivery_mode="compatibility",
    ),
    "llm-guided": SurfaceProfileSettings(
        name="llm-guided",
        server_name="blender-ai-mcp",
        provider_builders=(
            build_core_tools_provider,
            build_router_tools_provider,
            build_workflow_tools_provider,
        ),
        list_page_size=50,
        tasks_enabled=True,
        delivery_mode="structured_first",
    ),
    "internal-debug": SurfaceProfileSettings(
        name="internal-debug",
        server_name="blender-ai-mcp-debug",
        provider_builders=(
            build_core_tools_provider,
            build_router_tools_provider,
            build_workflow_tools_provider,
            build_internal_tools_provider,
        ),
        list_page_size=100,
        tasks_enabled=True,
        delivery_mode="structured_first",
    ),
    "code-mode-pilot": SurfaceProfileSettings(
        name="code-mode-pilot",
        server_name="blender-ai-mcp-code",
        provider_builders=(
            build_core_tools_provider,
            build_router_tools_provider,
            build_workflow_tools_provider,
            build_internal_tools_provider,
        ),
        list_page_size=50,
        tasks_enabled=True,
        delivery_mode="structured_first",
    ),
}


def get_surface_profile(name: str) -> SurfaceProfileSettings:
    """Return the configured surface profile or raise a clear error."""

    try:
        return SURFACE_PROFILES[name]
    except KeyError as exc:
        known = ", ".join(sorted(SURFACE_PROFILES))
        raise ValueError(f"Unknown MCP surface profile '{name}'. Expected one of: {known}") from exc
