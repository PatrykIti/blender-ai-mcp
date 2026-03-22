# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Structured contracts for scene context and inspection MCP tools."""

from __future__ import annotations

from typing import Any, Literal

from server.adapters.mcp.contracts.base import MCPContract


class SceneModeContract(MCPContract):
    mode: str
    active_object: str | None = None
    active_object_type: str | None = None
    selected_object_names: list[str]
    selection_count: int


class SceneSelectionContract(MCPContract):
    mode: str
    selected_object_names: list[str]
    selection_count: int
    edit_mode_vertex_count: int | None = None
    edit_mode_edge_count: int | None = None
    edit_mode_face_count: int | None = None


class SceneContextResponseContract(MCPContract):
    action: Literal["mode", "selection"]
    payload: SceneModeContract | SceneSelectionContract | None = None
    error: str | None = None


class SceneInspectResponseContract(MCPContract):
    action: Literal["object", "topology", "modifiers", "materials", "constraints", "modifier_data"]
    payload: dict[str, Any] | None = None
    error: str | None = None
