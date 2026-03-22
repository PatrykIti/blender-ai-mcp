# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Deterministic transform pipeline scaffold for FastMCP surface composition."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from server.adapters.mcp.settings import SurfaceProfileSettings
from .discovery import build_discovery_transform
from .naming import build_naming_transform
from .prompts_bridge import build_prompts_bridge_transform
from .visibility import build_visibility_transform


@dataclass(frozen=True)
class TransformStage:
    """One ordered stage in the MCP transform pipeline."""

    name: str
    transform: Any | None


def build_version_filter_transform(surface: SurfaceProfileSettings) -> Any | None:
    """Build the version-filter stage for the active surface.

    TASK-083 establishes the stage ordering; TASK-091 later populates it with real
    version rules once public contract lines exist.
    """

    return None


def build_surface_transform_pipeline(
    surface: SurfaceProfileSettings,
) -> tuple[TransformStage, ...]:
    """Return the ordered transform pipeline for a surface profile."""

    return (
        TransformStage("version_filter", build_version_filter_transform(surface)),
        TransformStage("naming", build_naming_transform(surface)),
        TransformStage("prompts_bridge", build_prompts_bridge_transform(surface)),
        TransformStage("visibility", build_visibility_transform(surface)),
        TransformStage("discovery", build_discovery_transform(surface)),
    )


def materialize_transforms(surface: SurfaceProfileSettings) -> list[Any]:
    """Return only the active transform objects for a surface profile."""

    materialized: list[Any] = []

    for stage in build_surface_transform_pipeline(surface):
        transform = stage.transform
        if transform is None:
            continue
        if isinstance(transform, (list, tuple)):
            materialized.extend(transform)
        else:
            materialized.append(transform)

    return materialized
