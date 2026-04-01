"""Tests for postcondition registry lookup and verification triggers."""

from server.router.application.policy.postcondition_registry import PostconditionRegistry
from server.router.domain.entities.correction_policy import CorrectionCategory


def test_postcondition_registry_covers_high_risk_correction_families():
    """Known high-risk correction categories should resolve to explicit verification requirements."""

    registry = PostconditionRegistry()

    assert registry.requires_verification(CorrectionCategory.PRECONDITION_MODE) is True
    assert registry.requires_verification(CorrectionCategory.PRECONDITION_SELECTION) is True
    assert registry.requires_verification(CorrectionCategory.PARAMETER_CLAMP) is True


def test_postcondition_registry_returns_none_for_non_registered_categories():
    """Non-registered categories should not trigger verification implicitly."""

    registry = PostconditionRegistry()

    assert registry.get(CorrectionCategory.PARAMETER_ALIAS) is None
    assert registry.requires_verification(CorrectionCategory.PARAMETER_ALIAS) is False


def test_postcondition_registry_exposes_stable_verification_keys():
    """Verification requirements should carry stable keys and rationale."""

    registry = PostconditionRegistry()
    requirement = registry.get(CorrectionCategory.PRECONDITION_ACTIVE_OBJECT)

    assert requirement.verification_key == "verify_active_object"
    assert "Active-object corrections" in requirement.reason
