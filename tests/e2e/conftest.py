"""
E2E/Integration test configuration for blender-ai-mcp.

These tests require a running Blender instance with the addon loaded.
They connect via RPC to execute real Blender operations.

To run:
    1. Start Blender with the addon enabled
    2. Run: pytest tests/e2e/ -v

The tests will skip automatically if RPC connection fails.
"""

import os
import time

import pytest
from server.adapters.rpc.client import RpcClient
from server.infrastructure.config import get_config


def _check_rpc_connection():
    """Check if Blender RPC server is available."""
    startup_wait_seconds = float(os.environ.get("E2E_RPC_STARTUP_WAIT_SECONDS", "8.0"))
    retry_interval_seconds = float(os.environ.get("E2E_RPC_RETRY_INTERVAL_SECONDS", "0.5"))
    deadline = time.time() + max(startup_wait_seconds, 0.0)

    while True:
        client = None
        try:
            config = get_config()
            client = RpcClient(
                host=config.BLENDER_RPC_HOST,
                port=config.BLENDER_RPC_PORT,
                rpc_timeout_seconds=2.0,
                addon_execution_timeout_seconds=2.0,
            )
            if client.connect():
                response = client.send_request("ping", {}, timeout_seconds=2.0, rpc_timeout_seconds=2.0)
                if response.status == "ok":
                    return True
        except Exception:
            pass
        finally:
            if client is not None:
                client.close()

        if time.time() >= deadline:
            return False
        time.sleep(retry_interval_seconds)


# Cache the connection check result
_rpc_available = None


def is_rpc_available():
    """Check RPC availability (cached)."""
    global _rpc_available
    if _rpc_available is None:
        _rpc_available = _check_rpc_connection()
    return _rpc_available


@pytest.fixture(scope="session")
def rpc_connection_available():
    """Session-scoped fixture to check RPC availability."""
    return is_rpc_available()


@pytest.fixture(scope="session")
def rpc_client():
    """Session-scoped RPC client shared by all E2E tests.

    This prevents connection exhaustion by reusing a single connection.
    """
    config = get_config()
    client = RpcClient(host=config.BLENDER_RPC_HOST, port=config.BLENDER_RPC_PORT)
    client.connect()
    yield client
    client.close()


def pytest_collection_modifyitems(config, items):
    """Mark E2E tests to skip if RPC is not available."""
    if not is_rpc_available():
        skip_marker = pytest.mark.skip(reason="Blender RPC server not available. Start Blender with addon enabled.")
        for item in items:
            path = str(item.fspath)
            if "/e2e/vision/" in path:
                continue
            if "/e2e/integration/" in path:
                continue
            if "/e2e/" in path:
                item.add_marker(skip_marker)
