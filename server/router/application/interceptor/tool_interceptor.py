"""
Tool Interceptor Implementation.

Captures and records LLM tool calls for router processing.
"""

from collections import deque
from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid

from server.router.domain.interfaces.i_interceptor import IToolInterceptor
from server.router.domain.entities.tool_call import InterceptedToolCall


class ToolInterceptor(IToolInterceptor):
    """Implementation of tool interception.

    Captures all incoming tool calls from the LLM before execution,
    maintaining a history for analysis and debugging.

    Attributes:
        max_history: Maximum number of calls to keep in history.
        history: Deque of intercepted calls (newest first).
        session_calls: Dict mapping session_id to list of calls.
    """

    def __init__(self, max_history: int = 100):
        """Initialize interceptor.

        Args:
            max_history: Maximum number of calls to keep in history.
        """
        self.max_history = max_history
        self._history: deque[InterceptedToolCall] = deque(maxlen=max_history)
        self._session_calls: Dict[str, List[InterceptedToolCall]] = {}
        self._current_session: Optional[str] = None

    def intercept(
        self,
        tool_name: str,
        params: Dict[str, Any],
        prompt: Optional[str] = None,
    ) -> InterceptedToolCall:
        """Intercept and record a tool call.

        Args:
            tool_name: Name of the tool being called.
            params: Parameters passed to the tool.
            prompt: Original user prompt (if available).

        Returns:
            InterceptedToolCall containing the captured information.
        """
        session_id = self._current_session or self._generate_session_id()

        call = InterceptedToolCall(
            tool_name=tool_name,
            params=params.copy() if params else {},
            timestamp=datetime.now(),
            source="llm",
            original_prompt=prompt,
            session_id=session_id,
        )

        # Add to history (newest first)
        self._history.appendleft(call)

        # Add to session tracking
        if session_id not in self._session_calls:
            self._session_calls[session_id] = []
        self._session_calls[session_id].append(call)

        return call

    def get_history(self, limit: int = 10) -> List[InterceptedToolCall]:
        """Get recent call history.

        Args:
            limit: Maximum number of calls to return.

        Returns:
            List of recent intercepted calls, newest first.
        """
        return list(self._history)[:limit]

    def clear_history(self) -> None:
        """Clear call history."""
        self._history.clear()
        self._session_calls.clear()

    def get_session_calls(self, session_id: str) -> List[InterceptedToolCall]:
        """Get all calls for a specific session.

        Args:
            session_id: Session identifier.

        Returns:
            List of calls for the session.
        """
        return self._session_calls.get(session_id, [])

    def start_session(self, session_id: Optional[str] = None) -> str:
        """Start a new session.

        Args:
            session_id: Optional session ID (generated if not provided).

        Returns:
            The session ID.
        """
        self._current_session = session_id or self._generate_session_id()
        return self._current_session

    def end_session(self) -> None:
        """End the current session."""
        self._current_session = None

    def get_current_session(self) -> Optional[str]:
        """Get current session ID."""
        return self._current_session

    def get_last_call(self) -> Optional[InterceptedToolCall]:
        """Get the most recent call.

        Returns:
            Most recent InterceptedToolCall or None if history is empty.
        """
        if self._history:
            return self._history[0]
        return None

    def get_calls_by_tool(self, tool_name: str, limit: int = 10) -> List[InterceptedToolCall]:
        """Get recent calls for a specific tool.

        Args:
            tool_name: Name of the tool to filter by.
            limit: Maximum number of calls to return.

        Returns:
            List of calls for the specified tool.
        """
        calls = [c for c in self._history if c.tool_name == tool_name]
        return calls[:limit]

    def get_calls_since(self, since: datetime) -> List[InterceptedToolCall]:
        """Get calls since a specific time.

        Args:
            since: Datetime to filter from.

        Returns:
            List of calls since the specified time.
        """
        return [c for c in self._history if c.timestamp >= since]

    @property
    def history_count(self) -> int:
        """Get total number of calls in history."""
        return len(self._history)

    @property
    def session_count(self) -> int:
        """Get number of tracked sessions."""
        return len(self._session_calls)

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return str(uuid.uuid4())[:8]
