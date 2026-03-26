# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Helpers for attaching vision artifacts to macro execution reports."""

from __future__ import annotations

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract
from server.adapters.mcp.contracts.vision import VisionCaptureBundleContract
from server.adapters.mcp.sampling.result_types import VisionAssistantContract


def attach_vision_artifacts(
    report: MacroExecutionReportContract,
    *,
    capture_bundle: VisionCaptureBundleContract | None = None,
    vision_assistant: VisionAssistantContract | None = None,
) -> MacroExecutionReportContract:
    """Return a macro report enriched with optional capture/vision artifacts."""

    return report.model_copy(
        update={
            "capture_bundle": capture_bundle,
            "vision_assistant": vision_assistant,
        }
    )
