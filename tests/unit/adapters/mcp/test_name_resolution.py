"""Tests for public/internal MCP tool name resolution."""

from server.adapters.mcp.dispatcher import ToolDispatcher
from server.adapters.mcp.platform.name_resolution import (
    get_llm_guided_alias_map,
    resolve_canonical_tool_name,
)
from server.adapters.mcp.version_policy import CONTRACT_LINE_LLM_GUIDED_V1, CONTRACT_LINE_LLM_GUIDED_V2


def test_llm_guided_alias_map_resolves_public_names():
    """Public aliases should resolve back to canonical internal tool ids."""

    alias_map = get_llm_guided_alias_map(contract_line=CONTRACT_LINE_LLM_GUIDED_V2)
    legacy_guided_alias_map = get_llm_guided_alias_map(contract_line=CONTRACT_LINE_LLM_GUIDED_V1)

    assert alias_map["check_scene"] == "scene_context"
    assert alias_map["inspect_scene"] == "scene_inspect"
    assert alias_map["browse_workflows"] == "workflow_catalog"
    assert legacy_guided_alias_map["scene_context"] == "scene_context"

    assert resolve_canonical_tool_name("check_scene", contract_line=CONTRACT_LINE_LLM_GUIDED_V2) == "scene_context"
    assert resolve_canonical_tool_name("scene_context", contract_line=CONTRACT_LINE_LLM_GUIDED_V1) == "scene_context"
    assert resolve_canonical_tool_name("workflow_catalog") == "workflow_catalog"


def test_dispatcher_accepts_public_aliases_via_canonical_resolution():
    """Dispatcher execution should tolerate public aliases as input."""

    dispatcher = ToolDispatcher.__new__(ToolDispatcher)
    dispatcher._tool_map = {
        "workflow_catalog": lambda action=None: f"workflow:{action}",
    }

    assert dispatcher.execute("browse_workflows", {"action": "list"}) == "workflow:list"
    assert dispatcher.has_tool("browse_workflows") is True


def test_unknown_public_alias_falls_back_to_deterministic_dispatcher_error():
    """Unknown aliases should not resolve silently to some unrelated internal tool."""

    dispatcher = ToolDispatcher.__new__(ToolDispatcher)
    dispatcher._tool_map = {
        "workflow_catalog": lambda action=None: f"workflow:{action}",
    }

    assert resolve_canonical_tool_name("unknown_alias") == "unknown_alias"
    assert dispatcher.has_tool("unknown_alias") is False
    assert dispatcher.execute("unknown_alias", {}) == "Error: Tool 'unknown_alias' not found in dispatcher."
