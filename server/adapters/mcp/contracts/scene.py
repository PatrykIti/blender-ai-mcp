# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Structured contracts for scene context and inspection MCP tools."""

from __future__ import annotations

from typing import Any, Literal

from server.adapters.mcp.contracts.base import MCPContract
from server.adapters.mcp.sampling.result_types import InspectionSummaryAssistantContract


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
    action: Literal[
        "object",
        "topology",
        "modifiers",
        "materials",
        "constraints",
        "modifier_data",
        "render",
        "color_management",
        "world",
    ]
    payload: dict[str, Any] | None = None
    error: str | None = None
    assistant: InspectionSummaryAssistantContract | None = None


class SceneConfigureResponseContract(MCPContract):
    action: Literal["render", "color_management", "world"]
    payload: dict[str, Any] | None = None
    error: str | None = None


class SceneSnapshotStateContract(MCPContract):
    snapshot: dict[str, Any] | None = None
    hash: str | None = None
    error: str | None = None
    assistant: InspectionSummaryAssistantContract | None = None


class SceneSnapshotDiffContract(MCPContract):
    objects_added: list[str] | None = None
    objects_removed: list[str] | None = None
    objects_modified: list[dict[str, Any]] | None = None
    baseline_hash: str | None = None
    target_hash: str | None = None
    baseline_timestamp: str | None = None
    target_timestamp: str | None = None
    has_changes: bool | None = None
    error: str | None = None
    assistant: InspectionSummaryAssistantContract | None = None


class SceneCustomPropertiesContract(MCPContract):
    object_name: str | None = None
    property_count: int | None = None
    properties: dict[str, Any] | None = None
    error: str | None = None


class SceneHierarchyContract(MCPContract):
    payload: dict[str, Any] | None = None
    error: str | None = None
    assistant: InspectionSummaryAssistantContract | None = None


class SceneBoundingBoxContract(MCPContract):
    payload: dict[str, Any] | None = None
    error: str | None = None
    assistant: InspectionSummaryAssistantContract | None = None


class SceneOriginInfoContract(MCPContract):
    payload: dict[str, Any] | None = None
    error: str | None = None
    assistant: InspectionSummaryAssistantContract | None = None


class SceneMeasureDistanceContract(MCPContract):
    payload: dict[str, Any] | None = None
    error: str | None = None


class SceneMeasureDimensionsContract(MCPContract):
    payload: dict[str, Any] | None = None
    error: str | None = None


class SceneMeasureGapContract(MCPContract):
    payload: dict[str, Any] | None = None
    error: str | None = None


class SceneMeasureAlignmentContract(MCPContract):
    payload: dict[str, Any] | None = None
    error: str | None = None


class SceneMeasureOverlapContract(MCPContract):
    payload: dict[str, Any] | None = None
    error: str | None = None


class SceneAssertionPayloadContract(MCPContract):
    assertion: str
    passed: bool
    subject: str
    target: str | None = None
    expected: dict[str, Any] | None = None
    actual: dict[str, Any] | None = None
    delta: dict[str, Any] | None = None
    tolerance: float | None = None
    units: str | None = None
    details: dict[str, Any] | None = None


class SceneAssertContactContract(MCPContract):
    payload: SceneAssertionPayloadContract | None = None
    error: str | None = None


class SceneAssertDimensionsContract(MCPContract):
    payload: SceneAssertionPayloadContract | None = None
    error: str | None = None


class SceneAssertContainmentContract(MCPContract):
    payload: SceneAssertionPayloadContract | None = None
    error: str | None = None


class SceneAssertSymmetryContract(MCPContract):
    payload: SceneAssertionPayloadContract | None = None
    error: str | None = None


class SceneAssertProportionContract(MCPContract):
    payload: SceneAssertionPayloadContract | None = None
    error: str | None = None
