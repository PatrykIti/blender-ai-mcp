# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Shared structured contract models for MCP adapter responses."""

from __future__ import annotations

from server.adapters.mcp.contracts.base import MCPContract, to_contract

_LAZY_EXPORTS = {
    "MacroActionRecordContract": "server.adapters.mcp.contracts.macro",
    "MacroExecutionReportContract": "server.adapters.mcp.contracts.macro",
    "MacroVerificationRecommendationContract": "server.adapters.mcp.contracts.macro",
    "ReferenceImageRecordContract": "server.adapters.mcp.contracts.reference",
    "ReferenceImagesResponseContract": "server.adapters.mcp.contracts.reference",
    "VisionCaptureBundleContract": "server.adapters.mcp.contracts.vision",
    "VisionCaptureImageContract": "server.adapters.mcp.contracts.vision",
    "get_output_schema": "server.adapters.mcp.contracts.output_schema",
}


def __getattr__(name: str):
    """Resolve contract exports lazily to avoid circular imports."""

    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)

    module = __import__(module_name, fromlist=[name])
    return getattr(module, name)


__all__ = [
    "MCPContract",
    "MacroActionRecordContract",
    "MacroExecutionReportContract",
    "MacroVerificationRecommendationContract",
    "ReferenceImageRecordContract",
    "ReferenceImagesResponseContract",
    "VisionCaptureBundleContract",
    "VisionCaptureImageContract",
    "get_output_schema",
    "to_contract",
]
