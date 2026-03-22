"""Tests for correction taxonomy and blast-radius classification."""

from server.router.domain.entities.correction_policy import (
    CorrectionCategory,
    CorrectionRisk,
    classify_correction_token,
    classify_firewall_action,
    classify_override_rule,
    get_correction_classification,
)


def test_correction_matrix_classifies_low_risk_deterministic_repairs():
    """Mode switches and alias normalization should stay in the low-risk bucket."""

    assert classify_correction_token("mode_switch:OBJECT->EDIT").category == CorrectionCategory.PRECONDITION_MODE
    assert classify_correction_token("mode_switch:OBJECT->EDIT").risk == CorrectionRisk.LOW
    assert classify_correction_token("alias_width->offset").category == CorrectionCategory.PARAMETER_ALIAS
    assert classify_correction_token("alias_width->offset").auto_safe is True


def test_correction_matrix_classifies_medium_and_high_risk_rewrites():
    """Selection injection, clamping, overrides, and firewall modifications should escalate risk."""

    assert classify_correction_token("auto_select_all").risk == CorrectionRisk.MEDIUM
    assert classify_correction_token("clamp_offset:100->1").risk == CorrectionRisk.MEDIUM
    assert classify_correction_token("override:extrude_for_screen").risk == CorrectionRisk.HIGH
    assert classify_correction_token("workflow:chair:step_1").risk == CorrectionRisk.HIGH
    assert classify_correction_token("firewall_auto_fix").risk == CorrectionRisk.HIGH


def test_firewall_and_override_classifiers_are_explicit():
    """Firewall actions and override rules should map onto explicit correction categories."""

    assert classify_firewall_action("block").category == CorrectionCategory.BLOCK
    assert classify_firewall_action("block").risk == CorrectionRisk.CRITICAL
    assert classify_firewall_action("modify").category == CorrectionCategory.FIREWALL_MODIFICATION
    assert classify_override_rule("tower_override").category == CorrectionCategory.TOOL_OVERRIDE


def test_unknown_correction_tokens_default_to_non_auto_safe_high_risk():
    """Unknown correction signals should fail closed at the taxonomy layer."""

    unknown = classify_correction_token("totally_new_signal")

    assert unknown.category == CorrectionCategory.UNKNOWN
    assert unknown.risk == CorrectionRisk.HIGH
    assert unknown.auto_safe is False
    assert get_correction_classification(CorrectionCategory.UNKNOWN) == unknown
