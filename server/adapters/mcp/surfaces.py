# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Surface profile selection for FastMCP factory composition."""

from __future__ import annotations

from dataclasses import replace

from server.adapters.mcp.providers import (
    build_core_tools_provider,
    build_internal_tools_provider,
    build_router_tools_provider,
    build_workflow_tools_provider,
)
from server.adapters.mcp.settings import SurfaceProfileSettings
from server.adapters.mcp.version_policy import (
    SURFACE_ALLOWED_CONTRACT_LINES,
    get_default_contract_line,
    resolve_contract_line,
)


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
        default_contract_line=get_default_contract_line("legacy-flat"),
        allowed_contract_lines=SURFACE_ALLOWED_CONTRACT_LINES["legacy-flat"],
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
        search_enabled=True,
        default_contract_line=get_default_contract_line("llm-guided"),
        allowed_contract_lines=SURFACE_ALLOWED_CONTRACT_LINES["llm-guided"],
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
        default_contract_line=get_default_contract_line("internal-debug"),
        allowed_contract_lines=SURFACE_ALLOWED_CONTRACT_LINES["internal-debug"],
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
        default_contract_line=get_default_contract_line("code-mode-pilot"),
        allowed_contract_lines=SURFACE_ALLOWED_CONTRACT_LINES["code-mode-pilot"],
    ),
}


def get_surface_profile(name: str) -> SurfaceProfileSettings:
    """Return the configured surface profile or raise a clear error."""

    try:
        return SURFACE_PROFILES[name]
    except KeyError as exc:
        known = ", ".join(sorted(SURFACE_PROFILES))
        raise ValueError(f"Unknown MCP surface profile '{name}'. Expected one of: {known}") from exc


def resolve_surface_contract_profile(
    name: str,
    *,
    contract_line: str | None = None,
) -> SurfaceProfileSettings:
    """Return a surface profile with a validated active contract line."""

    surface = get_surface_profile(name)
    selected_contract_line = resolve_contract_line(name, contract_line)
    return replace(surface, default_contract_line=selected_contract_line)
