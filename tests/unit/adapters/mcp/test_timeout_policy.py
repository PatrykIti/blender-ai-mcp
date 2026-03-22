"""Tests for platform timeout policy and configuration."""

from server.adapters.mcp.factory import build_server
from server.infrastructure.config import Config


def test_timeout_config_defaults_are_valid():
    """Default timeout configuration should satisfy the boundary hierarchy."""

    config = Config()

    assert config.MCP_TOOL_TIMEOUT_SECONDS == 30.0
    assert config.MCP_TASK_TIMEOUT_SECONDS == 300.0
    assert config.RPC_TIMEOUT_SECONDS == 30.0
    assert config.ADDON_EXECUTION_TIMEOUT_SECONDS == 30.0


def test_timeout_config_rejects_invalid_hierarchy():
    """Invalid timeout hierarchies should fail fast during config validation."""

    try:
        Config(RPC_TIMEOUT_SECONDS=10.0, ADDON_EXECUTION_TIMEOUT_SECONDS=20.0)
    except Exception as exc:
        assert "RPC_TIMEOUT_SECONDS must be >=" in str(exc)
    else:
        raise AssertionError("Expected invalid timeout hierarchy to fail")


def test_factory_attaches_timeout_policy_to_server():
    """Factory should attach the timeout policy deterministically to the built surface."""

    server = build_server("legacy-flat")

    assert server._bam_timeout_policy.tool_timeout_seconds == 30.0
    assert server._bam_timeout_policy.rpc_timeout_seconds == 30.0
