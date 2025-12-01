"""
Router Logger.

Logging and telemetry for router decisions.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import json


class EventType(Enum):
    """Types of router events."""

    INTERCEPT = "intercept"
    CONTEXT_ANALYZED = "context_analyzed"
    PATTERN_DETECTED = "pattern_detected"
    CORRECTION_APPLIED = "correction_applied"
    OVERRIDE_TRIGGERED = "override_triggered"
    WORKFLOW_EXPANDED = "workflow_expanded"
    FIREWALL_DECISION = "firewall_decision"
    EXECUTION_COMPLETE = "execution_complete"
    ERROR = "error"


@dataclass
class RouterEvent:
    """A single router event for telemetry.

    Attributes:
        event_type: Type of the event.
        timestamp: When the event occurred.
        tool_name: Tool involved (if applicable).
        data: Additional event data.
        session_id: Session identifier for grouping.
    """

    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    tool_name: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "tool_name": self.tool_name,
            "data": self.data,
            "session_id": self.session_id,
        }


class RouterLogger:
    """Logger for router decisions and telemetry.

    Logs events such as:
    - Tool intercepted (original call)
    - Scene context analyzed
    - Pattern detected
    - Correction applied
    - Override triggered
    - Workflow expanded
    - Firewall decision
    - Final execution

    Attributes:
        logger: Python logger instance.
        events: List of recorded events.
        enabled: Whether logging is enabled.
        max_events: Maximum events to keep in memory.
    """

    def __init__(
        self,
        name: str = "router",
        enabled: bool = True,
        max_events: int = 1000,
        log_level: int = logging.INFO,
    ):
        """Initialize router logger.

        Args:
            name: Logger name.
            enabled: Whether logging is enabled.
            max_events: Maximum events to keep in memory.
            log_level: Logging level for console output.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self._events: List[RouterEvent] = []
        self.enabled = enabled
        self.max_events = max_events
        self._session_id: Optional[str] = None
        self._stats: Dict[str, int] = {
            "total_events": 0,
            "intercepts": 0,
            "corrections": 0,
            "overrides": 0,
            "workflow_expansions": 0,
            "firewall_blocks": 0,
            "firewall_fixes": 0,
            "errors": 0,
        }

    def set_session_id(self, session_id: str) -> None:
        """Set current session ID for event grouping.

        Args:
            session_id: Session identifier.
        """
        self._session_id = session_id

    def _add_event(self, event: RouterEvent) -> None:
        """Add an event to the log.

        Args:
            event: Event to add.
        """
        if not self.enabled:
            return

        event.session_id = self._session_id
        self._events.append(event)
        self._stats["total_events"] += 1

        # Trim events if over limit
        if len(self._events) > self.max_events:
            self._events = self._events[-self.max_events:]

    def log_intercept(
        self,
        tool_name: str,
        params: Dict[str, Any],
        prompt: Optional[str] = None,
    ) -> None:
        """Log tool interception.

        Args:
            tool_name: Name of intercepted tool.
            params: Tool parameters.
            prompt: Original user prompt (if available).
        """
        self._stats["intercepts"] += 1

        event = RouterEvent(
            event_type=EventType.INTERCEPT,
            tool_name=tool_name,
            data={
                "params": params,
                "prompt": prompt,
            },
        )
        self._add_event(event)

        self.logger.debug(
            f"Intercepted: {tool_name} with params={json.dumps(params, default=str)}"
        )

    def log_context_analyzed(
        self,
        mode: str,
        active_object: Optional[str],
        has_selection: bool,
        object_count: int,
    ) -> None:
        """Log scene context analysis.

        Args:
            mode: Current Blender mode.
            active_object: Active object name.
            has_selection: Whether there is a selection.
            object_count: Number of objects in scene.
        """
        event = RouterEvent(
            event_type=EventType.CONTEXT_ANALYZED,
            data={
                "mode": mode,
                "active_object": active_object,
                "has_selection": has_selection,
                "object_count": object_count,
            },
        )
        self._add_event(event)

        self.logger.debug(
            f"Context: mode={mode}, active={active_object}, "
            f"selection={has_selection}, objects={object_count}"
        )

    def log_pattern_detected(
        self,
        pattern_name: str,
        confidence: float,
        suggested_workflow: Optional[str] = None,
    ) -> None:
        """Log pattern detection.

        Args:
            pattern_name: Detected pattern name.
            confidence: Detection confidence (0.0 to 1.0).
            suggested_workflow: Suggested workflow name.
        """
        event = RouterEvent(
            event_type=EventType.PATTERN_DETECTED,
            data={
                "pattern_name": pattern_name,
                "confidence": confidence,
                "suggested_workflow": suggested_workflow,
            },
        )
        self._add_event(event)

        self.logger.info(
            f"Pattern detected: {pattern_name} (confidence={confidence:.2f})"
        )

    def log_correction(
        self,
        original_tool: str,
        corrections: List[str],
        final_tools: List[Dict[str, Any]],
    ) -> None:
        """Log correction applied.

        Args:
            original_tool: Original tool name.
            corrections: List of corrections applied.
            final_tools: Final tool sequence.
        """
        self._stats["corrections"] += 1

        event = RouterEvent(
            event_type=EventType.CORRECTION_APPLIED,
            tool_name=original_tool,
            data={
                "corrections": corrections,
                "final_tools": final_tools,
            },
        )
        self._add_event(event)

        self.logger.info(
            f"Corrections applied to {original_tool}: {', '.join(corrections)}"
        )

    def log_override(
        self,
        original_tool: str,
        reason: str,
        replacement_tools: List[Dict[str, Any]],
    ) -> None:
        """Log override triggered.

        Args:
            original_tool: Original tool name.
            reason: Override reason.
            replacement_tools: Replacement tool sequence.
        """
        self._stats["overrides"] += 1

        event = RouterEvent(
            event_type=EventType.OVERRIDE_TRIGGERED,
            tool_name=original_tool,
            data={
                "reason": reason,
                "replacement_tools": replacement_tools,
            },
        )
        self._add_event(event)

        replacement_names = [t.get("tool", "unknown") for t in replacement_tools]
        self.logger.info(
            f"Override: {original_tool} → {', '.join(replacement_names)} "
            f"(reason: {reason})"
        )

    def log_workflow_expanded(
        self,
        workflow_name: str,
        step_count: int,
        trigger: str,
    ) -> None:
        """Log workflow expansion.

        Args:
            workflow_name: Expanded workflow name.
            step_count: Number of steps in workflow.
            trigger: What triggered the expansion.
        """
        self._stats["workflow_expansions"] += 1

        event = RouterEvent(
            event_type=EventType.WORKFLOW_EXPANDED,
            data={
                "workflow_name": workflow_name,
                "step_count": step_count,
                "trigger": trigger,
            },
        )
        self._add_event(event)

        self.logger.info(
            f"Workflow expanded: {workflow_name} ({step_count} steps)"
        )

    def log_firewall(
        self,
        tool_name: str,
        action: str,
        message: str,
    ) -> None:
        """Log firewall decision.

        Args:
            tool_name: Tool being validated.
            action: Firewall action (allow, block, modify, auto_fix).
            message: Decision message.
        """
        if action == "block":
            self._stats["firewall_blocks"] += 1
        elif action in ("auto_fix", "modify"):
            self._stats["firewall_fixes"] += 1

        event = RouterEvent(
            event_type=EventType.FIREWALL_DECISION,
            tool_name=tool_name,
            data={
                "action": action,
                "message": message,
            },
        )
        self._add_event(event)

        log_level = logging.WARNING if action == "block" else logging.DEBUG
        self.logger.log(log_level, f"Firewall: {tool_name} → {action}: {message}")

    def log_execution_complete(
        self,
        original_tool: str,
        executed_tools: List[str],
        duration_ms: float,
        success: bool,
    ) -> None:
        """Log execution completion.

        Args:
            original_tool: Original requested tool.
            executed_tools: Tools that were actually executed.
            duration_ms: Execution duration in milliseconds.
            success: Whether execution was successful.
        """
        event = RouterEvent(
            event_type=EventType.EXECUTION_COMPLETE,
            tool_name=original_tool,
            data={
                "executed_tools": executed_tools,
                "duration_ms": duration_ms,
                "success": success,
            },
        )
        self._add_event(event)

        status = "OK" if success else "FAILED"
        self.logger.info(
            f"Execution complete: {original_tool} → "
            f"{len(executed_tools)} tools ({duration_ms:.1f}ms) [{status}]"
        )

    def log_error(
        self,
        tool_name: str,
        error: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an error.

        Args:
            tool_name: Tool that caused the error.
            error: Error message.
            context: Additional error context.
        """
        self._stats["errors"] += 1

        event = RouterEvent(
            event_type=EventType.ERROR,
            tool_name=tool_name,
            data={
                "error": error,
                "context": context or {},
            },
        )
        self._add_event(event)

        self.logger.error(f"Error in {tool_name}: {error}")

    def get_events(
        self,
        limit: int = 100,
        event_type: Optional[EventType] = None,
        session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get recent events.

        Args:
            limit: Maximum number of events to return.
            event_type: Filter by event type.
            session_id: Filter by session ID.

        Returns:
            List of event dictionaries.
        """
        filtered = self._events

        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]

        if session_id:
            filtered = [e for e in filtered if e.session_id == session_id]

        return [e.to_dict() for e in filtered[-limit:]]

    def get_stats(self) -> Dict[str, int]:
        """Get logging statistics.

        Returns:
            Dictionary with event counts.
        """
        return dict(self._stats)

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        for key in self._stats:
            self._stats[key] = 0

    def clear_events(self) -> None:
        """Clear all recorded events."""
        self._events = []

    def export_events(self, filepath: str) -> bool:
        """Export events to JSON file.

        Args:
            filepath: Path to output file.

        Returns:
            True if export successful.
        """
        try:
            events_data = [e.to_dict() for e in self._events]
            with open(filepath, "w") as f:
                json.dump(events_data, f, indent=2, default=str)
            return True
        except Exception as e:
            self.logger.error(f"Failed to export events: {e}")
            return False

    def get_session_summary(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary for a session.

        Args:
            session_id: Session to summarize (current if None).

        Returns:
            Session summary dictionary.
        """
        sid = session_id or self._session_id
        session_events = [e for e in self._events if e.session_id == sid]

        if not session_events:
            return {"session_id": sid, "event_count": 0}

        # Count event types
        type_counts: Dict[str, int] = {}
        for event in session_events:
            type_name = event.event_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        # Get time range
        timestamps = [e.timestamp for e in session_events]
        start_time = min(timestamps)
        end_time = max(timestamps)
        duration = (end_time - start_time).total_seconds()

        return {
            "session_id": sid,
            "event_count": len(session_events),
            "event_types": type_counts,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
        }


# Global logger instance for convenience
_default_logger: Optional[RouterLogger] = None


def get_router_logger() -> RouterLogger:
    """Get the default router logger instance.

    Returns:
        RouterLogger instance.
    """
    global _default_logger
    if _default_logger is None:
        _default_logger = RouterLogger()
    return _default_logger


def configure_router_logging(
    level: int = logging.INFO,
    enabled: bool = True,
    max_events: int = 1000,
) -> RouterLogger:
    """Configure the default router logger.

    Args:
        level: Logging level.
        enabled: Whether logging is enabled.
        max_events: Maximum events to keep.

    Returns:
        Configured RouterLogger instance.
    """
    global _default_logger
    _default_logger = RouterLogger(
        enabled=enabled,
        max_events=max_events,
        log_level=level,
    )
    return _default_logger
