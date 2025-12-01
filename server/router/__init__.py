"""
Router Supervisor Module.

Intelligent router that intercepts, corrects, expands, and overrides
LLM tool calls before execution.
"""

from server.router.infrastructure.config import RouterConfig

__all__ = ["RouterConfig"]
