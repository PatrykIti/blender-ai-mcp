from __future__ import annotations

from unittest.mock import MagicMock

from server.router.application.triggerer.workflow_triggerer import WorkflowTriggerer
from server.router.domain.entities.pattern import DetectedPattern, PatternType
from server.router.domain.entities.scene_context import ProportionInfo, SceneContext


def test_triggerer_suppresses_heuristics_when_explicit_goal_has_no_workflow_match():
    triggerer = WorkflowTriggerer()
    triggerer._registry = MagicMock()
    triggerer._registry.find_by_keywords.return_value = None

    matched = triggerer.set_explicit_goal("build a low poly squirrel holding an acorn")
    result = triggerer.determine_workflow(
        "modeling_transform_object",
        {"name": "AcornCap", "scale": [1.0, 1.0, 0.06]},
        SceneContext.empty(),
    )

    assert matched is None
    assert result is None


def test_triggerer_keeps_pattern_suggested_workflow_under_explicit_goal_without_match():
    triggerer = WorkflowTriggerer()
    triggerer._registry = MagicMock()
    triggerer._registry.find_by_keywords.return_value = None

    matched = triggerer.set_explicit_goal("build a low poly squirrel holding an acorn")
    result = triggerer.determine_workflow(
        "modeling_transform_object",
        {"name": "AcornCap", "scale": [1.0, 1.0, 0.06]},
        SceneContext.empty(),
        DetectedPattern(
            pattern_type=PatternType.PHONE_LIKE,
            confidence=0.95,
            suggested_workflow="phone_workflow",
            metadata={},
            detection_rules=["strong_pattern_hit"],
        ),
    )

    assert matched is None
    assert result == "phone_workflow"


def test_triggerer_still_uses_explicit_workflow_when_goal_matches():
    triggerer = WorkflowTriggerer()
    triggerer._registry = MagicMock()
    triggerer._registry.find_by_keywords.return_value = "phone_workflow"

    matched = triggerer.set_explicit_goal("create a smartphone")
    result = triggerer.determine_workflow(
        "modeling_transform_object",
        {"name": "PhoneBody", "scale": [1.0, 1.0, 0.05]},
        SceneContext.empty(),
    )

    assert matched == "phone_workflow"
    assert result == "phone_workflow"


def test_triggerer_keeps_flat_scale_heuristic_when_no_explicit_goal_exists():
    triggerer = WorkflowTriggerer()

    result = triggerer.determine_workflow(
        "modeling_transform_object",
        {"name": "Panel", "scale": [1.0, 1.0, 0.05]},
        SceneContext.empty(),
    )

    assert result == "phone_workflow"


def test_triggerer_uses_public_primitive_type_parameter_for_flat_cube_heuristic():
    triggerer = WorkflowTriggerer()
    context = SceneContext(proportions=ProportionInfo(is_flat=True))

    result = triggerer.determine_workflow(
        "modeling_create_primitive",
        {"primitive_type": "CUBE", "name": "PhoneBody"},
        context,
    )

    assert result == "phone_workflow"
