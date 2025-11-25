import socket
import json
import time
import struct
from typing import Optional, Dict, Any
from server.domain.models.rpc import RpcRequest, RpcResponse
from server.domain.interfaces.rpc import IRpcClient

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

class RpcClient(IRpcClient):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = None
        self.timeout = 30.0 # Increased timeout for renders

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
            send_msg(self.socket, data)

            # Receive
            response_data = recv_msg(self.socket)
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