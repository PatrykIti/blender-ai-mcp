"""
Tests for EnsembleMatcher.

TASK-053-8: Integration tests for ensemble matcher orchestration.
"""

import pytest
from unittest.mock import MagicMock, patch

from server.router.application.matcher.ensemble_matcher import EnsembleMatcher
from server.router.domain.entities.ensemble import MatcherResult, EnsembleResult, ModifierResult
from server.router.domain.entities.scene_context import SceneContext


class TestEnsembleMatcher:
    """Tests for EnsembleMatcher."""

    @pytest.fixture
    def mock_keyword_matcher(self):
        """Create mock keyword matcher."""
        matcher = MagicMock()
        matcher.name = "keyword"
        matcher.weight = 0.40
        # KeywordMatcher doesn't have is_initialized, so remove the attribute
        del matcher.is_initialized
        return matcher

    @pytest.fixture
    def mock_semantic_matcher(self):
        """Create mock semantic matcher."""
        matcher = MagicMock()
        matcher.name = "semantic"
        matcher.weight = 0.40
        matcher.is_initialized.return_value = False
        return matcher

    @pytest.fixture
    def mock_pattern_matcher(self):
        """Create mock pattern matcher."""
        matcher = MagicMock()
        matcher.name = "pattern"
        matcher.weight = 0.15
        # PatternMatcher doesn't have is_initialized, so remove the attribute
        del matcher.is_initialized
        return matcher

    @pytest.fixture
    def mock_aggregator(self):
        """Create mock aggregator."""
        aggregator = MagicMock()
        return aggregator

    @pytest.fixture
    def ensemble_matcher(self, mock_keyword_matcher, mock_semantic_matcher,
                        mock_pattern_matcher, mock_aggregator):
        """Create EnsembleMatcher instance."""
        return EnsembleMatcher(
            keyword_matcher=mock_keyword_matcher,
            semantic_matcher=mock_semantic_matcher,
            pattern_matcher=mock_pattern_matcher,
            aggregator=mock_aggregator
        )

    def test_is_initialized_false_before_init(self, ensemble_matcher):
        """Test is_initialized returns False before initialize()."""
        assert ensemble_matcher.is_initialized() is False

    def test_initialize(self, ensemble_matcher, mock_semantic_matcher, mock_keyword_matcher):
        """Test initialize calls initialize on matchers that need it."""
        # Setup mocks
        mock_registry = MagicMock()

        ensemble_matcher.initialize(mock_registry)

        # Verify semantic matcher was initialized (it has initialize method and is_initialized)
        mock_semantic_matcher.initialize.assert_called_once_with(mock_registry)

        # Verify is_initialized flag
        assert ensemble_matcher.is_initialized() is True

    def test_initialize_skips_already_initialized(self, ensemble_matcher, mock_semantic_matcher):
        """Test initialize skips matchers already initialized."""
        # Setup semantic matcher as already initialized
        mock_semantic_matcher.is_initialized.return_value = True
        mock_registry = MagicMock()

        ensemble_matcher.initialize(mock_registry)

        # Should NOT call initialize if already initialized
        mock_semantic_matcher.initialize.assert_not_called()
        assert ensemble_matcher.is_initialized() is True

    def test_match_runs_all_matchers(self, ensemble_matcher, mock_keyword_matcher,
                                    mock_semantic_matcher, mock_pattern_matcher,
                                    mock_aggregator):
        """Test match runs all three matchers."""
        # Setup matcher results
        mock_keyword_matcher.match.return_value = MatcherResult("keyword", None, 0.0, 0.40)
        mock_semantic_matcher.match.return_value = MatcherResult("semantic", "table_workflow", 0.84, 0.40)
        mock_pattern_matcher.match.return_value = MatcherResult("pattern", None, 0.0, 0.15)

        # Setup aggregator result
        mock_aggregator.aggregate.return_value = EnsembleResult(
            workflow_name="table_workflow",
            final_score=0.336,
            confidence_level="LOW",
            modifiers={"leg_style": "straight"},
            matcher_contributions={"semantic": 0.336},
            requires_adaptation=True
        )

        result = ensemble_matcher.match("proste nogi")

        # Verify all matchers were called
        mock_keyword_matcher.match.assert_called_once_with("proste nogi", None)
        mock_semantic_matcher.match.assert_called_once_with("proste nogi", None)
        mock_pattern_matcher.match.assert_called_once_with("proste nogi", None)

        # Verify aggregator was called with all results
        mock_aggregator.aggregate.assert_called_once()
        results_arg = mock_aggregator.aggregate.call_args[0][0]
        assert len(results_arg) == 3

        # Verify final result
        assert isinstance(result, EnsembleResult)
        assert result.workflow_name == "table_workflow"

    def test_match_with_context(self, ensemble_matcher, mock_keyword_matcher,
                               mock_semantic_matcher, mock_pattern_matcher,
                               mock_aggregator):
        """Test match passes context to matchers."""
        # Setup context
        context = MagicMock(spec=SceneContext)
        context.to_dict.return_value = {
            "mode": "OBJECT",
            "detected_pattern": "phone_like"
        }

        # Setup matcher results
        mock_keyword_matcher.match.return_value = MatcherResult("keyword", None, 0.0, 0.40)
        mock_semantic_matcher.match.return_value = MatcherResult("semantic", "phone_workflow", 0.80, 0.40)
        mock_pattern_matcher.match.return_value = MatcherResult("pattern", "phone_workflow", 0.95, 0.15)

        # Setup aggregator result
        mock_aggregator.aggregate.return_value = EnsembleResult(
            workflow_name="phone_workflow",
            final_score=0.62,
            confidence_level="MEDIUM",
            modifiers={},
            matcher_contributions={"semantic": 0.32, "pattern": 0.1425},
            requires_adaptation=True
        )

        result = ensemble_matcher.match("create object", context=context)

        # Verify context was converted to dict and passed
        context.to_dict.assert_called_once()
        expected_context_dict = {
            "mode": "OBJECT",
            "detected_pattern": "phone_like"
        }
        mock_pattern_matcher.match.assert_called_once_with("create object", expected_context_dict)

    def test_match_handles_matcher_exception(self, ensemble_matcher, mock_keyword_matcher,
                                            mock_semantic_matcher, mock_pattern_matcher,
                                            mock_aggregator):
        """Test match handles exception from a matcher gracefully."""
        # Setup keyword matcher to raise exception
        mock_keyword_matcher.match.side_effect = Exception("Keyword matcher failed")

        # Other matchers work normally
        mock_semantic_matcher.match.return_value = MatcherResult("semantic", "table_workflow", 0.84, 0.40)
        mock_pattern_matcher.match.return_value = MatcherResult("pattern", None, 0.0, 0.15)

        # Setup aggregator result
        mock_aggregator.aggregate.return_value = EnsembleResult(
            workflow_name="table_workflow",
            final_score=0.336,
            confidence_level="LOW",
            modifiers={},
            matcher_contributions={"semantic": 0.336},
            requires_adaptation=True
        )

        result = ensemble_matcher.match("test prompt")

        # Should still complete successfully
        assert isinstance(result, EnsembleResult)

        # Verify aggregator was called with all results including failed one
        mock_aggregator.aggregate.assert_called_once()
        results_arg = mock_aggregator.aggregate.call_args[0][0]
        assert len(results_arg) == 3

        # Verify failed matcher result
        failed_result = results_arg[0]
        assert failed_result.matcher_name == "keyword"
        assert failed_result.workflow_name is None
        assert failed_result.confidence == 0.0
        assert "error" in failed_result.metadata

    def test_get_info(self, ensemble_matcher, mock_keyword_matcher,
                     mock_semantic_matcher, mock_pattern_matcher):
        """Test get_info returns matcher status."""
        # Setup semantic matcher as initialized
        mock_semantic_matcher.is_initialized.return_value = True

        # Initialize ensemble matcher
        ensemble_matcher._is_initialized = True

        info = ensemble_matcher.get_info()

        assert info["is_initialized"] is True
        assert len(info["matchers"]) == 3

        # Verify matcher info
        keyword_info = next(m for m in info["matchers"] if m["name"] == "keyword")
        assert keyword_info["weight"] == 0.40
        assert keyword_info["initialized"] is True  # Default for matchers without is_initialized

        semantic_info = next(m for m in info["matchers"] if m["name"] == "semantic")
        assert semantic_info["weight"] == 0.40
        assert semantic_info["initialized"] is True

        pattern_info = next(m for m in info["matchers"] if m["name"] == "pattern")
        assert pattern_info["weight"] == 0.15

        # Verify config
        assert "pattern_boost" in info["config"]
        assert "composition_threshold" in info["config"]

    def test_match_aggregator_receives_correct_results(self, ensemble_matcher,
                                                      mock_keyword_matcher,
                                                      mock_semantic_matcher,
                                                      mock_pattern_matcher,
                                                      mock_aggregator):
        """Test aggregator receives results from all matchers."""
        # Setup matcher results
        keyword_result = MatcherResult("keyword", "table_workflow", 1.0, 0.40)
        semantic_result = MatcherResult("semantic", "phone_workflow", 0.85, 0.40)
        pattern_result = MatcherResult("pattern", None, 0.0, 0.15)

        mock_keyword_matcher.match.return_value = keyword_result
        mock_semantic_matcher.match.return_value = semantic_result
        mock_pattern_matcher.match.return_value = pattern_result

        # Setup aggregator result
        mock_aggregator.aggregate.return_value = EnsembleResult(
            workflow_name="table_workflow",
            final_score=0.40,
            confidence_level="MEDIUM",
            modifiers={},
            matcher_contributions={"keyword": 0.40},
            requires_adaptation=True
        )

        ensemble_matcher.match("create table")

        # Verify aggregator was called with correct results and prompt
        mock_aggregator.aggregate.assert_called_once()
        results_arg, prompt_arg = mock_aggregator.aggregate.call_args[0]

        assert len(results_arg) == 3
        assert results_arg[0].matcher_name == "keyword"
        assert results_arg[1].matcher_name == "semantic"
        assert results_arg[2].matcher_name == "pattern"
        assert prompt_arg == "create table"

    def test_match_without_context(self, ensemble_matcher, mock_keyword_matcher,
                                  mock_semantic_matcher, mock_pattern_matcher,
                                  mock_aggregator):
        """Test match works without context parameter."""
        # Setup matcher results
        mock_keyword_matcher.match.return_value = MatcherResult("keyword", None, 0.0, 0.40)
        mock_semantic_matcher.match.return_value = MatcherResult("semantic", "table_workflow", 0.84, 0.40)
        mock_pattern_matcher.match.return_value = MatcherResult("pattern", None, 0.0, 0.15)

        # Setup aggregator result
        mock_aggregator.aggregate.return_value = EnsembleResult(
            workflow_name="table_workflow",
            final_score=0.336,
            confidence_level="LOW",
            modifiers={},
            matcher_contributions={"semantic": 0.336},
            requires_adaptation=True
        )

        result = ensemble_matcher.match("create table")

        # Verify matchers were called with None context
        mock_keyword_matcher.match.assert_called_once_with("create table", None)
        mock_semantic_matcher.match.assert_called_once_with("create table", None)
        mock_pattern_matcher.match.assert_called_once_with("create table", None)

        assert isinstance(result, EnsembleResult)

    def test_match_integration_full_pipeline(self, ensemble_matcher, mock_keyword_matcher,
                                            mock_semantic_matcher, mock_pattern_matcher,
                                            mock_aggregator):
        """Test full integration pipeline."""
        # Setup realistic scenario: semantic wins, modifiers extracted
        mock_keyword_matcher.match.return_value = MatcherResult("keyword", None, 0.0, 0.40)
        mock_semantic_matcher.match.return_value = MatcherResult(
            "semantic",
            "table_workflow",
            0.84,
            0.40,
            metadata={"confidence_level": "HIGH", "source_type": "description"}
        )
        mock_pattern_matcher.match.return_value = MatcherResult("pattern", None, 0.0, 0.15)

        # Setup aggregator result with modifiers
        mock_aggregator.aggregate.return_value = EnsembleResult(
            workflow_name="table_workflow",
            final_score=0.336,
            confidence_level="LOW",
            modifiers={"leg_style": "straight"},
            matcher_contributions={"semantic": 0.336},
            requires_adaptation=True
        )

        result = ensemble_matcher.match("prosty stół z prostymi nogami")

        # Verify full pipeline
        assert result.workflow_name == "table_workflow"
        assert result.modifiers == {"leg_style": "straight"}
        assert result.confidence_level == "LOW"
        assert "semantic" in result.matcher_contributions
