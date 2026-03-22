# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""FastMCP server factory and composition root."""

from __future__ import annotations

from fastmcp import FastMCP

from server.adapters.mcp.platform.capability_manifest import get_capability_manifest
from server.adapters.mcp.settings import SurfaceProfileSettings
from server.adapters.mcp.surfaces import get_surface_profile
from server.adapters.mcp.transforms import (
    build_surface_transform_pipeline,
    materialize_transforms,
)


def build_surface_providers(surface: SurfaceProfileSettings) -> list[object]:
    """Build provider instances for a surface profile."""

    return [builder() for builder in surface.provider_builders]


def build_server(surface_profile: str = "legacy-flat") -> FastMCP:
    """Build a FastMCP server from the configured surface profile."""

    surface = get_surface_profile(surface_profile)
    providers = build_surface_providers(surface)
    pipeline = build_surface_transform_pipeline(surface)
    transforms = materialize_transforms(surface)

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

    return server
