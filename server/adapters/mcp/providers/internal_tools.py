# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Reusable provider builder for internal-only MCP helper tools."""

from __future__ import annotations

from typing import Any, Dict

LocalProvider: Any = None

try:
    from fastmcp.server.providers import LocalProvider
except ImportError:  # pragma: no cover - exercised through explicit guard
    pass


def register_internal_tools(target: Any) -> Dict[str, Any]:
    """Register internal helper tools on a FastMCP-compatible target."""

    return {}


def build_internal_tools_provider() -> Any:
    """Build the reusable internal LocalProvider for FastMCP 3.x surfaces."""

    if LocalProvider is None:
        raise RuntimeError("LocalProvider requires FastMCP >=3.0 in the active environment.")

    provider = LocalProvider()
    register_internal_tools(provider)
    return provider
