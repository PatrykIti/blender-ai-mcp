"""
Tests for KeywordMatcher.

TASK-053-3: Tests for keyword matching extracted from SemanticWorkflowMatcher.
"""

import pytest
from unittest.mock import MagicMock

from server.router.application.matcher.keyword_matcher import KeywordMatcher
from server.router.domain.entities.ensemble import MatcherResult


class TestKeywordMatcher:
    """Tests for KeywordMatcher."""

    @pytest.fixture
    def mock_registry(self):
        """Create mock workflow registry."""
        registry = MagicMock()
        return registry

    @pytest.fixture
    def matcher(self, mock_registry):
        """Create KeywordMatcher instance."""
        return KeywordMatcher(mock_registry, weight=0.40)

    def test_name_property(self, matcher):
        """Test name property returns 'keyword'."""
        assert matcher.name == "keyword"

    def test_weight_property(self, matcher):
        """Test weight property returns configured weight."""
        assert matcher.weight == 0.40

    def test_weight_custom(self, mock_registry):
        """Test custom weight configuration."""
        matcher = KeywordMatcher(mock_registry, weight=0.35)
        assert matcher.weight == 0.35

    def test_match_with_keyword_found(self, matcher, mock_registry):
        """Test match when keyword is found in prompt."""
        # Setup mock to return workflow
        mock_registry.find_by_keywords.return_value = "phone_workflow"

        result = matcher.match("create a smartphone")

        # Verify registry was called
        mock_registry.find_by_keywords.assert_called_once_with("create a smartphone")

        # Verify result
        assert isinstance(result, MatcherResult)
        assert result.matcher_name == "keyword"
        assert result.workflow_name == "phone_workflow"
        assert result.confidence == 1.0  # Exact match = full confidence
        assert result.weight == 0.40
        assert result.metadata["matched_by"] == "keyword"

    def test_match_with_no_keyword_found(self, matcher, mock_registry):
        """Test match when no keyword is found."""
        # Setup mock to return None
        mock_registry.find_by_keywords.return_value = None

        result = matcher.match("some random prompt")

        # Verify registry was called
        mock_registry.find_by_keywords.assert_called_once_with("some random prompt")

        # Verify result
        assert isinstance(result, MatcherResult)
        assert result.matcher_name == "keyword"
        assert result.workflow_name is None
        assert result.confidence == 0.0
        assert result.weight == 0.40

    def test_match_ignores_context(self, matcher, mock_registry):
        """Test that context parameter is not used by keyword matcher."""
        # Setup mock
        mock_registry.find_by_keywords.return_value = "table_workflow"

        # Context should be ignored
        context = {"mode": "EDIT", "selected_objects": ["Cube"]}
        result = matcher.match("create a table", context=context)

        # Verify only prompt was used, context ignored
        mock_registry.find_by_keywords.assert_called_once_with("create a table")
        assert result.workflow_name == "table_workflow"

    def test_weighted_score_calculation(self, matcher, mock_registry):
        """Test weighted score is calculated correctly."""
        mock_registry.find_by_keywords.return_value = "tower_workflow"

        result = matcher.match("create a tower")

        # Weighted score should be confidence × weight
        expected_weighted_score = 1.0 * 0.40
        assert result.weighted_score == pytest.approx(expected_weighted_score)

    def test_weighted_score_no_match(self, matcher, mock_registry):
        """Test weighted score is 0 when no match."""
        mock_registry.find_by_keywords.return_value = None

        result = matcher.match("random text")

        # Weighted score should be 0 (confidence=0.0 × weight=0.40)
        assert result.weighted_score == 0.0

    def test_match_with_polish_prompt(self, matcher, mock_registry):
        """Test match with Polish language prompt."""
        mock_registry.find_by_keywords.return_value = "picnic_table_workflow"

        result = matcher.match("prosty stół")

        mock_registry.find_by_keywords.assert_called_once_with("prosty stół")
        assert result.workflow_name == "picnic_table_workflow"
        assert result.confidence == 1.0

    def test_match_with_multiple_keywords(self, matcher, mock_registry):
        """Test match with prompt containing multiple keywords."""
        mock_registry.find_by_keywords.return_value = "phone_workflow"

        result = matcher.match("create a smartphone with screen")

        # Registry handles keyword matching logic
        mock_registry.find_by_keywords.assert_called_once()
        assert result.workflow_name == "phone_workflow"

    def test_to_dict_result(self, matcher, mock_registry):
        """Test MatcherResult to_dict conversion."""
        mock_registry.find_by_keywords.return_value = "test_workflow"

        result = matcher.match("test prompt")
        data = result.to_dict()

        assert data["matcher_name"] == "keyword"
        assert data["workflow_name"] == "test_workflow"
        assert data["confidence"] == 1.0
        assert data["weight"] == 0.40
        assert data["weighted_score"] == 0.40
        assert "metadata" in data
