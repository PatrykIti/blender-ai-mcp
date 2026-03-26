# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Shared structured contract models for MCP adapter responses."""

from .base import MCPContract, to_contract
from .macro import (
    MacroActionRecordContract,
    MacroExecutionReportContract,
    MacroVerificationRecommendationContract,
)
from .output_schema import get_output_schema
from .reference import ReferenceImageRecordContract, ReferenceImagesResponseContract
from .vision import VisionCaptureBundleContract, VisionCaptureImageContract

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
