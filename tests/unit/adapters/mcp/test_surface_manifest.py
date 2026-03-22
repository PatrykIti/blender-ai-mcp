"""Tests for public surface manifest and naming conventions."""

from server.adapters.mcp.platform.capability_manifest import get_capability_manifest
from server.adapters.mcp.platform.naming_rules import (
    AUDIENCE_LEGACY,
    AUDIENCE_LLM_GUIDED,
    get_public_arg_name,
    get_public_tool_name,
)


def test_capability_manifest_attaches_public_contract_metadata():
    """Every capability manifest entry should carry explicit public contract lines."""

    manifest = {entry.capability_id: entry for entry in get_capability_manifest()}
    router_entry = manifest["router"]

    assert len(router_entry.public_contracts) == 2
    assert {contract.audience for contract in router_entry.public_contracts} == {
        AUDIENCE_LEGACY,
        AUDIENCE_LLM_GUIDED,
    }


def test_public_contracts_keep_explicit_internal_to_public_name_mapping():
    """Public contracts should expose explicit internal->public tool name mappings."""

    manifest = {entry.capability_id: entry for entry in get_capability_manifest()}
    workflow_entry = manifest["workflow_catalog"]

    llm_contract = next(
        contract
        for contract in workflow_entry.public_contracts
        if contract.audience == AUDIENCE_LLM_GUIDED
    )
    assert llm_contract.tool_name_map == (("workflow_catalog", "browse_workflows"),)


def test_naming_rules_are_explicit_even_when_identity_mapped():
    """Naming rules should stay explicit instead of being hidden in wrappers."""

    assert get_public_tool_name("router_set_goal", AUDIENCE_LEGACY) == "router_set_goal"
    assert get_public_tool_name("router_set_goal", AUDIENCE_LLM_GUIDED) == "router_set_goal"
    assert get_public_tool_name("scene_context", AUDIENCE_LLM_GUIDED) == "check_scene"
    assert get_public_arg_name("router_set_goal", "goal", AUDIENCE_LLM_GUIDED) == "goal"
