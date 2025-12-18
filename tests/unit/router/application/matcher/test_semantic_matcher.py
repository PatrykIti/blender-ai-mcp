"""
Tests for SemanticMatcher.

TASK-053-4: Tests for semantic matching implementing IMatcher interface.
Note: This is separate from test_semantic_workflow_matcher.py (legacy).
"""

import pytest
from unittest.mock import MagicMock

from server.router.application.matcher.semantic_matcher import SemanticMatcher
from server.router.domain.entities.ensemble import MatcherResult
from server.router.infrastructure.config import RouterConfig


class TestSemanticMatcher:
    """Tests for SemanticMatcher."""

    @pytest.fixture
    def mock_classifier(self):
        """Create mock workflow intent classifier."""
        classifier = MagicMock()
        return classifier

    @pytest.fixture
    def mock_registry(self):
        """Create mock workflow registry."""
        registry = MagicMock()
        registry.get_all_workflows.return_value = ["phone_workflow", "table_workflow"]

        # Setup workflows
        phone = MagicMock()
        phone.sample_prompts = ["create a phone"]

        table = MagicMock()
        table.sample_prompts = ["create a table"]

        registry.get_workflow.side_effect = lambda name: {
            "phone_workflow": phone,
            "table_workflow": table,
        }.get(name)

        return registry

    @pytest.fixture
    def config(self):
        """Create test config."""
        return RouterConfig()

    @pytest.fixture
    def matcher(self, mock_classifier, mock_registry, config):
        """Create SemanticMatcher instance."""
        return SemanticMatcher(mock_classifier, mock_registry, config, weight=0.40)

    def test_name_property(self, matcher):
        """Test name property returns 'semantic'."""
        assert matcher.name == "semantic"

    def test_weight_property(self, matcher):
        """Test weight property returns configured weight."""
        assert matcher.weight == 0.40

    def test_weight_custom(self, mock_classifier, mock_registry, config):
        """Test custom weight configuration."""
        matcher = SemanticMatcher(mock_classifier, mock_registry, config, weight=0.35)
        assert matcher.weight == 0.35

    def test_is_initialized_false_before_init(self, matcher):
        """Test is_initialized returns False before initialize()."""
        assert matcher.is_initialized() is False

    def test_initialize(self, matcher, mock_classifier, mock_registry):
        """Test initialize loads workflow embeddings."""
        matcher.initialize(mock_registry)

        # Verify classifier was called
        mock_classifier.load_workflow_embeddings.assert_called_once()

        # Verify initialized flag
        assert matcher.is_initialized() is True

    def test_match_before_initialize(self, matcher, mock_classifier):
        """Test match returns error when not initialized."""
        result = matcher.match("create a phone")

        assert isinstance(result, MatcherResult)
        assert result.matcher_name == "semantic"
        assert result.workflow_name is None
        assert result.confidence == 0.0
        assert result.metadata["error"] == "Not initialized"

    def test_match_with_high_confidence(self, matcher, mock_classifier, mock_registry):
        """Test match with HIGH confidence result."""
        # Initialize first
        matcher.initialize(mock_registry)

        # Setup classifier to return high confidence match
        mock_classifier.find_best_match_with_confidence.return_value = {
            "workflow_id": "phone_workflow",
            "score": 0.85,
            "confidence_level": "HIGH",
            "source_type": "description",
            "matched_text": "smartphone device",
            "language_detected": "en",
        }

        result = matcher.match("create a smartphone")

        # Verify classifier was called
        mock_classifier.find_best_match_with_confidence.assert_called_once_with("create a smartphone")

        # Verify result
        assert isinstance(result, MatcherResult)
        assert result.matcher_name == "semantic"
        assert result.workflow_name == "phone_workflow"
        assert result.confidence == 0.85
        assert result.weight == 0.40
        assert result.metadata["confidence_level"] == "HIGH"
        assert result.metadata["source_type"] == "description"

    def test_match_with_medium_confidence(self, matcher, mock_classifier, mock_registry):
        """Test match with MEDIUM confidence result."""
        matcher.initialize(mock_registry)

        mock_classifier.find_best_match_with_confidence.return_value = {
            "workflow_id": "table_workflow",
            "score": 0.62,
            "confidence_level": "MEDIUM",
            "source_type": "sample_prompts",
        }

        result = matcher.match("make a desk")

        assert result.workflow_name == "table_workflow"
        assert result.confidence == 0.62
        assert result.metadata["confidence_level"] == "MEDIUM"

    def test_match_with_low_confidence(self, matcher, mock_classifier, mock_registry):
        """Test match with LOW confidence result."""
        matcher.initialize(mock_registry)

        mock_classifier.find_best_match_with_confidence.return_value = {
            "workflow_id": "table_workflow",
            "score": 0.45,
            "confidence_level": "LOW",
        }

        result = matcher.match("build something")

        assert result.workflow_name == "table_workflow"
        assert result.confidence == 0.45
        assert result.metadata["confidence_level"] == "LOW"

    def test_match_with_none_confidence(self, matcher, mock_classifier, mock_registry):
        """Test match with NONE confidence returns no match."""
        matcher.initialize(mock_registry)

        mock_classifier.find_best_match_with_confidence.return_value = {
            "workflow_id": None,
            "score": 0.0,
            "confidence_level": "NONE",
        }

        result = matcher.match("random text")

        assert result.workflow_name is None
        assert result.confidence == 0.0
        assert result.metadata["confidence_level"] == "NONE"

    def test_match_no_workflow_id(self, matcher, mock_classifier, mock_registry):
        """Test match when no workflow_id returned."""
        matcher.initialize(mock_registry)

        mock_classifier.find_best_match_with_confidence.return_value = {
            "workflow_id": None,
            "score": 0.3,
            "confidence_level": "LOW",
        }

        result = matcher.match("something")

        # No workflow_id means no match
        assert result.workflow_name is None
        assert result.confidence == 0.0

    def test_weighted_score_calculation(self, matcher, mock_classifier, mock_registry):
        """Test weighted score is calculated correctly."""
        matcher.initialize(mock_registry)

        mock_classifier.find_best_match_with_confidence.return_value = {
            "workflow_id": "phone_workflow",
            "score": 0.84,
            "confidence_level": "HIGH",
        }

        result = matcher.match("create a phone")

        # Weighted score should be confidence × weight
        expected_weighted_score = 0.84 * 0.40
        assert result.weighted_score == pytest.approx(expected_weighted_score, rel=1e-3)

    def test_match_ignores_context(self, matcher, mock_classifier, mock_registry):
        """Test that context parameter is not used by semantic matcher."""
        matcher.initialize(mock_registry)

        mock_classifier.find_best_match_with_confidence.return_value = {
            "workflow_id": "table_workflow",
            "score": 0.75,
            "confidence_level": "HIGH",
        }

        # Context should be ignored
        context = {"mode": "EDIT", "selected_objects": ["Cube"]}
        result = matcher.match("create a table", context=context)

        # Verify only prompt was used
        mock_classifier.find_best_match_with_confidence.assert_called_once_with("create a table")
        assert result.workflow_name == "table_workflow"

    def test_match_with_polish_prompt(self, matcher, mock_classifier, mock_registry):
        """Test match with Polish language prompt."""
        matcher.initialize(mock_registry)

        mock_classifier.find_best_match_with_confidence.return_value = {
            "workflow_id": "picnic_table_workflow",
            "score": 0.82,
            "confidence_level": "HIGH",
            "language_detected": "pl",
        }

        result = matcher.match("prosty stół")

        assert result.workflow_name == "picnic_table_workflow"
        assert result.confidence == 0.82
        assert result.metadata["language_detected"] == "pl"

    def test_to_dict_result(self, matcher, mock_classifier, mock_registry):
        """Test MatcherResult to_dict conversion."""
        matcher.initialize(mock_registry)

        mock_classifier.find_best_match_with_confidence.return_value = {
            "workflow_id": "test_workflow",
            "score": 0.77,
            "confidence_level": "HIGH",
            "source_type": "description",
        }

        result = matcher.match("test prompt")
        data = result.to_dict()

        assert data["matcher_name"] == "semantic"
        assert data["workflow_name"] == "test_workflow"
        assert data["confidence"] == 0.77
        assert data["weight"] == 0.40
        assert data["weighted_score"] == pytest.approx(0.308, rel=1e-3)
        assert "metadata" in data
