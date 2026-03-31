# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Structured contracts for goal-scoped reference image MCP tools."""

from __future__ import annotations

from typing import Literal

from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.sampling.result_types import VisionAssistantContract

from .base import MCPContract


class ReferenceImageRecordContract(MCPContract):
    """One normalized reference image stored in session scope."""

    reference_id: str
    goal: str
    label: str | None = None
    notes: str | None = None
    target_object: str | None = None
    target_view: str | None = None
    media_type: str
    source_kind: Literal["local_path"] = "local_path"
    original_path: str
    stored_path: str
    host_visible_path: str | None = None
    added_at: str


class ReferenceImagesResponseContract(MCPContract):
    """Structured response for the goal-scoped reference image surface."""

    action: Literal["attach", "list", "remove", "clear"]
    goal: str | None = None
    reference_count: int = 0
    references: list[ReferenceImageRecordContract] = []
    removed_reference_id: str | None = None
    message: str | None = None
    error: str | None = None


class ReferenceCompareCheckpointResponseContract(MCPContract):
    """Structured response for bounded checkpoint-vs-reference comparison."""

    action: Literal["compare_checkpoint", "compare_current_view"] = "compare_checkpoint"
    goal: str | None = None
    target_object: str | None = None
    target_view: str | None = None
    checkpoint_path: str
    checkpoint_label: str | None = None
    reference_count: int = 0
    reference_ids: list[str] = []
    reference_labels: list[str] = []
    vision_assistant: VisionAssistantContract | None = None
    message: str | None = None
    error: str | None = None


class ReferenceCompareStageCheckpointResponseContract(MCPContract):
    """Structured response for deterministic stage checkpoint capture + compare."""

    action: Literal["compare_stage_checkpoint"] = "compare_stage_checkpoint"
    goal: str | None = None
    target_object: str | None = None
    target_objects: list[str] = []
    collection_name: str | None = None
    target_view: str | None = None
    checkpoint_id: str
    checkpoint_label: str | None = None
    preset_profile: Literal["compact", "rich"] = "compact"
    preset_names: list[str] = []
    capture_count: int = 0
    captures: list[VisionCaptureImageContract] = []
    reference_count: int = 0
    reference_ids: list[str] = []
    reference_labels: list[str] = []
    vision_assistant: VisionAssistantContract | None = None
    message: str | None = None
    error: str | None = None


class ReferenceIterateStageCheckpointResponseContract(MCPContract):
    """Structured response for session-aware iterative stage checkpoint loops."""

    action: Literal["iterate_stage_checkpoint"] = "iterate_stage_checkpoint"
    goal: str | None = None
    target_object: str | None = None
    target_objects: list[str] = []
    collection_name: str | None = None
    target_view: str | None = None
    checkpoint_id: str
    checkpoint_label: str | None = None
    iteration_index: int = 1
    loop_disposition: Literal["continue_build", "inspect_validate", "stop"] = "continue_build"
    continue_recommended: bool = True
    prior_checkpoint_id: str | None = None
    prior_correction_focus: list[str] = []
    correction_focus: list[str] = []
    repeated_correction_focus: list[str] = []
    stagnation_count: int = 0
    stop_reason: str | None = None
    compare_result: ReferenceCompareStageCheckpointResponseContract
    message: str | None = None
    error: str | None = None
