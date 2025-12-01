"""
E2E test fixtures for Router Supervisor.

Provides fixtures for router testing with real Blender connection.
These tests are automatically SKIPPED if Blender is not running.
"""

import pytest
from typing import Optional
from unittest.mock import MagicMock

from server.router.application.router import SupervisorRouter
from server.router.infrastructure.config import RouterConfig


@pytest.fixture
def router_config():
    """Default router configuration for E2E tests."""
    return RouterConfig(
        auto_mode_switch=True,
        auto_selection=True,
        clamp_parameters=True,
        enable_overrides=True,
        enable_workflow_expansion=True,
        block_invalid_operations=True,
    )


@pytest.fixture
def router(rpc_client, router_config, rpc_connection_available):
    """SupervisorRouter with real RPC client.

    Skips test if Blender is not available.
    """
    if not rpc_connection_available:
        pytest.skip("Blender RPC server not available")

    return SupervisorRouter(config=router_config, rpc_client=rpc_client)


@pytest.fixture
def clean_scene(rpc_client, rpc_connection_available):
    """Ensure clean scene before each test.

    Skips if Blender not available.
    """
    if not rpc_connection_available:
        pytest.skip("Blender RPC server not available")

    try:
        rpc_client.send_request("scene.clean_scene", {"hard_reset": True})
    except Exception:
        pass  # Ignore if clean fails
    yield
    # Cleanup after test
    try:
        rpc_client.send_request("scene.clean_scene", {"hard_reset": True})
    except Exception:
        pass


@pytest.fixture
def mock_router(router_config):
    """Router without RPC client - for testing router logic only."""
    return SupervisorRouter(config=router_config, rpc_client=None)


def execute_tool(rpc_client, tool_name: str, params: dict) -> str:
    """Execute a tool via RPC and return result."""
    # Map tool name to RPC method
    area = tool_name.split("_")[0]
    method = tool_name.replace(f"{area}_", "", 1)
    rpc_method = f"{area}.{method}"

    try:
        result = rpc_client.send_request(rpc_method, params)
        return result
    except Exception as e:
        return f"Error: {e}"
