"""Tests for vision golden loading and scoring."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
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


def test_load_golden_scenario_without_references_is_supported():
    resolved = load_golden_scenario(_fixture("default_cube_to_picnic_table"))

    assert resolved.scenario.scenario_id == "default_cube_to_picnic_table"
    assert resolved.bundle_path.is_absolute()
    assert resolved.references_path is None


@pytest.mark.parametrize(
    "fixture_name",
    [
        "squirrel_head_to_face_user_top",
        "squirrel_face_to_body_user_top",
        "squirrel_head_to_body_user_top",
        "squirrel_head_to_face_camera_perspective",
        "squirrel_face_to_body_camera_perspective",
        "squirrel_head_to_body_camera_perspective",
    ],
)
def test_load_golden_scenario_supports_new_real_view_variants(fixture_name: str):
    resolved = load_golden_scenario(_fixture(fixture_name))

    assert resolved.scenario.scenario_id == fixture_name
    assert resolved.bundle_path.is_absolute()
    assert resolved.references_path is None

    bundle = json.loads(resolved.bundle_path.read_text(encoding="utf-8"))
    for item in [*bundle.get("captures_before", []), *bundle.get("captures_after", [])]:
        image_path = resolved.bundle_path.parent / str(item["image_path"])
        assert image_path.exists(), f"missing image fixture: {image_path}"


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


def test_evaluate_vision_result_classifies_real_viewport_replacement_as_improved():
    scenario = load_golden_scenario(_fixture("default_cube_to_picnic_table"))
    entry = {
        "backend": "mlx_local",
        "status": "success",
        "result": {
            "goal_summary": "The after image shows a detailed picnic table model replacing the default cube, indicating a significant object replacement in the scene.",
            "reference_match_summary": None,
            "visible_changes": [
                "A detailed picnic table model is now present in the scene, replacing the original cube."
            ],
            "likely_issues": [],
            "recommended_checks": [],
            "captures_used": ["context_wide_before", "context_wide_after"],
        },
    }

    summary = evaluate_vision_result(entry, scenario)

    assert summary.dimensions["direction_match"].passed is True


def test_evaluate_vision_result_classifies_progressive_face_detailing_as_improved():
    scenario = load_golden_scenario(_fixture("squirrel_head_to_face"))
    entry = {
        "backend": "mlx_local",
        "status": "success",
        "result": {
            "goal_summary": "The after image shows a detailed squirrel face with eyes, snout, and nose, while the before image only shows a blockout with ears.",
            "reference_match_summary": None,
            "visible_changes": [
                "Eyes added to the face",
                "Snout and nose details added",
                "Face details refined from a simple head blockout",
            ],
            "likely_issues": [],
            "recommended_checks": [],
            "captures_used": ["context_wide_before", "context_wide_after"],
        },
    }

    summary = evaluate_vision_result(entry, scenario)

    assert summary.dimensions["direction_match"].passed is True


def test_evaluate_vision_result_classifies_progressive_body_addition_as_improved():
    scenario = load_golden_scenario(_fixture("squirrel_face_to_body"))
    entry = {
        "backend": "mlx_local",
        "status": "success",
        "result": {
            "goal_summary": "The after image shows a complete squirrel model with a head and body, while the before image only shows the head with face details.",
            "reference_match_summary": None,
            "visible_changes": [
                "A full squirrel body has been added below the head.",
                "The head retains its face details including eyes, nose, and ears.",
            ],
            "likely_issues": [],
            "recommended_checks": [],
            "captures_used": ["context_wide_before", "context_wide_after"],
        },
    }

    summary = evaluate_vision_result(entry, scenario)

    assert summary.dimensions["direction_match"].passed is True


def test_evaluate_vision_result_penalizes_extra_issue_and_check_noise_when_budgeted():
    scenario = load_golden_scenario(_fixture("default_cube_to_picnic_table"))
    entry = {
        "backend": "mlx_local",
        "status": "success",
        "result": {
            "goal_summary": "The after image shows a detailed picnic table model replacing the default cube.",
            "reference_match_summary": None,
            "visible_changes": ["A detailed picnic table model is now present in the scene."],
            "likely_issues": [
                {"category": "reported_issue", "summary": "The result may still need review.", "severity": "medium"}
            ],
            "recommended_checks": [
                {"tool_name": "follow_up_check", "reason": "Confirm the object replacement.", "priority": "normal"}
            ],
            "captures_used": ["context_wide_before", "context_wide_after"],
        },
    }

    summary = evaluate_vision_result(entry, scenario)

    assert summary.dimensions["likely_issues_budget"].passed is False
    assert summary.dimensions["recommended_checks_budget"].passed is False
    assert summary.normalized_score is not None
    assert summary.normalized_score < 1.0


def test_evaluate_vision_result_accepts_fuller_squirrel_progression_wording():
    scenario = load_golden_scenario(_fixture("squirrel_head_to_body_user_top"))
    entry = {
        "backend": "mlx_local",
        "status": "success",
        "result": {
            "goal_summary": "The after image shows a fuller squirrel model with face details and body, progressing from a simple head blockout.",
            "reference_match_summary": None,
            "visible_changes": [
                "Added facial details like eyes and nose",
                "Included body elements with limbs and tail",
            ],
            "likely_issues": [],
            "recommended_checks": [],
            "captures_used": ["user_top_before", "user_top_after"],
        },
    }

    summary = evaluate_vision_result(entry, scenario)

    assert summary.dimensions["direction_match"].passed is True


def test_evaluate_vision_result_does_not_treat_retained_face_details_as_no_change():
    scenario = load_golden_scenario(_fixture("squirrel_face_to_body_camera_perspective"))
    entry = {
        "backend": "mlx_local",
        "status": "success",
        "result": {
            "goal_summary": "The after image shows a complete squirrel model with a body added to the previously detailed head, maintaining the same fixed camera perspective.",
            "reference_match_summary": None,
            "visible_changes": [
                "A full body has been added beneath the head, featuring spherical limbs and a rounded torso.",
                "The face details remain unchanged, confirming the progression is from head to full body.",
            ],
            "likely_issues": [],
            "recommended_checks": [],
            "captures_used": ["camera_perspective_before", "camera_perspective_after"],
        },
    }

    summary = evaluate_vision_result(entry, scenario)

    assert summary.dimensions["direction_match"].passed is True


@pytest.mark.parametrize(
    ("fixture_name", "goal_summary", "visible_changes"),
    [
        (
            "squirrel_head_to_face_user_top",
            "The after image shows a more detailed squirrel face with eyes, snout, and nose, while the before image only shows the head blockout with ears from a direct top user view.",
            [
                "Eyes are now visible in the head.",
                "Snout and nose details have been added to the face.",
            ],
        ),
        (
            "squirrel_face_to_body_user_top",
            "The after image shows a fuller squirrel model with body added, while the before image shows only the head with face details from a direct top user view.",
            [
                "A full body has been added below the head.",
                "The head still retains eyes, nose, and ears.",
            ],
        ),
        (
            "squirrel_head_to_body_user_top",
            "The after image shows a complete squirrel model with face details and body, while the before image only shows a simple head blockout from a direct top user view.",
            [
                "Face details are now present on the head.",
                "A full body is now attached beneath the head.",
            ],
        ),
        (
            "squirrel_head_to_face_camera_perspective",
            "The after image shows a more detailed squirrel face with eyes, snout, and nose, while the before image only shows the head blockout with ears from a fixed camera perspective.",
            [
                "Eyes are now visible in the face.",
                "Snout and nose details have been added.",
            ],
        ),
        (
            "squirrel_face_to_body_camera_perspective",
            "The after image shows a fuller squirrel model with body added, while the before image shows only the head with face details from a fixed camera perspective.",
            [
                "A full squirrel body has been added below the head.",
                "The head keeps the visible face details.",
            ],
        ),
        (
            "squirrel_head_to_body_camera_perspective",
            "The after image shows a complete squirrel model with face details and body, while the before image only shows a simple head blockout from a fixed camera perspective.",
            [
                "The face is now more detailed with eyes, snout, and nose.",
                "A full body has been added to complete the squirrel.",
            ],
        ),
    ],
)
def test_evaluate_vision_result_classifies_new_real_view_variants_as_improved(
    fixture_name: str,
    goal_summary: str,
    visible_changes: list[str],
):
    scenario = load_golden_scenario(_fixture(fixture_name))
    entry = {
        "backend": "mlx_local",
        "status": "success",
        "result": {
            "goal_summary": goal_summary,
            "reference_match_summary": None,
            "visible_changes": visible_changes,
            "likely_issues": [],
            "recommended_checks": [],
            "captures_used": [
                *scenario.scenario.expectations.expected_capture_labels,
            ],
        },
    }

    summary = evaluate_vision_result(entry, scenario)

    assert summary.dimensions["direction_match"].passed is True
    assert summary.dimensions["captures_used_match"].passed is True
