# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Structured contracts for correction audit events."""

from __future__ import annotations

from typing import Any

from server.adapters.mcp.contracts.base import MCPContract


class CorrectionIntentContract(MCPContract):
    original_tool_name: str
    original_params: dict[str, Any]
    corrected_tool_name: str
    corrected_params: dict[str, Any]
    category: str


class CorrectionExecutionContract(MCPContract):
    tool_name: str
    params: dict[str, Any]
    result: Any
    error: str | None = None


class CorrectionVerificationContract(MCPContract):
    status: str = "not_run"
    details: dict[str, Any] | None = None


class CorrectionAuditEventContract(MCPContract):
    event_id: str
    decision: str | None = None
    reason: str | None = None
    confidence: dict[str, Any] | None = None
    intent: CorrectionIntentContract
    execution: CorrectionExecutionContract
    verification: CorrectionVerificationContract
