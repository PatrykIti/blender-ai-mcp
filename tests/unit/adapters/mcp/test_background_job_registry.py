"""Tests for MCP background job bookkeeping primitives."""

from server.adapters.mcp.tasks.job_registry import (
    get_background_job_registry,
    reset_background_job_registry_for_tests,
)
from server.adapters.mcp.tasks.result_store import (
    get_background_result_store,
    reset_background_result_store_for_tests,
)
from server.adapters.mcp.tasks.runtime_policy import get_task_runtime_report


def setup_function():
    reset_background_job_registry_for_tests()
    reset_background_result_store_for_tests()


def test_background_job_registry_tracks_identity_progress_and_completion():
    """Registry should keep FastMCP task identity, backend identity, and final result refs."""

    registry = get_background_job_registry()
    store = get_background_result_store()

    registry.register(task_id="task-1", tool_name="scene_get_viewport", backend_kind="addon_job")
    registry.bind_backend_job("task-1", "job-1")
    registry.update_progress("task-1", current=1, total=3, message="rendering", status="running")

    stored = store.put(task_id="task-1", tool_name="scene_get_viewport", payload={"ok": True})
    registry.mark_completed("task-1", result_ref=stored.result_ref)

    record = registry.get("task-1")
    assert record is not None
    assert record.backend_job_id == "job-1"
    assert record.status == "completed"
    assert record.progress.current == 1
    assert record.progress.total == 3
    assert record.result_ref == "task-result:task-1"

    stored_again = store.get("task-result:task-1")
    assert stored_again is not None
    assert stored_again.payload == {"ok": True}

def test_task_runtime_report_matches_current_supported_pair():
    """Current environment should resolve to the supported FastMCP+Docket task pair."""

    report = get_task_runtime_report(tasks_required=True)

    assert report.supported is True
    assert report.fastmcp_version == "3.1.1"
    assert report.pydocket_version == "0.18.2"
