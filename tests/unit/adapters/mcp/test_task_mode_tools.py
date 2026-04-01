"""Tests for adopted TASK-088 MCP tool entrypoints."""

from __future__ import annotations

import asyncio
from threading import Event
from typing import cast

import pytest
from fastmcp import Context
from server.adapters.mcp.areas.extraction import extraction_render_angles
from server.adapters.mcp.areas.scene import scene_get_viewport
from server.adapters.mcp.areas.system import export_obj, import_glb, import_image_as_plane
from server.adapters.mcp.areas.workflow_catalog import workflow_catalog
from server.adapters.mcp.tasks.job_registry import (
    get_background_job_registry,
    reset_background_job_registry_for_tests,
)
from server.adapters.mcp.tasks.result_store import (
    get_background_result_store,
    reset_background_result_store_for_tests,
)
from server.adapters.mcp.tasks.task_bridge import run_local_background_operation
from server.adapters.mcp.timeout_policy import build_timeout_policy
from server.domain.models.rpc import RpcResponse


class BackgroundContext:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.is_background_task = True
        self.progress_events: list[tuple[float, float | None, str | None]] = []
        self.info_messages: list[str] = []

    async def report_progress(self, progress: float, total: float | None = None, message: str | None = None) -> None:
        self.progress_events.append((progress, total, message))

    def info(self, message: str, logger_name=None, extra=None) -> None:
        self.info_messages.append(message)


def setup_function():
    reset_background_job_registry_for_tests()
    reset_background_result_store_for_tests()


def test_scene_get_viewport_background_path_tracks_registry_and_returns_formatted_payload(monkeypatch):
    """scene_get_viewport should use the addon job bridge when running in task mode."""

    class FakeRpcClient:
        def __init__(self) -> None:
            self.poll_count = 0

        def launch_background_job(self, cmd, args, *, timeout_seconds=None):
            assert cmd == "scene.get_viewport"
            return RpcResponse(request_id="req-1", status="ok", result={"job_id": "job-1"})

        def get_background_job_status(self, job_id):
            self.poll_count += 1
            if self.poll_count == 1:
                return RpcResponse(
                    request_id="req-2",
                    status="ok",
                    result={
                        "job_id": job_id,
                        "status": "running",
                        "progress_current": 0,
                        "progress_total": 1,
                        "status_message": "Rendering viewport",
                    },
                )
            return RpcResponse(
                request_id="req-3",
                status="ok",
                result={
                    "job_id": job_id,
                    "status": "completed",
                    "progress_current": 1,
                    "progress_total": 1,
                    "status_message": "Completed",
                },
            )

        def collect_background_job_result(self, job_id):
            return RpcResponse(
                request_id="req-4",
                status="ok",
                result={"job_id": job_id, "result": "aGVsbG8="},
            )

        def cancel_background_job(self, job_id):
            return RpcResponse(request_id="req-5", status="ok", result={"job_id": job_id})

    monkeypatch.setattr("server.adapters.mcp.tasks.task_bridge.get_rpc_client", lambda: FakeRpcClient())

    ctx = BackgroundContext("task-viewport")
    result = asyncio.run(scene_get_viewport(ctx, output_mode="BASE64"))

    assert result == "aGVsbG8="
    assert ctx.progress_events[-1] == (1, 1, "Viewport capture completed")
    registry_record = get_background_job_registry().get("task-viewport")
    assert registry_record is not None
    assert registry_record.backend_job_id == "job-1"
    assert registry_record.status == "completed"
    assert get_background_result_store().get("task-result:task-viewport") is not None


def test_extraction_render_angles_background_path_formats_json_result(monkeypatch):
    """extraction_render_angles should use the addon job bridge and keep legacy JSON formatting."""

    class FakeRpcClient:
        def __init__(self) -> None:
            self.poll_count = 0

        def launch_background_job(self, cmd, args, *, timeout_seconds=None):
            assert cmd == "extraction.render_angles"
            return RpcResponse(request_id="req-1", status="ok", result={"job_id": "job-2"})

        def get_background_job_status(self, job_id):
            self.poll_count += 1
            if self.poll_count == 1:
                return RpcResponse(
                    request_id="req-2",
                    status="ok",
                    result={
                        "job_id": job_id,
                        "status": "running",
                        "progress_current": 1,
                        "progress_total": 2,
                        "status_message": "Rendered front view",
                    },
                )
            return RpcResponse(
                request_id="req-3",
                status="ok",
                result={
                    "job_id": job_id,
                    "status": "completed",
                    "progress_current": 2,
                    "progress_total": 2,
                    "status_message": "Completed",
                },
            )

        def collect_background_job_result(self, job_id):
            return RpcResponse(
                request_id="req-4",
                status="ok",
                result={
                    "job_id": job_id,
                    "result": {
                        "object_name": "Cube",
                        "renders": [{"angle": "front", "path": "/tmp/front.png"}],
                    },
                },
            )

        def cancel_background_job(self, job_id):
            return RpcResponse(request_id="req-5", status="ok", result={"job_id": job_id})

    monkeypatch.setattr("server.adapters.mcp.tasks.task_bridge.get_rpc_client", lambda: FakeRpcClient())

    ctx = BackgroundContext("task-render")
    result = asyncio.run(extraction_render_angles(ctx, object_name="Cube"))

    assert '"object_name": "Cube"' in result
    assert "Rendered 1 views of 'Cube'" in ctx.info_messages[-1]
    registry_record = get_background_job_registry().get("task-render")
    assert registry_record is not None
    assert registry_record.status == "completed"


def test_workflow_catalog_import_finalize_uses_local_background_bridge(monkeypatch):
    """workflow_catalog(import_finalize) should support task-mode local execution."""

    class Handler:
        def finalize_import_session(
            self,
            session_id,
            overwrite=None,
            *,
            progress_callback=None,
            is_cancelled=None,
        ):
            progress_callback(1, 2, "Assembling workflow")
            return {
                "status": "imported",
                "workflow_name": "chair",
                "message": "ok",
            }

    monkeypatch.setattr("server.adapters.mcp.areas.workflow_catalog.get_workflow_catalog_handler", lambda: Handler())

    ctx = BackgroundContext("task-workflow")
    result = asyncio.run(workflow_catalog(ctx, action="import_finalize", session_id="sess-1"))

    assert result.status == "imported"
    assert result.workflow_name == "chair"
    registry_record = get_background_job_registry().get("task-workflow")
    assert registry_record is not None
    assert registry_record.status == "completed"
    assert ctx.progress_events[-1] == (1, 1, "Workflow import finalization completed")


def test_workflow_catalog_import_finalize_times_out_in_local_background_bridge(monkeypatch):
    """Local background bridge should enforce MCP_TASK_TIMEOUT_SECONDS."""

    class Handler:
        def finalize_import_session(
            self,
            session_id,
            overwrite=None,
            *,
            progress_callback=None,
            is_cancelled=None,
        ):
            import time

            time.sleep(0.2)
            return {"status": "imported", "workflow_name": "chair", "message": "ok"}

    monkeypatch.setattr("server.adapters.mcp.areas.workflow_catalog.get_workflow_catalog_handler", lambda: Handler())
    monkeypatch.setattr(
        "server.adapters.mcp.tasks.task_bridge._get_timeout_policy",
        lambda ctx: build_timeout_policy(
            tool_timeout_seconds=30.0,
            task_timeout_seconds=0.01,
            rpc_timeout_seconds=30.0,
            addon_execution_timeout_seconds=30.0,
        ),
    )

    ctx = BackgroundContext("task-workflow-timeout")

    result = asyncio.run(workflow_catalog(ctx, action="import_finalize", session_id="sess-1"))

    assert result.error is not None
    assert "exceeded MCP_TASK_TIMEOUT_SECONDS" in result.error

    registry_record = get_background_job_registry().get("task-workflow-timeout")
    assert registry_record is not None
    assert registry_record.status == "failed"


def test_run_local_background_operation_ignores_late_progress_after_timeout(monkeypatch):
    """Late local progress callbacks must not resurrect a timed-out task."""

    late_progress_seen = Event()

    def background_executor(progress_callback, is_cancelled):
        import time

        time.sleep(0.05)
        progress_callback(1, 2, "Late progress")
        late_progress_seen.set()
        return {"status": "imported", "workflow_name": "chair", "message": "ok"}

    monkeypatch.setattr(
        "server.adapters.mcp.tasks.task_bridge._get_timeout_policy",
        lambda ctx: build_timeout_policy(
            tool_timeout_seconds=30.0,
            task_timeout_seconds=0.01,
            rpc_timeout_seconds=30.0,
            addon_execution_timeout_seconds=30.0,
        ),
    )

    async def _scenario() -> BackgroundContext:
        ctx = BackgroundContext("task-local-late-progress")
        with pytest.raises(RuntimeError, match="exceeded MCP_TASK_TIMEOUT_SECONDS"):
            await run_local_background_operation(
                cast(Context, ctx),
                tool_name="workflow_catalog.import_finalize",
                foreground_executor=lambda: {"status": "imported"},
                background_executor=background_executor,
                result_formatter=lambda result: result,
                start_message="Starting workflow import finalization",
                completion_message="Workflow import finalization completed",
            )
        await asyncio.to_thread(late_progress_seen.wait, 0.5)
        return ctx

    ctx = asyncio.run(_scenario())

    assert late_progress_seen.is_set()
    registry_record = get_background_job_registry().get("task-local-late-progress")
    assert registry_record is not None
    assert registry_record.status == "failed"
    assert registry_record.progress.message == "Starting workflow import finalization"
    assert all(message != "Late progress" for _, _, message in ctx.progress_events)


def test_workflow_catalog_import_finalize_marks_failed_on_local_execution_error(monkeypatch):
    """Unhandled local background errors should mark the task as failed."""

    class Handler:
        def finalize_import_session(
            self,
            session_id,
            overwrite=None,
            *,
            progress_callback=None,
            is_cancelled=None,
        ):
            raise RuntimeError("finalize boom")

    monkeypatch.setattr("server.adapters.mcp.areas.workflow_catalog.get_workflow_catalog_handler", lambda: Handler())

    ctx = BackgroundContext("task-workflow-error")

    result = asyncio.run(workflow_catalog(ctx, action="import_finalize", session_id="sess-1"))

    assert result.error == "finalize boom"

    registry_record = get_background_job_registry().get("task-workflow-error")
    assert registry_record is not None
    assert registry_record.status == "failed"


def test_export_obj_background_path_uses_system_bridge(monkeypatch):
    """export_obj should use the addon job bridge when running in task mode."""

    class FakeRpcClient:
        def __init__(self) -> None:
            self.poll_count = 0

        def launch_background_job(self, cmd, args, *, timeout_seconds=None):
            assert cmd == "export.obj"
            assert args["filepath"] == "/tmp/test.obj"
            return RpcResponse(request_id="req-1", status="ok", result={"job_id": "job-export"})

        def get_background_job_status(self, job_id):
            self.poll_count += 1
            if self.poll_count == 1:
                return RpcResponse(
                    request_id="req-2",
                    status="ok",
                    result={
                        "job_id": job_id,
                        "status": "running",
                        "progress_current": 2,
                        "progress_total": 4,
                        "status_message": "Verifying OBJ export output",
                    },
                )
            return RpcResponse(
                request_id="req-3",
                status="ok",
                result={
                    "job_id": job_id,
                    "status": "completed",
                    "progress_current": 4,
                    "progress_total": 4,
                    "status_message": "Completed",
                },
            )

        def collect_background_job_result(self, job_id):
            return RpcResponse(
                request_id="req-4",
                status="ok",
                result={"job_id": job_id, "result": "Successfully exported to '/tmp/test.obj'"},
            )

        def cancel_background_job(self, job_id):
            return RpcResponse(request_id="req-5", status="ok", result={"job_id": job_id})

    monkeypatch.setattr("server.adapters.mcp.tasks.task_bridge.get_rpc_client", lambda: FakeRpcClient())

    ctx = BackgroundContext("task-export-obj")
    result = asyncio.run(export_obj(ctx, filepath="/tmp/test.obj"))

    assert "Successfully exported" in result
    assert "Exported OBJ to: /tmp/test.obj" in ctx.info_messages[-1]
    registry_record = get_background_job_registry().get("task-export-obj")
    assert registry_record is not None
    assert registry_record.backend_job_id == "job-export"
    assert registry_record.status == "completed"


def test_import_glb_background_path_uses_system_bridge(monkeypatch):
    """import_glb should use the addon job bridge when running in task mode."""

    class FakeRpcClient:
        def __init__(self) -> None:
            self.poll_count = 0

        def launch_background_job(self, cmd, args, *, timeout_seconds=None):
            assert cmd == "import.glb"
            assert args["filepath"] == "/tmp/model.glb"
            return RpcResponse(request_id="req-1", status="ok", result={"job_id": "job-import"})

        def get_background_job_status(self, job_id):
            self.poll_count += 1
            if self.poll_count == 1:
                return RpcResponse(
                    request_id="req-2",
                    status="ok",
                    result={
                        "job_id": job_id,
                        "status": "running",
                        "progress_current": 2,
                        "progress_total": 3,
                        "status_message": "Collecting imported GLB/GLTF objects",
                    },
                )
            return RpcResponse(
                request_id="req-3",
                status="ok",
                result={
                    "job_id": job_id,
                    "status": "completed",
                    "progress_current": 3,
                    "progress_total": 3,
                    "status_message": "Completed",
                },
            )

        def collect_background_job_result(self, job_id):
            return RpcResponse(
                request_id="req-4",
                status="ok",
                result={
                    "job_id": job_id,
                    "result": "Successfully imported GLB/GLTF from '/tmp/model.glb'. Objects: Cube",
                },
            )

        def cancel_background_job(self, job_id):
            return RpcResponse(request_id="req-5", status="ok", result={"job_id": job_id})

    monkeypatch.setattr("server.adapters.mcp.tasks.task_bridge.get_rpc_client", lambda: FakeRpcClient())

    ctx = BackgroundContext("task-import-glb")
    result = asyncio.run(import_glb(ctx, filepath="/tmp/model.glb"))

    assert "Successfully imported GLB/GLTF" in result
    assert "Imported GLB/GLTF from: /tmp/model.glb" in ctx.info_messages[-1]
    registry_record = get_background_job_registry().get("task-import-glb")
    assert registry_record is not None
    assert registry_record.backend_job_id == "job-import"
    assert registry_record.status == "completed"


def test_import_image_as_plane_background_path_uses_system_bridge(monkeypatch):
    """import_image_as_plane should use the addon job bridge when running in task mode."""

    class FakeRpcClient:
        def __init__(self) -> None:
            self.poll_count = 0

        def launch_background_job(self, cmd, args, *, timeout_seconds=None):
            assert cmd == "import.image_as_plane"
            assert args["filepath"] == "/tmp/image.png"
            return RpcResponse(request_id="req-1", status="ok", result={"job_id": "job-image"})

        def get_background_job_status(self, job_id):
            self.poll_count += 1
            if self.poll_count == 1:
                return RpcResponse(
                    request_id="req-2",
                    status="ok",
                    result={
                        "job_id": job_id,
                        "status": "running",
                        "progress_current": 2,
                        "progress_total": 4,
                        "status_message": "Building image material",
                    },
                )
            return RpcResponse(
                request_id="req-3",
                status="ok",
                result={
                    "job_id": job_id,
                    "status": "completed",
                    "progress_current": 4,
                    "progress_total": 4,
                    "status_message": "Completed",
                },
            )

        def collect_background_job_result(self, job_id):
            return RpcResponse(
                request_id="req-4",
                status="ok",
                result={
                    "job_id": job_id,
                    "result": "Successfully imported image as plane 'RefImage' from '/tmp/image.png'",
                },
            )

        def cancel_background_job(self, job_id):
            return RpcResponse(request_id="req-5", status="ok", result={"job_id": job_id})

    monkeypatch.setattr("server.adapters.mcp.tasks.task_bridge.get_rpc_client", lambda: FakeRpcClient())

    ctx = BackgroundContext("task-image-plane")
    result = asyncio.run(import_image_as_plane(ctx, filepath="/tmp/image.png", name="RefImage"))

    assert "Successfully imported image as plane" in result
    assert "Imported image as plane from: /tmp/image.png" in ctx.info_messages[-1]
    registry_record = get_background_job_registry().get("task-image-plane")
    assert registry_record is not None
    assert registry_record.backend_job_id == "job-image"
    assert registry_record.status == "completed"


def test_scene_get_viewport_background_path_times_out_during_polling(monkeypatch):
    """Background polling should respect MCP_TASK_TIMEOUT_SECONDS, not loop forever."""

    class FakeRpcClient:
        def __init__(self) -> None:
            self.cancelled: list[str] = []

        def launch_background_job(self, cmd, args, *, timeout_seconds=None):
            return RpcResponse(request_id="req-1", status="ok", result={"job_id": "job-timeout"})

        def get_background_job_status(self, job_id):
            return RpcResponse(
                request_id="req-2",
                status="ok",
                result={
                    "job_id": job_id,
                    "status": "running",
                    "progress_current": 0,
                    "progress_total": 1,
                    "status_message": "Still running",
                },
            )

        def collect_background_job_result(self, job_id):
            raise AssertionError("collect should not be called on timeout")

        def cancel_background_job(self, job_id):
            self.cancelled.append(job_id)
            return RpcResponse(request_id="req-3", status="ok", result={"job_id": job_id})

    fake_rpc = FakeRpcClient()
    monotonic_values = iter([0.0, 0.1, 0.3])

    monkeypatch.setattr("server.adapters.mcp.tasks.task_bridge.get_rpc_client", lambda: fake_rpc)
    monkeypatch.setattr(
        "server.adapters.mcp.tasks.task_bridge._get_timeout_policy",
        lambda ctx: build_timeout_policy(
            tool_timeout_seconds=30.0,
            task_timeout_seconds=0.2,
            rpc_timeout_seconds=30.0,
            addon_execution_timeout_seconds=30.0,
        ),
    )
    monkeypatch.setattr("server.adapters.mcp.tasks.task_bridge._monotonic_now", lambda: next(monotonic_values))

    ctx = BackgroundContext("task-timeout")

    with pytest.raises(RuntimeError, match="exceeded MCP_TASK_TIMEOUT_SECONDS"):
        asyncio.run(scene_get_viewport(ctx, output_mode="BASE64"))

    registry_record = get_background_job_registry().get("task-timeout")
    assert registry_record is not None
    assert registry_record.status == "failed"
    assert fake_rpc.cancelled == ["job-timeout"]


def test_scene_get_viewport_background_path_marks_failed_on_result_formatter_error(monkeypatch):
    """Formatter failures after completed addon jobs should mark the task as failed."""

    class FakeRpcClient:
        def __init__(self) -> None:
            self.poll_count = 0

        def launch_background_job(self, cmd, args, *, timeout_seconds=None):
            return RpcResponse(request_id="req-1", status="ok", result={"job_id": "job-format"})

        def get_background_job_status(self, job_id):
            self.poll_count += 1
            return RpcResponse(
                request_id="req-2",
                status="ok",
                result={
                    "job_id": job_id,
                    "status": "completed",
                    "progress_current": 1,
                    "progress_total": 1,
                    "status_message": "Completed",
                },
            )

        def collect_background_job_result(self, job_id):
            return RpcResponse(
                request_id="req-3",
                status="ok",
                result={"job_id": job_id, "result": {"not": "a base64 string"}},
            )

        def cancel_background_job(self, job_id):
            return RpcResponse(request_id="req-4", status="ok", result={"job_id": job_id})

    monkeypatch.setattr("server.adapters.mcp.tasks.task_bridge.get_rpc_client", lambda: FakeRpcClient())

    ctx = BackgroundContext("task-format-error")

    with pytest.raises(RuntimeError, match="invalid payload"):
        asyncio.run(scene_get_viewport(ctx, output_mode="BASE64"))

    registry_record = get_background_job_registry().get("task-format-error")
    assert registry_record is not None
    assert registry_record.status == "failed"
