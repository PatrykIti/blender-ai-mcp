"""Tests for structured router and workflow catalog contracts."""

from __future__ import annotations

import asyncio

from server.adapters.mcp.areas.router import router_get_status, router_set_goal
from server.adapters.mcp.areas.workflow_catalog import workflow_catalog
from server.adapters.mcp.contracts.router import RouterGoalResponseContract, RouterStatusContract
from server.adapters.mcp.contracts.workflow_catalog import WorkflowCatalogResponseContract


class DummyContext:
    async def elicit(self, *args, **kwargs):
        raise RuntimeError("not used")

    def get_state(self, key):
        return None

    def set_state(self, key, value, *, serializable=True):
        return None

    def info(self, message, logger_name=None, extra=None):
        return None


def test_router_set_goal_returns_structured_contract(monkeypatch):
    """router_set_goal should return a typed contract instead of JSON text."""

    class Handler:
        def set_goal(self, goal, resolved_params=None):
            return {
                "status": "ready",
                "workflow": "chair_workflow",
                "resolved": {"height": 1.0},
                "unresolved": [],
                "resolution_sources": {"height": "default"},
                "message": "ok",
                "phase_hint": "build",
                "executed": 0,
            }

    monkeypatch.setattr("server.adapters.mcp.areas.router.get_router_handler", lambda: Handler())

    callable_router_set_goal = getattr(router_set_goal, "fn", router_set_goal)
    result = asyncio.run(callable_router_set_goal(DummyContext(), goal="chair"))

    assert isinstance(result, RouterGoalResponseContract)
    assert result.status == "ready"


def test_workflow_catalog_returns_structured_contract(monkeypatch):
    """workflow_catalog should return a typed contract instead of JSON text."""

    class Handler:
        def list_workflows(self):
            return {"workflows_dir": "/tmp", "count": 1, "workflows": [{"name": "chair"}]}

    monkeypatch.setattr("server.adapters.mcp.areas.workflow_catalog.get_workflow_catalog_handler", lambda: Handler())

    callable_workflow_catalog = getattr(workflow_catalog, "fn", workflow_catalog)
    result = callable_workflow_catalog(DummyContext(), action="list")

    assert isinstance(result, WorkflowCatalogResponseContract)
    assert result.action == "list"
    assert result.count == 1


def test_router_get_status_returns_structured_contract(monkeypatch):
    """router_get_status should return a typed status contract instead of prose text."""

    monkeypatch.setattr(
        "server.adapters.mcp.areas.router.get_router_status",
        lambda: {
            "enabled": True,
            "initialized": True,
            "ready": True,
            "component_status": {"classifier": True},
            "stats": {"total_calls": 3},
            "config": "RouterConfig(...)",
        },
    )

    callable_router_get_status = getattr(router_get_status, "fn", router_get_status)
    result = callable_router_get_status(DummyContext())

    assert isinstance(result, RouterStatusContract)
    assert result.enabled is True
    assert result.stats["total_calls"] == 3
