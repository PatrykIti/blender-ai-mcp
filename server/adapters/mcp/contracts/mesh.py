# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Structured contracts for mesh introspection MCP tools."""

from __future__ import annotations

from typing import Any, Literal

from server.adapters.mcp.contracts.base import MCPContract


class MeshInspectResponseContract(MCPContract):
    """Structured envelope for mesh_inspect actions."""

    action: Literal[
        "summary",
        "vertices",
        "edges",
        "faces",
        "uvs",
        "normals",
        "attributes",
        "shape_keys",
        "group_weights",
    ]
    object_name: str | None = None
    total: int | None = None
    returned: int | None = None
    offset: int | None = None
    limit: int | None = None
    has_more: bool | None = None
    items: list[dict[str, Any]] | None = None
    summary: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    error: str | None = None
