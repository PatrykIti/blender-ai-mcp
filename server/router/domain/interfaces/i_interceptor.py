"""
Tool Interceptor Interface.

Abstract interface for capturing LLM tool calls.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from server.router.domain.entities.tool_call import InterceptedToolCall


class IToolInterceptor(ABC):
    """Abstract interface for tool interception.

    Captures all incoming tool calls from the LLM before execution.
    """

    @abstractmethod
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
        pass

    @abstractmethod
    def get_history(self, limit: int = 10) -> List[InterceptedToolCall]:
        """Get recent call history.

        Args:
            limit: Maximum number of calls to return.

        Returns:
            List of recent intercepted calls, newest first.
        """
        pass

    @abstractmethod
    def clear_history(self) -> None:
        """Clear call history."""
        pass

    @abstractmethod
    def get_session_calls(self, session_id: str) -> List[InterceptedToolCall]:
        """Get all calls for a specific session.

        Args:
            session_id: Session identifier.

        Returns:
            List of calls for the session.
        """
        pass
