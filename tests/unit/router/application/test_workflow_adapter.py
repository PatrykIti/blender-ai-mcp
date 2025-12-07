"""
Tests for WorkflowAdapter engine.

TASK-051: Confidence-Based Workflow Adaptation.
"""

import pytest
from unittest.mock import MagicMock, patch

from server.router.application.engines.workflow_adapter import (
    WorkflowAdapter,
    AdaptationResult,
)
from server.router.application.workflows.base import WorkflowStep, WorkflowDefinition
from server.router.infrastructure.config import RouterConfig


@pytest.fixture
def config():
    """Create router config."""
    return RouterConfig(
        enable_workflow_adaptation=True,
        adaptation_semantic_threshold=0.6,
    )


@pytest.fixture
def adapter(config):
    """Create workflow adapter without classifier."""
    return WorkflowAdapter(config=config)


@pytest.fixture
def sample_workflow():
    """Create sample workflow with optional steps."""
    return WorkflowDefinition(
        name="picnic_table_workflow",
        description="Picnic table with optional benches",
        steps=[
            # Core steps (not optional)
            WorkflowStep(
                tool="modeling_create_primitive",
                params={"primitive_type": "CUBE", "name": "TableTop"},
                description="Create table top",
                optional=False,
            ),
            WorkflowStep(
                tool="modeling_transform_object",
                params={"name": "TableTop", "scale": [1, 1, 0.1]},
                description="Scale table top",
                optional=False,
            ),
            WorkflowStep(
                tool="modeling_create_primitive",
                params={"primitive_type": "CUBE", "name": "Leg1"},
                description="Create table leg",
                optional=False,
            ),
            # Optional bench steps with tags
            WorkflowStep(
                tool="modeling_create_primitive",
                params={"primitive_type": "CUBE", "name": "BenchLeft"},
                description="Create left bench",
                optional=True,
                tags=["bench", "seating", "side"],
            ),
            WorkflowStep(
                tool="modeling_transform_object",
                params={"name": "BenchLeft", "location": [-1, 0, 0]},
                description="Position left bench",
                optional=True,
                tags=["bench", "seating", "side"],
            ),
            WorkflowStep(
                tool="modeling_create_primitive",
                params={"primitive_type": "CUBE", "name": "BenchRight"},
                description="Create right bench",
                optional=True,
                tags=["bench", "seating", "side"],
            ),
            WorkflowStep(
                tool="modeling_transform_object",
                params={"name": "BenchRight", "location": [1, 0, 0]},
                description="Position right bench",
                optional=True,
                tags=["bench", "seating", "side"],
            ),
        ],
    )


class TestWorkflowAdapterHighConfidence:
    """Tests for HIGH confidence (≥0.90) - all steps returned."""

    def test_high_confidence_returns_all_steps(self, adapter, sample_workflow):
        """HIGH confidence should return ALL steps (no adaptation)."""
        steps, result = adapter.adapt(
            definition=sample_workflow,
            confidence_level="HIGH",
            user_prompt="create a picnic table",
        )

        assert len(steps) == 7
        assert result.original_step_count == 7
        assert result.adapted_step_count == 7
        assert result.adaptation_strategy == "FULL"
        assert result.skipped_steps == []

    def test_high_confidence_result_metadata(self, adapter, sample_workflow):
        """HIGH confidence result should have correct metadata."""
        _, result = adapter.adapt(
            definition=sample_workflow,
            confidence_level="HIGH",
            user_prompt="create a picnic table",
        )

        assert result.confidence_level == "HIGH"
        assert result.requires_adaptation is False if hasattr(result, 'requires_adaptation') else True


class TestWorkflowAdapterLowConfidence:
    """Tests for LOW confidence (≥0.60) - core steps only."""

    def test_low_confidence_skips_all_optional(self, adapter, sample_workflow):
        """LOW confidence should skip ALL optional steps."""
        steps, result = adapter.adapt(
            definition=sample_workflow,
            confidence_level="LOW",
            user_prompt="simple table with 4 legs",
        )

        # Should have only 3 core steps
        assert len(steps) == 3
        assert result.original_step_count == 7
        assert result.adapted_step_count == 3
        assert result.adaptation_strategy == "CORE_ONLY"

        # All bench steps should be skipped
        assert len(result.skipped_steps) == 4

    def test_low_confidence_preserves_core_steps(self, adapter, sample_workflow):
        """LOW confidence should preserve all core (non-optional) steps."""
        steps, _ = adapter.adapt(
            definition=sample_workflow,
            confidence_level="LOW",
            user_prompt="simple table",
        )

        tool_names = [s.tool for s in steps]
        assert "modeling_create_primitive" in tool_names
        assert "modeling_transform_object" in tool_names


class TestWorkflowAdapterNoneConfidence:
    """Tests for NONE confidence (<0.60) - core steps only (fallback)."""

    def test_none_confidence_skips_all_optional(self, adapter, sample_workflow):
        """NONE confidence should skip ALL optional steps (fallback)."""
        steps, result = adapter.adapt(
            definition=sample_workflow,
            confidence_level="NONE",
            user_prompt="something random",
        )

        assert len(steps) == 3
        assert result.adaptation_strategy == "CORE_ONLY"
        assert result.confidence_level == "NONE"


class TestWorkflowAdapterMediumConfidence:
    """Tests for MEDIUM confidence (≥0.75) - core + filtered optional."""

    def test_medium_confidence_filters_by_tags(self, adapter, sample_workflow):
        """MEDIUM confidence should include optional steps matching tags."""
        steps, result = adapter.adapt(
            definition=sample_workflow,
            confidence_level="MEDIUM",
            user_prompt="table with bench",  # Contains "bench" tag
        )

        # Should have core steps + bench steps (tag match)
        assert len(steps) == 7  # All steps because "bench" tag matches
        assert result.adaptation_strategy == "FILTERED"

    def test_medium_confidence_without_matching_tags(self, adapter, sample_workflow):
        """MEDIUM confidence without matching tags should return core only."""
        steps, result = adapter.adapt(
            definition=sample_workflow,
            confidence_level="MEDIUM",
            user_prompt="wooden furniture",  # No matching tags
        )

        # Should have only core steps (no tags match)
        assert len(steps) == 3
        assert result.adaptation_strategy == "FILTERED"
        assert len(result.skipped_steps) == 4

    def test_medium_confidence_partial_tag_match(self, adapter, sample_workflow):
        """MEDIUM confidence with partial tag match includes matching steps."""
        steps, result = adapter.adapt(
            definition=sample_workflow,
            confidence_level="MEDIUM",
            user_prompt="table with seating",  # "seating" tag matches
        )

        # All bench steps have "seating" tag, so all should be included
        assert len(steps) == 7


class TestWorkflowAdapterSimpleTablePrompt:
    """Tests for specific "simple table" use case."""

    def test_simple_table_prompt_skips_benches(self, adapter, sample_workflow):
        """'simple table with 4 legs' should skip bench steps."""
        steps, result = adapter.adapt(
            definition=sample_workflow,
            confidence_level="LOW",
            user_prompt="simple table with 4 legs",
        )

        # Should not include any bench
        step_names = [s.params.get("name", "") for s in steps]
        assert "BenchLeft" not in step_names
        assert "BenchRight" not in step_names
        assert len(result.skipped_steps) == 4

    def test_table_with_benches_includes_bench_steps(self, adapter, sample_workflow):
        """'table with benches' should include bench steps."""
        steps, result = adapter.adapt(
            definition=sample_workflow,
            confidence_level="MEDIUM",
            user_prompt="table with benches",
        )

        # Should include bench steps (tag match)
        step_names = [s.params.get("name", "") for s in steps]
        assert "BenchLeft" in step_names
        assert "BenchRight" in step_names


class TestWorkflowAdapterEdgeCases:
    """Edge case tests."""

    def test_empty_optional_steps_returns_core_only(self, adapter):
        """Workflow with no optional steps returns all steps."""
        workflow = WorkflowDefinition(
            name="simple_workflow",
            description="No optional steps",
            steps=[
                WorkflowStep(
                    tool="tool1",
                    params={},
                    optional=False,
                ),
                WorkflowStep(
                    tool="tool2",
                    params={},
                    optional=False,
                ),
            ],
        )

        steps, result = adapter.adapt(
            definition=workflow,
            confidence_level="LOW",
            user_prompt="anything",
        )

        assert len(steps) == 2
        assert result.skipped_steps == []

    def test_all_optional_steps_workflow(self, adapter):
        """Workflow with all optional steps returns empty on LOW confidence."""
        workflow = WorkflowDefinition(
            name="all_optional",
            description="All steps are optional",
            steps=[
                WorkflowStep(
                    tool="optional1",
                    params={},
                    optional=True,
                    tags=["tag1"],
                ),
                WorkflowStep(
                    tool="optional2",
                    params={},
                    optional=True,
                    tags=["tag2"],
                ),
            ],
        )

        steps, result = adapter.adapt(
            definition=workflow,
            confidence_level="LOW",
            user_prompt="no matching tags",
        )

        assert len(steps) == 0
        assert result.adapted_step_count == 0
        assert len(result.skipped_steps) == 2


class TestAdaptationResult:
    """Tests for AdaptationResult dataclass."""

    def test_adaptation_result_to_dict(self, adapter, sample_workflow):
        """AdaptationResult.to_dict() should return all fields."""
        _, result = adapter.adapt(
            definition=sample_workflow,
            confidence_level="LOW",
            user_prompt="simple table",
        )

        result_dict = result.to_dict()

        assert "original_step_count" in result_dict
        assert "adapted_step_count" in result_dict
        assert "skipped_steps" in result_dict
        assert "included_optional" in result_dict
        assert "confidence_level" in result_dict
        assert "adaptation_strategy" in result_dict

    def test_adaptation_result_contains_skipped_info(self, adapter, sample_workflow):
        """AdaptationResult should contain descriptions of skipped steps."""
        _, result = adapter.adapt(
            definition=sample_workflow,
            confidence_level="LOW",
            user_prompt="simple table",
        )

        # Skipped steps should contain descriptions
        assert any("bench" in s.lower() for s in result.skipped_steps)


class TestWorkflowAdapterShouldAdapt:
    """Tests for should_adapt() helper method."""

    def test_should_adapt_returns_false_for_high(self, adapter, sample_workflow):
        """should_adapt returns False for HIGH confidence."""
        assert not adapter.should_adapt("HIGH", sample_workflow)

    def test_should_adapt_returns_true_for_low_with_optional(self, adapter, sample_workflow):
        """should_adapt returns True for LOW confidence with optional steps."""
        assert adapter.should_adapt("LOW", sample_workflow)

    def test_should_adapt_returns_false_without_optional(self, adapter):
        """should_adapt returns False if workflow has no optional steps."""
        workflow = WorkflowDefinition(
            name="no_optional",
            description="No optional",
            steps=[
                WorkflowStep(tool="t1", params={}, optional=False),
            ],
        )
        assert not adapter.should_adapt("LOW", workflow)


class TestWorkflowAdapterSemanticFallback:
    """Tests for semantic similarity fallback."""

    def test_semantic_fallback_when_no_tags(self, config):
        """Test semantic fallback for steps without tags."""
        # Create mock classifier
        mock_classifier = MagicMock()
        mock_classifier.similarity.return_value = 0.8  # Above threshold

        adapter = WorkflowAdapter(config=config, classifier=mock_classifier)

        workflow = WorkflowDefinition(
            name="test",
            description="Test",
            steps=[
                WorkflowStep(
                    tool="core",
                    params={},
                    optional=False,
                ),
                WorkflowStep(
                    tool="optional_no_tags",
                    params={},
                    description="Add decorative elements",
                    optional=True,
                    tags=[],  # No tags!
                ),
            ],
        )

        steps, result = adapter.adapt(
            definition=workflow,
            confidence_level="MEDIUM",
            user_prompt="add decoration",
        )

        # Should include optional step via semantic fallback
        assert len(steps) == 2
        mock_classifier.similarity.assert_called()

    def test_semantic_fallback_below_threshold(self, config):
        """Test semantic fallback below threshold excludes step."""
        mock_classifier = MagicMock()
        mock_classifier.similarity.return_value = 0.3  # Below threshold (0.6)

        adapter = WorkflowAdapter(config=config, classifier=mock_classifier)

        workflow = WorkflowDefinition(
            name="test",
            description="Test",
            steps=[
                WorkflowStep(
                    tool="core",
                    params={},
                    optional=False,
                ),
                WorkflowStep(
                    tool="optional_no_tags",
                    params={},
                    description="Something unrelated",
                    optional=True,
                    tags=[],
                ),
            ],
        )

        steps, result = adapter.adapt(
            definition=workflow,
            confidence_level="MEDIUM",
            user_prompt="completely different",
        )

        # Should NOT include optional step (below threshold)
        assert len(steps) == 1


class TestWorkflowAdapterInfo:
    """Tests for get_info() method."""

    def test_get_info_returns_config(self, adapter):
        """get_info should return adapter configuration."""
        info = adapter.get_info()

        assert "semantic_threshold" in info
        assert "has_classifier" in info
        assert "config" in info
        assert info["semantic_threshold"] == 0.6
        assert info["has_classifier"] is False  # No classifier in fixture
