"""
Tests for SemanticWorkflowMatcher.

TASK-046-3
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Optional

from server.router.application.matcher.semantic_workflow_matcher import (
    SemanticWorkflowMatcher,
    MatchResult,
)
from server.router.infrastructure.config import RouterConfig


class TestMatchResult:
    """Tests for MatchResult dataclass."""

    def test_is_match_with_workflow(self):
        """Test is_match returns True when workflow matched."""
        result = MatchResult(
            workflow_name="phone_workflow",
            confidence=0.85,
            match_type="semantic",
        )

        assert result.is_match() is True

    def test_is_match_with_none_workflow(self):
        """Test is_match returns False when no workflow."""
        result = MatchResult(match_type="none")

        assert result.is_match() is False

    def test_is_exact(self):
        """Test is_exact returns True for exact matches."""
        result = MatchResult(
            workflow_name="phone_workflow",
            match_type="exact",
            confidence=1.0,
        )

        assert result.is_exact() is True

    def test_is_generalized(self):
        """Test is_generalized returns True for generalized matches."""
        result = MatchResult(
            workflow_name="table_workflow",
            match_type="generalized",
            confidence=0.6,
            similar_workflows=[("table_workflow", 0.72), ("tower_workflow", 0.45)],
        )

        assert result.is_generalized() is True

    def test_to_dict(self):
        """Test to_dict conversion."""
        result = MatchResult(
            workflow_name="phone_workflow",
            confidence=0.85,
            match_type="semantic",
        )

        d = result.to_dict()

        assert d["workflow_name"] == "phone_workflow"
        assert d["confidence"] == 0.85
        assert d["match_type"] == "semantic"


class TestSemanticWorkflowMatcher:
    """Tests for SemanticWorkflowMatcher."""

    @pytest.fixture
    def config(self):
        """Create test config."""
        return RouterConfig(
            workflow_similarity_threshold=0.5,
            generalization_threshold=0.3,
            enable_generalization=True,
        )

    @pytest.fixture
    def mock_registry(self):
        """Create mock workflow registry."""
        registry = MagicMock()

        # Setup get_all_workflows
        registry.get_all_workflows.return_value = ["phone_workflow", "table_workflow"]

        # Setup get_workflow
        phone = MagicMock()
        phone.sample_prompts = ["create a phone"]
        phone.trigger_keywords = ["phone", "smartphone"]
        phone.description = "Phone workflow"

        table = MagicMock()
        table.sample_prompts = ["create a table"]
        table.trigger_keywords = ["table", "desk"]
        table.description = "Table workflow"

        registry.get_workflow.side_effect = lambda name: {
            "phone_workflow": phone,
            "table_workflow": table,
        }.get(name)

        registry.get_definition.return_value = None
        registry.find_by_keywords.return_value = None
        registry.find_by_pattern.return_value = None

        return registry

    @pytest.fixture
    def matcher(self, config, mock_registry):
        """Create matcher with mock registry."""
        matcher = SemanticWorkflowMatcher(config=config)

        # Patch classifier to avoid loading model
        with patch.object(matcher._classifier, 'load_workflow_embeddings'):
            matcher.initialize(mock_registry)

        return matcher

    def test_init(self, config):
        """Test matcher initialization."""
        matcher = SemanticWorkflowMatcher(config=config)

        assert not matcher.is_initialized()

    def test_initialize(self, matcher):
        """Test initialize sets up matcher."""
        assert matcher.is_initialized()

    def test_match_not_initialized(self, config):
        """Test match when not initialized returns error."""
        matcher = SemanticWorkflowMatcher(config=config)

        result = matcher.match("create a phone")

        assert result.match_type == "error"
        assert "error" in result.metadata

    def test_match_exact_keyword(self, matcher, mock_registry):
        """Test exact keyword match."""
        mock_registry.find_by_keywords.return_value = "phone_workflow"

        result = matcher.match("create a phone")

        assert result.workflow_name == "phone_workflow"
        assert result.confidence == 1.0
        assert result.match_type == "exact"

    def test_match_by_pattern(self, matcher, mock_registry):
        """Test pattern-based match."""
        mock_registry.find_by_keywords.return_value = None
        mock_registry.find_by_pattern.return_value = "tower_workflow"

        context = {"detected_pattern": "tower_like"}
        result = matcher.match("some prompt", context=context)

        assert result.workflow_name == "tower_workflow"
        assert result.confidence == 0.95
        assert result.match_type == "exact"

    def test_match_no_match(self, matcher, mock_registry):
        """Test when no match found."""
        mock_registry.find_by_keywords.return_value = None

        # Patch classifier to return no results
        with patch.object(matcher._classifier, 'find_best_match', return_value=None):
            with patch.object(matcher._classifier, 'get_generalization_candidates', return_value=[]):
                result = matcher.match("create something unknown")

        assert result.match_type == "none"
        assert result.workflow_name is None

    def test_match_semantic(self, matcher, mock_registry):
        """Test semantic similarity match."""
        mock_registry.find_by_keywords.return_value = None

        # Patch classifier to return semantic match
        with patch.object(
            matcher._classifier,
            'find_best_match',
            return_value=("phone_workflow", 0.75)
        ):
            result = matcher.match("make a mobile device")

        assert result.workflow_name == "phone_workflow"
        assert result.confidence == 0.75
        assert result.match_type == "semantic"

    def test_match_generalized(self, matcher, mock_registry):
        """Test generalized match from similar workflows."""
        mock_registry.find_by_keywords.return_value = None

        # Patch classifier - no semantic match but generalization candidates
        with patch.object(matcher._classifier, 'find_best_match', return_value=None):
            with patch.object(
                matcher._classifier,
                'get_generalization_candidates',
                return_value=[("table_workflow", 0.72), ("tower_workflow", 0.45)],
            ):
                result = matcher.match("create a chair")

        assert result.match_type == "generalized"
        assert result.workflow_name == "table_workflow"
        # Generalized confidence is reduced
        assert result.confidence == 0.72 * 0.8
        assert len(result.similar_workflows) == 2

    def test_find_similar(self, matcher):
        """Test find_similar method."""
        with patch.object(
            matcher._classifier,
            'find_similar',
            return_value=[("phone_workflow", 0.8), ("table_workflow", 0.5)],
        ):
            results = matcher.find_similar("create a device", top_k=2)

        assert len(results) == 2
        assert results[0][0] == "phone_workflow"

    def test_get_match_explanation_exact(self, matcher):
        """Test explanation for exact match."""
        result = MatchResult(
            workflow_name="phone_workflow",
            match_type="exact",
            confidence=1.0,
        )

        explanation = matcher.get_match_explanation(result)

        assert "Exact match" in explanation
        assert "phone_workflow" in explanation

    def test_get_match_explanation_semantic(self, matcher):
        """Test explanation for semantic match."""
        result = MatchResult(
            workflow_name="phone_workflow",
            match_type="semantic",
            confidence=0.85,
        )

        explanation = matcher.get_match_explanation(result)

        assert "Semantic match" in explanation
        assert "85" in explanation  # 85%

    def test_get_match_explanation_generalized(self, matcher):
        """Test explanation for generalized match."""
        result = MatchResult(
            workflow_name="table_workflow",
            match_type="generalized",
            confidence=0.6,
            similar_workflows=[("table_workflow", 0.72), ("tower_workflow", 0.45)],
        )

        explanation = matcher.get_match_explanation(result)

        assert "Generalized" in explanation
        assert "table_workflow" in explanation

    def test_get_match_explanation_none(self, matcher):
        """Test explanation for no match."""
        result = MatchResult(match_type="none")

        explanation = matcher.get_match_explanation(result)

        assert "No matching workflow" in explanation

    def test_get_info(self, matcher):
        """Test get_info returns expected structure."""
        info = matcher.get_info()

        assert "is_initialized" in info
        assert "classifier_info" in info
        assert "config" in info
