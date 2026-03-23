from __future__ import annotations

import asyncio

from server.adapters.mcp.areas.workflow_catalog import workflow_catalog


class DummyContext:
    def __init__(self) -> None:
        class SessionStub:
            def check_client_capability(self, capability):
                sampling = getattr(capability, "sampling", None)
                return sampling is not None

        self.session = SessionStub()
        self.fastmcp = type("ServerStub", (), {"sampling_handler_behavior": None, "sampling_handler": None})()
        self.request_id = "req_workflow"

    def get_state(self, key):
        return None

    def set_state(self, key, value, *, serializable=True):
        return None

    def info(self, message, logger_name=None, extra=None):
        return None

    async def sample(self, *args, **kwargs):
        return type(
            "SamplingResultStub",
            (),
            {
                "result": {
                    "summary": "Handle workflow issue",
                    "actions": [{"kind": "clarify", "reason": "Provide missing import information."}],
                    "requires_user_input": True,
                    "requires_inspection": False,
                    "safety_notes": [],
                    "truth_source": "router_diagnostics",
                },
                "text": None,
                "history": [],
            },
        )()


def test_workflow_catalog_parameter_validation_paths(monkeypatch):
    class Handler:
        def list_workflows(self, offset=0, limit=None):
            return {"count": 0, "workflows": []}

        def begin_import_session(self, **kwargs):
            return {"status": "ready", "session_id": "sess-1"}

        def abort_import_session(self, session_id):
            return {"status": "aborted", "session_id": session_id}

    monkeypatch.setattr("server.adapters.mcp.areas.workflow_catalog.get_workflow_catalog_handler", lambda: Handler())

    assert asyncio.run(workflow_catalog(DummyContext(), action="get")).error == "workflow_name required for get action"
    assert asyncio.run(workflow_catalog(DummyContext(), action="search")).error == "query required for search action"
    assert (
        asyncio.run(workflow_catalog(DummyContext(), action="import")).error
        == "filepath or content required for import action"
    )
    assert (
        asyncio.run(workflow_catalog(DummyContext(), action="import_append")).error
        == "session_id required for import_append"
    )
    assert (
        asyncio.run(workflow_catalog(DummyContext(), action="import_append", session_id="sess-1")).error
        == "chunk_data required for import_append"
    )
    assert (
        asyncio.run(workflow_catalog(DummyContext(), action="import_abort")).error
        == "session_id required for import_abort"
    )

    init_result = asyncio.run(workflow_catalog(DummyContext(), action="import_init", content_type="yaml"))
    abort_result = asyncio.run(workflow_catalog(DummyContext(), action="import_abort", session_id="sess-1"))

    assert init_result.session_id == "sess-1"
    assert abort_result.session_id == "sess-1"


def test_workflow_catalog_get_returns_steps_count(monkeypatch):
    class Handler:
        def get_workflow(self, workflow_name):
            return {
                "workflow_name": workflow_name,
                "steps_count": 15,
                "workflow": {"name": workflow_name, "steps": []},
            }

    monkeypatch.setattr("server.adapters.mcp.areas.workflow_catalog.get_workflow_catalog_handler", lambda: Handler())

    result = asyncio.run(
        workflow_catalog(
            DummyContext(),
            action="get",
            workflow_name="simple_house_workflow",
        )
    )

    assert result.workflow_name == "simple_house_workflow"
    assert result.steps_count == 15


def test_workflow_catalog_background_finalize_uses_local_background_operation(monkeypatch):
    class Handler:
        def finalize_import_session(self, **kwargs):
            return {
                "status": "needs_input",
                "workflow_name": "chair",
                "message": "confirm overwrite",
            }

    async def fake_run_local_background_operation(ctx, **kwargs):
        payload = kwargs["background_executor"](lambda *a, **k: None, lambda: False)
        return kwargs["result_formatter"](payload)

    monkeypatch.setattr("server.adapters.mcp.areas.workflow_catalog.get_workflow_catalog_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.workflow_catalog.is_background_task_context", lambda ctx: True)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.workflow_catalog.run_local_background_operation", fake_run_local_background_operation
    )

    result = asyncio.run(
        workflow_catalog(
            DummyContext(),
            action="import_finalize",
            session_id="sess-1",
            overwrite=False,
        )
    )

    assert result.status == "needs_input"
    assert result.clarification is not None
    assert result.repair_suggestion is not None


def test_workflow_catalog_finalize_imported_preserves_chunk_metadata(monkeypatch):
    class Handler:
        def finalize_import_session(self, **kwargs):
            return {
                "status": "imported",
                "workflow_name": "simple_house_workflow",
                "message": "ok",
                "saved_path": "/tmp/simple_house_workflow.yaml",
                "source_path": "simple_house.yaml",
                "overwritten": False,
                "removed_files": [],
                "removed_embeddings": 0,
                "workflows_dir": "/tmp",
                "embeddings_reloaded": True,
            }

    monkeypatch.setattr("server.adapters.mcp.areas.workflow_catalog.get_workflow_catalog_handler", lambda: Handler())

    result = asyncio.run(
        workflow_catalog(
            DummyContext(),
            action="import_finalize",
            session_id="sess-1",
        )
    )

    assert result.status == "imported"
    assert result.saved_path == "/tmp/simple_house_workflow.yaml"
