# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Reusable provider builder for router MCP tools."""

from __future__ import annotations

from typing import Any, Dict

from server.adapters.mcp.areas.router import register_router_tools

LocalProvider: Any = None

try:
    from fastmcp.server.providers import LocalProvider
except ImportError:  # pragma: no cover - exercised through explicit guard
    pass


def register_router_provider_tools(target: Any) -> Dict[str, Any]:
    """Register router tools on a FastMCP-compatible target."""

    return register_router_tools(target)


def build_router_tools_provider() -> Any:
    """Build the reusable router LocalProvider for FastMCP 3.x surfaces."""

    if LocalProvider is None:
        raise RuntimeError("LocalProvider requires FastMCP >=3.0 in the active environment.")

    provider = LocalProvider()
    register_router_provider_tools(provider)
    return provider
