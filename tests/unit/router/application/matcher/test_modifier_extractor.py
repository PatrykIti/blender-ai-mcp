"""
Tests for ModifierExtractor.

TASK-053-6: Tests for modifier extraction implementing IModifierExtractor interface.
"""

import pytest
from unittest.mock import MagicMock

from server.router.application.matcher.modifier_extractor import ModifierExtractor
from server.router.domain.entities.ensemble import ModifierResult


class TestModifierExtractor:
    """Tests for ModifierExtractor."""

    @pytest.fixture
    def mock_registry(self):
        """Create mock workflow registry."""
        registry = MagicMock()
        return registry

    @pytest.fixture
    def extractor(self, mock_registry):
        """Create ModifierExtractor instance."""
        return ModifierExtractor(mock_registry)

    def test_extract_with_no_definition(self, extractor, mock_registry):
        """Test extract returns empty result when no definition found."""
        mock_registry.get_definition.return_value = None

        result = extractor.extract("some prompt", "unknown_workflow")

        assert isinstance(result, ModifierResult)
        assert result.modifiers == {}
        assert result.matched_keywords == []
        assert result.confidence_map == {}

    def test_extract_with_no_modifiers(self, extractor, mock_registry):
        """Test extract with definition that has no modifiers."""
        # Setup definition with defaults only
        definition = MagicMock()
        definition.defaults = {"default_value": 1.0}
        definition.modifiers = None
        mock_registry.get_definition.return_value = definition

        result = extractor.extract("any prompt", "table_workflow")

        # Should return defaults only
        assert result.modifiers == {"default_value": 1.0}
        assert result.matched_keywords == []
        assert result.confidence_map == {}

    def test_extract_with_no_matches(self, extractor, mock_registry):
        """Test extract when prompt doesn't match any modifiers."""
        # Setup definition with modifiers
        definition = MagicMock()
        definition.defaults = {"leg_style": "default"}
        definition.modifiers = {
            "proste nogi": {"leg_style": "straight"},
            "zakrzywione nogi": {"leg_style": "curved"}
        }
        mock_registry.get_definition.return_value = definition

        result = extractor.extract("random text", "table_workflow")

        # Should return defaults only
        assert result.modifiers == {"leg_style": "default"}
        assert result.matched_keywords == []
        assert result.confidence_map == {}

    def test_extract_with_single_match(self, extractor, mock_registry):
        """Test extract with single modifier match."""
        # Setup definition
        definition = MagicMock()
        definition.defaults = {"leg_style": "default", "height": 0.8}
        definition.modifiers = {
            "proste nogi": {"leg_style": "straight"},
            "zakrzywione nogi": {"leg_style": "curved"}
        }
        mock_registry.get_definition.return_value = definition

        result = extractor.extract("proste nogi", "table_workflow")

        # Should return defaults + modifier override
        assert result.modifiers == {"leg_style": "straight", "height": 0.8}
        assert result.matched_keywords == ["proste nogi"]
        assert result.confidence_map == {"proste nogi": 1.0}

    def test_extract_with_multiple_matches(self, extractor, mock_registry):
        """Test extract with multiple modifier matches."""
        # Setup definition
        definition = MagicMock()
        definition.defaults = {"leg_style": "default", "height": 0.8, "surface": "wood"}
        definition.modifiers = {
            "proste nogi": {"leg_style": "straight"},
            "wysoki": {"height": 1.0},
            "metalowy": {"surface": "metal"}
        }
        mock_registry.get_definition.return_value = definition

        result = extractor.extract("wysoki stół z proste nogi", "table_workflow")

        # Should return defaults + all modifier overrides
        assert result.modifiers == {"leg_style": "straight", "height": 1.0, "surface": "wood"}
        assert set(result.matched_keywords) == {"proste nogi", "wysoki"}
        assert result.confidence_map == {"proste nogi": 1.0, "wysoki": 1.0}

    def test_extract_case_insensitive(self, extractor, mock_registry):
        """Test extract is case insensitive."""
        # Setup definition
        definition = MagicMock()
        definition.defaults = {}
        definition.modifiers = {
            "proste nogi": {"leg_style": "straight"}
        }
        mock_registry.get_definition.return_value = definition

        # Test uppercase prompt
        result = extractor.extract("PROSTE NOGI", "table_workflow")

        assert result.modifiers == {"leg_style": "straight"}
        assert result.matched_keywords == ["proste nogi"]

    def test_extract_with_empty_prompt(self, extractor, mock_registry):
        """Test extract with empty prompt."""
        # Setup definition
        definition = MagicMock()
        definition.defaults = {"leg_style": "default"}
        definition.modifiers = {
            "proste nogi": {"leg_style": "straight"}
        }
        mock_registry.get_definition.return_value = definition

        result = extractor.extract("", "table_workflow")

        # Should return defaults only
        assert result.modifiers == {"leg_style": "default"}
        assert result.matched_keywords == []
        assert result.confidence_map == {}

    def test_extract_with_no_defaults(self, extractor, mock_registry):
        """Test extract when definition has no defaults."""
        # Setup definition
        definition = MagicMock()
        definition.defaults = None
        definition.modifiers = {
            "proste nogi": {"leg_style": "straight"}
        }
        mock_registry.get_definition.return_value = definition

        result = extractor.extract("proste nogi", "table_workflow")

        # Should return modifier values only
        assert result.modifiers == {"leg_style": "straight"}
        assert result.matched_keywords == ["proste nogi"]

    def test_extract_modifier_override_defaults(self, extractor, mock_registry):
        """Test that modifier values override defaults."""
        # Setup definition
        definition = MagicMock()
        definition.defaults = {"leg_style": "default", "height": 0.8}
        definition.modifiers = {
            "proste nogi": {"leg_style": "straight", "height": 0.9}
        }
        mock_registry.get_definition.return_value = definition

        result = extractor.extract("proste nogi", "table_workflow")

        # Modifier should override both defaults
        assert result.modifiers == {"leg_style": "straight", "height": 0.9}
        assert result.matched_keywords == ["proste nogi"]

    def test_extract_with_partial_keyword_match(self, extractor, mock_registry):
        """Test extract with keyword as substring."""
        # Setup definition
        definition = MagicMock()
        definition.defaults = {}
        definition.modifiers = {
            "proste": {"leg_style": "straight"}
        }
        mock_registry.get_definition.return_value = definition

        # "proste" is substring of "proste nogi"
        result = extractor.extract("proste nogi", "table_workflow")

        # Should match substring
        assert result.modifiers == {"leg_style": "straight"}
        assert result.matched_keywords == ["proste"]

    def test_extract_preserves_defaults_not_in_modifiers(self, extractor, mock_registry):
        """Test that defaults not overridden by modifiers are preserved."""
        # Setup definition
        definition = MagicMock()
        definition.defaults = {"leg_style": "default", "height": 0.8, "width": 1.0, "depth": 0.6}
        definition.modifiers = {
            "proste nogi": {"leg_style": "straight"}
        }
        mock_registry.get_definition.return_value = definition

        result = extractor.extract("proste nogi", "table_workflow")

        # Should preserve all defaults and override only leg_style
        assert result.modifiers == {
            "leg_style": "straight",
            "height": 0.8,
            "width": 1.0,
            "depth": 0.6
        }

    def test_extract_with_empty_modifiers_dict(self, extractor, mock_registry):
        """Test extract when modifiers dict is empty."""
        # Setup definition
        definition = MagicMock()
        definition.defaults = {"leg_style": "default"}
        definition.modifiers = {}
        mock_registry.get_definition.return_value = definition

        result = extractor.extract("proste nogi", "table_workflow")

        # Should return defaults only
        assert result.modifiers == {"leg_style": "default"}
        assert result.matched_keywords == []
        assert result.confidence_map == {}

    def test_extract_confidence_always_one(self, extractor, mock_registry):
        """Test that confidence is always 1.0 for exact keyword matches."""
        # Setup definition
        definition = MagicMock()
        definition.defaults = {}
        definition.modifiers = {
            "proste nogi": {"leg_style": "straight"},
            "wysoki": {"height": 1.0}
        }
        mock_registry.get_definition.return_value = definition

        result = extractor.extract("proste nogi wysoki", "table_workflow")

        # All matched keywords should have 1.0 confidence
        assert result.confidence_map == {"proste nogi": 1.0, "wysoki": 1.0}

    def test_extract_result_structure(self, extractor, mock_registry):
        """Test that extract returns proper ModifierResult structure."""
        # Setup definition
        definition = MagicMock()
        definition.defaults = {"value": 1}
        definition.modifiers = {"keyword": {"value": 2}}
        mock_registry.get_definition.return_value = definition

        result = extractor.extract("keyword", "test_workflow")

        # Verify result type and structure
        assert isinstance(result, ModifierResult)
        assert hasattr(result, "modifiers")
        assert hasattr(result, "matched_keywords")
        assert hasattr(result, "confidence_map")
        assert isinstance(result.modifiers, dict)
        assert isinstance(result.matched_keywords, list)
        assert isinstance(result.confidence_map, dict)
