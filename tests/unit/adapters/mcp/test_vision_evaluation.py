"""Tests for vision golden loading and scoring."""

from __future__ import annotations

from pathlib import Path

from server.adapters.mcp.vision import evaluate_vision_result, load_golden_scenario


def _fixture(name: str) -> Path:
    return (
        Path(__file__).resolve().parents[3]
        / "fixtures"
        / "vision_eval"
        / name
        / "golden.json"
    )


def test_load_golden_scenario_resolves_relative_bundle_and_reference_paths():
    resolved = load_golden_scenario(_fixture("synthetic_round_cutout"))

    assert resolved.scenario.scenario_id == "synthetic_round_cutout"
    assert resolved.bundle_path.is_absolute()
    assert resolved.bundle_path.name == "bundle.json"
    assert resolved.references_path is not None
    assert resolved.references_path.name == "references.json"


def test_evaluate_vision_result_scores_improvement_scenario():
    scenario = load_golden_scenario(_fixture("synthetic_round_cutout"))
    entry = {
        "backend": "mlx_local",
        "status": "success",
        "result": {
            "goal_summary": "The after image is closer to the rounded cutout target and matches the reference.",
            "reference_match_summary": "The after image is consistent with the reference silhouette.",
            "visible_changes": ["The housing looks rounder than before."],
            "likely_issues": [],
            "recommended_checks": [],
            "captures_used": ["context_wide_before", "context_wide_after", "target_reference"],
        },
    }

    summary = evaluate_vision_result(entry, scenario)

    assert summary.verdict == "strong"
    assert summary.dimensions["direction_match"].passed is True
    assert summary.dimensions["reference_relation_match"].passed is True


def test_evaluate_vision_result_accepts_goal_and_reference_friendly_phrasing():
    scenario = load_golden_scenario(_fixture("synthetic_round_cutout"))
    entry = {
        "backend": "mlx_local",
        "status": "success",
        "result": {
            "goal_summary": "The after image is consistent with the goal and moves toward the rounded cutout target.",
            "reference_match_summary": "The reference image shows a similar shape that matches the after image.",
            "visible_changes": ["Rounded edges are more visible after the change."],
            "likely_issues": [],
            "recommended_checks": [],
            "captures_used": ["context_wide_before", "context_wide_after", "target_reference"],
        },
    }

    summary = evaluate_vision_result(entry, scenario)

    assert summary.dimensions["direction_match"].passed is True
    assert summary.dimensions["reference_relation_match"].passed is True


def test_evaluate_vision_result_scores_no_change_scenario():
    scenario = load_golden_scenario(_fixture("synthetic_no_change"))
    entry = {
        "backend": "mlx_local",
        "status": "success",
        "result": {
            "goal_summary": "No visible change is present between the before and after images.",
            "reference_match_summary": None,
            "visible_changes": [],
            "likely_issues": [],
            "recommended_checks": [],
            "captures_used": ["context_wide_before", "context_wide_after", "target_reference"],
        },
    }

    summary = evaluate_vision_result(entry, scenario)

    assert summary.verdict == "strong"
    assert summary.dimensions["direction_match"].passed is True


def test_evaluate_vision_result_detects_truth_claim_risk():
    scenario = load_golden_scenario(_fixture("synthetic_round_cutout"))
    entry = {
        "backend": "mlx_local",
        "status": "success",
        "result": {
            "goal_summary": "The after image exactly matches the reference with exact dimensions.",
            "reference_match_summary": None,
            "visible_changes": ["The housing looks rounder than before."],
            "likely_issues": [],
            "recommended_checks": [],
            "captures_used": ["context_wide_before", "context_wide_after", "target_reference"],
        },
    }

    summary = evaluate_vision_result(entry, scenario)

    assert summary.dimensions["truth_claim_safety"].passed is False


def test_evaluate_vision_result_fails_error_entry():
    scenario = load_golden_scenario(_fixture("synthetic_round_cutout"))
    entry = {
        "backend": "mlx_local",
        "status": "error",
        "error": "boom",
    }

    summary = evaluate_vision_result(entry, scenario)

    assert summary.verdict == "failed"
    assert summary.dimensions["status_success"].passed is False
