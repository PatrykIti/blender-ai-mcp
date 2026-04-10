# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

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
from server.adapters.mcp.areas.reference import REFERENCE_PUBLIC_TOOL_NAMES
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
from server.adapters.mcp.visibility.tags import get_capability_phase_hints, get_capability_tags


@dataclass(frozen=True)
class CapabilityManifestEntry:
    """Minimal manifest entry used by the factory/bootstrap baseline."""

    capability_id: str
    provider_group: str
    tool_names: tuple[str, ...]
    tags: tuple[str, ...]
    phase_hints: tuple[str, ...]
    public_contracts: tuple[CapabilityPublicContract, ...]
    discovery_category: str
    pinned_tools: tuple[str, ...] = ()
    hidden_from_search_tools: tuple[str, ...] = ()

    def runtime_tool_names(self) -> tuple[str, ...]:
        """Return all known internal/public runtime names for this capability."""

        names: set[str] = set(self.tool_names)
        for contract in self.public_contracts:
            for internal_name, public_name in contract.tool_name_map:
                names.add(internal_name)
                names.add(public_name)
        return tuple(sorted(names))


CAPABILITY_MANIFEST = (
    CapabilityManifestEntry(
        "scene",
        "core_tools",
        SCENE_PUBLIC_TOOL_NAMES,
        get_capability_tags("scene"),
        get_capability_phase_hints("scene"),
        build_capability_public_contracts("scene", SCENE_PUBLIC_TOOL_NAMES),
        "scene",
        pinned_tools=("scene_scope_graph", "scene_relation_graph", "scene_view_diagnostics"),
    ),
    CapabilityManifestEntry(
        "mesh",
        "core_tools",
        MESH_PUBLIC_TOOL_NAMES,
        get_capability_tags("mesh"),
        get_capability_phase_hints("mesh"),
        build_capability_public_contracts("mesh", MESH_PUBLIC_TOOL_NAMES),
        "mesh",
    ),
    CapabilityManifestEntry(
        "modeling",
        "core_tools",
        MODELING_PUBLIC_TOOL_NAMES,
        get_capability_tags("modeling"),
        get_capability_phase_hints("modeling"),
        build_capability_public_contracts("modeling", MODELING_PUBLIC_TOOL_NAMES),
        "modeling",
    ),
    CapabilityManifestEntry(
        "material",
        "core_tools",
        MATERIAL_PUBLIC_TOOL_NAMES,
        get_capability_tags("material"),
        get_capability_phase_hints("material"),
        build_capability_public_contracts("material", MATERIAL_PUBLIC_TOOL_NAMES),
        "material",
    ),
    CapabilityManifestEntry(
        "reference",
        "core_tools",
        REFERENCE_PUBLIC_TOOL_NAMES,
        get_capability_tags("reference"),
        get_capability_phase_hints("reference"),
        build_capability_public_contracts("reference", REFERENCE_PUBLIC_TOOL_NAMES),
        "reference",
        pinned_tools=("reference_images",),
    ),
    CapabilityManifestEntry(
        "uv",
        "core_tools",
        UV_PUBLIC_TOOL_NAMES,
        get_capability_tags("uv"),
        get_capability_phase_hints("uv"),
        build_capability_public_contracts("uv", UV_PUBLIC_TOOL_NAMES),
        "uv",
    ),
    CapabilityManifestEntry(
        "collection",
        "core_tools",
        COLLECTION_PUBLIC_TOOL_NAMES,
        get_capability_tags("collection"),
        get_capability_phase_hints("collection"),
        build_capability_public_contracts("collection", COLLECTION_PUBLIC_TOOL_NAMES),
        "collection",
    ),
    CapabilityManifestEntry(
        "curve",
        "core_tools",
        CURVE_PUBLIC_TOOL_NAMES,
        get_capability_tags("curve"),
        get_capability_phase_hints("curve"),
        build_capability_public_contracts("curve", CURVE_PUBLIC_TOOL_NAMES),
        "curve",
    ),
    CapabilityManifestEntry(
        "lattice",
        "core_tools",
        LATTICE_PUBLIC_TOOL_NAMES,
        get_capability_tags("lattice"),
        get_capability_phase_hints("lattice"),
        build_capability_public_contracts("lattice", LATTICE_PUBLIC_TOOL_NAMES),
        "lattice",
    ),
    CapabilityManifestEntry(
        "sculpt",
        "core_tools",
        SCULPT_PUBLIC_TOOL_NAMES,
        get_capability_tags("sculpt"),
        get_capability_phase_hints("sculpt"),
        build_capability_public_contracts("sculpt", SCULPT_PUBLIC_TOOL_NAMES),
        "sculpt",
    ),
    CapabilityManifestEntry(
        "baking",
        "core_tools",
        BAKING_PUBLIC_TOOL_NAMES,
        get_capability_tags("baking"),
        get_capability_phase_hints("baking"),
        build_capability_public_contracts("baking", BAKING_PUBLIC_TOOL_NAMES),
        "baking",
    ),
    CapabilityManifestEntry(
        "text",
        "core_tools",
        TEXT_PUBLIC_TOOL_NAMES,
        get_capability_tags("text"),
        get_capability_phase_hints("text"),
        build_capability_public_contracts("text", TEXT_PUBLIC_TOOL_NAMES),
        "text",
    ),
    CapabilityManifestEntry(
        "armature",
        "core_tools",
        ARMATURE_PUBLIC_TOOL_NAMES,
        get_capability_tags("armature"),
        get_capability_phase_hints("armature"),
        build_capability_public_contracts("armature", ARMATURE_PUBLIC_TOOL_NAMES),
        "armature",
    ),
    CapabilityManifestEntry(
        "system",
        "core_tools",
        SYSTEM_PUBLIC_TOOL_NAMES,
        get_capability_tags("system"),
        get_capability_phase_hints("system"),
        build_capability_public_contracts("system", SYSTEM_PUBLIC_TOOL_NAMES),
        "system",
    ),
    CapabilityManifestEntry(
        "extraction",
        "core_tools",
        EXTRACTION_PUBLIC_TOOL_NAMES,
        get_capability_tags("extraction"),
        get_capability_phase_hints("extraction"),
        build_capability_public_contracts("extraction", EXTRACTION_PUBLIC_TOOL_NAMES),
        "extraction",
    ),
    CapabilityManifestEntry(
        "router",
        "router_tools",
        ROUTER_PUBLIC_TOOL_NAMES,
        get_capability_tags("router"),
        get_capability_phase_hints("router"),
        build_capability_public_contracts("router", ROUTER_PUBLIC_TOOL_NAMES),
        "router",
        pinned_tools=("router_set_goal", "router_get_status"),
    ),
    CapabilityManifestEntry(
        "workflow_catalog",
        "workflow_tools",
        WORKFLOW_PUBLIC_TOOL_NAMES,
        get_capability_tags("workflow_catalog"),
        get_capability_phase_hints("workflow_catalog"),
        build_capability_public_contracts("workflow_catalog", WORKFLOW_PUBLIC_TOOL_NAMES),
        "workflow",
        pinned_tools=("workflow_catalog",),
    ),
)


def get_capability_manifest() -> tuple[CapabilityManifestEntry, ...]:
    """Return the minimal platform capability manifest scaffold."""

    return CAPABILITY_MANIFEST
