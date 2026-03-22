# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Core MCP provider inventory.

TASK-083-02 starts with the modeling family as the first extracted registrar seam.
Additional core families migrate into this provider in later slices.
"""

from __future__ import annotations

from typing import Any, Dict

from server.adapters.mcp.areas.mesh import register_mesh_tools
from server.adapters.mcp.areas.scene import register_scene_tools
from server.adapters.mcp.areas.modeling import register_modeling_tools

try:
    from fastmcp.server.providers import LocalProvider
except ImportError:  # pragma: no cover - exercised through explicit guard
    LocalProvider = None


def register_core_tools(target: Any) -> Dict[str, Any]:
    """Register the current core tool slice on a FastMCP-compatible target."""

    registered: Dict[str, Any] = {}
    registered.update(register_scene_tools(target))
    registered.update(register_mesh_tools(target))
    registered.update(register_modeling_tools(target))
    return registered


def build_core_tools_provider() -> Any:
    """Build the reusable core LocalProvider for FastMCP 3.x surfaces."""

    if LocalProvider is None:
        raise RuntimeError("LocalProvider requires FastMCP >=3.0 in the active environment.")

    provider = LocalProvider()
    register_core_tools(provider)
    return provider
