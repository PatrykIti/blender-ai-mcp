"""
E2E-style router tests for guided manual-build handoff after no-match.
"""

from __future__ import annotations

from server.application.tool_handlers.router_handler import RouterToolHandler


def test_router_set_goal_meta_capture_build_request_returns_guided_manual_no_match(router, clean_scene):
    """Meta capture/build goals should hand off into guided manual build instead of irrelevant workflow routing."""

    handler = RouterToolHandler(router=router, enabled=True)

    result = handler.set_goal(
        "squirrel vision test - 3 progressive screenshots: head blockout, face features, full body - low poly squirrel with consistent camera"
    )

    assert result["status"] == "no_match"
    assert result["continuation_mode"] == "guided_manual_build"
    assert result["workflow"] is None
    assert result["phase_hint"] == "build"
    assert "guided build surface" in result["message"]
    assert router.get_pending_workflow() is None
