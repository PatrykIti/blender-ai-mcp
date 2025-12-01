"""
Unit tests for Router Logger.

Tests logging and telemetry functionality.
"""

import pytest
import tempfile
import json
from datetime import datetime
from pathlib import Path

from server.router.infrastructure.logger import (
    RouterLogger,
    RouterEvent,
    EventType,
    get_router_logger,
    configure_router_logging,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def logger():
    """Create a RouterLogger instance."""
    return RouterLogger()


@pytest.fixture
def disabled_logger():
    """Create a disabled RouterLogger instance."""
    return RouterLogger(enabled=False)


# ============================================================================
# RouterEvent Tests
# ============================================================================


class TestRouterEvent:
    """Tests for RouterEvent dataclass."""

    def test_create_event(self):
        """Test creating an event."""
        event = RouterEvent(
            event_type=EventType.INTERCEPT,
            tool_name="mesh_extrude_region",
            data={"params": {"depth": 0.5}},
        )
        assert event.event_type == EventType.INTERCEPT
        assert event.tool_name == "mesh_extrude_region"
        assert event.data["params"]["depth"] == 0.5
        assert event.timestamp is not None

    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        event = RouterEvent(
            event_type=EventType.CORRECTION_APPLIED,
            tool_name="test_tool",
            data={"corrections": ["mode_switch"]},
            session_id="session_123",
        )
        d = event.to_dict()
        assert d["event_type"] == "correction_applied"
        assert d["tool_name"] == "test_tool"
        assert d["data"]["corrections"] == ["mode_switch"]
        assert d["session_id"] == "session_123"
        assert "timestamp" in d


# ============================================================================
# RouterLogger Initialization Tests
# ============================================================================


class TestRouterLoggerInit:
    """Tests for RouterLogger initialization."""

    def test_init_default(self):
        """Test default initialization."""
        logger = RouterLogger()
        assert logger.enabled is True
        assert logger.max_events == 1000
        assert len(logger._events) == 0

    def test_init_disabled(self):
        """Test disabled initialization."""
        logger = RouterLogger(enabled=False)
        assert logger.enabled is False

    def test_init_custom_max_events(self):
        """Test custom max events."""
        logger = RouterLogger(max_events=50)
        assert logger.max_events == 50


# ============================================================================
# Log Intercept Tests
# ============================================================================


class TestLogIntercept:
    """Tests for log_intercept method."""

    def test_log_intercept_basic(self, logger):
        """Test basic intercept logging."""
        logger.log_intercept("mesh_extrude_region", {"depth": 0.5})

        assert logger._stats["intercepts"] == 1
        assert len(logger._events) == 1

        event = logger._events[0]
        assert event.event_type == EventType.INTERCEPT
        assert event.tool_name == "mesh_extrude_region"

    def test_log_intercept_with_prompt(self, logger):
        """Test intercept logging with prompt."""
        logger.log_intercept(
            "mesh_bevel",
            {"width": 0.1},
            prompt="bevel the edges",
        )

        event = logger._events[0]
        assert event.data["prompt"] == "bevel the edges"

    def test_log_intercept_disabled(self, disabled_logger):
        """Test intercept not logged when disabled."""
        disabled_logger.log_intercept("test", {})
        assert len(disabled_logger._events) == 0


# ============================================================================
# Log Correction Tests
# ============================================================================


class TestLogCorrection:
    """Tests for log_correction method."""

    def test_log_correction(self, logger):
        """Test correction logging."""
        logger.log_correction(
            "mesh_extrude_region",
            ["mode_switch", "auto_select"],
            [{"tool": "system_set_mode", "params": {"mode": "EDIT"}}],
        )

        assert logger._stats["corrections"] == 1
        event = logger._events[0]
        assert event.event_type == EventType.CORRECTION_APPLIED
        assert "mode_switch" in event.data["corrections"]


# ============================================================================
# Log Override Tests
# ============================================================================


class TestLogOverride:
    """Tests for log_override method."""

    def test_log_override(self, logger):
        """Test override logging."""
        logger.log_override(
            "mesh_extrude_region",
            "phone_pattern",
            [
                {"tool": "mesh_inset", "params": {"thickness": 0.03}},
                {"tool": "mesh_extrude_region", "params": {"depth": -0.02}},
            ],
        )

        assert logger._stats["overrides"] == 1
        event = logger._events[0]
        assert event.event_type == EventType.OVERRIDE_TRIGGERED
        assert event.data["reason"] == "phone_pattern"


# ============================================================================
# Log Firewall Tests
# ============================================================================


class TestLogFirewall:
    """Tests for log_firewall method."""

    def test_log_firewall_allow(self, logger):
        """Test firewall allow logging."""
        logger.log_firewall("mesh_bevel", "allow", "Valid operation")

        event = logger._events[0]
        assert event.event_type == EventType.FIREWALL_DECISION
        assert event.data["action"] == "allow"

    def test_log_firewall_block(self, logger):
        """Test firewall block logging."""
        logger.log_firewall("scene_delete", "block", "No objects to delete")

        assert logger._stats["firewall_blocks"] == 1

    def test_log_firewall_auto_fix(self, logger):
        """Test firewall auto_fix logging."""
        logger.log_firewall("mesh_extrude", "auto_fix", "Mode switched")

        assert logger._stats["firewall_fixes"] == 1


# ============================================================================
# Log Context & Pattern Tests
# ============================================================================


class TestLogContextAndPattern:
    """Tests for context and pattern logging."""

    def test_log_context_analyzed(self, logger):
        """Test context analysis logging."""
        logger.log_context_analyzed(
            mode="EDIT",
            active_object="Cube",
            has_selection=True,
            object_count=5,
        )

        event = logger._events[0]
        assert event.event_type == EventType.CONTEXT_ANALYZED
        assert event.data["mode"] == "EDIT"
        assert event.data["object_count"] == 5

    def test_log_pattern_detected(self, logger):
        """Test pattern detection logging."""
        logger.log_pattern_detected(
            pattern_name="phone_like",
            confidence=0.85,
            suggested_workflow="phone_workflow",
        )

        event = logger._events[0]
        assert event.event_type == EventType.PATTERN_DETECTED
        assert event.data["confidence"] == 0.85


# ============================================================================
# Log Workflow & Execution Tests
# ============================================================================


class TestLogWorkflowAndExecution:
    """Tests for workflow and execution logging."""

    def test_log_workflow_expanded(self, logger):
        """Test workflow expansion logging."""
        logger.log_workflow_expanded(
            workflow_name="phone_workflow",
            step_count=10,
            trigger="pattern_detected",
        )

        assert logger._stats["workflow_expansions"] == 1
        event = logger._events[0]
        assert event.data["step_count"] == 10

    def test_log_execution_complete(self, logger):
        """Test execution completion logging."""
        logger.log_execution_complete(
            original_tool="mesh_extrude_region",
            executed_tools=["system_set_mode", "mesh_select", "mesh_extrude_region"],
            duration_ms=45.5,
            success=True,
        )

        event = logger._events[0]
        assert event.event_type == EventType.EXECUTION_COMPLETE
        assert event.data["duration_ms"] == 45.5
        assert event.data["success"] is True


# ============================================================================
# Log Error Tests
# ============================================================================


class TestLogError:
    """Tests for error logging."""

    def test_log_error(self, logger):
        """Test error logging."""
        logger.log_error(
            "mesh_bevel",
            "Invalid parameter: width must be positive",
            context={"width": -0.5},
        )

        assert logger._stats["errors"] == 1
        event = logger._events[0]
        assert event.event_type == EventType.ERROR
        assert "Invalid parameter" in event.data["error"]


# ============================================================================
# Session Management Tests
# ============================================================================


class TestSessionManagement:
    """Tests for session management."""

    def test_set_session_id(self, logger):
        """Test setting session ID."""
        logger.set_session_id("session_abc")
        logger.log_intercept("test", {})

        event = logger._events[0]
        assert event.session_id == "session_abc"

    def test_get_session_summary(self, logger):
        """Test getting session summary."""
        logger.set_session_id("session_xyz")
        logger.log_intercept("tool1", {})
        logger.log_correction("tool1", ["fix1"], [])
        logger.log_intercept("tool2", {})

        summary = logger.get_session_summary()
        assert summary["session_id"] == "session_xyz"
        assert summary["event_count"] == 3
        assert "intercept" in summary["event_types"]


# ============================================================================
# Event Retrieval Tests
# ============================================================================


class TestEventRetrieval:
    """Tests for event retrieval."""

    def test_get_events_limit(self, logger):
        """Test getting events with limit."""
        for i in range(10):
            logger.log_intercept(f"tool_{i}", {})

        events = logger.get_events(limit=5)
        assert len(events) == 5

    def test_get_events_by_type(self, logger):
        """Test filtering events by type."""
        logger.log_intercept("tool1", {})
        logger.log_correction("tool1", [], [])
        logger.log_intercept("tool2", {})

        events = logger.get_events(event_type=EventType.INTERCEPT)
        assert len(events) == 2

    def test_get_events_by_session(self, logger):
        """Test filtering events by session."""
        logger.set_session_id("session_a")
        logger.log_intercept("tool1", {})

        logger.set_session_id("session_b")
        logger.log_intercept("tool2", {})

        events = logger.get_events(session_id="session_a")
        assert len(events) == 1
        assert events[0]["data"]["params"] == {}


# ============================================================================
# Statistics Tests
# ============================================================================


class TestStatistics:
    """Tests for statistics."""

    def test_get_stats(self, logger):
        """Test getting statistics."""
        logger.log_intercept("tool", {})
        logger.log_correction("tool", [], [])
        logger.log_override("tool", "reason", [])

        stats = logger.get_stats()
        assert stats["intercepts"] == 1
        assert stats["corrections"] == 1
        assert stats["overrides"] == 1
        assert stats["total_events"] == 3

    def test_reset_stats(self, logger):
        """Test resetting statistics."""
        logger.log_intercept("tool", {})
        logger.reset_stats()

        stats = logger.get_stats()
        assert stats["intercepts"] == 0
        assert stats["total_events"] == 0


# ============================================================================
# Event Management Tests
# ============================================================================


class TestEventManagement:
    """Tests for event management."""

    def test_clear_events(self, logger):
        """Test clearing events."""
        logger.log_intercept("tool", {})
        logger.clear_events()

        assert len(logger._events) == 0

    def test_max_events_trimming(self):
        """Test events are trimmed when over max."""
        logger = RouterLogger(max_events=5)

        for i in range(10):
            logger.log_intercept(f"tool_{i}", {})

        assert len(logger._events) == 5
        # Should keep the most recent events
        assert logger._events[-1].tool_name == "tool_9"

    def test_export_events(self, logger):
        """Test exporting events to file."""
        logger.log_intercept("tool1", {"param": "value"})
        logger.log_correction("tool1", ["fix"], [])

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            result = logger.export_events(filepath)
            assert result is True

            with open(filepath) as f:
                data = json.load(f)

            assert len(data) == 2
            assert data[0]["event_type"] == "intercept"
        finally:
            Path(filepath).unlink(missing_ok=True)


# ============================================================================
# Global Logger Tests
# ============================================================================


class TestGlobalLogger:
    """Tests for global logger functions."""

    def test_get_router_logger(self):
        """Test getting default logger."""
        logger = get_router_logger()
        assert logger is not None
        assert isinstance(logger, RouterLogger)

    def test_configure_router_logging(self):
        """Test configuring default logger."""
        logger = configure_router_logging(
            enabled=True,
            max_events=500,
        )
        assert logger.max_events == 500
        assert logger.enabled is True
