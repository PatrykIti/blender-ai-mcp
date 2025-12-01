"""
Tool Call Entities.

Data classes for representing tool calls in the router pipeline.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class InterceptedToolCall:
    """Represents a tool call intercepted from the LLM.

    Attributes:
        tool_name: Name of the tool being called.
        params: Parameters passed to the tool.
        timestamp: When the call was intercepted.
        source: Origin of the call ("llm" or "router").
        original_prompt: User prompt that triggered this call (if available).
        session_id: Session identifier for grouping related calls.
    """

    tool_name: str
    params: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "llm"
    original_prompt: Optional[str] = None
    session_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "tool_name": self.tool_name,
            "params": self.params,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "original_prompt": self.original_prompt,
            "session_id": self.session_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InterceptedToolCall":
        """Create from dictionary."""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()

        return cls(
            tool_name=data["tool_name"],
            params=data.get("params", {}),
            timestamp=timestamp,
            source=data.get("source", "llm"),
            original_prompt=data.get("original_prompt"),
            session_id=data.get("session_id"),
        )


@dataclass
class CorrectedToolCall:
    """Represents a tool call after router corrections.

    Attributes:
        tool_name: Name of the tool (may differ from original).
        params: Corrected parameters.
        corrections_applied: List of corrections that were applied.
        original_tool_name: Original tool name before any overrides.
        original_params: Original parameters before corrections.
        is_injected: Whether this call was injected by the router.
    """

    tool_name: str
    params: Dict[str, Any]
    corrections_applied: List[str] = field(default_factory=list)
    original_tool_name: Optional[str] = None
    original_params: Optional[Dict[str, Any]] = None
    is_injected: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for execution."""
        return {
            "tool": self.tool_name,
            "params": self.params,
        }

    def to_full_dict(self) -> Dict[str, Any]:
        """Convert to full dictionary with metadata."""
        return {
            "tool_name": self.tool_name,
            "params": self.params,
            "corrections_applied": self.corrections_applied,
            "original_tool_name": self.original_tool_name,
            "original_params": self.original_params,
            "is_injected": self.is_injected,
        }


@dataclass
class ToolCallSequence:
    """Represents a sequence of tool calls to execute.

    Used when a single LLM call expands into multiple tool calls.

    Attributes:
        calls: List of corrected tool calls to execute in order.
        original_call: The original intercepted call.
        expansion_reason: Why the call was expanded (if applicable).
    """

    calls: List[CorrectedToolCall]
    original_call: Optional[InterceptedToolCall] = None
    expansion_reason: Optional[str] = None

    def __len__(self) -> int:
        """Return number of calls in sequence."""
        return len(self.calls)

    def __iter__(self):
        """Iterate over calls."""
        return iter(self.calls)

    def to_execution_list(self) -> List[Dict[str, Any]]:
        """Convert to list of dicts for execution."""
        return [call.to_dict() for call in self.calls]
