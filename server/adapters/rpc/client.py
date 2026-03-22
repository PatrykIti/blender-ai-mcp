import json
import socket
import struct
import time
from typing import Any, Dict, Optional

from server.domain.interfaces.rpc import IRpcClient
from server.domain.models.rpc import RpcRequest, RpcResponse


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


class RpcClient(IRpcClient):
    def __init__(
        self,
        host: str,
        port: int,
        *,
        rpc_timeout_seconds: float = 30.0,
        addon_execution_timeout_seconds: float = 30.0,
    ):
        self.host = host
        self.port = port
        self.socket = None
        self.timeout = rpc_timeout_seconds
        self.addon_execution_timeout_seconds = addon_execution_timeout_seconds

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
            except Exception:
                pass
            self.socket = None

    def send_request(
        self,
        cmd: str,
        args: Dict[str, Any] = None,
        timeout_seconds: Optional[float] = None,
    ) -> RpcResponse:
        if args is None:
            args = {}

        addon_timeout = timeout_seconds or self.addon_execution_timeout_seconds
        request = RpcRequest(
            cmd=cmd,
            args=args,
            timeout_seconds=addon_timeout,
            deadline_unix_ms=int((time.time() + addon_timeout) * 1000),
        )

        # Auto-reconnect logic
        if not self.socket:
            if not self.connect():
                return RpcResponse(
                    request_id=request.request_id,
                    status="error",
                    error="Could not connect to Blender Addon. Is Blender running with the addon installed?",
                )

        try:
            # Keep the socket boundary explicit per request.
            self.socket.settimeout(self.timeout)

            # Send
            data = request.model_dump_json().encode("utf-8")
            send_msg(self.socket, data)

            # Receive
            response_data = recv_msg(self.socket)
            if not response_data:
                raise ConnectionResetError("Connection closed by server")

            response_dict = json.loads(response_data.decode("utf-8"))
            return RpcResponse(**response_dict)

        except (socket.timeout, ConnectionResetError, BrokenPipeError) as e:
            print(f"Connection lost: {e}")
            self.close()
            return RpcResponse(
                request_id=request.request_id,
                status="error",
                error=f"RPC client timeout after {self.timeout:.1f}s while waiting for '{cmd}'",
                error_code="timeout" if isinstance(e, socket.timeout) else "connection_error",
                error_boundary="rpc_client",
            )
        except Exception as e:
            return RpcResponse(
                request_id=request.request_id,
                status="error",
                error=f"Unexpected error: {str(e)}",
                error_code="unexpected_error",
                error_boundary="rpc_client",
            )

    def launch_background_job(
        self,
        cmd: str,
        args: Optional[Dict[str, Any]] = None,
        *,
        timeout_seconds: Optional[float] = None,
    ) -> RpcResponse:
        """Launch a background-capable addon job through the explicit RPC control plane."""

        return self.send_request(
            "rpc.launch_job",
            {
                "cmd": cmd,
                "args": args or {},
            },
            timeout_seconds=timeout_seconds,
        )

    def get_background_job_status(self, job_id: str) -> RpcResponse:
        """Poll background job status without collecting the final result payload."""

        return self.send_request("rpc.get_job", {"job_id": job_id})

    def cancel_background_job(self, job_id: str) -> RpcResponse:
        """Request cancellation for an existing background addon job."""

        return self.send_request("rpc.cancel_job", {"job_id": job_id})

    def collect_background_job_result(self, job_id: str) -> RpcResponse:
        """Collect the final result payload for a completed background addon job."""

        return self.send_request("rpc.collect_job", {"job_id": job_id})
