"""
Tests for EnsembleAggregator.

TASK-053-7: Tests for weighted consensus aggregation.
"""

import pytest
from unittest.mock import MagicMock

from server.router.application.matcher.ensemble_aggregator import EnsembleAggregator
from server.router.domain.entities.ensemble import MatcherResult, EnsembleResult, ModifierResult


class TestEnsembleAggregator:
    """Tests for EnsembleAggregator."""

    @pytest.fixture
    def mock_modifier_extractor(self):
        """Create mock modifier extractor."""
        extractor = MagicMock()
        # Default: return empty modifiers
        extractor.extract.return_value = ModifierResult(
            modifiers={},
            matched_keywords=[],
            confidence_map={}
        )
        return extractor

    @pytest.fixture
    def aggregator(self, mock_modifier_extractor):
        """Create EnsembleAggregator instance."""
        return EnsembleAggregator(mock_modifier_extractor)

    def test_aggregate_no_matches(self, aggregator):
        """Test aggregate when no matcher returns a match."""
        results = [
            MatcherResult("keyword", None, 0.0, 0.40),
            MatcherResult("semantic", None, 0.0, 0.40),
            MatcherResult("pattern", None, 0.0, 0.15)
        ]

        ensemble = aggregator.aggregate(results, "random text")

        assert isinstance(ensemble, EnsembleResult)
        assert ensemble.workflow_name is None
        assert ensemble.final_score == 0.0
        assert ensemble.confidence_level == "NONE"
        assert ensemble.modifiers == {}
        assert ensemble.matcher_contributions == {}
        assert ensemble.requires_adaptation is False

    def test_aggregate_single_matcher_match(self, aggregator, mock_modifier_extractor):
        """Test aggregate when only one matcher returns a match."""
        # Setup modifier extractor
        mock_modifier_extractor.extract.return_value = ModifierResult(
            modifiers={"leg_style": "straight"},
            matched_keywords=["proste nogi"],
            confidence_map={"proste nogi": 1.0}
        )

        results = [
            MatcherResult("keyword", None, 0.0, 0.40),
            MatcherResult("semantic", "table_workflow", 0.84, 0.40),
            MatcherResult("pattern", None, 0.0, 0.15)
        ]

        ensemble = aggregator.aggregate(results, "proste nogi")

        # Verify result
        assert ensemble.workflow_name == "table_workflow"
        assert ensemble.final_score == pytest.approx(0.336, rel=1e-3)  # 0.84 × 0.40
        assert ensemble.confidence_level == "LOW"  # 0.336 < 0.4
        assert ensemble.modifiers == {"leg_style": "straight"}
        assert ensemble.matcher_contributions == {"semantic": pytest.approx(0.336, rel=1e-3)}
        assert ensemble.requires_adaptation is True  # Not HIGH confidence

    def test_aggregate_multiple_matchers_same_workflow(self, aggregator, mock_modifier_extractor):
        """Test aggregate when multiple matchers agree on same workflow."""
        results = [
            MatcherResult("keyword", "phone_workflow", 1.0, 0.40),
            MatcherResult("semantic", "phone_workflow", 0.85, 0.40),
            MatcherResult("pattern", None, 0.0, 0.15)
        ]

        ensemble = aggregator.aggregate(results, "create phone")

        # Final score = (1.0 × 0.40) + (0.85 × 0.40) = 0.40 + 0.34 = 0.74
        assert ensemble.workflow_name == "phone_workflow"
        assert ensemble.final_score == pytest.approx(0.74, rel=1e-3)
        assert ensemble.confidence_level == "HIGH"  # 0.74 >= 0.7
        assert ensemble.matcher_contributions == {
            "keyword": pytest.approx(0.40, rel=1e-3),
            "semantic": pytest.approx(0.34, rel=1e-3)
        }
        assert ensemble.requires_adaptation is False  # HIGH confidence

    def test_aggregate_multiple_matchers_different_workflows(self, aggregator):
        """Test aggregate when matchers vote for different workflows."""
        results = [
            MatcherResult("keyword", "table_workflow", 1.0, 0.40),
            MatcherResult("semantic", "phone_workflow", 0.85, 0.40),
            MatcherResult("pattern", None, 0.0, 0.15)
        ]

        ensemble = aggregator.aggregate(results, "create something")

        # table_workflow: 1.0 × 0.40 = 0.40
        # phone_workflow: 0.85 × 0.40 = 0.34
        # table_workflow wins
        assert ensemble.workflow_name == "table_workflow"
        assert ensemble.final_score == pytest.approx(0.40, rel=1e-3)

    def test_aggregate_with_pattern_boost(self, aggregator):
        """Test pattern boost multiplier when pattern matcher fires."""
        results = [
            MatcherResult("keyword", None, 0.0, 0.40),
            MatcherResult("semantic", "phone_workflow", 0.50, 0.40),
            MatcherResult("pattern", "phone_workflow", 0.95, 0.15)
        ]

        ensemble = aggregator.aggregate(results, "create phone-like object")

        # Base score: (0.50 × 0.40) + (0.95 × 0.15) = 0.20 + 0.1425 = 0.3425
        # With pattern boost: 0.3425 × 1.3 = 0.44525
        assert ensemble.workflow_name == "phone_workflow"
        assert ensemble.final_score == pytest.approx(0.44525, rel=1e-3)
        assert ensemble.confidence_level == "MEDIUM"  # 0.44525 >= 0.4

    def test_aggregate_pattern_boost_selects_different_workflow(self, aggregator):
        """Test pattern boost can change which workflow wins."""
        results = [
            MatcherResult("keyword", "table_workflow", 1.0, 0.40),
            MatcherResult("semantic", "phone_workflow", 0.70, 0.40),
            MatcherResult("pattern", "phone_workflow", 0.95, 0.15)
        ]

        ensemble = aggregator.aggregate(results, "create phone")

        # table_workflow: 1.0 × 0.40 = 0.40 (no boost)
        # phone_workflow: ((0.70 × 0.40) + (0.95 × 0.15)) × 1.3 = (0.28 + 0.1425) × 1.3 = 0.54925
        # phone_workflow wins due to pattern boost
        assert ensemble.workflow_name == "phone_workflow"
        assert ensemble.final_score == pytest.approx(0.54925, rel=1e-3)

    def test_aggregate_simple_keyword_forces_low_confidence(self, aggregator):
        """Test that 'simple' keyword forces LOW confidence."""
        results = [
            MatcherResult("keyword", "table_workflow", 1.0, 0.40),
            MatcherResult("semantic", "table_workflow", 0.85, 0.40),
            MatcherResult("pattern", None, 0.0, 0.15)
        ]

        # Score is 0.74 (HIGH), but "simple" keyword should force LOW
        ensemble = aggregator.aggregate(results, "simple table")

        assert ensemble.workflow_name == "table_workflow"
        assert ensemble.final_score == pytest.approx(0.74, rel=1e-3)
        assert ensemble.confidence_level == "LOW"  # Forced by "simple"
        assert ensemble.requires_adaptation is True

    def test_aggregate_polish_simple_keyword(self, aggregator):
        """Test Polish 'prosty' keyword forces LOW confidence."""
        results = [
            MatcherResult("keyword", "table_workflow", 1.0, 0.40),
            MatcherResult("semantic", "table_workflow", 0.85, 0.40),
            MatcherResult("pattern", None, 0.0, 0.15)
        ]

        ensemble = aggregator.aggregate(results, "prosty stół")

        assert ensemble.confidence_level == "LOW"  # Forced by "prosty"

    def test_aggregate_composition_mode_activated(self, aggregator):
        """Test composition mode when two workflows have similar scores."""
        results = [
            MatcherResult("keyword", "table_workflow", 1.0, 0.40),
            MatcherResult("semantic", "chair_workflow", 0.95, 0.40),
            MatcherResult("pattern", None, 0.0, 0.15)
        ]

        ensemble = aggregator.aggregate(results, "furniture")

        # table_workflow: 1.0 × 0.40 = 0.40
        # chair_workflow: 0.95 × 0.40 = 0.38
        # Difference: 0.02 < 0.15 (COMPOSITION_THRESHOLD)
        assert ensemble.workflow_name == "table_workflow"  # Wins by small margin
        assert ensemble.composition_mode is True
        assert ensemble.extra_workflows == ["chair_workflow"]

    def test_aggregate_composition_mode_not_activated(self, aggregator):
        """Test composition mode NOT activated when scores differ significantly."""
        results = [
            MatcherResult("keyword", "table_workflow", 1.0, 0.40),
            MatcherResult("semantic", "chair_workflow", 0.50, 0.40),
            MatcherResult("pattern", None, 0.0, 0.15)
        ]

        ensemble = aggregator.aggregate(results, "furniture")

        # table_workflow: 1.0 × 0.40 = 0.40
        # chair_workflow: 0.50 × 0.40 = 0.20
        # Difference: 0.20 > 0.15 (COMPOSITION_THRESHOLD)
        assert ensemble.workflow_name == "table_workflow"
        assert ensemble.composition_mode is False
        assert ensemble.extra_workflows == []

    def test_aggregate_always_extracts_modifiers(self, aggregator, mock_modifier_extractor):
        """Test that modifiers are ALWAYS extracted (bug fix verification)."""
        # Setup modifier extractor
        mock_modifier_extractor.extract.return_value = ModifierResult(
            modifiers={"leg_style": "straight"},
            matched_keywords=["proste nogi"],
            confidence_map={"proste nogi": 1.0}
        )

        results = [
            MatcherResult("keyword", None, 0.0, 0.40),
            MatcherResult("semantic", "table_workflow", 0.84, 0.40),
            MatcherResult("pattern", None, 0.0, 0.15)
        ]

        ensemble = aggregator.aggregate(results, "proste nogi")

        # Verify modifier extractor was called
        mock_modifier_extractor.extract.assert_called_once_with("proste nogi", "table_workflow")

        # Verify modifiers are in result
        assert ensemble.modifiers == {"leg_style": "straight"}

    def test_aggregate_modifiers_extracted_even_when_keyword_loses(self, aggregator, mock_modifier_extractor):
        """Test modifiers extracted when semantic matcher wins (THE BUG FIX)."""
        # Setup modifier extractor
        mock_modifier_extractor.extract.return_value = ModifierResult(
            modifiers={"leg_style": "straight"},
            matched_keywords=["proste nogi"],
            confidence_map={"proste nogi": 1.0}
        )

        results = [
            MatcherResult("keyword", None, 0.0, 0.40),  # Keyword didn't match
            MatcherResult("semantic", "table_workflow", 0.84, 0.40),  # Semantic wins
            MatcherResult("pattern", None, 0.0, 0.15)
        ]

        ensemble = aggregator.aggregate(results, "prosty stół z prostymi nogami")

        # THIS IS THE BUG FIX: Modifiers are extracted even though keyword matcher lost
        assert ensemble.modifiers == {"leg_style": "straight"}
        mock_modifier_extractor.extract.assert_called_once()

    def test_confidence_level_high(self, aggregator):
        """Test HIGH confidence level (score >= 0.7)."""
        level = aggregator._determine_confidence_level(0.75, "create table")
        assert level == "HIGH"

    def test_confidence_level_medium(self, aggregator):
        """Test MEDIUM confidence level (0.4 <= score < 0.7)."""
        level = aggregator._determine_confidence_level(0.55, "create table")
        assert level == "MEDIUM"

    def test_confidence_level_low(self, aggregator):
        """Test LOW confidence level (score < 0.4)."""
        level = aggregator._determine_confidence_level(0.30, "create table")
        assert level == "LOW"

    def test_confidence_level_simple_override(self, aggregator):
        """Test 'simple' keyword overrides score-based level."""
        # High score but "simple" keyword
        level = aggregator._determine_confidence_level(0.85, "simple table")
        assert level == "LOW"

    def test_weighted_score_calculation(self, aggregator):
        """Test weighted score is correctly calculated from contributions."""
        results = [
            MatcherResult("keyword", "table_workflow", 1.0, 0.40),
            MatcherResult("semantic", "table_workflow", 0.60, 0.40),
            MatcherResult("pattern", None, 0.0, 0.15)
        ]

        ensemble = aggregator.aggregate(results, "table")

        # Expected: (1.0 × 0.40) + (0.60 × 0.40) = 0.40 + 0.24 = 0.64
        assert ensemble.final_score == pytest.approx(0.64, rel=1e-3)
        assert ensemble.matcher_contributions == {
            "keyword": pytest.approx(0.40, rel=1e-3),
            "semantic": pytest.approx(0.24, rel=1e-3)
        }

    def test_aggregate_requires_adaptation_flag(self, aggregator):
        """Test requires_adaptation flag is set correctly."""
        # HIGH confidence -> requires_adaptation = False
        results_high = [
            MatcherResult("keyword", "table_workflow", 1.0, 0.40),
            MatcherResult("semantic", "table_workflow", 0.85, 0.40),
            MatcherResult("pattern", None, 0.0, 0.15)
        ]
        ensemble_high = aggregator.aggregate(results_high, "create")
        assert ensemble_high.confidence_level == "HIGH"
        assert ensemble_high.requires_adaptation is False

        # MEDIUM confidence -> requires_adaptation = True
        # Need score >= 0.4 for MEDIUM: 1.0 * 0.40 = 0.40, 0.50 * 0.40 = 0.20, sum = 0.60
        results_medium = [
            MatcherResult("keyword", "table_workflow", 1.0, 0.40),
            MatcherResult("semantic", "table_workflow", 0.50, 0.40),
            MatcherResult("pattern", None, 0.0, 0.15)
        ]
        ensemble_medium = aggregator.aggregate(results_medium, "create")
        # Score: 0.40 + 0.20 = 0.60 (MEDIUM range: 0.4 <= score < 0.7)
        assert ensemble_medium.confidence_level == "MEDIUM"
        assert ensemble_medium.requires_adaptation is True
