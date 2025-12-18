"""
E2E test fixtures for Router Supervisor.

Provides fixtures for router testing with real Blender connection.
These tests are automatically SKIPPED if Blender is not running.

IMPORTANT: Fixtures are session-scoped to prevent memory exhaustion.
The IntentClassifier loads LaBSE model (~1.8GB RAM), so sharing it
between tests is essential.
"""

import pytest
from typing import Optional

from server.router.application.router import SupervisorRouter
from server.router.application.classifier.intent_classifier import IntentClassifier
from server.router.infrastructure.config import RouterConfig


@pytest.fixture(scope="session")
def router_config():
    """Session-scoped router configuration for E2E tests."""
    return RouterConfig(
        auto_mode_switch=True,
        auto_selection=True,
        clamp_parameters=True,
        enable_overrides=True,
        enable_workflow_expansion=True,
        block_invalid_operations=True,
    )


@pytest.fixture(scope="session")
def shared_classifier(router_config, request):
    """Session-scoped IntentClassifier - LaBSE model loaded once.

    This prevents loading the ~1.8GB model for each test.
    35 tests × 1.8GB = ~63GB without sharing.
    """
    classifier = IntentClassifier(config=router_config)

    # Explicit cleanup when session ends
    def cleanup():
        import gc
        # Clear any cached data
        if hasattr(classifier, '_model'):
            del classifier._model
        gc.collect()

    request.addfinalizer(cleanup)
    return classifier


@pytest.fixture(scope="session")
def router(rpc_client, router_config, shared_classifier, rpc_connection_available):
    """Session-scoped SupervisorRouter with shared classifier.

    Skips all tests if Blender is not available.
    Uses shared IntentClassifier to prevent memory exhaustion.
    """
    if not rpc_connection_available:
        pytest.skip("Blender RPC server not available")

    return SupervisorRouter(
        config=router_config,
        rpc_client=rpc_client,
        classifier=shared_classifier,
    )


@pytest.fixture
def clean_scene(rpc_client, rpc_connection_available):
    """Ensure clean scene before each test.

    Function-scoped to run before/after each test.
    Skips if Blender not available.
    """
    if not rpc_connection_available:
        pytest.skip("Blender RPC server not available")

    def do_cleanup():
        try:
            # Delete all objects (keep_lights_and_cameras=False for full reset)
            rpc_client.send_request("scene.clean_scene", {"keep_lights_and_cameras": False})
        except Exception:
            pass
        try:
            # Purge orphan data-blocks to free memory
            rpc_client.send_request("system.purge_orphans", {})
        except Exception:
            pass  # Method might not exist yet

    do_cleanup()
    yield
    do_cleanup()


@pytest.fixture(scope="session")
def mock_router(router_config, shared_classifier):
    """Session-scoped router without RPC client - for testing router logic only.

    Uses shared classifier to prevent memory exhaustion.
    """
    return SupervisorRouter(
        config=router_config,
        rpc_client=None,
        classifier=shared_classifier,
    )


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
