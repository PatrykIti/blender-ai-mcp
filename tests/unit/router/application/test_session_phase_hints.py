"""Tests for coarse router phase hints."""

from server.router.application.session_phase_hints import (
    BUILD_PHASE_HINT,
    INSPECT_VALIDATE_PHASE_HINT,
    PLANNING_PHASE_HINT,
    derive_phase_hint_from_router_result,
)


def test_phase_hints_default_to_planning_for_non_ready_states():
    """Router non-ready states should keep the session in planning."""

    assert derive_phase_hint_from_router_result({"status": "needs_input"}) == PLANNING_PHASE_HINT
    assert derive_phase_hint_from_router_result({"status": "no_match"}) == PLANNING_PHASE_HINT
    assert derive_phase_hint_from_router_result({"status": "error"}) == PLANNING_PHASE_HINT


def test_phase_hints_use_build_for_ready_router_results():
    """Ready router results should move the guided surface into build."""

    assert derive_phase_hint_from_router_result({"status": "ready"}) == BUILD_PHASE_HINT


def test_phase_hints_allow_explicit_inspection_handoffs():
    """Inspection recommendation should override other coarse status mapping."""

    assert (
        derive_phase_hint_from_router_result({"status": "ready", "inspection_recommended": True})
        == INSPECT_VALIDATE_PHASE_HINT
    )
