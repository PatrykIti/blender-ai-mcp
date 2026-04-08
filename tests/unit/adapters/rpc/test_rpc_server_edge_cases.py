from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import blender_addon.infrastructure.rpc_server as rpc_module
from blender_addon.infrastructure.rpc_server import BlenderRpcServer


def test_should_push_undo_and_safe_undo_push(monkeypatch):
    fake_bpy = SimpleNamespace(ops=SimpleNamespace(ed=SimpleNamespace(undo_push=MagicMock())))
    monkeypatch.setattr(rpc_module, "bpy", fake_bpy)

    assert rpc_module._should_push_undo("mesh.extrude_region") is True
    assert rpc_module._should_push_undo("scene.list_objects") is False

    rpc_module._safe_undo_push("test")
    fake_bpy.ops.ed.undo_push.assert_called_once_with(message="test")


def test_schedule_and_invoke_background_job_paths(monkeypatch):
    server = BlenderRpcServer()
    registered = []
    fake_bpy = SimpleNamespace(app=SimpleNamespace(timers=SimpleNamespace(register=lambda fn: registered.append(fn))))
    monkeypatch.setattr(rpc_module, "bpy", fake_bpy)

    server._schedule_background_job("job-1")
    assert registered

    job = rpc_module.BackgroundJob(job_id="job-1", cmd="demo.long", args={}, timeout_seconds=5.0)
    server.background_jobs[job.job_id] = job

    def handler(progress_callback=None, is_cancelled=None):
        progress_callback(1, 2, "halfway")
        assert is_cancelled() is False
        return {"ok": True}

    result = server._invoke_background_handler(handler, job)
    assert result == {"ok": True}
    assert server.background_jobs[job.job_id].progress_current == 1.0


def test_run_background_job_error_paths_and_ping(monkeypatch):
    server = BlenderRpcServer()
    server._run_background_job("missing")

    server.background_jobs["job-1"] = rpc_module.BackgroundJob(
        job_id="job-1", cmd="unknown", args={}, timeout_seconds=5.0
    )
    server._run_background_job("job-1")
    assert server.background_jobs["job-1"].status == "failed"

    cancelled = rpc_module.BackgroundJob(
        job_id="job-2", cmd="demo", args={}, timeout_seconds=5.0, cancel_requested=True
    )
    server.background_jobs["job-2"] = cancelled
    server.register_background_handler("demo", lambda **kwargs: {"ok": True})
    server._run_background_job("job-2")
    assert server.background_jobs["job-2"].status == "cancelled"

    response = server._process_request({"request_id": "req", "cmd": "ping", "args": {}})
    assert response["status"] == "ok"


def test_rpc_server_watchdog_restarts_unhealthy_listener(monkeypatch):
    server = BlenderRpcServer()
    server.running = True
    server.server_socket = MagicMock()
    server.server_socket.fileno.return_value = -1
    server.server_thread = None

    restarted = []

    monkeypatch.setattr(server, "stop", lambda: restarted.append("stop"))
    monkeypatch.setattr(server, "start", lambda: restarted.append("start"))

    assert server.ensure_running() is False
    assert restarted == ["stop", "start"]


def test_rpc_server_watchdog_register_and_stop(monkeypatch):
    registered = []
    unregistered = []
    fake_timers = SimpleNamespace(
        register=lambda fn, first_interval=0.0: registered.append((fn, first_interval)),
        unregister=lambda fn: unregistered.append(fn),
        is_registered=lambda fn: True,
    )
    monkeypatch.setattr(rpc_module, "bpy", SimpleNamespace(app=SimpleNamespace(timers=fake_timers)))

    server = BlenderRpcServer()

    assert server.start_watchdog(interval_seconds=1.5) is True
    assert registered
    assert registered[0][1] == 1.5

    server.stop_watchdog()
    assert unregistered == [registered[0][0]]


def test_process_request_unknown_command_and_background_errors(monkeypatch):
    server = BlenderRpcServer()
    monkeypatch.setattr(rpc_module, "bpy", None)

    unknown = server._process_request({"request_id": "req", "cmd": "unknown.cmd", "args": {}})
    assert unknown["status"] == "error"
    assert "Unknown command" in unknown["error"]

    missing_cmd = server._handle_background_rpc("rpc.launch_job", "req", {}, 5.0)
    assert missing_cmd["error_code"] == "missing_background_command"

    unknown_cmd = server._handle_background_rpc("rpc.launch_job", "req", {"cmd": "unknown"}, 5.0)
    assert unknown_cmd["error_code"] == "unknown_background_command"

    missing_job_id = server._handle_background_rpc("rpc.get_job", "req", {}, 5.0)
    assert missing_job_id["error_code"] == "missing_job_id"

    unknown_job = server._handle_background_rpc("rpc.get_job", "req", {"job_id": "missing"}, 5.0)
    assert unknown_job["error_code"] == "unknown_job_id"

    server.background_jobs["job-1"] = rpc_module.BackgroundJob(job_id="job-1", cmd="demo", args={}, timeout_seconds=5.0)
    collect = server._handle_background_rpc("rpc.collect_job", "req", {"job_id": "job-1"}, 5.0)
    assert collect["error_code"] == "job_not_completed"

    unknown_verb = server._handle_background_rpc("rpc.unknown", "req", {"job_id": "job-1"}, 5.0)
    assert unknown_verb["error_code"] == "unknown_background_verb"


def test_rpc_server_writes_trace_file(tmp_path, monkeypatch):
    server = BlenderRpcServer()
    monkeypatch.setattr(server, "trace_file_path", tmp_path / "rpc_trace.jsonl")
    monkeypatch.setattr(rpc_module, "bpy", None)

    response = server._process_request({"request_id": "req-1", "cmd": "unknown.cmd", "args": {"foo": "bar"}})

    assert response["status"] == "error"
    content = server.trace_file_path.read_text(encoding="utf-8")
    assert '"event": "rpc_received"' in content
    assert '"event": "rpc_handler_failed"' in content
    assert '"request_id": "req-1"' in content
    assert '"cmd": "unknown.cmd"' in content


def test_handle_client_invalid_json(monkeypatch):
    server = BlenderRpcServer()
    server.running = True

    sent_payloads = []
    messages = [b"not-json", None]

    monkeypatch.setattr(rpc_module, "recv_msg", lambda conn: messages.pop(0))
    monkeypatch.setattr(
        rpc_module, "send_msg", lambda conn, data: sent_payloads.append(json.loads(data.decode("utf-8")))
    )

    class DummyConn:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    server._handle_client(DummyConn())

    assert sent_payloads[0]["status"] == "error"
    assert sent_payloads[0]["error"] == "Invalid JSON"
