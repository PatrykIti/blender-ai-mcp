"""Tests for TASK-095 boundary telemetry markers."""

from __future__ import annotations

from unittest.mock import MagicMock

from server.infrastructure.telemetry import (
    get_memory_exporter,
    initialize_telemetry,
    reset_telemetry_for_tests,
)
from server.router.application.matcher.ensemble_aggregator import EnsembleAggregator
from server.router.application.resolver.parameter_resolver import ParameterResolver
from server.router.application.resolver.parameter_store import ParameterStore
from server.router.domain.entities.ensemble import MatcherResult, ModifierResult
from server.router.domain.entities.parameter import ParameterSchema


class DummyClassifier:
    def similarity(self, text1, text2):
        if text2 in text1:
            return 0.9
        return 0.2

    def get_embedding(self, text):
        return [0.1] * 4


class DummyVectorStore:
    def search(self, **kwargs):
        return []

    def upsert(self, records):
        return None


class DummyStore:
    def __init__(self):
        self.incremented = 0

    def find_mapping(self, *args, **kwargs):
        return None

    def increment_usage(self, mapping):
        self.incremented += 1


def setup_function():
    reset_telemetry_for_tests()


def teardown_function():
    reset_telemetry_for_tests()


def test_parameter_resolver_emits_boundary_marker_for_irrelevant_default():
    """Parameter resolution should emit telemetry that semantic memory stayed in its allowed scope."""

    initialize_telemetry(enabled=True, service_name="bam-test", exporter="memory", force=True)

    resolver = ParameterResolver(
        classifier=DummyClassifier(),
        store=DummyStore(),
        relevance_threshold=0.5,
        memory_threshold=0.85,
    )

    resolver.resolve(
        prompt="simple table",
        workflow_name="picnic_table",
        parameters={
            "top_width": ParameterSchema(
                name="top_width",
                type="float",
                default=1.5,
                description="table width",
                semantic_hints=["width", "size"],
            )
        },
        existing_modifiers={},
    )

    spans = get_memory_exporter().get_finished_spans()
    span = next(s for s in spans if s.name == "router.semantic_parameter_resolution")
    assert span.attributes["router.outcome"] == "default_irrelevant"
    assert span.attributes["router.semantic_scope"] == "parameter_memory_only"


def test_parameter_store_emits_lookup_miss_boundary_marker():
    """ParameterStore should emit a semantic-memory telemetry marker on lookup miss."""

    initialize_telemetry(enabled=True, service_name="bam-test", exporter="memory", force=True)

    store = ParameterStore(
        classifier=DummyClassifier(),
        vector_store=DummyVectorStore(),
        similarity_threshold=0.85,
    )

    result = store.find_mapping(
        prompt="simple table",
        parameter_name="top_width",
        workflow_name="picnic_table",
    )

    assert result is None
    spans = get_memory_exporter().get_finished_spans()
    span = next(s for s in spans if s.name == "router.semantic_parameter_store_lookup")
    assert span.attributes["router.outcome"] == "miss"
    assert span.attributes["router.semantic_scope"] == "parameter_memory_only"


def test_ensemble_aggregator_emits_semantic_workflow_boundary_marker():
    """Semantic workflow aggregation should emit telemetry that marks its scope as workflow retrieval only."""

    initialize_telemetry(enabled=True, service_name="bam-test", exporter="memory", force=True)

    modifier_extractor = MagicMock()
    modifier_extractor.extract.return_value = ModifierResult(
        modifiers={},
        matched_keywords=[],
        confidence_map={},
    )
    aggregator = EnsembleAggregator(modifier_extractor)

    aggregator.aggregate(
        [
            MatcherResult("semantic", "table_workflow", 0.85, 0.40),
        ],
        "create a table",
    )

    spans = get_memory_exporter().get_finished_spans()
    span = next(s for s in spans if s.name == "router.semantic_workflow_match")
    assert span.attributes["router.semantic_scope"] == "workflow_retrieval_only"
    assert span.attributes["router.policy_approval_delegated"] is False
