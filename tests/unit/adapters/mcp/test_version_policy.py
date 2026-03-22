"""Tests for TASK-091 version policy and contract-line matrix."""

import pytest

from server.adapters.mcp.version_policy import (
    CONTRACT_LINE_LEGACY_V1,
    CONTRACT_LINE_LLM_GUIDED_V1,
    CONTRACT_LINE_LLM_GUIDED_V2,
    get_contract_line_spec,
    get_default_contract_line,
    get_versioned_tool_versions,
    resolve_contract_line,
)


def test_surface_default_contract_lines_are_explicit():
    assert get_default_contract_line("legacy-flat") == CONTRACT_LINE_LEGACY_V1
    assert get_default_contract_line("llm-guided") == CONTRACT_LINE_LLM_GUIDED_V2


def test_contract_line_override_must_match_allowed_surface_matrix():
    assert resolve_contract_line("llm-guided", CONTRACT_LINE_LLM_GUIDED_V1) == CONTRACT_LINE_LLM_GUIDED_V1

    with pytest.raises(ValueError, match="not allowed"):
        resolve_contract_line("legacy-flat", CONTRACT_LINE_LLM_GUIDED_V2)


def test_contract_line_specs_define_version_filter_ranges():
    legacy = get_contract_line_spec(CONTRACT_LINE_LEGACY_V1)
    guided_v2 = get_contract_line_spec(CONTRACT_LINE_LLM_GUIDED_V2)

    assert legacy.version_lt == "2"
    assert guided_v2.version_gte == "2"
    assert guided_v2.version_lt == "3"
    assert guided_v2.include_unversioned is True


def test_versioned_tool_versions_cover_public_evolution_targets():
    assert get_versioned_tool_versions("scene_context") == ("1", "2")
    assert get_versioned_tool_versions("scene_inspect") == ("1", "2")
    assert get_versioned_tool_versions("workflow_catalog") == ("1", "2")
    assert get_versioned_tool_versions("router_set_goal") == ()
