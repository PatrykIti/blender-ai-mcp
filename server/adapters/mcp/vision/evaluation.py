# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Evaluation helpers for vision harness goldens and scorecards."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal, cast

from pydantic import BaseModel, ConfigDict, Field

DirectionExpectation = Literal["improved", "regressed", "no_change", "unspecified"]
ReferenceRelationExpectation = Literal["match", "mismatch", "unspecified"]
EvaluationVerdict = Literal["failed", "weak", "usable", "strong"]

_NO_CHANGE_HINTS = (
    "no meaningful change",
    "no visible change",
    "unchanged",
    "same as before",
    "little change",
)
_IMPROVEMENT_HINTS = (
    "closer",
    "improved",
    "better",
    "matches the reference",
    "matching the reference",
    "moves toward",
    "positive step",
    "more consistent",
    "consistent with the goal",
    "toward the goal",
    "towards the goal",
    "replacing the default cube",
    "replacing the original cube",
    "replacing the cube",
    "more detailed",
    "detailed face",
    "face details refined",
    "full body has been added",
    "body has been added",
    "body added",
    "fuller squirrel model",
    "complete squirrel model",
    "fully detailed",
    "expanded into a full",
    "expanded into a full squirrel",
    "progressing from",
)
_REGRESSION_HINTS = (
    "worse",
    "further",
    "regression",
    "less consistent",
    "does not match",
    "doesn't match",
    "mismatch",
    "diverges",
)
_REFERENCE_MATCH_HINTS = (
    "matches the reference",
    "matching the reference",
    "similar to the reference",
    "consistent with the reference",
)
_REFERENCE_MISMATCH_HINTS = (
    "mismatch",
    "does not match the reference",
    "doesn't match the reference",
    "unlike the reference",
    "different from the reference",
)
_TRUTH_CLAIM_HINTS = (
    "exact dimensions",
    "exact size",
    "exact width",
    "exactly matches",
    "perfectly aligned",
    "perfectly centered",
    "definitely correct",
    "confirmed correct",
    "precise dimensions",
)

_PROGRESSION_GAIN_HINTS = (
    "added",
    "detailed",
    "refined",
    "complete",
    "fully detailed",
    "expanded into",
    "developed",
    "full body",
    "face details",
)

_PROGRESSION_SIMPLE_START_HINTS = (
    "blockout",
    "simple head",
    "simple head blockout",
    "head blockout",
    "only shows a blockout",
    "only shows the head",
    "only shows a simple head",
    "only shows a default cube",
)

_PROGRESSION_ADDED_PART_HINTS = (
    "eyes",
    "nose",
    "snout",
    "ears",
    "body",
    "torso",
    "face",
    "face details",
)


class VisionGoldenExpectations(BaseModel):
    """Stable expectation set for one reusable vision scenario."""

    model_config = ConfigDict(extra="forbid")

    require_goal_summary: bool = True
    expected_direction: DirectionExpectation = "unspecified"
    reference_relation: ReferenceRelationExpectation = "unspecified"
    expected_capture_labels: list[str] = Field(default_factory=list)
    minimum_visible_changes: int = Field(default=0, ge=0)
    minimum_likely_issues: int = Field(default=0, ge=0)
    minimum_recommended_checks: int = Field(default=0, ge=0)
    maximum_likely_issues: int | None = Field(default=None, ge=0)
    maximum_recommended_checks: int | None = Field(default=None, ge=0)
    expected_issue_categories: list[str] = Field(default_factory=list)
    expected_tool_names: list[str] = Field(default_factory=list)
    should_avoid_truth_claims: bool = True


class VisionGoldenScenario(BaseModel):
    """One repository-tracked bundle/reference scenario for scoring."""

    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    description: str | None = None
    goal: str
    target_object: str | None = None
    prompt_hint: str | None = None
    bundle_path: str
    references_path: str | None = None
    expectations: VisionGoldenExpectations


class VisionEvaluationDimension(BaseModel):
    """One scored dimension in the evaluation summary."""

    model_config = ConfigDict(extra="forbid")

    score: float = Field(ge=0.0)
    max_score: float = Field(ge=0.0)
    passed: bool
    detail: str


class VisionEvaluationSummary(BaseModel):
    """Structured evaluation result for one backend run."""

    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    verdict: EvaluationVerdict
    total_score: float = Field(ge=0.0)
    max_score: float = Field(ge=0.0)
    normalized_score: float | None = None
    dimensions: dict[str, VisionEvaluationDimension]


class ResolvedVisionGoldenScenario(BaseModel):
    """Scenario plus resolved fixture paths."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    scenario_path: Path
    scenario: VisionGoldenScenario
    bundle_path: Path
    references_path: Path | None = None


def _score_bool(passed: bool, detail: str, *, max_score: float = 1.0) -> VisionEvaluationDimension:
    return VisionEvaluationDimension(score=max_score if passed else 0.0, max_score=max_score, passed=passed, detail=detail)


def _score_ratio(matched: int, total: int, detail: str) -> VisionEvaluationDimension:
    if total <= 0:
        return VisionEvaluationDimension(score=0.0, max_score=0.0, passed=True, detail=detail)
    score = float(matched) / float(total)
    return VisionEvaluationDimension(score=score, max_score=1.0, passed=matched == total, detail=detail)


def _combined_text(result: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("goal_summary", "reference_match_summary"):
        value = result.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())
    for value in result.get("visible_changes") or []:
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())
    for issue in result.get("likely_issues") or []:
        if isinstance(issue, dict):
            summary = issue.get("summary")
            if isinstance(summary, str) and summary.strip():
                parts.append(summary.strip())
    return " ".join(parts).lower()


def _classify_direction(text: str) -> DirectionExpectation | Literal["unknown"]:
    no_change_hits = sum(1 for hint in _NO_CHANGE_HINTS if hint in text)
    improvement_hits = sum(1 for hint in _IMPROVEMENT_HINTS if hint in text)
    regression_hits = sum(1 for hint in _REGRESSION_HINTS if hint in text)
    if (
        ("replacing" in text or "replaced" in text or "instead of" in text)
        and any(hint in text for hint in ("default cube", "original cube", "simple cube", "cube"))
        and any(hint in text for hint in ("picnic table", "detailed", "more complex", "realistic object", "multiple components"))
        and regression_hits == 0
    ):
        return "improved"
    if (
        regression_hits == 0
        and "after image" in text
        and "before image" in text
        and any(hint in text for hint in _PROGRESSION_GAIN_HINTS)
        and (
            any(hint in text for hint in _PROGRESSION_SIMPLE_START_HINTS)
            or any(hint in text for hint in _PROGRESSION_ADDED_PART_HINTS)
        )
    ):
        return "improved"
    if (
        regression_hits == 0
        and any(hint in text for hint in _PROGRESSION_GAIN_HINTS)
        and (
            any(hint in text for hint in _PROGRESSION_SIMPLE_START_HINTS)
            or any(hint in text for hint in _PROGRESSION_ADDED_PART_HINTS)
        )
    ):
        return "improved"
    if improvement_hits > regression_hits and improvement_hits > 0:
        return "improved"
    if regression_hits > improvement_hits and regression_hits > 0:
        return "regressed"
    if no_change_hits > 0 and improvement_hits == 0 and regression_hits == 0:
        return "no_change"
    return "unknown"


def _classify_reference_relation(text: str) -> ReferenceRelationExpectation | Literal["unknown"]:
    if "reference" in text:
        if any(hint in text for hint in _REFERENCE_MISMATCH_HINTS):
            return "mismatch"
        if any(hint in text for hint in _REFERENCE_MATCH_HINTS) or " matches " in f" {text} " or " consistent " in f" {text} ":
            return "match"
    mismatch_hits = sum(1 for hint in _REFERENCE_MISMATCH_HINTS if hint in text)
    match_hits = sum(1 for hint in _REFERENCE_MATCH_HINTS if hint in text)
    if mismatch_hits > match_hits and mismatch_hits > 0:
        return "mismatch"
    if match_hits > mismatch_hits and match_hits > 0:
        return "match"
    return "unknown"


def _has_truth_claim_risk(text: str) -> bool:
    return any(hint in text for hint in _TRUTH_CLAIM_HINTS)


def load_golden_scenario(path: str | Path) -> ResolvedVisionGoldenScenario:
    """Load one golden scenario file and resolve relative bundle/reference paths."""

    scenario_path = Path(path).resolve()
    payload = json.loads(scenario_path.read_text(encoding="utf-8"))
    scenario = VisionGoldenScenario.model_validate(payload)
    base_dir = scenario_path.parent
    bundle_path = (base_dir / scenario.bundle_path).resolve()
    references_path = (base_dir / scenario.references_path).resolve() if scenario.references_path else None
    return ResolvedVisionGoldenScenario(
        scenario_path=scenario_path,
        scenario=scenario,
        bundle_path=bundle_path,
        references_path=references_path,
    )


def evaluate_vision_result(
    entry: dict[str, Any],
    scenario: VisionGoldenScenario | ResolvedVisionGoldenScenario,
) -> VisionEvaluationSummary:
    """Score one harness result entry against a reusable golden scenario."""

    resolved = scenario if isinstance(scenario, ResolvedVisionGoldenScenario) else None
    scenario_model = resolved.scenario if resolved is not None else cast(VisionGoldenScenario, scenario)
    expectations = scenario_model.expectations

    status = str(entry.get("status") or "error")
    dimensions: dict[str, VisionEvaluationDimension] = {
        "status_success": _score_bool(status == "success", f"status={status}"),
    }

    if status != "success":
        return _finalize_summary(scenario_model.scenario_id, dimensions)

    result = entry.get("result")
    if not isinstance(result, dict):
        dimensions["result_payload"] = _score_bool(False, "missing result payload")
        return _finalize_summary(scenario_model.scenario_id, dimensions)

    goal_summary = result.get("goal_summary")
    goal_present = isinstance(goal_summary, str) and bool(goal_summary.strip())
    if expectations.require_goal_summary:
        dimensions["goal_summary_present"] = _score_bool(goal_present, "goal_summary is present" if goal_present else "goal_summary missing")
    else:
        dimensions["goal_summary_present"] = VisionEvaluationDimension(
            score=0.0,
            max_score=0.0,
            passed=True,
            detail="goal_summary not required for this scenario",
        )

    captures_used = [str(item) for item in result.get("captures_used") or []]
    expected_captures = expectations.expected_capture_labels
    capture_hits = len([label for label in expected_captures if label in captures_used])
    dimensions["captures_used_match"] = _score_ratio(
        capture_hits,
        len(expected_captures),
        f"matched {capture_hits}/{len(expected_captures)} expected captures",
    )

    combined = _combined_text(result)
    classified_direction = _classify_direction(combined)
    if expectations.expected_direction == "unspecified":
        dimensions["direction_match"] = VisionEvaluationDimension(
            score=0.0,
            max_score=0.0,
            passed=True,
            detail="direction not scored for this scenario",
        )
    else:
        dimensions["direction_match"] = _score_bool(
            classified_direction == expectations.expected_direction,
            f"classified={classified_direction}, expected={expectations.expected_direction}",
        )

    classified_reference = _classify_reference_relation(combined)
    if expectations.reference_relation == "unspecified":
        dimensions["reference_relation_match"] = VisionEvaluationDimension(
            score=0.0,
            max_score=0.0,
            passed=True,
            detail="reference relation not scored for this scenario",
        )
    else:
        dimensions["reference_relation_match"] = _score_bool(
            classified_reference == expectations.reference_relation,
            f"classified={classified_reference}, expected={expectations.reference_relation}",
        )

    visible_changes = result.get("visible_changes") or []
    visible_count = len(visible_changes) if isinstance(visible_changes, list) else 0
    dimensions["visible_changes_minimum"] = _score_bool(
        visible_count >= expectations.minimum_visible_changes,
        f"found {visible_count}, required >= {expectations.minimum_visible_changes}",
    )

    likely_issues = result.get("likely_issues") or []
    issue_count = len(likely_issues) if isinstance(likely_issues, list) else 0
    dimensions["likely_issues_minimum"] = _score_bool(
        issue_count >= expectations.minimum_likely_issues,
        f"found {issue_count}, required >= {expectations.minimum_likely_issues}",
    )
    if expectations.maximum_likely_issues is None:
        dimensions["likely_issues_budget"] = VisionEvaluationDimension(
            score=0.0,
            max_score=0.0,
            passed=True,
            detail="likely issue budget not scored for this scenario",
        )
    else:
        dimensions["likely_issues_budget"] = _score_bool(
            issue_count <= expectations.maximum_likely_issues,
            f"found {issue_count}, required <= {expectations.maximum_likely_issues}",
        )

    recommended_checks = result.get("recommended_checks") or []
    check_count = len(recommended_checks) if isinstance(recommended_checks, list) else 0
    dimensions["recommended_checks_minimum"] = _score_bool(
        check_count >= expectations.minimum_recommended_checks,
        f"found {check_count}, required >= {expectations.minimum_recommended_checks}",
    )
    if expectations.maximum_recommended_checks is None:
        dimensions["recommended_checks_budget"] = VisionEvaluationDimension(
            score=0.0,
            max_score=0.0,
            passed=True,
            detail="recommended check budget not scored for this scenario",
        )
    else:
        dimensions["recommended_checks_budget"] = _score_bool(
            check_count <= expectations.maximum_recommended_checks,
            f"found {check_count}, required <= {expectations.maximum_recommended_checks}",
        )

    issue_categories = [
        str(item.get("category"))
        for item in likely_issues
        if isinstance(item, dict) and item.get("category") is not None
    ]
    issue_hits = len([category for category in expectations.expected_issue_categories if category in issue_categories])
    dimensions["issue_category_match"] = _score_ratio(
        issue_hits,
        len(expectations.expected_issue_categories),
        f"matched {issue_hits}/{len(expectations.expected_issue_categories)} expected issue categories",
    )

    tool_names = [
        str(item.get("tool_name"))
        for item in recommended_checks
        if isinstance(item, dict) and item.get("tool_name") is not None
    ]
    tool_hits = len([tool_name for tool_name in expectations.expected_tool_names if tool_name in tool_names])
    dimensions["recommended_tool_match"] = _score_ratio(
        tool_hits,
        len(expectations.expected_tool_names),
        f"matched {tool_hits}/{len(expectations.expected_tool_names)} expected recommended tools",
    )

    if expectations.should_avoid_truth_claims:
        dimensions["truth_claim_safety"] = _score_bool(
            not _has_truth_claim_risk(combined),
            "no risky truth-claim language detected" if not _has_truth_claim_risk(combined) else "truth-claim language detected",
        )
    else:
        dimensions["truth_claim_safety"] = VisionEvaluationDimension(
            score=0.0,
            max_score=0.0,
            passed=True,
            detail="truth-claim safety not scored for this scenario",
        )

    return _finalize_summary(scenario_model.scenario_id, dimensions)


def _finalize_summary(scenario_id: str, dimensions: dict[str, VisionEvaluationDimension]) -> VisionEvaluationSummary:
    total_score = sum(item.score for item in dimensions.values())
    max_score = sum(item.max_score for item in dimensions.values())
    normalized = (total_score / max_score) if max_score > 0 else None

    if normalized is None:
        verdict: EvaluationVerdict = "failed"
    elif normalized >= 0.85:
        verdict = "strong"
    elif normalized >= 0.65:
        verdict = "usable"
    elif normalized >= 0.40:
        verdict = "weak"
    else:
        verdict = "failed"

    return VisionEvaluationSummary(
        scenario_id=scenario_id,
        verdict=verdict,
        total_score=round(total_score, 4),
        max_score=round(max_score, 4),
        normalized_score=round(normalized, 4) if normalized is not None else None,
        dimensions=dimensions,
    )
