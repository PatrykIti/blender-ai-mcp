# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""FastMCP platform inventory and bootstrap scaffolding."""

from .runtime_inventory import (
    FASTMCP_BASELINE,
    FASTMCP_FEATURE_GATE_BASELINE,
    MCP_RUNTIME_COUPLINGS,
    MCP_SURFACE_MODULES,
    SUPPORTED_PYTHON_BASELINE,
    SURFACE_PROFILES,
    build_runtime_couplings,
    build_runtime_inventory,
    get_bootstrap_side_effect_modules,
    get_filesystem_area_modules,
    get_metadata_loader_gap_areas,
    get_router_metadata_directories,
)

__all__ = [
    "FASTMCP_BASELINE",
    "FASTMCP_FEATURE_GATE_BASELINE",
    "MCP_RUNTIME_COUPLINGS",
    "MCP_SURFACE_MODULES",
    "SUPPORTED_PYTHON_BASELINE",
    "SURFACE_PROFILES",
    "build_runtime_inventory",
    "build_runtime_couplings",
    "get_bootstrap_side_effect_modules",
    "get_filesystem_area_modules",
    "get_metadata_loader_gap_areas",
    "get_router_metadata_directories",
]
