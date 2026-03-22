# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Legacy MCP decorator shim.

The FastMCP runtime source of truth moved to `server.adapters.mcp.factory`
during TASK-083. This module remains only as a no-op compatibility seam for
older out-of-tree imports that still expect `mcp.tool(...)` to exist.

TODO(post-TASK-083 cleanup): remove this shim once external compatibility with
legacy decorator imports is no longer needed.
"""

from __future__ import annotations

from typing import Any, Callable


class LegacyMCPDecoratorShim:
    """Minimal compatibility shim for legacy `@mcp.tool()` imports."""

    def tool(self, name_or_fn: Any = None, **_: Any) -> Callable[..., Any]:
        """Return the wrapped function unchanged.

        The real registration path is provider-based (`register_*_tools(...)`).
        """

        def register(fn: Callable[..., Any]) -> Callable[..., Any]:
            return fn

        if callable(name_or_fn):
            return register(name_or_fn)

        return register


mcp = LegacyMCPDecoratorShim()

__all__ = ["LegacyMCPDecoratorShim", "mcp"]
