import socket
import threading
import json
import queue
import time
import traceback
import struct
import os
from typing import Dict, Any

# Try importing bpy, but allow running outside blender for testing
try:
    import bpy
except ImportError:
    bpy = None

HOST = "0.0.0.0" # Listen on all interfaces within container
PORT = 8765

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
}

_NO_UNDO_PUSH_PREFIXES = (
    # Read-only inspections
    "scene.inspect_",
    "collection.list",
    "collection.list_objects",
    "material.list",
    "material.inspect_nodes",
    "uv.list_maps",
    "mesh.get_vertex_data",
    "mesh.list_groups",
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
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
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

class BlenderRpcServer:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.server_thread = None
        self.running = False
        self.command_registry = {}
        
        # Queue for results from main thread
        self.result_queues = {}  # request_id -> Queue

    def register_handler(self, cmd: str, handler_func):
        """Register a function to handle a specific command."""
        self.command_registry[cmd] = handler_func

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
            except:
                pass
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
                        message = json.loads(data.decode('utf-8'))
                        response = self._process_request(message)
                        
                        response_data = json.dumps(response).encode('utf-8')
                        send_msg(conn, response_data)
                        
                    except json.JSONDecodeError:
                        err = {"status": "error", "error": "Invalid JSON"}
                        send_msg(conn, json.dumps(err).encode('utf-8'))
                        
                except Exception as e:
                    print(f"[BlenderRpc] Client handler error: {e}")
                    break

    def _process_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        request_id = message.get("request_id")
        cmd = message.get("cmd")
        args = message.get("args", {})

        if not request_id or not cmd:
            return {"status": "error", "error": "Missing request_id or cmd", "request_id": request_id}

        print(f"[BlenderRpc] Received cmd: {cmd}")

        if cmd == "ping":
            return {
                "request_id": request_id,
                "status": "ok",
                "result": {"version": bpy.app.version_string if bpy else "Mock Blender"}
            }

        # Dispatch to Main Thread via Timer
        result_queue = queue.Queue()
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
            # Timeout after 30 seconds (increased for heavy renders)
            response_payload = result_queue.get(timeout=30.0)
        except queue.Empty:
            response_payload = {"status": "error", "error": "Command timed out"}
        
        del self.result_queues[request_id]
        
        return {
            "request_id": request_id,
            **response_payload
        }

# Singleton instance
rpc_server = BlenderRpcServer()
