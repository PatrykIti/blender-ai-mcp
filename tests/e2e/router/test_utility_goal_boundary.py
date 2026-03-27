"""
E2E-style router tests for utility/capture goal boundaries.

These use the real router stack and real workflow catalog, but the assertions
focus on goal routing behavior rather than Blender geometry changes.
"""

from __future__ import annotations

import pytest

from server.application.tool_handlers.router_handler import RouterToolHandler


def test_router_set_goal_treats_viewport_screenshot_request_as_utility(router, clean_scene):
    """Utility capture goals should not resolve into unrelated modeling workflows."""

    handler = RouterToolHandler(router=router, enabled=True)

    result = handler.set_goal("capture viewport screenshot save to file")

    assert result["status"] == "no_match"
    assert result["workflow"] is None
    assert "utility/capture request" in result["message"]
    assert router.get_pending_workflow() is None
