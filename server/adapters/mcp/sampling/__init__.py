# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Bounded server-side sampling assistant helpers."""

from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantPolicy,
    AssistantRunResult,
    InspectionSummaryAssistantContract,
    InspectionSummaryContract,
    RepairSuggestionActionContract,
    RepairSuggestionAssistantContract,
    RepairSuggestionContract,
    VisionAssistantContract,
    VisionAssistContract,
    VisionInputSummaryContract,
    VisionIssueContract,
    VisionRecommendedCheckContract,
    to_inspection_assistant_contract,
    to_repair_assistant_contract,
    to_vision_assistant_contract,
)

_RUNNER_EXPORTS = {
    "INSPECTION_SUMMARIZER_POLICY",
    "REPAIR_SUGGESTER_POLICY",
    "run_inspection_summary_assistant",
    "run_repair_suggestion_assistant",
    "run_typed_assistant",
}


def __getattr__(name: str):
    """Resolve runner exports lazily to avoid circular imports during contract import."""

    if name not in _RUNNER_EXPORTS:
        raise AttributeError(name)

    from server.adapters.mcp.sampling import assistant_runner

    return getattr(assistant_runner, name)

__all__ = [
    "AssistantBudgetContract",
    "AssistantPolicy",
    "AssistantRunResult",
    "INSPECTION_SUMMARIZER_POLICY",
    "InspectionSummaryAssistantContract",
    "InspectionSummaryContract",
    "REPAIR_SUGGESTER_POLICY",
    "RepairSuggestionActionContract",
    "RepairSuggestionAssistantContract",
    "RepairSuggestionContract",
    "VisionAssistantContract",
    "VisionAssistContract",
    "VisionInputSummaryContract",
    "VisionIssueContract",
    "VisionRecommendedCheckContract",
    "run_inspection_summary_assistant",
    "run_repair_suggestion_assistant",
    "run_typed_assistant",
    "to_inspection_assistant_contract",
    "to_repair_assistant_contract",
    "to_vision_assistant_contract",
]
