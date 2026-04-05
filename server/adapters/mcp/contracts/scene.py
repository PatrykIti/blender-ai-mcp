# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

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


class SceneCreateResponseContract(MCPContract):
    action: Literal["light", "camera", "empty"]
    payload: dict[str, Any] | None = None
    error: str | None = None


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


class ScenePartGroupContract(MCPContract):
    group_name: str
    group_kind: Literal["explicit_objects", "named_group", "collection", "role"] = "explicit_objects"
    object_names: list[str] = []
    collection_name: str | None = None
    role: str | None = None


class SceneAssembledTargetScopeContract(MCPContract):
    scope_kind: Literal["single_object", "object_set", "collection", "part_groups", "scene"] = "scene"
    primary_target: str | None = None
    object_names: list[str] = []
    object_count: int = 0
    collection_name: str | None = None
    part_groups: list[ScenePartGroupContract] = []


class SceneCorrectionTruthPairContract(MCPContract):
    from_object: str
    to_object: str
    gap: dict[str, Any] | None = None
    alignment: dict[str, Any] | None = None
    overlap: dict[str, Any] | None = None
    contact_assertion: SceneAssertionPayloadContract | None = None
    error: str | None = None


class SceneCorrectionTruthSummaryContract(MCPContract):
    pairing_strategy: Literal["none", "primary_to_others"] = "none"
    pair_count: int = 0
    evaluated_pairs: int = 0
    contact_failures: int = 0
    overlap_pairs: int = 0
    separated_pairs: int = 0
    misaligned_pairs: int = 0


class SceneCorrectionTruthBundleContract(MCPContract):
    scope: SceneAssembledTargetScopeContract
    summary: SceneCorrectionTruthSummaryContract
    checks: list[SceneCorrectionTruthPairContract] = []
    error: str | None = None


class SceneTruthFollowupItemContract(MCPContract):
    kind: Literal["contact_failure", "gap", "overlap", "alignment", "measurement_error", "insufficient_scope"]
    summary: str
    priority: Literal["high", "normal"] = "normal"
    from_object: str | None = None
    to_object: str | None = None
    tool_name: str | None = None


class SceneRepairMacroCandidateContract(MCPContract):
    macro_name: str
    reason: str
    priority: Literal["high", "normal"] = "normal"
    arguments_hint: dict[str, Any] | None = None


class SceneTruthFollowupContract(MCPContract):
    scope: SceneAssembledTargetScopeContract
    continue_recommended: bool = False
    message: str
    focus_pairs: list[str] = []
    items: list[SceneTruthFollowupItemContract] = []
    macro_candidates: list[SceneRepairMacroCandidateContract] = []


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
