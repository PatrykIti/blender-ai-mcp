"""Tests for structured router and workflow catalog contracts."""

from __future__ import annotations

import asyncio

import server.adapters.mcp.areas.router as router_area
from server.adapters.mcp.areas.router import router_get_status, router_set_goal
from server.adapters.mcp.areas.workflow_catalog import workflow_catalog
from server.adapters.mcp.contracts.router import (
    RouterGoalResponseContract,
    RouterPolicyContextContract,
    RouterStatusContract,
)
from server.adapters.mcp.contracts.workflow_catalog import WorkflowCatalogResponseContract
from server.adapters.mcp.elicitation_contracts import ClarificationFallbackPayload
from server.adapters.mcp.tasks.job_registry import reset_background_job_registry_for_tests
from server.adapters.mcp.tasks.runtime_policy import TaskRuntimeReport


class DummyContext:
    def __init__(self) -> None:
        class SessionStub:
            def check_client_capability(self, capability):
                sampling = getattr(capability, "sampling", None)
                return sampling is not None

        self.fastmcp = type(
            "ServerStub",
            (),
            {
                "list_page_size": 50,
                "sampling_handler_behavior": None,
                "sampling_handler": None,
                "_bam_timeout_policy": type(
                    "TimeoutPolicyStub",
                    (),
                    {
                        "to_dict": lambda self: {
                            "tool_timeout_seconds": 30.0,
                            "task_timeout_seconds": 300.0,
                            "rpc_timeout_seconds": 30.0,
                            "addon_execution_timeout_seconds": 30.0,
                            "boundary_names": (
                                "mcp_tool",
                                "mcp_task",
                                "rpc_client",
                                "addon_execution",
                            ),
                        }
                    },
                )(),
                "_bam_task_runtime_report": TaskRuntimeReport(
                    fastmcp_version="3.1.1",
                    pydocket_version="0.18.2",
                    tasks_required=True,
                    supported=True,
                ),
            },
        )()
        self.session = SessionStub()
        self.request_id = "req_router"
        self.sample_result = None
        self.state: dict[str, object] = {}

    async def elicit(self, *args, **kwargs):
        raise RuntimeError("not used")

    async def sample(self, *args, **kwargs):
        result = self.sample_result
        if result is None:
            raise RuntimeError("sample_result not configured")

        return type("SamplingResultStub", (), {"result": result, "text": None, "history": []})()

    def get_state(self, key):
        return self.state.get(key)

    def set_state(self, key, value, *, serializable=True):
        self.state[key] = value
        return None

    def info(self, message, logger_name=None, extra=None):
        return None

    async def reset_visibility(self):
        return None

    async def enable_components(self, **kwargs):
        return None

    async def disable_components(self, **kwargs):
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


def test_guided_scene_meaningful_objects_ignores_stock_startup_scene(monkeypatch):
    """The default Cube/Camera/Light scene should still enter guided bootstrap."""

    class SceneHandler:
        def list_objects(self):
            return [
                {"name": "Cube", "type": "MESH", "location": [0.0, 0.0, 0.0]},
                {"name": "Camera", "type": "CAMERA", "location": [0.0, -3.0, 3.0]},
                {"name": "Light", "type": "LIGHT", "location": [4.0, 1.0, 6.0]},
            ]

    monkeypatch.setattr(router_area, "get_scene_handler", lambda: SceneHandler())

    assert router_area._scene_has_meaningful_guided_objects() is False


def test_guided_scene_meaningful_objects_keeps_real_placeholder_blockout(monkeypatch):
    """A multi-object rough blockout should not be mistaken for the stock startup scene."""

    class SceneHandler:
        def list_objects(self):
            return [
                {"name": "Cube", "type": "MESH", "location": [0.0, 0.0, 0.0]},
                {"name": "Sphere", "type": "MESH", "location": [1.0, 0.0, 0.0]},
                {"name": "Camera", "type": "CAMERA", "location": [0.0, -3.0, 3.0]},
            ]

    monkeypatch.setattr(router_area, "get_scene_handler", lambda: SceneHandler())

    assert router_area._scene_has_meaningful_guided_objects() is True


def test_router_set_goal_contract_accepts_guided_manual_build_no_match(monkeypatch):
    """router_set_goal should expose continuation_mode for guided manual handoff."""

    monkeypatch.setattr(
        "server.adapters.mcp.areas.router.get_config",
        lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})(),
    )

    class Handler:
        def set_goal(self, goal, resolved_params=None):
            return {
                "status": "no_match",
                "continuation_mode": "guided_manual_build",
                "workflow": None,
                "resolved": {},
                "unresolved": [],
                "resolution_sources": {},
                "message": "Continue on the guided build surface.",
                "phase_hint": "build",
            }

    monkeypatch.setattr("server.adapters.mcp.areas.router.get_router_handler", lambda: Handler())

    callable_router_set_goal = getattr(router_set_goal, "fn", router_set_goal)
    result = asyncio.run(
        callable_router_set_goal(
            DummyContext(),
            goal="create a low-poly squirrel matching front and side reference images",
        )
    )

    assert isinstance(result, RouterGoalResponseContract)
    assert result.status == "no_match"
    assert result.continuation_mode == "guided_manual_build"
    assert result.guided_handoff is not None
    assert result.guided_handoff.kind == "guided_manual_build"
    assert result.guided_handoff.recipe_id == "low_poly_creature_blockout"
    assert result.guided_handoff.target_phase == "build"
    assert result.guided_handoff.workflow_import_recommended is False


def test_workflow_catalog_returns_structured_contract(monkeypatch):
    """workflow_catalog should return a typed contract instead of JSON text."""

    class Handler:
        def list_workflows(self, offset=0, limit=None):
            return {
                "workflows_dir": "/tmp",
                "count": 1,
                "total": 3,
                "returned": 1,
                "offset": 1,
                "limit": 1,
                "has_more": True,
                "workflows": [{"name": "chair"}],
            }

    monkeypatch.setattr("server.adapters.mcp.areas.workflow_catalog.get_workflow_catalog_handler", lambda: Handler())

    callable_workflow_catalog = getattr(workflow_catalog, "fn", workflow_catalog)
    result = asyncio.run(callable_workflow_catalog(DummyContext(), action="list"))

    assert isinstance(result, WorkflowCatalogResponseContract)
    assert result.action == "list"
    assert result.count == 1
    assert result.total == 3
    assert result.returned == 1
    assert result.has_more is True


def test_router_get_status_exposes_reference_image_diagnostics(monkeypatch):
    class Handler:
        def set_goal(self, goal, resolved_params=None):
            return {
                "status": "ready",
                "workflow": "chair_workflow",
                "resolved": {},
                "unresolved": [],
                "resolution_sources": {},
                "message": "ok",
            }

    monkeypatch.setattr("server.adapters.mcp.areas.router.get_router_handler", lambda: Handler())

    ctx = DummyContext()
    ctx.state["reference_images"] = [
        {
            "reference_id": "ref_1",
            "goal": "chair",
            "media_type": "image/png",
            "source_kind": "local_path",
            "original_path": "/tmp/ref.png",
            "stored_path": "/tmp/stored.png",
            "added_at": "2026-03-26T00:00:00Z",
        }
    ]

    result = asyncio.run(router_get_status(ctx))

    assert isinstance(result, RouterStatusContract)
    assert result.reference_image_count == 1
    assert result.reference_images is not None
    assert result.reference_images[0].reference_id == "ref_1"


def test_router_get_status_exposes_guided_handoff_from_session(monkeypatch):
    """router_get_status should surface the active guided handoff contract from session state."""

    class Handler:
        def set_goal(self, goal, resolved_params=None):
            return {
                "status": "ready",
                "workflow": "chair_workflow",
                "resolved": {},
                "unresolved": [],
                "resolution_sources": {},
                "message": "ok",
            }

    monkeypatch.setattr("server.adapters.mcp.areas.router.get_router_handler", lambda: Handler())

    ctx = DummyContext()
    ctx.state["guided_handoff"] = {
        "kind": "guided_manual_build",
        "target_phase": "build",
        "surface_profile": "llm-guided",
        "direct_tools": ["scene_create", "macro_finish_form"],
        "supporting_tools": ["reference_images", "router_get_status"],
        "discovery_tools": ["search_tools", "call_tool"],
        "workflow_import_recommended": False,
        "message": "Continue on the guided build surface.",
    }

    result = asyncio.run(router_get_status(ctx))

    assert isinstance(result, RouterStatusContract)
    assert result.guided_handoff is not None
    assert result.guided_handoff.kind == "guided_manual_build"
    assert result.guided_handoff.direct_tools == ["scene_create", "macro_finish_form"]


def test_workflow_catalog_get_accepts_steps_count_metadata(monkeypatch):
    """workflow_catalog get should accept the top-level steps_count field."""

    class Handler:
        def get_workflow(self, workflow_name):
            return {
                "workflow_name": workflow_name,
                "steps_count": 15,
                "workflow": {"name": workflow_name, "steps": []},
            }

    monkeypatch.setattr("server.adapters.mcp.areas.workflow_catalog.get_workflow_catalog_handler", lambda: Handler())

    callable_workflow_catalog = getattr(workflow_catalog, "fn", workflow_catalog)
    result = asyncio.run(callable_workflow_catalog(DummyContext(), action="get", workflow_name="simple_house_workflow"))

    assert isinstance(result, WorkflowCatalogResponseContract)
    assert result.workflow_name == "simple_house_workflow"
    assert result.steps_count == 15


def test_workflow_catalog_import_needs_input_can_carry_typed_clarification(monkeypatch):
    """workflow_catalog should accept typed clarification payloads for tool-only fallback flows."""

    class Handler:
        def import_workflow_content(self, **kwargs):
            return {
                "status": "needs_input",
                "workflow_name": "chair",
                "message": "confirm overwrite",
                "clarification": ClarificationFallbackPayload(
                    request_id="req_1",
                    question_set_id="qs_1",
                    goal="workflow_import",
                    workflow_name="chair",
                    fields=[],
                ).model_dump(),
            }

    monkeypatch.setattr("server.adapters.mcp.areas.workflow_catalog.get_workflow_catalog_handler", lambda: Handler())

    ctx = DummyContext()
    ctx.sample_result = {
        "summary": "Confirm the overwrite choice before retrying the import.",
        "actions": [
            {"kind": "clarify", "reason": "Choose whether to overwrite the existing workflow."},
            {"kind": "retry", "reason": "Retry after confirming overwrite behavior."},
        ],
        "requires_user_input": True,
        "requires_inspection": False,
        "safety_notes": ["Do not overwrite existing workflows unintentionally."],
        "truth_source": "router_diagnostics",
    }

    callable_workflow_catalog = getattr(workflow_catalog, "fn", workflow_catalog)
    result = asyncio.run(callable_workflow_catalog(ctx, action="import", content="{}", content_type="json"))

    assert isinstance(result, WorkflowCatalogResponseContract)
    assert result.status == "needs_input"
    assert result.clarification.question_set_id == "qs_1"
    assert result.repair_suggestion is not None
    assert result.repair_suggestion.status == "success"


def test_workflow_catalog_imported_response_accepts_import_metadata(monkeypatch):
    """workflow_catalog import should accept the richer imported payload metadata."""

    class Handler:
        def import_workflow_content(self, **kwargs):
            return {
                "status": "imported",
                "workflow_name": "simple_house_workflow",
                "message": "ok",
                "source_type": "inline",
                "content_type": "yaml",
                "saved_path": "/tmp/simple_house_workflow.yaml",
                "source_path": "simple_house.yaml",
                "overwritten": False,
                "removed_files": [],
                "removed_embeddings": 0,
                "workflows_dir": "/tmp",
                "embeddings_reloaded": True,
            }

    monkeypatch.setattr("server.adapters.mcp.areas.workflow_catalog.get_workflow_catalog_handler", lambda: Handler())

    callable_workflow_catalog = getattr(workflow_catalog, "fn", workflow_catalog)
    result = asyncio.run(callable_workflow_catalog(DummyContext(), action="import", content="{}", content_type="yaml"))

    assert isinstance(result, WorkflowCatalogResponseContract)
    assert result.status == "imported"
    assert result.saved_path == "/tmp/simple_house_workflow.yaml"
    assert result.overwritten is False
    assert result.embeddings_reloaded is True


def test_router_get_status_returns_structured_contract(monkeypatch):
    """router_get_status should return a typed status contract instead of prose text."""

    reset_background_job_registry_for_tests()

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
    result = asyncio.run(callable_router_get_status(DummyContext()))

    assert isinstance(result, RouterStatusContract)
    assert result.enabled is True
    assert result.stats["total_calls"] == 3
    assert result.surface_profile == "legacy-flat"
    assert "router" in result.visible_capabilities
    assert result.hidden_capability_count == 0
    assert result.pending_question_set_id is None
    assert result.partial_answers is None
    assert result.router_failure_policy == "fail_open"
    assert result.timeout_policy["task_timeout_seconds"] == 300.0
    assert result.task_runtime["pydocket_version"] == "0.18.2"
    assert result.telemetry["enabled"] is False
    assert result.list_page_size == 50
    assert result.background_job_count == 0


def test_router_goal_contract_accepts_policy_context():
    """router_set_goal contract should carry structured policy transparency when present."""

    contract = RouterGoalResponseContract(
        status="needs_input",
        workflow="chair_workflow",
        resolved={},
        unresolved=[],
        resolution_sources={},
        message="confirm",
        policy_context=RouterPolicyContextContract(
            decision="ask",
            reason="medium confidence",
            source="workflow_match",
            score=0.7,
            band="medium",
            risk="high",
        ),
    )

    assert contract.policy_context.decision == "ask"


def test_router_set_goal_error_can_attach_bounded_repair_suggestion(monkeypatch):
    """router_set_goal should attach typed repair guidance on bounded error paths."""

    class Handler:
        def set_goal(self, goal, resolved_params=None):
            return {
                "status": "error",
                "workflow": None,
                "resolved": {},
                "unresolved": [],
                "resolution_sources": {},
                "message": "router failed",
                "error": {
                    "type": "RuntimeError",
                    "details": "boom",
                    "stage": "workflow_match",
                },
            }

    monkeypatch.setattr("server.adapters.mcp.areas.router.get_router_handler", lambda: Handler())

    ctx = DummyContext()
    ctx.sample_result = {
        "summary": "Inspect the workflow match failure before retrying.",
        "actions": [
            {"kind": "inspect", "reason": "Check router diagnostics and workflow inputs."},
            {"kind": "clarify", "reason": "Refine the goal if the intent was ambiguous."},
        ],
        "requires_user_input": True,
        "requires_inspection": False,
        "safety_notes": ["Do not assume Blender state from router errors alone."],
        "truth_source": "router_diagnostics",
    }

    callable_router_set_goal = getattr(router_set_goal, "fn", router_set_goal)
    result = asyncio.run(callable_router_set_goal(ctx, goal="chair"))

    assert result.status == "error"
    assert result.repair_suggestion is not None
    assert result.repair_suggestion.status == "success"
    assert result.repair_suggestion.result.actions[0].kind == "inspect"


def test_router_get_status_can_attach_bounded_repair_suggestion(monkeypatch):
    """router_get_status should expose repair guidance for recent router failures."""

    reset_background_job_registry_for_tests()

    monkeypatch.setattr(
        "server.adapters.mcp.areas.router.get_router_status",
        lambda: {
            "enabled": True,
            "initialized": True,
            "ready": True,
            "component_status": {"classifier": True},
            "stats": {"total_calls": 3},
            "config": "RouterConfig(...)",
            "assistant_diagnostics": {"last_match": {"match_type": "error"}},
        },
    )

    ctx = DummyContext()
    ctx.set_state("last_router_error", "Router processing failed for mesh_extrude_region: boom")
    ctx.sample_result = {
        "summary": "Inspect the last router failure before retrying.",
        "actions": [
            {"kind": "inspect", "reason": "Review last_router_error and correction audit context."},
            {"kind": "retry", "reason": "Retry only after confirming the failing preconditions."},
        ],
        "requires_user_input": False,
        "requires_inspection": True,
        "safety_notes": ["Use inspection tools to verify scene truth before retrying."],
        "truth_source": "inspection_required",
    }

    callable_router_get_status = getattr(router_get_status, "fn", router_get_status)
    result = asyncio.run(callable_router_get_status(ctx))

    assert result.repair_suggestion is not None
    assert result.repair_suggestion.status == "success"
    assert result.repair_suggestion.result.requires_inspection is True
