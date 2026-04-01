"""Tests for workflow_catalog bounded repair suggestions."""

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
        self.fastmcp = type(
            "ServerStub",
            (),
            {"sampling_handler_behavior": None, "sampling_handler": None},
        )()
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
                    "summary": "Review the workflow import conflict before retrying.",
                    "actions": [
                        {
                            "kind": "clarify",
                            "reason": "Confirm whether the workflow should overwrite the existing definition.",
                        },
                        {"kind": "retry", "reason": "Retry the import after choosing overwrite behavior."},
                    ],
                    "requires_user_input": True,
                    "requires_inspection": False,
                    "safety_notes": ["Do not overwrite an existing workflow unintentionally."],
                    "truth_source": "router_diagnostics",
                },
                "text": None,
                "history": [],
            },
        )()


def test_workflow_catalog_import_needs_input_attaches_repair_suggestion(monkeypatch):
    """Import conflicts should attach bounded repair guidance."""

    class Handler:
        def import_workflow_content(self, **kwargs):
            return {
                "status": "needs_input",
                "workflow_name": "chair",
                "message": "confirm overwrite",
            }

    monkeypatch.setattr("server.adapters.mcp.areas.workflow_catalog.get_workflow_catalog_handler", lambda: Handler())

    result = asyncio.run(
        workflow_catalog(
            DummyContext(),
            action="import",
            content="{}",
            content_type="json",
        )
    )

    assert result.repair_suggestion is not None
    assert result.repair_suggestion.status == "success"
    assert result.repair_suggestion.result.requires_user_input is True


def test_workflow_catalog_import_finalize_error_attaches_repair_suggestion(monkeypatch):
    """Missing import-finalize session ids should surface bounded repair guidance."""

    class Handler:
        pass

    monkeypatch.setattr("server.adapters.mcp.areas.workflow_catalog.get_workflow_catalog_handler", lambda: Handler())

    result = asyncio.run(
        workflow_catalog(
            DummyContext(),
            action="import_finalize",
        )
    )

    assert result.error == "session_id required for import_finalize"
    assert result.repair_suggestion is not None
    assert result.repair_suggestion.result.actions[0].kind == "clarify"
