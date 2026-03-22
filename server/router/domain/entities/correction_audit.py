"""Structured correction audit entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CorrectionIntent:
    """What the system intended to change before execution."""

    original_tool_name: str
    original_params: dict[str, Any]
    corrected_tool_name: str
    corrected_params: dict[str, Any]
    category: str


@dataclass(frozen=True)
class CorrectionExecution:
    """What actually executed for the correction path."""

    tool_name: str
    params: dict[str, Any]
    result: Any
    error: str | None = None


@dataclass(frozen=True)
class CorrectionVerification:
    """What verification state is known after execution."""

    status: str = "not_run"
    details: dict[str, Any] | None = None


@dataclass(frozen=True)
class CorrectionAuditEvent:
    """One correction audit event with separated intent/execution/verification fields."""

    event_id: str
    decision: str | None
    reason: str | None
    confidence: dict[str, Any] | None
    intent: CorrectionIntent
    execution: CorrectionExecution
    verification: CorrectionVerification = field(default_factory=CorrectionVerification)
