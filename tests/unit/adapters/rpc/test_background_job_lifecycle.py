"""Tests for explicit background-job RPC lifecycle verbs."""

from __future__ import annotations

from blender_addon.infrastructure.rpc_server import BlenderRpcServer
from server.adapters.rpc.client import RpcClient
from server.domain.models.rpc import RpcResponse


def test_rpc_client_background_job_methods_use_explicit_control_plane(monkeypatch):
    """RpcClient should route launch/poll/cancel/collect through distinct RPC verbs."""

    calls = []
    client = RpcClient(host="127.0.0.1", port=8765)

    def fake_send_request(cmd, args=None, timeout_seconds=None, *, rpc_timeout_seconds=None):
        calls.append((cmd, args, timeout_seconds, rpc_timeout_seconds))
        return RpcResponse(request_id="req", status="ok", result={"ok": True})

    monkeypatch.setattr(client, "send_request", fake_send_request)

    client.launch_background_job("scene.get_viewport", {"width": 1}, timeout_seconds=12.0)
    client.get_background_job_status("job-1", timeout_seconds=5.0)
    client.cancel_background_job("job-1")
    client.collect_background_job_result("job-1", timeout_seconds=4.0)

    assert calls == [
        ("rpc.launch_job", {"cmd": "scene.get_viewport", "args": {"width": 1}}, 12.0, None),
        ("rpc.get_job", {"job_id": "job-1"}, 5.0, 5.0),
        ("rpc.cancel_job", {"job_id": "job-1"}, None, None),
        ("rpc.collect_job", {"job_id": "job-1"}, 4.0, 4.0),
    ]


def test_rpc_server_launch_poll_cancel_and_collect_background_jobs(monkeypatch):
    """Addon RPC server should keep explicit launch/poll/cancel/collect lifecycle state."""

    server = BlenderRpcServer()

    def background_handler(progress_callback=None, is_cancelled=None):
        progress_callback(1, 2, "halfway")
        return {"ok": True}

    server.register_background_handler("demo.long", background_handler)
    monkeypatch.setattr(server, "_schedule_background_job", lambda job_id: None)

    launch = server._process_request(
        {
            "request_id": "req-1",
            "cmd": "rpc.launch_job",
            "args": {"cmd": "demo.long", "args": {}},
            "timeout_seconds": 15.0,
            "deadline_unix_ms": 0,
        }
    )
    job_id = launch["result"]["job_id"]

    poll_queued = server._process_request(
        {
            "request_id": "req-2",
            "cmd": "rpc.get_job",
            "args": {"job_id": job_id},
            "timeout_seconds": 15.0,
            "deadline_unix_ms": 0,
        }
    )
    assert poll_queued["result"]["status"] == "queued"

    server._run_background_job(job_id)

    poll_completed = server._process_request(
        {
            "request_id": "req-3",
            "cmd": "rpc.get_job",
            "args": {"job_id": job_id},
            "timeout_seconds": 15.0,
            "deadline_unix_ms": 0,
        }
    )
    assert poll_completed["result"]["status"] == "completed"
    assert poll_completed["result"]["progress_total"] == 2.0

    collect = server._process_request(
        {
            "request_id": "req-4",
            "cmd": "rpc.collect_job",
            "args": {"job_id": job_id},
            "timeout_seconds": 15.0,
            "deadline_unix_ms": 0,
        }
    )
    assert collect["status"] == "ok"
    assert collect["result"]["result"] == {"ok": True}

    cancel_after_completion = server._process_request(
        {
            "request_id": "req-5",
            "cmd": "rpc.cancel_job",
            "args": {"job_id": job_id},
            "timeout_seconds": 15.0,
            "deadline_unix_ms": 0,
        }
    )
    assert cancel_after_completion["result"]["status"] == "completed"


def test_rpc_server_can_cancel_a_queued_background_job(monkeypatch):
    """Queued jobs should become cancelled before the addon starts executing them."""

    server = BlenderRpcServer()
    server.register_background_handler("demo.long", lambda **kwargs: {"ok": True})
    monkeypatch.setattr(server, "_schedule_background_job", lambda job_id: None)

    launch = server._process_request(
        {
            "request_id": "req-1",
            "cmd": "rpc.launch_job",
            "args": {"cmd": "demo.long", "args": {}},
            "timeout_seconds": 15.0,
            "deadline_unix_ms": 0,
        }
    )
    job_id = launch["result"]["job_id"]

    cancel = server._process_request(
        {
            "request_id": "req-2",
            "cmd": "rpc.cancel_job",
            "args": {"job_id": job_id},
            "timeout_seconds": 15.0,
            "deadline_unix_ms": 0,
        }
    )

    assert cancel["status"] == "ok"
    assert cancel["result"]["status"] == "cancelled"
    assert cancel["result"]["cancelled"] is True
