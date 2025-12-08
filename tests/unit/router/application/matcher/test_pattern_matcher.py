"""
Tests for PatternMatcher.

TASK-053-5: Tests for pattern matching extracted from SemanticWorkflowMatcher.
"""

import pytest
from unittest.mock import MagicMock

from server.router.application.matcher.pattern_matcher import PatternMatcher
from server.router.domain.entities.ensemble import MatcherResult


class TestPatternMatcher:
    """Tests for PatternMatcher."""

    @pytest.fixture
    def mock_registry(self):
        """Create mock workflow registry."""
        registry = MagicMock()
        return registry

    @pytest.fixture
    def matcher(self, mock_registry):
        """Create PatternMatcher instance."""
        return PatternMatcher(mock_registry, weight=0.15)

    def test_name_property(self, matcher):
        """Test name property returns 'pattern'."""
        assert matcher.name == "pattern"

    def test_weight_property(self, matcher):
        """Test weight property returns configured weight."""
        assert matcher.weight == 0.15

    def test_weight_custom(self, mock_registry):
        """Test custom weight configuration."""
        matcher = PatternMatcher(mock_registry, weight=0.20)
        assert matcher.weight == 0.20

    def test_match_no_context(self, matcher, mock_registry):
        """Test match returns no match when context is None."""
        result = matcher.match("create something")

        assert isinstance(result, MatcherResult)
        assert result.matcher_name == "pattern"
        assert result.workflow_name is None
        assert result.confidence == 0.0
        assert result.weight == 0.15

    def test_match_context_without_pattern(self, matcher, mock_registry):
        """Test match returns no match when context has no detected_pattern."""
        context = {"mode": "OBJECT", "selected_objects": ["Cube"]}
        result = matcher.match("create something", context)

        assert result.workflow_name is None
        assert result.confidence == 0.0

    def test_match_with_phone_pattern(self, matcher, mock_registry):
        """Test match with phone_like pattern."""
        # Setup mock to return workflow for pattern
        mock_registry.find_by_pattern.return_value = "phone_workflow"

        context = {"detected_pattern": "phone_like"}
        result = matcher.match("create object", context)

        # Verify registry was called
        mock_registry.find_by_pattern.assert_called_once_with("phone_like")

        # Verify result
        assert isinstance(result, MatcherResult)
        assert result.matcher_name == "pattern"
        assert result.workflow_name == "phone_workflow"
        assert result.confidence == 0.95  # High confidence for patterns
        assert result.weight == 0.15
        assert result.metadata["matched_by"] == "pattern"
        assert result.metadata["pattern"] == "phone_like"

    def test_match_with_tower_pattern(self, matcher, mock_registry):
        """Test match with tower_like pattern."""
        mock_registry.find_by_pattern.return_value = "tower_workflow"

        context = {"detected_pattern": "tower_like"}
        result = matcher.match("add details", context)

        mock_registry.find_by_pattern.assert_called_once_with("tower_like")
        assert result.workflow_name == "tower_workflow"
        assert result.confidence == 0.95

    def test_match_pattern_detected_but_no_workflow(self, matcher, mock_registry):
        """Test when pattern is detected but no matching workflow."""
        # Registry returns None for unknown pattern
        mock_registry.find_by_pattern.return_value = None

        context = {"detected_pattern": "unknown_pattern"}
        result = matcher.match("create something", context)

        mock_registry.find_by_pattern.assert_called_once_with("unknown_pattern")

        # Should return no match
        assert result.workflow_name is None
        assert result.confidence == 0.0

        # But metadata should indicate pattern was detected
        assert result.metadata["pattern_detected"] == "unknown_pattern"
        assert result.metadata["no_matching_workflow"] is True

    def test_match_ignores_prompt(self, matcher, mock_registry):
        """Test that prompt parameter is not used by pattern matcher."""
        mock_registry.find_by_pattern.return_value = "table_workflow"

        context = {"detected_pattern": "table_like"}

        # Prompt should be ignored
        result = matcher.match("random prompt text here", context)

        # Verify only pattern was used
        mock_registry.find_by_pattern.assert_called_once_with("table_like")
        assert result.workflow_name == "table_workflow"

    def test_weighted_score_calculation(self, matcher, mock_registry):
        """Test weighted score is calculated correctly."""
        mock_registry.find_by_pattern.return_value = "tower_workflow"

        context = {"detected_pattern": "tower_like"}
        result = matcher.match("create tower", context)

        # Weighted score should be confidence × weight
        expected_weighted_score = 0.95 * 0.15
        assert result.weighted_score == pytest.approx(expected_weighted_score, rel=1e-3)

    def test_weighted_score_no_match(self, matcher, mock_registry):
        """Test weighted score is 0 when no match."""
        mock_registry.find_by_pattern.return_value = None

        context = {"detected_pattern": "unknown"}
        result = matcher.match("create", context)

        # Weighted score should be 0 (confidence=0.0 × weight=0.15)
        assert result.weighted_score == 0.0

    def test_match_with_multiple_context_keys(self, matcher, mock_registry):
        """Test match with context containing multiple keys."""
        mock_registry.find_by_pattern.return_value = "phone_workflow"

        # Context with many keys, pattern should be extracted
        context = {
            "mode": "OBJECT",
            "detected_pattern": "phone_like",
            "selected_objects": ["Cube"],
            "topology": {"vertices": 100},
        }

        result = matcher.match("create", context)

        mock_registry.find_by_pattern.assert_called_once_with("phone_like")
        assert result.workflow_name == "phone_workflow"

    def test_to_dict_result(self, matcher, mock_registry):
        """Test MatcherResult to_dict conversion."""
        mock_registry.find_by_pattern.return_value = "test_workflow"

        context = {"detected_pattern": "test_pattern"}
        result = matcher.match("test", context)
        data = result.to_dict()

        assert data["matcher_name"] == "pattern"
        assert data["workflow_name"] == "test_workflow"
        assert data["confidence"] == 0.95
        assert data["weight"] == 0.15
        assert data["weighted_score"] == pytest.approx(0.1425, rel=1e-3)
        assert "metadata" in data
        assert data["metadata"]["pattern"] == "test_pattern"
