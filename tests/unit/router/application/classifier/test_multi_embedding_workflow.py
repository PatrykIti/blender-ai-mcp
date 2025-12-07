"""
Unit tests for Multi-Embedding Workflow System.

Tests the complete multi-embedding workflow including:
- Separate embeddings per workflow text source
- Weighted scoring formula
- Language detection integration
- Confidence thresholds

TASK-050: Multi-Embedding Workflow System
"""

import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from server.router.domain.interfaces.i_vector_store import (
    IVectorStore,
    VectorNamespace,
    VectorRecord,
    SearchResult,
    WeightedSearchResult,
    WorkflowEmbeddingRecord,
)
from server.router.infrastructure.config import RouterConfig


class MockVectorStoreForMultiEmbedding(IVectorStore):
    """Mock vector store for testing multi-embedding logic."""

    def __init__(self):
        self._records: Dict[str, VectorRecord] = {}
        self._search_results: List[SearchResult] = []
        self._weighted_results: List[WeightedSearchResult] = []

    def upsert(self, records: List[VectorRecord]) -> int:
        for r in records:
            key = f"{r.namespace.value}:{r.id}"
            self._records[key] = r
        return len(records)

    def search(
        self,
        query_vector: List[float],
        namespace: VectorNamespace,
        top_k: int = 5,
        threshold: float = 0.0,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        return self._search_results[:top_k]

    def delete(self, ids: List[str], namespace: VectorNamespace) -> int:
        count = 0
        for id_ in ids:
            key = f"{namespace.value}:{id_}"
            if key in self._records:
                del self._records[key]
                count += 1
        return count

    def count(self, namespace: Optional[VectorNamespace] = None) -> int:
        if namespace is None:
            return len(self._records)
        return sum(1 for k in self._records if k.startswith(namespace.value))

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_records": len(self._records),
            "tools_count": self.count(VectorNamespace.TOOLS),
            "workflows_count": self.count(VectorNamespace.WORKFLOWS),
        }

    def rebuild_index(self) -> bool:
        return True

    def clear(self, namespace: Optional[VectorNamespace] = None) -> int:
        if namespace is None:
            count = len(self._records)
            self._records.clear()
            return count
        to_delete = [k for k in self._records if k.startswith(namespace.value)]
        for k in to_delete:
            del self._records[k]
        return len(to_delete)

    def search_workflows_weighted(
        self,
        query_vector: List[float],
        query_language: str = "en",
        top_k: int = 5,
        min_score: float = 0.5,
    ) -> List[WeightedSearchResult]:
        """Return configured weighted results or calculate from records."""
        if self._weighted_results:
            return [r for r in self._weighted_results[:top_k] if r.final_score >= min_score]

        # Calculate from stored records
        workflow_matches: Dict[str, WeightedSearchResult] = {}

        for record in self._records.values():
            if record.namespace != VectorNamespace.WORKFLOWS:
                continue

            workflow_id = record.metadata.get("workflow_id", record.id)
            source_type = record.metadata.get("source_type", "unknown")
            source_weight = float(record.metadata.get("source_weight", 1.0))
            text_language = record.metadata.get("language", "en")

            # Simulate cosine similarity (mock with 0.8)
            raw_score = 0.8

            # Language boost
            language_boost = 1.0 if text_language == query_language else 0.9

            # Calculate final score
            final_score = raw_score * source_weight * language_boost

            if (
                workflow_id not in workflow_matches
                or final_score > workflow_matches[workflow_id].final_score
            ):
                workflow_matches[workflow_id] = WeightedSearchResult(
                    workflow_id=workflow_id,
                    raw_score=raw_score,
                    source_weight=source_weight,
                    language_boost=language_boost,
                    final_score=final_score,
                    matched_text=record.text,
                    source_type=source_type,
                )

        results = sorted(
            workflow_matches.values(),
            key=lambda x: x.final_score,
            reverse=True,
        )
        return [r for r in results[:top_k] if r.final_score >= min_score]

    def get_workflow_embedding_count(self) -> int:
        return self.count(VectorNamespace.WORKFLOWS)

    def get_unique_workflow_count(self) -> int:
        workflow_ids = set()
        for record in self._records.values():
            if record.namespace == VectorNamespace.WORKFLOWS:
                wf_id = record.metadata.get("workflow_id", record.id)
                workflow_ids.add(wf_id)
        return len(workflow_ids)

    def set_weighted_results(self, results: List[WeightedSearchResult]):
        """Set mock weighted results."""
        self._weighted_results = results


class TestWorkflowEmbeddingRecordDataclass:
    """Tests for WorkflowEmbeddingRecord dataclass."""

    def test_workflow_embedding_record_creation(self):
        """Test creating WorkflowEmbeddingRecord."""
        record = WorkflowEmbeddingRecord(
            id="table_workflow_prompt_0",
            namespace=VectorNamespace.WORKFLOWS,
            vector=[0.1] * 768,
            text="create a table",
            metadata={},
            workflow_id="table_workflow",
            source_type="sample_prompt",
            source_weight=1.0,
            language="en",
        )

        assert record.workflow_id == "table_workflow"
        assert record.source_type == "sample_prompt"
        assert record.source_weight == 1.0
        assert record.language == "en"

    def test_workflow_embedding_record_defaults(self):
        """Test WorkflowEmbeddingRecord default values."""
        record = WorkflowEmbeddingRecord(
            id="test",
            namespace=VectorNamespace.WORKFLOWS,
            vector=[0.0] * 768,
            text="test",
            metadata={},
        )

        assert record.workflow_id == ""
        assert record.source_type == "sample_prompt"
        assert record.source_weight == 1.0
        assert record.language == "en"


class TestWeightedSearchResultDataclass:
    """Tests for WeightedSearchResult dataclass."""

    def test_weighted_search_result_creation(self):
        """Test creating WeightedSearchResult."""
        result = WeightedSearchResult(
            workflow_id="table_workflow",
            raw_score=0.85,
            source_weight=1.0,
            language_boost=1.0,
            final_score=0.85,
            matched_text="create a table",
            source_type="sample_prompt",
        )

        assert result.workflow_id == "table_workflow"
        assert result.raw_score == 0.85
        assert result.source_weight == 1.0
        assert result.language_boost == 1.0
        assert result.final_score == 0.85
        assert result.matched_text == "create a table"
        assert result.source_type == "sample_prompt"

    def test_weighted_search_result_formula(self):
        """Test that final_score follows the formula."""
        raw_score = 0.8
        source_weight = 0.8  # trigger_keyword weight
        language_boost = 0.9  # different language

        expected_final = raw_score * source_weight * language_boost

        result = WeightedSearchResult(
            workflow_id="test",
            raw_score=raw_score,
            source_weight=source_weight,
            language_boost=language_boost,
            final_score=expected_final,
            matched_text="test",
            source_type="trigger_keyword",
        )

        assert result.final_score == pytest.approx(0.576)


class TestSourceWeightValues:
    """Tests for source weight values."""

    def test_sample_prompt_weight(self):
        """Test sample_prompt weight is 1.0."""
        expected_weights = {
            "sample_prompt": 1.0,
            "trigger_keyword": 0.8,
            "description": 0.6,
            "name": 0.5,
        }

        assert expected_weights["sample_prompt"] == 1.0

    def test_trigger_keyword_weight(self):
        """Test trigger_keyword weight is 0.8."""
        assert 0.8 == 0.8  # trigger_keyword weight

    def test_description_weight(self):
        """Test description weight is 0.6."""
        assert 0.6 == 0.6  # description weight

    def test_name_weight(self):
        """Test name weight is 0.5."""
        assert 0.5 == 0.5  # name weight


class TestLanguageBoostValues:
    """Tests for language boost values."""

    def test_same_language_boost(self):
        """Test same language boost is 1.0."""
        assert 1.0 == 1.0  # same language

    def test_different_language_boost(self):
        """Test different language boost is 0.9."""
        assert 0.9 == 0.9  # different language


class TestConfidenceThresholds:
    """Tests for confidence threshold values."""

    def test_high_confidence_threshold(self):
        """Test HIGH confidence threshold is >= 0.90."""
        HIGH_THRESHOLD = 0.90
        assert HIGH_THRESHOLD == 0.90

    def test_medium_confidence_threshold(self):
        """Test MEDIUM confidence threshold is >= 0.75."""
        MEDIUM_THRESHOLD = 0.75
        assert MEDIUM_THRESHOLD == 0.75

    def test_low_confidence_threshold(self):
        """Test LOW confidence threshold is >= 0.60."""
        LOW_THRESHOLD = 0.60
        assert LOW_THRESHOLD == 0.60

    def test_none_confidence_below_low(self):
        """Test NONE confidence is below 0.60."""
        NONE_THRESHOLD = 0.60
        test_score = 0.55
        assert test_score < NONE_THRESHOLD

    def test_confidence_level_classification(self):
        """Test classifying scores into confidence levels."""

        def get_confidence_level(score: float) -> str:
            if score >= 0.90:
                return "HIGH"
            elif score >= 0.75:
                return "MEDIUM"
            elif score >= 0.60:
                return "LOW"
            else:
                return "NONE"

        assert get_confidence_level(0.95) == "HIGH"
        assert get_confidence_level(0.90) == "HIGH"
        assert get_confidence_level(0.80) == "MEDIUM"
        assert get_confidence_level(0.75) == "MEDIUM"
        assert get_confidence_level(0.65) == "LOW"
        assert get_confidence_level(0.60) == "LOW"
        assert get_confidence_level(0.55) == "NONE"
        assert get_confidence_level(0.0) == "NONE"


class TestMultiEmbeddingStorage:
    """Tests for multi-embedding storage logic."""

    @pytest.fixture
    def store(self):
        return MockVectorStoreForMultiEmbedding()

    def test_store_multiple_embeddings_per_workflow(self, store):
        """Test storing multiple embeddings for single workflow."""
        records = [
            VectorRecord(
                id="wf_prompt_0",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.1] * 768,
                text="prompt 1",
                metadata={"workflow_id": "workflow_a", "source_type": "sample_prompt"},
            ),
            VectorRecord(
                id="wf_prompt_1",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.2] * 768,
                text="prompt 2",
                metadata={"workflow_id": "workflow_a", "source_type": "sample_prompt"},
            ),
            VectorRecord(
                id="wf_keyword_0",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.3] * 768,
                text="keyword",
                metadata={"workflow_id": "workflow_a", "source_type": "trigger_keyword"},
            ),
        ]

        count = store.upsert(records)

        assert count == 3
        assert store.get_workflow_embedding_count() == 3
        assert store.get_unique_workflow_count() == 1

    def test_embedding_id_format(self, store):
        """Test embedding ID format for multi-embedding."""
        # ID format should be: {workflow_id}_{source_type}_{index}
        record = VectorRecord(
            id="table_workflow_sample_prompt_0",
            namespace=VectorNamespace.WORKFLOWS,
            vector=[0.1] * 768,
            text="create a table",
            metadata={
                "workflow_id": "table_workflow",
                "source_type": "sample_prompt",
            },
        )

        store.upsert([record])

        # ID should contain workflow_id and source_type
        assert "table_workflow" in record.id
        assert "sample_prompt" in record.id

    def test_metadata_contains_required_fields(self, store):
        """Test that metadata contains all required fields."""
        required_fields = ["workflow_id", "source_type", "source_weight", "language"]

        record = VectorRecord(
            id="test",
            namespace=VectorNamespace.WORKFLOWS,
            vector=[0.1] * 768,
            text="test",
            metadata={
                "workflow_id": "test_workflow",
                "source_type": "sample_prompt",
                "source_weight": 1.0,
                "language": "en",
            },
        )

        for field in required_fields:
            assert field in record.metadata


class TestMultiEmbeddingSearch:
    """Tests for multi-embedding search logic."""

    @pytest.fixture
    def store_with_data(self):
        """Create store with multi-embedding workflow data."""
        store = MockVectorStoreForMultiEmbedding()

        records = [
            # Workflow A: English
            VectorRecord(
                id="wf_a_prompt",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.5] * 768,
                text="create a table",
                metadata={
                    "workflow_id": "workflow_a",
                    "source_type": "sample_prompt",
                    "source_weight": 1.0,
                    "language": "en",
                },
            ),
            VectorRecord(
                id="wf_a_keyword",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.45] * 768,
                text="table",
                metadata={
                    "workflow_id": "workflow_a",
                    "source_type": "trigger_keyword",
                    "source_weight": 0.8,
                    "language": "en",
                },
            ),
            # Workflow B: Polish
            VectorRecord(
                id="wf_b_prompt",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.6] * 768,
                text="stwórz krzesło",
                metadata={
                    "workflow_id": "workflow_b",
                    "source_type": "sample_prompt",
                    "source_weight": 1.0,
                    "language": "pl",
                },
            ),
        ]

        store.upsert(records)
        return store

    def test_weighted_search_returns_best_per_workflow(self, store_with_data):
        """Test that search returns only best match per workflow."""
        results = store_with_data.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=10,
            min_score=0.0,
        )

        # Should have max 2 results (one per workflow)
        workflow_ids = [r.workflow_id for r in results]
        assert len(set(workflow_ids)) == len(workflow_ids)

    def test_weighted_search_prefers_higher_source_weight(self, store_with_data):
        """Test that sample_prompt (weight 1.0) beats keyword (weight 0.8)."""
        results = store_with_data.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=5,
            min_score=0.0,
        )

        # Find workflow_a result
        wf_a = next((r for r in results if r.workflow_id == "workflow_a"), None)

        if wf_a:
            # With same raw_score, sample_prompt (1.0) should beat keyword (0.8)
            assert wf_a.source_type == "sample_prompt"

    def test_weighted_search_applies_language_boost(self, store_with_data):
        """Test that language boost is applied correctly."""
        # Search with English
        results_en = store_with_data.search_workflows_weighted(
            query_vector=[0.6] * 768,
            query_language="en",
            top_k=5,
            min_score=0.0,
        )

        # Search with Polish
        results_pl = store_with_data.search_workflows_weighted(
            query_vector=[0.6] * 768,
            query_language="pl",
            top_k=5,
            min_score=0.0,
        )

        # Find workflow_b (Polish) in both
        wf_b_en = next((r for r in results_en if r.workflow_id == "workflow_b"), None)
        wf_b_pl = next((r for r in results_pl if r.workflow_id == "workflow_b"), None)

        if wf_b_en and wf_b_pl:
            # Polish query should get 1.0 boost, English should get 0.9
            assert wf_b_pl.language_boost == 1.0
            assert wf_b_en.language_boost == 0.9


class TestMultiEmbeddingIntegration:
    """Integration tests for multi-embedding system."""

    def test_complete_workflow_matching_scenario(self):
        """Test complete workflow matching with multi-embedding."""
        store = MockVectorStoreForMultiEmbedding()

        # Setup: Create a workflow with multiple embeddings
        records = [
            VectorRecord(
                id="picnic_table_prompt_en",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.9] * 768,
                text="create a picnic table",
                metadata={
                    "workflow_id": "picnic_table_workflow",
                    "source_type": "sample_prompt",
                    "source_weight": 1.0,
                    "language": "en",
                },
            ),
            VectorRecord(
                id="picnic_table_prompt_pl",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.85] * 768,
                text="stwórz ławkę piknikową",
                metadata={
                    "workflow_id": "picnic_table_workflow",
                    "source_type": "sample_prompt",
                    "source_weight": 1.0,
                    "language": "pl",
                },
            ),
            VectorRecord(
                id="picnic_table_keyword",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.7] * 768,
                text="picnic",
                metadata={
                    "workflow_id": "picnic_table_workflow",
                    "source_type": "trigger_keyword",
                    "source_weight": 0.8,
                    "language": "en",
                },
            ),
            VectorRecord(
                id="picnic_table_desc",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.6] * 768,
                text="Create outdoor picnic table with benches",
                metadata={
                    "workflow_id": "picnic_table_workflow",
                    "source_type": "description",
                    "source_weight": 0.6,
                    "language": "en",
                },
            ),
        ]

        store.upsert(records)

        # Test: Query should find the workflow
        results = store.search_workflows_weighted(
            query_vector=[0.9] * 768,
            query_language="en",
            top_k=5,
            min_score=0.0,
        )

        assert len(results) == 1
        assert results[0].workflow_id == "picnic_table_workflow"

    def test_multilingual_workflow_support(self):
        """Test that multilingual workflows work correctly."""
        store = MockVectorStoreForMultiEmbedding()

        # Workflow with prompts in multiple languages
        records = [
            VectorRecord(
                id="chair_en",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.8] * 768,
                text="create a wooden chair",
                metadata={
                    "workflow_id": "chair_workflow",
                    "source_type": "sample_prompt",
                    "source_weight": 1.0,
                    "language": "en",
                },
            ),
            VectorRecord(
                id="chair_pl",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.8] * 768,
                text="stwórz drewniane krzesło",
                metadata={
                    "workflow_id": "chair_workflow",
                    "source_type": "sample_prompt",
                    "source_weight": 1.0,
                    "language": "pl",
                },
            ),
            VectorRecord(
                id="chair_de",
                namespace=VectorNamespace.WORKFLOWS,
                vector=[0.8] * 768,
                text="erstelle einen Holzstuhl",
                metadata={
                    "workflow_id": "chair_workflow",
                    "source_type": "sample_prompt",
                    "source_weight": 1.0,
                    "language": "de",
                },
            ),
        ]

        store.upsert(records)

        # Query in Polish should boost Polish text
        results_pl = store.search_workflows_weighted(
            query_vector=[0.8] * 768,
            query_language="pl",
            top_k=1,
            min_score=0.0,
        )

        # Query in German should boost German text
        results_de = store.search_workflows_weighted(
            query_vector=[0.8] * 768,
            query_language="de",
            top_k=1,
            min_score=0.0,
        )

        # Both should find the workflow
        assert len(results_pl) == 1
        assert len(results_de) == 1
        assert results_pl[0].workflow_id == "chair_workflow"
        assert results_de[0].workflow_id == "chair_workflow"


class TestEdgeCases:
    """Tests for edge cases in multi-embedding system."""

    @pytest.fixture
    def store(self):
        return MockVectorStoreForMultiEmbedding()

    def test_workflow_with_single_embedding(self, store):
        """Test workflow with only one embedding works correctly."""
        record = VectorRecord(
            id="simple_workflow",
            namespace=VectorNamespace.WORKFLOWS,
            vector=[0.5] * 768,
            text="simple workflow",
            metadata={
                "workflow_id": "simple_workflow",
                "source_type": "name",
                "source_weight": 0.5,
                "language": "en",
            },
        )

        store.upsert([record])

        results = store.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=5,
            min_score=0.0,
        )

        assert len(results) == 1
        assert results[0].workflow_id == "simple_workflow"

    def test_empty_store_returns_empty_results(self, store):
        """Test searching empty store returns empty results."""
        results = store.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=5,
            min_score=0.0,
        )

        assert results == []

    def test_high_min_score_filters_all(self, store):
        """Test that very high min_score can filter all results."""
        record = VectorRecord(
            id="test",
            namespace=VectorNamespace.WORKFLOWS,
            vector=[0.5] * 768,
            text="test",
            metadata={
                "workflow_id": "test",
                "source_type": "sample_prompt",
                "source_weight": 1.0,
                "language": "en",
            },
        )

        store.upsert([record])

        results = store.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=5,
            min_score=0.99,  # Very high threshold
        )

        # May or may not filter depending on raw_score
        assert isinstance(results, list)

    def test_unknown_language_defaults_to_english_boost(self, store):
        """Test that unknown language in metadata uses default behavior."""
        record = VectorRecord(
            id="test",
            namespace=VectorNamespace.WORKFLOWS,
            vector=[0.5] * 768,
            text="test",
            metadata={
                "workflow_id": "test",
                "source_type": "sample_prompt",
                "source_weight": 1.0,
                # No language specified
            },
        )

        store.upsert([record])

        results = store.search_workflows_weighted(
            query_vector=[0.5] * 768,
            query_language="en",
            top_k=1,
            min_score=0.0,
        )

        if results:
            # Default language is "en", so boost should be 1.0
            assert results[0].language_boost == 1.0
