"""
Unit tests for ParameterResolver.

TASK-055-3
"""

import pytest
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

from server.router.application.resolver.parameter_resolver import ParameterResolver
from server.router.domain.entities.parameter import (
    ParameterResolutionResult,
    ParameterSchema,
    StoredMapping,
    UnresolvedParameter,
)
from server.router.domain.interfaces.i_parameter_resolver import IParameterStore
from server.router.domain.interfaces.i_workflow_intent_classifier import (
    IWorkflowIntentClassifier,
)


class MockClassifier(IWorkflowIntentClassifier):
    """Mock classifier for testing."""

    def __init__(self):
        self._similarity_map: Dict[tuple, float] = {}
        self._default_similarity = 0.3

    def set_similarity(self, text1: str, text2: str, score: float) -> None:
        """Set similarity score for a pair of texts."""
        self._similarity_map[(text1, text2)] = score
        self._similarity_map[(text2, text1)] = score

    def similarity(self, text1: str, text2: str) -> float:
        """Get similarity between texts."""
        # Check exact match
        if (text1, text2) in self._similarity_map:
            return self._similarity_map[(text1, text2)]

        # Check if text2 is in text1 (hint in prompt)
        if text2.lower() in text1.lower():
            return 0.85

        return self._default_similarity

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding."""
        return [0.1] * 768

    def load_workflow_embeddings(self, workflows: Dict[str, Any]) -> None:
        pass

    def find_similar(
        self, prompt: str, top_k: int = 3, threshold: float = 0.0
    ) -> List[tuple]:
        return []

    def find_best_match(
        self, prompt: str, min_confidence: float = 0.5
    ) -> Optional[tuple]:
        return None

    def get_generalization_candidates(
        self, prompt: str, min_similarity: float = 0.3, max_candidates: int = 3
    ) -> List[tuple]:
        return []

    def is_loaded(self) -> bool:
        return True

    def get_info(self) -> Dict[str, Any]:
        return {"mock": True}

    def clear_cache(self) -> bool:
        return True


class MockParameterStore(IParameterStore):
    """Mock parameter store for testing."""

    def __init__(self):
        self._mappings: Dict[str, StoredMapping] = {}
        self._increment_calls = 0

    def add_mapping(
        self,
        context: str,
        parameter_name: str,
        value: Any,
        workflow_name: str,
        similarity: float = 0.9,
    ) -> None:
        """Add a mapping for testing."""
        key = f"{workflow_name}:{parameter_name}"
        self._mappings[key] = StoredMapping(
            context=context,
            value=value,
            similarity=similarity,
            workflow_name=workflow_name,
            parameter_name=parameter_name,
        )

    def find_mapping(
        self,
        prompt: str,
        parameter_name: str,
        workflow_name: str,
        similarity_threshold: float = 0.85,
    ) -> Optional[StoredMapping]:
        """Find mapping."""
        key = f"{workflow_name}:{parameter_name}"
        return self._mappings.get(key)

    def store_mapping(
        self,
        context: str,
        parameter_name: str,
        value: Any,
        workflow_name: str,
    ) -> None:
        """Store mapping."""
        key = f"{workflow_name}:{parameter_name}"
        self._mappings[key] = StoredMapping(
            context=context,
            value=value,
            similarity=1.0,
            workflow_name=workflow_name,
            parameter_name=parameter_name,
        )

    def increment_usage(self, mapping: StoredMapping) -> None:
        """Increment usage."""
        self._increment_calls += 1

    def list_mappings(
        self,
        workflow_name: Optional[str] = None,
        parameter_name: Optional[str] = None,
    ) -> List[StoredMapping]:
        return list(self._mappings.values())

    def delete_mapping(
        self, context: str, parameter_name: str, workflow_name: str
    ) -> bool:
        key = f"{workflow_name}:{parameter_name}"
        if key in self._mappings:
            del self._mappings[key]
            return True
        return False


@pytest.fixture
def mock_classifier():
    """Create mock classifier."""
    return MockClassifier()


@pytest.fixture
def mock_store():
    """Create mock store."""
    return MockParameterStore()


@pytest.fixture
def resolver(mock_classifier, mock_store):
    """Create resolver with mocks."""
    return ParameterResolver(
        classifier=mock_classifier,
        store=mock_store,
        relevance_threshold=0.5,
        memory_threshold=0.85,
    )


@pytest.fixture
def sample_parameters():
    """Create sample parameter schemas."""
    return {
        "leg_angle_left": ParameterSchema(
            name="leg_angle_left",
            type="float",
            range=(-1.57, 1.57),
            default=0.32,
            description="rotation angle for left table legs",
            semantic_hints=["angle", "rotation", "legs", "nogi"],
            group="leg_angles",
        ),
        "leg_angle_right": ParameterSchema(
            name="leg_angle_right",
            type="float",
            range=(-1.57, 1.57),
            default=-0.32,
            description="rotation angle for right table legs",
            semantic_hints=["angle", "rotation", "legs"],
            group="leg_angles",
        ),
        "top_width": ParameterSchema(
            name="top_width",
            type="float",
            range=(0.5, 3.0),
            default=1.5,
            description="width of the table top",
            semantic_hints=["width", "size", "top"],
        ),
    }


class TestParameterResolverTier1:
    """Tests for TIER 1: YAML modifier resolution."""

    def test_yaml_modifier_takes_priority(self, resolver, sample_parameters):
        """Test that YAML modifiers are used first."""
        existing_modifiers = {
            "leg_angle_left": 0,
            "leg_angle_right": 0,
        }

        result = resolver.resolve(
            prompt="table with straight legs",
            workflow_name="picnic_table",
            parameters=sample_parameters,
            existing_modifiers=existing_modifiers,
        )

        assert result.is_complete
        assert result.resolved["leg_angle_left"] == 0
        assert result.resolved["leg_angle_right"] == 0
        assert result.resolution_sources["leg_angle_left"] == "yaml_modifier"
        assert result.resolution_sources["leg_angle_right"] == "yaml_modifier"

    def test_yaml_modifier_overrides_learned(
        self, resolver, mock_store, sample_parameters
    ):
        """Test YAML modifier takes priority over learned mapping."""
        # Add a learned mapping with different value
        mock_store.add_mapping(
            context="straight legs",
            parameter_name="leg_angle_left",
            value=0.5,  # Different from YAML
            workflow_name="picnic_table",
        )

        existing_modifiers = {
            "leg_angle_left": 0,  # YAML value
        }

        result = resolver.resolve(
            prompt="table with straight legs",
            workflow_name="picnic_table",
            parameters={"leg_angle_left": sample_parameters["leg_angle_left"]},
            existing_modifiers=existing_modifiers,
        )

        # Should use YAML value, not learned
        assert result.resolved["leg_angle_left"] == 0
        assert result.resolution_sources["leg_angle_left"] == "yaml_modifier"


class TestParameterResolverTier2:
    """Tests for TIER 2: Learned mapping resolution."""

    def test_learned_mapping_used_when_no_yaml(
        self, resolver, mock_store, sample_parameters
    ):
        """Test learned mapping is used when no YAML modifier exists."""
        mock_store.add_mapping(
            context="prostymi nogami",
            parameter_name="leg_angle_left",
            value=0,
            workflow_name="picnic_table",
            similarity=0.92,
        )

        result = resolver.resolve(
            prompt="stół z prostymi nogami",
            workflow_name="picnic_table",
            parameters={"leg_angle_left": sample_parameters["leg_angle_left"]},
            existing_modifiers={},
        )

        assert result.resolved["leg_angle_left"] == 0
        assert result.resolution_sources["leg_angle_left"] == "learned"

    def test_usage_incremented_when_mapping_used(
        self, resolver, mock_store, sample_parameters
    ):
        """Test usage count is incremented when mapping is reused."""
        mock_store.add_mapping(
            context="test context",
            parameter_name="leg_angle_left",
            value=0,
            workflow_name="picnic_table",
        )

        resolver.resolve(
            prompt="test prompt",
            workflow_name="picnic_table",
            parameters={"leg_angle_left": sample_parameters["leg_angle_left"]},
            existing_modifiers={},
        )

        assert mock_store._increment_calls == 1


class TestParameterResolverTier3:
    """Tests for TIER 3: Unresolved parameters."""

    def test_unresolved_when_prompt_relates_to_param(
        self, resolver, mock_classifier, sample_parameters
    ):
        """Test parameter marked unresolved when prompt relates to it."""
        # Set high similarity for prompt and hint
        mock_classifier.set_similarity(
            "table with angled legs",
            "angle",
            0.8,
        )

        result = resolver.resolve(
            prompt="table with angled legs",
            workflow_name="picnic_table",
            parameters={"leg_angle_left": sample_parameters["leg_angle_left"]},
            existing_modifiers={},
        )

        # Should be unresolved (no YAML, no learned, but relates to param)
        assert result.needs_llm_input
        assert len(result.unresolved) == 1
        assert result.unresolved[0].name == "leg_angle_left"
        assert result.unresolved[0].relevance > 0.5

    def test_default_when_prompt_doesnt_relate(
        self, resolver, mock_classifier, sample_parameters
    ):
        """Test default value used when prompt doesn't mention parameter."""
        # Low similarity for all
        mock_classifier._default_similarity = 0.2

        result = resolver.resolve(
            prompt="simple table",
            workflow_name="picnic_table",
            parameters={"top_width": sample_parameters["top_width"]},
            existing_modifiers={},
        )

        # Should use default (prompt doesn't mention width)
        assert result.is_complete
        assert result.resolved["top_width"] == 1.5
        assert result.resolution_sources["top_width"] == "default"


class TestParameterResolverRelevance:
    """Tests for relevance calculation."""

    def test_relevance_from_description(self, resolver, mock_classifier):
        """Test relevance calculated from description."""
        mock_classifier.set_similarity(
            "adjust the rotation",
            "rotation angle for left table legs",
            0.75,
        )

        schema = ParameterSchema(
            name="angle",
            type="float",
            description="rotation angle for left table legs",
        )

        relevance = resolver.calculate_relevance("adjust the rotation", schema)

        assert relevance >= 0.75

    def test_relevance_from_semantic_hints(self, resolver, mock_classifier):
        """Test relevance calculated from semantic hints."""
        # Set similarity between full prompt and hint
        mock_classifier.set_similarity("stół z nogami", "nogi", 0.9)

        schema = ParameterSchema(
            name="angle",
            type="float",
            semantic_hints=["nogi", "legs"],
        )

        relevance = resolver.calculate_relevance("stół z nogami", schema)

        # Should find "nogi" literally in prompt (boosted to 0.8)
        # or via similarity (0.9)
        assert relevance >= 0.8

    def test_literal_hint_boosts_relevance(self, resolver):
        """Test that literal hint in prompt boosts relevance."""
        schema = ParameterSchema(
            name="angle",
            type="float",
            semantic_hints=["straight", "legs"],
        )

        # "straight" appears literally in prompt
        relevance = resolver.calculate_relevance(
            "table with straight legs", schema
        )

        assert relevance >= 0.8


class TestParameterResolverContextExtraction:
    """Tests for context extraction."""

    def test_extract_context_with_hint(self, resolver):
        """Test extracting context when hint is found."""
        schema = ParameterSchema(
            name="angle",
            type="float",
            semantic_hints=["legs", "nogi"],
        )

        context = resolver.extract_context(
            "create a table with straight legs and wooden top",
            schema,
        )

        assert "legs" in context.lower()
        # Should extract phrase around "legs"

    def test_extract_context_fallback_to_full_prompt(self, resolver):
        """Test fallback to full prompt when no hint found."""
        schema = ParameterSchema(
            name="unknown",
            type="float",
            semantic_hints=["xyz", "abc"],
        )

        context = resolver.extract_context(
            "simple table",
            schema,
        )

        assert context == "simple table"


class TestParameterResolverStoreValue:
    """Tests for storing resolved values."""

    def test_store_valid_value(self, resolver, mock_store):
        """Test storing a valid value."""
        schema = ParameterSchema(
            name="angle",
            type="float",
            range=(-1.57, 1.57),
        )

        result = resolver.store_resolved_value(
            context="straight legs",
            parameter_name="angle",
            value=0.0,
            workflow_name="table",
            schema=schema,
        )

        assert "Stored" in result
        assert "angle=0.0" in result

    def test_store_invalid_value_rejected(self, resolver):
        """Test that invalid value is rejected."""
        schema = ParameterSchema(
            name="angle",
            type="float",
            range=(-1.57, 1.57),
        )

        result = resolver.store_resolved_value(
            context="test",
            parameter_name="angle",
            value=5.0,  # Out of range!
            workflow_name="table",
            schema=schema,
        )

        assert "Error" in result
        assert "invalid" in result.lower()

    def test_store_without_validation(self, resolver, mock_store):
        """Test storing without schema validation."""
        result = resolver.store_resolved_value(
            context="test",
            parameter_name="param",
            value=999,  # Any value
            workflow_name="wf",
            schema=None,  # No validation
        )

        assert "Stored" in result


class TestParameterResolverIntegration:
    """Integration tests for complete resolution flow."""

    def test_multiple_parameters_mixed_resolution(
        self, resolver, mock_store, mock_classifier, sample_parameters
    ):
        """Test resolving multiple parameters with different sources."""
        # Setup: one learned mapping
        mock_store.add_mapping(
            context="wide table",
            parameter_name="top_width",
            value=2.5,
            workflow_name="picnic_table",
        )

        # Setup: high relevance for one param
        mock_classifier.set_similarity(
            "table with angled legs and wide top",
            "rotation",
            0.7,
        )

        existing_modifiers = {
            "leg_angle_right": -0.32,  # YAML modifier
        }

        result = resolver.resolve(
            prompt="table with angled legs and wide top",
            workflow_name="picnic_table",
            parameters=sample_parameters,
            existing_modifiers=existing_modifiers,
        )

        # leg_angle_right: from YAML
        assert result.resolution_sources["leg_angle_right"] == "yaml_modifier"

        # top_width: from learned
        assert result.resolution_sources["top_width"] == "learned"
        assert result.resolved["top_width"] == 2.5

        # leg_angle_left: should be either unresolved or default
        # depending on relevance calculation

    def test_empty_parameters_returns_complete(self, resolver):
        """Test that empty parameters returns complete result."""
        result = resolver.resolve(
            prompt="anything",
            workflow_name="test",
            parameters={},
            existing_modifiers={},
        )

        assert result.is_complete
        assert len(result.resolved) == 0
        assert len(result.unresolved) == 0
