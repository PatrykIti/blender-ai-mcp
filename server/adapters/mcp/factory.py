# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""FastMCP server factory and composition root."""

from __future__ import annotations

from fastmcp import FastMCP

from server.adapters.mcp.platform.capability_manifest import get_capability_manifest
from server.adapters.mcp.settings import SurfaceProfileSettings
from server.adapters.mcp.surfaces import resolve_surface_contract_profile
from server.adapters.mcp.timeout_policy import build_timeout_policy
from server.adapters.mcp.transforms import (
    build_surface_transform_pipeline,
    materialize_transforms,
)
from server.infrastructure.config import get_config


def build_surface_providers(surface: SurfaceProfileSettings) -> list[object]:
    """Build provider instances for a surface profile."""

    return [builder() for builder in surface.provider_builders]


def build_server(
    surface_profile: str = "legacy-flat",
    *,
    contract_line: str | None = None,
) -> FastMCP:
    """Build a FastMCP server from the configured surface profile."""

    config = get_config()
    selected_contract_line = contract_line or config.MCP_DEFAULT_CONTRACT_LINE
    surface = resolve_surface_contract_profile(
        surface_profile,
        contract_line=selected_contract_line,
    )
    providers = build_surface_providers(surface)
    pipeline = build_surface_transform_pipeline(surface)
    transforms = materialize_transforms(surface)
    timeout_policy = build_timeout_policy(
        tool_timeout_seconds=config.MCP_TOOL_TIMEOUT_SECONDS,
        task_timeout_seconds=config.MCP_TASK_TIMEOUT_SECONDS,
        rpc_timeout_seconds=config.RPC_TIMEOUT_SECONDS,
        addon_execution_timeout_seconds=config.ADDON_EXECUTION_TIMEOUT_SECONDS,
    )

    server = FastMCP(
        surface.server_name,
        providers=providers,
        transforms=transforms,
        list_page_size=surface.list_page_size,
        tasks=surface.tasks_enabled,
        instructions=surface.instructions,
    )

    # Factory-owned bootstrap metadata used by tests and later TASK-083/084/086 work.
    server._bam_surface_profile = surface.name
    server._bam_capability_manifest = get_capability_manifest()
    server._bam_transform_count = len(transforms)
    server._bam_transform_pipeline = tuple(stage.name for stage in pipeline)
    server._bam_timeout_policy = timeout_policy
    server._bam_delivery_mode = surface.delivery_mode
    server._bam_contract_line = surface.default_contract_line

    return server
