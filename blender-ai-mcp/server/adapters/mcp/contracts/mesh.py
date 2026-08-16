# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Structured contracts for mesh introspection MCP tools."""

from __future__ import annotations

from typing import Any, Literal

from server.adapters.mcp.contracts.base import MCPContract
from server.adapters.mcp.sampling.result_types import InspectionSummaryAssistantContract


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
    assistant: InspectionSummaryAssistantContract | None = None


class MeshSelectionResponseContract(MCPContract):
    """Structured envelope for grouped mesh selection tools."""

    action: Literal[
        "all",
        "none",
        "linked",
        "more",
        "less",
        "boundary",
        "by_index",
        "loop",
        "ring",
        "by_location",
    ]
    payload: dict[str, Any] | None = None
    error: str | None = None
