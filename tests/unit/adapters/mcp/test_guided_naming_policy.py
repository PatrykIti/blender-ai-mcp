"""Tests for guided naming policy decisions on llm-guided."""

from __future__ import annotations

from server.adapters.mcp.guided_naming_policy import evaluate_guided_object_name


def test_guided_naming_policy_allows_semantic_prefixed_body_name():
    decision = evaluate_guided_object_name(
        object_name="Squirrel_Body",
        role="body_core",
        domain_profile="creature",
        current_step="create_primary_masses",
    )

    assert decision.status == "allowed"
    assert decision.reason_code == "semantic_name"
    assert decision.suggested_names == ["Body"]


def test_guided_naming_policy_warns_for_forel_abbreviation_by_default():
    decision = evaluate_guided_object_name(
        object_name="ForeL",
        role="foreleg_pair",
        domain_profile="creature",
        current_step="place_secondary_parts",
    )

    assert decision.status == "warning"
    assert decision.reason_code == "weak_abbreviation"
    assert "ForeLegPair" in decision.message
    assert decision.suggested_names == ["ForeLegPair", "ForeLeg_L", "ForeLeg_R"]


def test_guided_naming_policy_blocks_placeholder_name_for_role_sensitive_path():
    decision = evaluate_guided_object_name(
        object_name="Sphere",
        role="body_core",
        domain_profile="creature",
        current_step="create_primary_masses",
    )

    assert decision.status == "blocked"
    assert decision.reason_code == "placeholder_name"
    assert "Body" in decision.message


def test_guided_naming_policy_can_block_weak_abbreviation_in_strict_mode():
    decision = evaluate_guided_object_name(
        object_name="ForeL",
        role="foreleg_pair",
        domain_profile="creature",
        current_step="place_secondary_parts",
        mode="block_opaque_role_sensitive",
    )

    assert decision.status == "blocked"
    assert decision.reason_code == "opaque_abbreviation"


def test_guided_naming_policy_keeps_building_role_suggestions_domain_specific():
    decision = evaluate_guided_object_name(
        object_name="Tower_WindowCuts",
        role="facade_opening",
        domain_profile="building",
        current_step="place_secondary_parts",
    )

    assert decision.status == "allowed"
    assert decision.canonical_pattern == "WindowOpening_A or DoorOpening_A"
    assert decision.suggested_names == ["WindowOpening_A", "DoorOpening_A"]
