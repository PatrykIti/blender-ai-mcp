"""
Unit tests for MCP Integration Adapter.

Tests the router integration with MCP server tool execution.
"""

import pytest
from unittest.mock import MagicMock, patch
import asyncio

from server.router.adapters.mcp_integration import (
    MCPRouterIntegration,
    RouterMiddleware,
    create_router_integration,
)
from server.router.infrastructure.config import RouterConfig
from server.router.domain.entities.scene_context import (
    SceneContext,
    ObjectInfo,
    TopologyInfo,
)


def run_async(coro):
    """Helper to run async coroutines in sync tests."""
    return asyncio.new_event_loop().run_until_complete(coro)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def integration():
    """Create MCPRouterIntegration instance."""
    return MCPRouterIntegration()


@pytest.fixture
def disabled_integration():
    """Create disabled MCPRouterIntegration instance."""
    return MCPRouterIntegration(enabled=False)


@pytest.fixture
def mock_executor():
    """Create mock async executor."""
    async def executor(tool_name: str, params: dict) -> str:
        return f"Executed {tool_name}"
    return executor


@pytest.fixture
def mock_sync_executor():
    """Create mock sync executor."""
    def executor(tool_name: str, params: dict) -> str:
        return f"Executed {tool_name}"
    return executor


@pytest.fixture
def edit_mode_context():
    """Create edit mode context."""
    return SceneContext(
        mode="EDIT",
        active_object="Cube",
        selected_objects=["Cube"],
        objects=[
            ObjectInfo(
                name="Cube",
                type="MESH",
                dimensions=[2.0, 2.0, 2.0],
                selected=True,
                active=True,
            )
        ],
        topology=TopologyInfo(
            vertices=8,
            edges=12,
            faces=6,
            selected_verts=8,
            selected_edges=12,
            selected_faces=6,
        ),
    )


# ============================================================================
# Initialization Tests
# ============================================================================


class TestMCPRouterIntegrationInit:
    """Tests for MCPRouterIntegration initialization."""

    def test_init_default(self):
        """Test default initialization."""
        integration = MCPRouterIntegration()
        assert integration.router is not None
        assert integration.enabled is True
        assert integration._bypass_tools == set()

    def test_init_custom_config(self):
        """Test initialization with custom config."""
        config = RouterConfig(auto_mode_switch=False)
        integration = MCPRouterIntegration(config=config)
        assert integration.config.auto_mode_switch is False

    def test_init_disabled(self):
        """Test disabled initialization."""
        integration = MCPRouterIntegration(enabled=False)
        assert integration.enabled is False


# ============================================================================
# Enable/Disable Tests
# ============================================================================


class TestEnableDisable:
    """Tests for enable/disable functionality."""

    def test_enable(self, disabled_integration):
        """Test enabling integration."""
        disabled_integration.enable()
        assert disabled_integration.enabled is True

    def test_disable(self, integration):
        """Test disabling integration."""
        integration.disable()
        assert integration.enabled is False


# ============================================================================
# Bypass Tests
# ============================================================================


class TestBypass:
    """Tests for bypass functionality."""

    def test_add_bypass_tool(self, integration):
        """Test adding bypass tool."""
        integration.add_bypass_tool("test_tool")
        assert "test_tool" in integration._bypass_tools

    def test_remove_bypass_tool(self, integration):
        """Test removing bypass tool."""
        integration.add_bypass_tool("test_tool")
        integration.remove_bypass_tool("test_tool")
        assert "test_tool" not in integration._bypass_tools

    def test_should_bypass(self, integration):
        """Test bypass check."""
        integration.add_bypass_tool("bypassed_tool")
        assert integration.should_bypass("bypassed_tool") is True
        assert integration.should_bypass("normal_tool") is False


# ============================================================================
# Async Executor Wrapping Tests
# ============================================================================


class TestAsyncExecutorWrapping:
    """Tests for async executor wrapping."""

    def test_wrap_executor_passthrough_disabled(self, disabled_integration, mock_executor):
        """Test passthrough when integration disabled."""
        wrapped = disabled_integration.wrap_tool_executor(mock_executor)
        result = run_async(wrapped("mesh_extrude_region", {"depth": 0.5}))
        assert result == "Executed mesh_extrude_region"

    def test_wrap_executor_passthrough_bypassed(self, integration, mock_executor):
        """Test passthrough for bypassed tools."""
        integration.add_bypass_tool("mesh_extrude_region")
        wrapped = integration.wrap_tool_executor(mock_executor)
        result = run_async(wrapped("mesh_extrude_region", {"depth": 0.5}))
        assert result == "Executed mesh_extrude_region"

    def test_wrap_executor_routes_through_router(self, integration, mock_executor, edit_mode_context):
        """Test that executor routes through router."""
        with patch.object(integration.router.analyzer, 'analyze', return_value=edit_mode_context):
            wrapped = integration.wrap_tool_executor(mock_executor)
            result = run_async(wrapped("mesh_extrude_region", {"depth": 0.5}))
            # Should execute at least the original tool
            assert "mesh_extrude_region" in result

    def test_wrap_executor_increments_count(self, integration, mock_executor, edit_mode_context):
        """Test execution count increments."""
        with patch.object(integration.router.analyzer, 'analyze', return_value=edit_mode_context):
            wrapped = integration.wrap_tool_executor(mock_executor)
            run_async(wrapped("mesh_extrude_region", {"depth": 0.5}))
            assert integration._execution_count == 1

    def test_wrap_executor_error_fallback(self, integration, mock_executor):
        """Test fallback on router error."""
        # Cause router to fail
        with patch.object(integration.router, 'process_llm_tool_call', side_effect=Exception("Router error")):
            wrapped = integration.wrap_tool_executor(mock_executor)
            result = run_async(wrapped("mesh_extrude_region", {"depth": 0.5}))
            # Should fall back to original execution
            assert result == "Executed mesh_extrude_region"
            assert integration._error_count == 1


# ============================================================================
# Sync Executor Wrapping Tests
# ============================================================================


class TestSyncExecutorWrapping:
    """Tests for sync executor wrapping."""

    def test_wrap_sync_passthrough_disabled(self, disabled_integration, mock_sync_executor):
        """Test passthrough when integration disabled."""
        wrapped = disabled_integration.wrap_sync_executor(mock_sync_executor)
        result = wrapped("mesh_extrude_region", {"depth": 0.5})
        assert result == "Executed mesh_extrude_region"

    def test_wrap_sync_passthrough_bypassed(self, integration, mock_sync_executor):
        """Test passthrough for bypassed tools."""
        integration.add_bypass_tool("mesh_extrude_region")
        wrapped = integration.wrap_sync_executor(mock_sync_executor)
        result = wrapped("mesh_extrude_region", {"depth": 0.5})
        assert result == "Executed mesh_extrude_region"

    def test_wrap_sync_routes_through_router(self, integration, mock_sync_executor, edit_mode_context):
        """Test that sync executor routes through router."""
        with patch.object(integration.router.analyzer, 'analyze', return_value=edit_mode_context):
            wrapped = integration.wrap_sync_executor(mock_sync_executor)
            result = wrapped("mesh_extrude_region", {"depth": 0.5})
            assert "mesh_extrude_region" in result


# ============================================================================
# Result Combining Tests
# ============================================================================


class TestResultCombining:
    """Tests for result combining."""

    def test_combine_empty_results(self, integration):
        """Test combining empty results."""
        result = integration._combine_results([], [])
        assert result == "No operations performed."

    def test_combine_single_result(self, integration):
        """Test combining single result."""
        result = integration._combine_results(
            ["Success"],
            [{"tool": "test_tool"}],
        )
        assert result == "Success"

    def test_combine_multiple_results(self, integration):
        """Test combining multiple results."""
        result = integration._combine_results(
            ["Result 1", "Result 2"],
            [{"tool": "tool_1"}, {"tool": "tool_2"}],
        )
        assert "[Step 1: tool_1]" in result
        assert "[Step 2: tool_2]" in result
        assert "Result 1" in result
        assert "Result 2" in result


# ============================================================================
# Statistics Tests
# ============================================================================


class TestStatistics:
    """Tests for integration statistics."""

    def test_get_stats(self, integration):
        """Test getting stats."""
        stats = integration.get_stats()
        assert "enabled" in stats
        assert "execution_count" in stats
        assert "error_count" in stats
        assert "bypass_tools" in stats
        assert "router_stats" in stats

    def test_reset_stats(self, integration):
        """Test resetting stats."""
        integration._execution_count = 10
        integration._error_count = 5
        integration.reset_stats()
        assert integration._execution_count == 0
        assert integration._error_count == 0


# ============================================================================
# RPC Client Tests
# ============================================================================


class TestRPCClient:
    """Tests for RPC client management."""

    def test_set_rpc_client(self, integration):
        """Test setting RPC client."""
        mock_rpc = MagicMock()
        integration.set_rpc_client(mock_rpc)
        assert integration.router._rpc_client == mock_rpc


# ============================================================================
# RouterMiddleware Tests
# ============================================================================


class TestRouterMiddleware:
    """Tests for RouterMiddleware."""

    def test_init_default(self):
        """Test default initialization."""
        middleware = RouterMiddleware()
        assert middleware.integration is not None

    def test_init_with_integration(self, integration):
        """Test initialization with integration."""
        middleware = RouterMiddleware(integration=integration)
        assert middleware.integration == integration

    def test_call_wraps_handler(self):
        """Test middleware wraps handler."""
        middleware = RouterMiddleware()

        async def handler(tool_name: str, params: dict) -> str:
            return f"Handled {tool_name}"

        wrapped = middleware(handler)
        assert callable(wrapped)


# ============================================================================
# Factory Function Tests
# ============================================================================


class TestFactoryFunction:
    """Tests for create_router_integration factory."""

    def test_create_default(self):
        """Test creating with defaults."""
        integration = create_router_integration()
        assert integration is not None
        assert integration.enabled is True

    def test_create_with_config(self):
        """Test creating with config."""
        config = RouterConfig(auto_mode_switch=False)
        integration = create_router_integration(config=config)
        assert integration.config.auto_mode_switch is False

    def test_create_disabled(self):
        """Test creating disabled."""
        integration = create_router_integration(enabled=False)
        assert integration.enabled is False

    def test_create_with_bypass_tools(self):
        """Test creating with bypass tools."""
        integration = create_router_integration(
            bypass_tools=["tool_1", "tool_2"],
        )
        assert integration.should_bypass("tool_1") is True
        assert integration.should_bypass("tool_2") is True

    def test_create_with_rpc_client(self):
        """Test creating with RPC client."""
        mock_rpc = MagicMock()
        integration = create_router_integration(rpc_client=mock_rpc)
        assert integration.router._rpc_client == mock_rpc


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for MCP integration."""

    def test_full_pipeline_with_corrections(self, integration, edit_mode_context):
        """Test full pipeline with mode correction."""
        # Create context in OBJECT mode (needs correction)
        object_mode_context = SceneContext(
            mode="OBJECT",
            active_object="Cube",
            selected_objects=["Cube"],
            objects=[
                ObjectInfo(
                    name="Cube",
                    type="MESH",
                    dimensions=[2.0, 2.0, 2.0],
                    selected=True,
                    active=True,
                )
            ],
            topology=TopologyInfo(
                vertices=8,
                edges=12,
                faces=6,
                selected_verts=0,
                selected_edges=0,
                selected_faces=0,
            ),
        )

        executed_tools = []

        async def mock_executor(tool_name: str, params: dict) -> str:
            executed_tools.append(tool_name)
            return f"OK: {tool_name}"

        with patch.object(integration.router.analyzer, 'analyze', return_value=object_mode_context):
            wrapped = integration.wrap_tool_executor(mock_executor)
            result = run_async(wrapped("mesh_extrude_region", {"depth": 0.5}))

        # Should have executed mode switch and selection
        assert "system_set_mode" in executed_tools
        assert "mesh_select" in executed_tools

    def test_tool_execution_error_handling(self, integration, edit_mode_context):
        """Test error handling during tool execution."""
        async def failing_executor(tool_name: str, params: dict) -> str:
            raise Exception("Tool failed")

        with patch.object(integration.router.analyzer, 'analyze', return_value=edit_mode_context):
            wrapped = integration.wrap_tool_executor(failing_executor)
            result = run_async(wrapped("mesh_extrude_region", {"depth": 0.5}))

        # Should handle error gracefully
        assert "Error executing" in result
        assert integration._error_count >= 1
