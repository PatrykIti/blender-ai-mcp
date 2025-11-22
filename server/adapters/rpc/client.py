import socket
import json
import time
from typing import Optional, Dict, Any
from server.domain.models.rpc import RpcRequest, RpcResponse

class RpcClient:
    def __init__(self, host="127.0.0.1", port=8765):
        self.host = host
        self.port = port
        self.socket = None
        self.timeout = 10.0

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            return True
        except ConnectionRefusedError:
            self.socket = None
            return False
        except Exception as e:
            print(f"Error connecting to Blender: {e}")
            self.socket = None
            return False

    def close(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

    def send_request(self, cmd: str, args: Dict[str, Any] = None) -> RpcResponse:
        if args is None:
            args = {}

        request = RpcRequest(cmd=cmd, args=args)
        
        # Auto-reconnect logic
        if not self.socket:
            if not self.connect():
                return RpcResponse(
                    request_id=request.request_id,
                    status="error",
                    error="Could not connect to Blender Addon. Is Blender running with the addon installed?"
                )

        try:
            # Send
            data = request.model_dump_json().encode('utf-8')
            self.socket.sendall(data)

            # Receive
            # For prototype, we assume response comes in one chunk or small enough
            # In production, implement buffering/delimiter
            response_data = self.socket.recv(16384) 
            if not response_data:
                 raise ConnectionResetError("Connection closed by server")

            response_dict = json.loads(response_data.decode('utf-8'))
            return RpcResponse(**response_dict)

        except (socket.timeout, ConnectionResetError, BrokenPipeError) as e:
            print(f"Connection lost: {e}")
            self.close()
            return RpcResponse(
                request_id=request.request_id,
                status="error",
                error=f"Connection error: {str(e)}"
            )
        except Exception as e:
            return RpcResponse(
                request_id=request.request_id,
                status="error",
                error=f"Unexpected error: {str(e)}"
            )
