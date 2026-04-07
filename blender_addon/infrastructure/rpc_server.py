import inspect
import json
import os
import queue
import socket
import struct
import threading
import time
import traceback
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict

from ..application.handlers.job_utils import JobCancelledError

# Try importing bpy, but allow running outside blender for testing
try:
    import bpy
except ImportError:
    bpy = None

HOST = "0.0.0.0"  # Listen on all interfaces within container
PORT = 8765
DEFAULT_EXECUTION_TIMEOUT_SECONDS = float(os.environ.get("ADDON_EXECUTION_TIMEOUT_SECONDS", "30.0"))

# If enabled, the addon will push an explicit undo step after each mutating RPC command.
# This makes `system_undo(steps=1)` behave more like "undo the last MCP tool call"
# instead of undoing a large batch of changes.
#
# Disable by setting: BLENDER_AI_MCP_AUTO_UNDO_PUSH=0
AUTO_UNDO_PUSH = os.environ.get("BLENDER_AI_MCP_AUTO_UNDO_PUSH", "1") not in ("0", "false", "False")

_NO_UNDO_PUSH_CMDS = {
    "ping",
    # System tools that manage undo/redo or files should not create new undo steps.
    "system.undo",
    "system.redo",
    "system.snapshot",
    "system.save_file",
    "system.new_file",
    "system.purge_orphans",
    "system.set_mode",
    # Scene/context inspection and viewport utilities (no geometry changes expected).
    "scene.list_objects",
    "scene.get_mode",
    "scene.list_selection",
    "scene.snapshot_state",
    "scene.get_viewport",
    "scene.get_custom_properties",
    "scene.get_hierarchy",
    "scene.get_bounding_box",
    "scene.get_origin_info",
    "scene.camera_orbit",
    "scene.camera_focus",
    "scene.get_view_state",
    "scene.restore_view_state",
    "scene.set_standard_view",
    "scene.get_view_diagnostics",
    "scene.isolate_object",
    "scene.hide_object",
    "scene.show_all_objects",
    "scene.set_active_object",
    "scene.set_mode",
    # Selection-only helpers (avoid polluting undo history).
    "mesh.select_all",
    "mesh.select_none",
    "mesh.select_linked",
    "mesh.select_more",
    "mesh.select_less",
    "mesh.select_boundary",
    "mesh.select_by_index",
    "mesh.select_loop",
    "mesh.select_ring",
    "mesh.select_by_location",
    "mesh.set_proportional_edit",
    "mesh.select",
}

_NO_UNDO_PUSH_PREFIXES = (
    # Read-only inspections
    "scene.inspect_",
    "scene.get_constraints",
    "collection.list",
    "collection.list_objects",
    "material.list",
    "material.inspect_nodes",
    "uv.list_maps",
    "mesh.get_vertex_data",
    "mesh.get_edge_data",
    "mesh.get_face_data",
    "mesh.get_uv_data",
    "mesh.get_loop_normals",
    "mesh.get_vertex_group_weights",
    "mesh.get_attributes",
    "mesh.get_shape_keys",
    "mesh.list_groups",
    "curve.get_data",
    "lattice.get_points",
    "armature.get_data",
    "modeling.get_modifier_data",
    # Pure output generation (no scene edits expected)
    "export.",
    "baking.",
    "extraction.",
)


def _should_push_undo(cmd: str) -> bool:
    if not AUTO_UNDO_PUSH:
        return False
    if not cmd:
        return False
    if cmd in _NO_UNDO_PUSH_CMDS:
        return False
    for prefix in _NO_UNDO_PUSH_PREFIXES:
        if cmd.startswith(prefix):
            return False
    return True


def _safe_undo_push(message: str) -> None:
    if not bpy:
        return
    # Blender may reject undo operations in some contexts (e.g., background mode).
    # Undo push is best-effort and must never break the RPC call.
    try:
        bpy.ops.ed.undo_push(message=message)
    except Exception:
        pass


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack(">I", len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack(">I", raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


@dataclass
class BackgroundJob:
    """Tracked addon-side job state for long-running task-mode work."""

    job_id: str
    cmd: str
    args: Dict[str, Any]
    timeout_seconds: float
    status: str = "queued"
    progress_current: float = 0.0
    progress_total: float | None = None
    status_message: str | None = None
    result: Any = None
    error: str | None = None
    cancelled: bool = False
    cancel_requested: bool = False
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    finished_at: float | None = None
    updated_at: float = field(default_factory=time.time)


class BlenderRpcServer:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.server_thread = None
        self.running = False
        self.command_registry = {}
        self.background_command_registry = {}

        # Queue for results from main thread
        self.result_queues = {}  # request_id -> Queue
        self.background_jobs: Dict[str, BackgroundJob] = {}
        self._jobs_lock = threading.Lock()

    def register_handler(self, cmd: str, handler_func):
        """Register a function to handle a specific command."""
        self.command_registry[cmd] = handler_func

    def register_background_handler(self, cmd: str, handler_func: Callable[..., Any]):
        """Register a function as task-capable background work."""

        self.background_command_registry[cmd] = handler_func

    def start(self):
        if self.running:
            return

        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            print(f"[BlenderRpc] Server started on {self.host}:{self.port}")

            self.server_thread = threading.Thread(target=self._accept_loop, daemon=True)
            self.server_thread.start()
        except Exception as e:
            print(f"[BlenderRpc] Failed to start server: {e}")
            self.running = False

    def stop(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
        with self._jobs_lock:
            self.background_jobs.clear()
        print("[BlenderRpc] Server stopped")

    def _accept_loop(self):
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                try:
                    conn, addr = self.server_socket.accept()
                except socket.timeout:
                    continue

                print(f"[BlenderRpc] Connected by {addr}")
                self._handle_client(conn)
            except Exception as e:
                if self.running:
                    print(f"[BlenderRpc] Accept loop error: {e}")

    def _handle_client(self, conn):
        with conn:
            while self.running:
                try:
                    data = recv_msg(conn)
                    if not data:
                        break

                    try:
                        message = json.loads(data.decode("utf-8"))
                        response = self._process_request(message)

                        response_data = json.dumps(response).encode("utf-8")
                        send_msg(conn, response_data)

                    except json.JSONDecodeError:
                        err = {"status": "error", "error": "Invalid JSON"}
                        send_msg(conn, json.dumps(err).encode("utf-8"))

                except Exception as e:
                    print(f"[BlenderRpc] Client handler error: {e}")
                    break

    def _build_job_snapshot(self, job: BackgroundJob, *, include_result: bool = False) -> Dict[str, Any]:
        """Serialize background job state for poll/collect RPC responses."""

        snapshot = {
            "job_id": job.job_id,
            "cmd": job.cmd,
            "status": job.status,
            "timeout_seconds": job.timeout_seconds,
            "progress_current": job.progress_current,
            "progress_total": job.progress_total,
            "status_message": job.status_message,
            "cancelled": job.cancelled,
            "cancel_requested": job.cancel_requested,
            "error": job.error,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "finished_at": job.finished_at,
            "updated_at": job.updated_at,
            "result_ready": job.status == "completed",
        }
        if include_result:
            snapshot["result"] = job.result
        return snapshot

    def _get_background_job(self, job_id: str) -> BackgroundJob | None:
        with self._jobs_lock:
            return self.background_jobs.get(job_id)

    def _update_background_job(self, job_id: str, **changes: Any) -> BackgroundJob | None:
        with self._jobs_lock:
            job = self.background_jobs.get(job_id)
            if job is None:
                return None
            for key, value in changes.items():
                setattr(job, key, value)
            job.updated_at = time.time()
            return job

    def _schedule_background_job(self, job_id: str) -> None:
        """Schedule a background job without blocking the RPC network loop."""

        if bpy:

            def run_on_main_thread() -> None:
                self._run_background_job(job_id)
                return None

            bpy.app.timers.register(run_on_main_thread)
            return

        threading.Thread(
            target=self._run_background_job,
            args=(job_id,),
            daemon=True,
        ).start()

    def _invoke_background_handler(self, handler_func: Callable[..., Any], job: BackgroundJob) -> Any:
        """Invoke a background handler with cooperative progress/cancel hooks."""

        def progress_callback(current: float, total: float | None = None, message: str | None = None) -> None:
            self._update_background_job(
                job.job_id,
                progress_current=float(current),
                progress_total=float(total) if isinstance(total, (int, float)) else total,
                status_message=message,
                status="running",
            )

        def is_cancelled() -> bool:
            tracked = self._get_background_job(job.job_id)
            if tracked is None:
                return True
            if (
                tracked.started_at is not None
                and tracked.timeout_seconds > 0
                and (time.time() - tracked.started_at) >= tracked.timeout_seconds
            ):
                self._update_background_job(
                    job.job_id,
                    cancel_requested=True,
                    status="cancelling",
                    error=f"Background job exceeded timeout budget ({tracked.timeout_seconds:.1f}s)",
                    status_message="Timeout budget exceeded",
                )
            return bool(tracked.cancel_requested)

        kwargs = dict(job.args)
        signature = inspect.signature(handler_func)
        if "progress_callback" in signature.parameters:
            kwargs["progress_callback"] = progress_callback
        if "is_cancelled" in signature.parameters:
            kwargs["is_cancelled"] = is_cancelled
        return handler_func(**kwargs)

    def _run_background_job(self, job_id: str) -> None:
        """Execute a scheduled background job on the safe runtime path."""

        job = self._get_background_job(job_id)
        if job is None:
            return

        handler_func = self.background_command_registry.get(job.cmd)
        if handler_func is None:
            self._update_background_job(
                job_id,
                status="failed",
                error=f"No background handler registered for '{job.cmd}'",
                finished_at=time.time(),
            )
            return

        if job.cancel_requested:
            self._update_background_job(
                job_id,
                status="cancelled",
                cancelled=True,
                error="Background job cancelled before start",
                finished_at=time.time(),
            )
            return

        self._update_background_job(
            job_id,
            status="running",
            started_at=time.time(),
            status_message=f"Running {job.cmd}",
        )

        try:
            result = self._invoke_background_handler(handler_func, job)
            tracked = self._get_background_job(job_id)
            if tracked is not None and tracked.cancel_requested:
                self._update_background_job(
                    job_id,
                    status="cancelled",
                    cancelled=True,
                    error="Background job cancelled",
                    finished_at=time.time(),
                )
                return

            self._update_background_job(
                job_id,
                status="completed",
                result=result,
                finished_at=time.time(),
                progress_current=(
                    tracked.progress_total or tracked.progress_current or 1 if tracked is not None else 1
                ),
                progress_total=(tracked.progress_total or tracked.progress_current or 1 if tracked is not None else 1),
                status_message="Completed",
                error=None,
            )
        except JobCancelledError as exc:
            self._update_background_job(
                job_id,
                status="cancelled",
                cancelled=True,
                error=str(exc),
                finished_at=time.time(),
                status_message="Cancelled",
            )
        except Exception as exc:
            traceback.print_exc()
            self._update_background_job(
                job_id,
                status="failed",
                error=str(exc),
                finished_at=time.time(),
                status_message="Failed",
            )

    def _handle_background_rpc(
        self,
        rpc_cmd: str,
        request_id: str,
        args: Dict[str, Any],
        timeout_seconds: Any,
    ) -> Dict[str, Any]:
        """Handle explicit background job lifecycle RPC verbs."""

        cmd = args.get("cmd")
        job_id = args.get("job_id")

        if rpc_cmd == "rpc.launch_job":
            if not isinstance(cmd, str):
                return {
                    "request_id": request_id,
                    "status": "error",
                    "error": "cmd required for rpc.launch_job",
                    "error_code": "missing_background_command",
                    "error_boundary": "addon_execution",
                }
            if cmd not in self.background_command_registry:
                return {
                    "request_id": request_id,
                    "status": "error",
                    "error": f"Unknown background command: {cmd}",
                    "error_code": "unknown_background_command",
                    "error_boundary": "addon_execution",
                }

            background_job = BackgroundJob(
                job_id=uuid.uuid4().hex,
                cmd=cmd,
                args=args.get("args", {}) or {},
                timeout_seconds=(
                    float(timeout_seconds)
                    if isinstance(timeout_seconds, (int, float)) and timeout_seconds > 0
                    else DEFAULT_EXECUTION_TIMEOUT_SECONDS
                ),
                progress_total=1,
                status_message=f"Queued {cmd}",
            )
            with self._jobs_lock:
                self.background_jobs[background_job.job_id] = background_job
            self._schedule_background_job(background_job.job_id)
            return {
                "request_id": request_id,
                "status": "ok",
                "result": self._build_job_snapshot(background_job),
            }

        if not isinstance(job_id, str) or not job_id:
            return {
                "request_id": request_id,
                "status": "error",
                "error": "job_id required",
                "error_code": "missing_job_id",
                "error_boundary": "addon_execution",
            }

        tracked_job = self._get_background_job(job_id)
        if tracked_job is None:
            return {
                "request_id": request_id,
                "status": "error",
                "error": f"Unknown background job: {job_id}",
                "error_code": "unknown_job_id",
                "error_boundary": "addon_execution",
            }

        if rpc_cmd == "rpc.get_job":
            return {
                "request_id": request_id,
                "status": "ok",
                "result": self._build_job_snapshot(tracked_job),
            }

        if rpc_cmd == "rpc.cancel_job":
            if tracked_job.status in {"completed", "failed", "cancelled"}:
                return {
                    "request_id": request_id,
                    "status": "ok",
                    "result": self._build_job_snapshot(tracked_job),
                }
            self._update_background_job(
                job_id,
                cancel_requested=True,
                status="cancelling" if tracked_job.status == "running" else "cancelled",
                cancelled=tracked_job.status != "running",
                error="Cancellation requested",
                finished_at=time.time() if tracked_job.status != "running" else tracked_job.finished_at,
                status_message="Cancellation requested",
            )
            updated_job = self._get_background_job(job_id)
            return {
                "request_id": request_id,
                "status": "ok",
                "result": self._build_job_snapshot(updated_job or tracked_job),
            }

        if rpc_cmd == "rpc.collect_job":
            if tracked_job.status != "completed":
                return {
                    "request_id": request_id,
                    "status": "error",
                    "error": f"Background job {job_id} is not completed yet",
                    "error_code": "job_not_completed",
                    "error_boundary": "addon_execution",
                }
            return {
                "request_id": request_id,
                "status": "ok",
                "result": self._build_job_snapshot(tracked_job, include_result=True),
            }

        return {
            "request_id": request_id,
            "status": "error",
            "error": f"Unknown RPC background verb: {rpc_cmd}",
            "error_code": "unknown_background_verb",
            "error_boundary": "addon_execution",
        }

    def _process_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        request_id = message.get("request_id")
        cmd = message.get("cmd")
        args = message.get("args", {})
        timeout_seconds = message.get("timeout_seconds")
        deadline_unix_ms = message.get("deadline_unix_ms")

        if not request_id or not cmd:
            return {"status": "error", "error": "Missing request_id or cmd", "request_id": request_id}

        print(f"[BlenderRpc] Received cmd: {cmd}")

        if cmd == "ping":
            return {
                "request_id": request_id,
                "status": "ok",
                "result": {"version": bpy.app.version_string if bpy else "Mock Blender"},
            }

        if cmd in {"rpc.launch_job", "rpc.get_job", "rpc.cancel_job", "rpc.collect_job"}:
            return self._handle_background_rpc(cmd, request_id, args, timeout_seconds)

        # Dispatch to Main Thread via Timer
        result_queue: queue.Queue[Dict[str, Any]] = queue.Queue()
        self.result_queues[request_id] = result_queue

        # Define the execution wrapper
        def main_thread_exec():
            try:
                if cmd in self.command_registry:
                    res = self.command_registry[cmd](**args)
                    if _should_push_undo(cmd):
                        _safe_undo_push(f"MCP: {cmd}")
                    result_queue.put({"status": "ok", "result": res})
                else:
                    result_queue.put({"status": "error", "error": f"Unknown command: {cmd}"})
            except Exception as e:
                traceback.print_exc()
                result_queue.put({"status": "error", "error": str(e)})

        # Schedule on main thread
        if bpy:
            bpy.app.timers.register(lambda: (main_thread_exec(), None)[1])
        else:
            # For testing outside blender
            main_thread_exec()

        # Wait for result (blocking the network thread, not the main thread)
        try:
            effective_timeout = (
                float(timeout_seconds)
                if isinstance(timeout_seconds, (int, float)) and timeout_seconds > 0
                else DEFAULT_EXECUTION_TIMEOUT_SECONDS
            )
            if isinstance(deadline_unix_ms, (int, float)):
                remaining_seconds = max(0.0, (float(deadline_unix_ms) / 1000.0) - time.time())
                effective_timeout = min(effective_timeout, remaining_seconds)
            response_payload = result_queue.get(timeout=effective_timeout)
        except queue.Empty:
            response_payload = {
                "status": "error",
                "error": f"Addon execution timeout after {effective_timeout:.1f}s for '{cmd}'",
                "error_code": "timeout",
                "error_boundary": "addon_execution",
            }

        del self.result_queues[request_id]

        return {"request_id": request_id, **response_payload}


# Singleton instance
rpc_server = BlenderRpcServer()
