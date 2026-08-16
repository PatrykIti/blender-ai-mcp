"""Domain-neutral clarification requirements for structured elicitation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ClarificationRequirement:
    """One missing input requirement derived from workflow parameter state."""

    field_name: str
    prompt: str
    value_type: str
    required: bool = True
    choices: tuple[str, ...] | None = None
    allows_multiple: bool = False
    default: Any | None = None
    context: str | None = None
    description: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class ClarificationPlan:
    """A set of clarification requirements for one workflow-driven request."""

    goal: str
    workflow_name: str
    requirements: tuple[ClarificationRequirement, ...] = field(default_factory=tuple)

    @property
    def is_empty(self) -> bool:
        """Return True when there are no outstanding clarification requirements."""

        return len(self.requirements) == 0
