import threading
import time
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from blender_addon.infrastructure.rpc_server import rpc_server
from server.adapters.rpc.client import RpcClient
from server.infrastructure.config import get_config

def test_connection():
    print("--- Starting RPC Integration Test ---")
    
    # 1. Start Server (Mock Mode)
    print("[Test] Starting Server...")
    rpc_server.start()
    time.sleep(1) # Wait for startup

    # 2. Connect Client
    print("[Test] Connecting Client...")
    config = get_config()
    client = RpcClient(host=config.BLENDER_RPC_HOST, port=config.BLENDER_RPC_PORT)
    connected = client.connect()
    
    if not connected:
        print("❌ FAILED: Could not connect to server.")
        rpc_server.stop()
        return

    print("✅ Client Connected")

    # 3. Send Ping
    print("[Test] Sending 'ping'...")
    response = client.send_request("ping")
    
    print(f"[Test] Response: {response}")

    # 4. Verify
    if response.status == "ok" and "version" in response.result:
        print("✅ SUCCESS: Ping response valid.")
    else:
        print("❌ FAILED: Invalid ping response.")

    # 5. Cleanup
    client.close()
    rpc_server.stop()

if __name__ == "__main__":
    test_connection()
