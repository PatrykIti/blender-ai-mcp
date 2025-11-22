import socket
import threading
import json
import queue
import time
import traceback
from typing import Dict, Any

# Try importing bpy, but allow running outside blender for testing
try:
    import bpy
except ImportError:
    bpy = None

HOST = "127.0.0.1"
PORT = 8765

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
                    # Basic length-prefixed or newline-delimited protocol could be used
                    # For simplicity, let's use a buffer size, but robust parsing is better.
                    # Here we assume one JSON object per send for the prototype.
                    data = conn.recv(4096)
                    if not data:
                        break
                    
                    try:
                        message = json.loads(data.decode('utf-8'))
                        response = self._process_request(message)
                        
                        response_data = json.dumps(response).encode('utf-8')
                        conn.sendall(response_data)
                        
                    except json.JSONDecodeError:
                        err = {"status": "error", "error": "Invalid JSON"}
                        conn.sendall(json.dumps(err).encode('utf-8'))
                        
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
            # Timeout after 10 seconds
            response_payload = result_queue.get(timeout=10.0)
        except queue.Empty:
            response_payload = {"status": "error", "error": "Command timed out"}
        
        del self.result_queues[request_id]
        
        return {
            "request_id": request_id,
            **response_payload
        }

# Singleton instance
rpc_server = BlenderRpcServer()
