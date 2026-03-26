# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Shared structured contracts for the future macro-tool layer."""

from __future__ import annotations

from typing import Any, Literal

from server.adapters.mcp.contracts.base import MCPContract
from server.adapters.mcp.contracts.vision import VisionCaptureBundleContract
from server.adapters.mcp.sampling.result_types import VisionAssistantContract


class MacroActionRecordContract(MCPContract):
    """One bounded action taken by a macro tool."""

    status: Literal["applied", "skipped", "failed"]
    action: str
    tool_name: str | None = None
    summary: str | None = None
    details: dict[str, Any] | None = None


class MacroVerificationRecommendationContract(MCPContract):
    """One deterministic follow-up verification recommendation."""

    tool_name: str
    reason: str
    priority: Literal["high", "normal"] = "normal"
    arguments_hint: dict[str, Any] | None = None


class MacroExecutionReportContract(MCPContract):
    """Shared machine-readable report envelope for bounded macro tools."""

    status: Literal["success", "partial", "needs_followup", "blocked", "failed"]
    macro_name: str
    intent: str | None = None
    actions_taken: list[MacroActionRecordContract]
    objects_created: list[str] | None = None
    objects_modified: list[str] | None = None
    verification_recommended: list[MacroVerificationRecommendationContract] | None = None
    capture_bundle: VisionCaptureBundleContract | None = None
    vision_assistant: VisionAssistantContract | None = None
    requires_followup: bool = False
    error: str | None = None
    assistant: dict[str, Any] | None = None
