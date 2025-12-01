"""
Unit tests for Tool Interceptor.

Tests for ToolInterceptor implementation.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from server.router.application.interceptor.tool_interceptor import ToolInterceptor
from server.router.domain.entities.tool_call import InterceptedToolCall


class TestToolInterceptorBasic:
    """Test basic interception functionality."""

    def test_intercept_creates_call(self):
        """Test that intercept creates an InterceptedToolCall."""
        interceptor = ToolInterceptor()

        call = interceptor.intercept("mesh_extrude", {"depth": 1.0})

        assert isinstance(call, InterceptedToolCall)
        assert call.tool_name == "mesh_extrude"
        assert call.params == {"depth": 1.0}
        assert call.source == "llm"

    def test_intercept_with_prompt(self):
        """Test interception with original prompt."""
        interceptor = ToolInterceptor()

        call = interceptor.intercept(
            "mesh_bevel",
            {"width": 0.5},
            prompt="bevel the edges",
        )

        assert call.original_prompt == "bevel the edges"

    def test_intercept_empty_params(self):
        """Test interception with empty params."""
        interceptor = ToolInterceptor()

        call = interceptor.intercept("scene_list_objects", {})

        assert call.params == {}

    def test_intercept_none_params(self):
        """Test interception with None params."""
        interceptor = ToolInterceptor()

        call = interceptor.intercept("scene_list_objects", None)

        assert call.params == {}

    def test_intercept_assigns_timestamp(self):
        """Test that intercept assigns a timestamp."""
        interceptor = ToolInterceptor()
        before = datetime.now()

        call = interceptor.intercept("mesh_select", {"action": "all"})

        after = datetime.now()
        assert before <= call.timestamp <= after


class TestToolInterceptorHistory:
    """Test call history functionality."""

    def test_get_history_empty(self):
        """Test get_history on empty interceptor."""
        interceptor = ToolInterceptor()

        history = interceptor.get_history()

        assert history == []

    def test_get_history_single_call(self):
        """Test get_history with single call."""
        interceptor = ToolInterceptor()
        interceptor.intercept("mesh_extrude", {"depth": 1.0})

        history = interceptor.get_history()

        assert len(history) == 1
        assert history[0].tool_name == "mesh_extrude"

    def test_get_history_multiple_calls(self):
        """Test get_history with multiple calls (newest first)."""
        interceptor = ToolInterceptor()
        interceptor.intercept("tool_a", {})
        interceptor.intercept("tool_b", {})
        interceptor.intercept("tool_c", {})

        history = interceptor.get_history()

        assert len(history) == 3
        assert history[0].tool_name == "tool_c"  # Newest first
        assert history[1].tool_name == "tool_b"
        assert history[2].tool_name == "tool_a"

    def test_get_history_with_limit(self):
        """Test get_history respects limit."""
        interceptor = ToolInterceptor()
        for i in range(10):
            interceptor.intercept(f"tool_{i}", {})

        history = interceptor.get_history(limit=3)

        assert len(history) == 3
        assert history[0].tool_name == "tool_9"
        assert history[1].tool_name == "tool_8"
        assert history[2].tool_name == "tool_7"

    def test_max_history_enforced(self):
        """Test that max_history is enforced."""
        interceptor = ToolInterceptor(max_history=5)

        for i in range(10):
            interceptor.intercept(f"tool_{i}", {})

        assert interceptor.history_count == 5
        history = interceptor.get_history()
        assert history[0].tool_name == "tool_9"
        assert history[4].tool_name == "tool_5"

    def test_clear_history(self):
        """Test clearing history."""
        interceptor = ToolInterceptor()
        interceptor.intercept("tool_a", {})
        interceptor.intercept("tool_b", {})

        interceptor.clear_history()

        assert interceptor.history_count == 0
        assert interceptor.get_history() == []


class TestToolInterceptorSession:
    """Test session management."""

    def test_start_session(self):
        """Test starting a session."""
        interceptor = ToolInterceptor()

        session_id = interceptor.start_session()

        assert session_id is not None
        assert len(session_id) == 8  # UUID prefix

    def test_start_session_with_custom_id(self):
        """Test starting session with custom ID."""
        interceptor = ToolInterceptor()

        session_id = interceptor.start_session("my-session")

        assert session_id == "my-session"

    def test_get_current_session(self):
        """Test getting current session."""
        interceptor = ToolInterceptor()
        assert interceptor.get_current_session() is None

        session_id = interceptor.start_session()
        assert interceptor.get_current_session() == session_id

    def test_end_session(self):
        """Test ending a session."""
        interceptor = ToolInterceptor()
        interceptor.start_session()

        interceptor.end_session()

        assert interceptor.get_current_session() is None

    def test_get_session_calls(self):
        """Test getting calls for a session."""
        interceptor = ToolInterceptor()
        session_id = interceptor.start_session()

        interceptor.intercept("tool_a", {})
        interceptor.intercept("tool_b", {})

        calls = interceptor.get_session_calls(session_id)

        assert len(calls) == 2
        assert calls[0].tool_name == "tool_a"
        assert calls[1].tool_name == "tool_b"

    def test_get_session_calls_unknown_session(self):
        """Test getting calls for unknown session."""
        interceptor = ToolInterceptor()

        calls = interceptor.get_session_calls("unknown-session")

        assert calls == []

    def test_calls_grouped_by_session(self):
        """Test that calls are grouped by session."""
        interceptor = ToolInterceptor()

        session1 = interceptor.start_session("session-1")
        interceptor.intercept("tool_a", {})
        interceptor.end_session()

        session2 = interceptor.start_session("session-2")
        interceptor.intercept("tool_b", {})
        interceptor.intercept("tool_c", {})

        assert len(interceptor.get_session_calls(session1)) == 1
        assert len(interceptor.get_session_calls(session2)) == 2


class TestToolInterceptorQueries:
    """Test query functionality."""

    def test_get_last_call(self):
        """Test getting last call."""
        interceptor = ToolInterceptor()
        interceptor.intercept("tool_a", {})
        interceptor.intercept("tool_b", {})

        last = interceptor.get_last_call()

        assert last.tool_name == "tool_b"

    def test_get_last_call_empty(self):
        """Test getting last call when empty."""
        interceptor = ToolInterceptor()

        last = interceptor.get_last_call()

        assert last is None

    def test_get_calls_by_tool(self):
        """Test getting calls by tool name."""
        interceptor = ToolInterceptor()
        interceptor.intercept("mesh_extrude", {"depth": 1.0})
        interceptor.intercept("mesh_bevel", {"width": 0.5})
        interceptor.intercept("mesh_extrude", {"depth": 2.0})

        extrude_calls = interceptor.get_calls_by_tool("mesh_extrude")

        assert len(extrude_calls) == 2
        assert extrude_calls[0].params["depth"] == 2.0  # Newest first
        assert extrude_calls[1].params["depth"] == 1.0

    def test_get_calls_by_tool_with_limit(self):
        """Test getting calls by tool with limit."""
        interceptor = ToolInterceptor()
        for i in range(5):
            interceptor.intercept("mesh_extrude", {"depth": float(i)})

        calls = interceptor.get_calls_by_tool("mesh_extrude", limit=2)

        assert len(calls) == 2

    def test_get_calls_since(self):
        """Test getting calls since a time."""
        interceptor = ToolInterceptor()
        interceptor.intercept("old_call", {})

        cutoff = datetime.now()
        interceptor.intercept("new_call", {})

        calls = interceptor.get_calls_since(cutoff)

        assert len(calls) == 1
        assert calls[0].tool_name == "new_call"


class TestToolInterceptorProperties:
    """Test property accessors."""

    def test_history_count(self):
        """Test history_count property."""
        interceptor = ToolInterceptor()
        assert interceptor.history_count == 0

        interceptor.intercept("tool_a", {})
        assert interceptor.history_count == 1

        interceptor.intercept("tool_b", {})
        assert interceptor.history_count == 2

    def test_session_count(self):
        """Test session_count property."""
        interceptor = ToolInterceptor()
        assert interceptor.session_count == 0

        interceptor.start_session("session-1")
        interceptor.intercept("tool_a", {})
        assert interceptor.session_count == 1

        interceptor.start_session("session-2")
        interceptor.intercept("tool_b", {})
        assert interceptor.session_count == 2
