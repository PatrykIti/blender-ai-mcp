# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Minimal platform-owned capability manifest scaffold for TASK-083-03."""

from __future__ import annotations

from dataclasses import dataclass

from server.adapters.mcp.areas.armature import ARMATURE_PUBLIC_TOOL_NAMES
from server.adapters.mcp.areas.baking import BAKING_PUBLIC_TOOL_NAMES
from server.adapters.mcp.areas.collection import COLLECTION_PUBLIC_TOOL_NAMES
from server.adapters.mcp.areas.curve import CURVE_PUBLIC_TOOL_NAMES
from server.adapters.mcp.areas.extraction import EXTRACTION_PUBLIC_TOOL_NAMES
from server.adapters.mcp.areas.lattice import LATTICE_PUBLIC_TOOL_NAMES
from server.adapters.mcp.areas.material import MATERIAL_PUBLIC_TOOL_NAMES
from server.adapters.mcp.areas.mesh import MESH_PUBLIC_TOOL_NAMES
from server.adapters.mcp.areas.modeling import MODELING_PUBLIC_TOOL_NAMES
from server.adapters.mcp.areas.router import ROUTER_PUBLIC_TOOL_NAMES
from server.adapters.mcp.areas.scene import SCENE_PUBLIC_TOOL_NAMES
from server.adapters.mcp.areas.sculpt import SCULPT_PUBLIC_TOOL_NAMES
from server.adapters.mcp.areas.system import SYSTEM_PUBLIC_TOOL_NAMES
from server.adapters.mcp.areas.text import TEXT_PUBLIC_TOOL_NAMES
from server.adapters.mcp.areas.uv import UV_PUBLIC_TOOL_NAMES
from server.adapters.mcp.areas.workflow_catalog import WORKFLOW_PUBLIC_TOOL_NAMES
from server.adapters.mcp.platform.public_contracts import (
    CapabilityPublicContract,
    build_capability_public_contracts,
)
from server.adapters.mcp.visibility.tags import get_capability_tags


@dataclass(frozen=True)
class CapabilityManifestEntry:
    """Minimal manifest entry used by the factory/bootstrap baseline."""

    capability_id: str
    provider_group: str
    tool_names: tuple[str, ...]
    tags: tuple[str, ...]
    public_contracts: tuple[CapabilityPublicContract, ...]


CAPABILITY_MANIFEST = (
    CapabilityManifestEntry(
        "scene",
        "core_tools",
        SCENE_PUBLIC_TOOL_NAMES,
        get_capability_tags("scene"),
        build_capability_public_contracts("scene", SCENE_PUBLIC_TOOL_NAMES),
    ),
    CapabilityManifestEntry(
        "mesh",
        "core_tools",
        MESH_PUBLIC_TOOL_NAMES,
        get_capability_tags("mesh"),
        build_capability_public_contracts("mesh", MESH_PUBLIC_TOOL_NAMES),
    ),
    CapabilityManifestEntry(
        "modeling",
        "core_tools",
        MODELING_PUBLIC_TOOL_NAMES,
        get_capability_tags("modeling"),
        build_capability_public_contracts("modeling", MODELING_PUBLIC_TOOL_NAMES),
    ),
    CapabilityManifestEntry(
        "material",
        "core_tools",
        MATERIAL_PUBLIC_TOOL_NAMES,
        get_capability_tags("material"),
        build_capability_public_contracts("material", MATERIAL_PUBLIC_TOOL_NAMES),
    ),
    CapabilityManifestEntry(
        "uv",
        "core_tools",
        UV_PUBLIC_TOOL_NAMES,
        get_capability_tags("uv"),
        build_capability_public_contracts("uv", UV_PUBLIC_TOOL_NAMES),
    ),
    CapabilityManifestEntry(
        "collection",
        "core_tools",
        COLLECTION_PUBLIC_TOOL_NAMES,
        get_capability_tags("collection"),
        build_capability_public_contracts("collection", COLLECTION_PUBLIC_TOOL_NAMES),
    ),
    CapabilityManifestEntry(
        "curve",
        "core_tools",
        CURVE_PUBLIC_TOOL_NAMES,
        get_capability_tags("curve"),
        build_capability_public_contracts("curve", CURVE_PUBLIC_TOOL_NAMES),
    ),
    CapabilityManifestEntry(
        "lattice",
        "core_tools",
        LATTICE_PUBLIC_TOOL_NAMES,
        get_capability_tags("lattice"),
        build_capability_public_contracts("lattice", LATTICE_PUBLIC_TOOL_NAMES),
    ),
    CapabilityManifestEntry(
        "sculpt",
        "core_tools",
        SCULPT_PUBLIC_TOOL_NAMES,
        get_capability_tags("sculpt"),
        build_capability_public_contracts("sculpt", SCULPT_PUBLIC_TOOL_NAMES),
    ),
    CapabilityManifestEntry(
        "baking",
        "core_tools",
        BAKING_PUBLIC_TOOL_NAMES,
        get_capability_tags("baking"),
        build_capability_public_contracts("baking", BAKING_PUBLIC_TOOL_NAMES),
    ),
    CapabilityManifestEntry(
        "text",
        "core_tools",
        TEXT_PUBLIC_TOOL_NAMES,
        get_capability_tags("text"),
        build_capability_public_contracts("text", TEXT_PUBLIC_TOOL_NAMES),
    ),
    CapabilityManifestEntry(
        "armature",
        "core_tools",
        ARMATURE_PUBLIC_TOOL_NAMES,
        get_capability_tags("armature"),
        build_capability_public_contracts("armature", ARMATURE_PUBLIC_TOOL_NAMES),
    ),
    CapabilityManifestEntry(
        "system",
        "core_tools",
        SYSTEM_PUBLIC_TOOL_NAMES,
        get_capability_tags("system"),
        build_capability_public_contracts("system", SYSTEM_PUBLIC_TOOL_NAMES),
    ),
    CapabilityManifestEntry(
        "extraction",
        "core_tools",
        EXTRACTION_PUBLIC_TOOL_NAMES,
        get_capability_tags("extraction"),
        build_capability_public_contracts("extraction", EXTRACTION_PUBLIC_TOOL_NAMES),
    ),
    CapabilityManifestEntry(
        "router",
        "router_tools",
        ROUTER_PUBLIC_TOOL_NAMES,
        get_capability_tags("router"),
        build_capability_public_contracts("router", ROUTER_PUBLIC_TOOL_NAMES),
    ),
    CapabilityManifestEntry(
        "workflow_catalog",
        "workflow_tools",
        WORKFLOW_PUBLIC_TOOL_NAMES,
        get_capability_tags("workflow_catalog"),
        build_capability_public_contracts("workflow_catalog", WORKFLOW_PUBLIC_TOOL_NAMES),
    ),
)


def get_capability_manifest() -> tuple[CapabilityManifestEntry, ...]:
    """Return the minimal platform capability manifest scaffold."""

    return CAPABILITY_MANIFEST
