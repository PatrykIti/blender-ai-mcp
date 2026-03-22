# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Reusable provider builder for workflow catalog MCP tools."""

from __future__ import annotations

from typing import Any, Dict

from server.adapters.mcp.areas.workflow_catalog import register_workflow_tools

try:
    from fastmcp.server.providers import LocalProvider
except ImportError:  # pragma: no cover - exercised through explicit guard
    LocalProvider = None


def register_workflow_provider_tools(target: Any) -> Dict[str, Any]:
    """Register workflow catalog tools on a FastMCP-compatible target."""

    return register_workflow_tools(target)


def build_workflow_tools_provider() -> Any:
    """Build the reusable workflow LocalProvider for FastMCP 3.x surfaces."""

    if LocalProvider is None:
        raise RuntimeError("LocalProvider requires FastMCP >=3.0 in the active environment.")

    provider = LocalProvider()
    register_workflow_provider_tools(provider)
    return provider
