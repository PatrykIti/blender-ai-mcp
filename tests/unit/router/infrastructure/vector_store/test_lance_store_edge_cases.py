from __future__ import annotations

from types import SimpleNamespace

from server.router.domain.interfaces.i_vector_store import VectorNamespace, VectorRecord
from server.router.infrastructure.vector_store.lance_store import LanceVectorStore


def test_list_tables_falls_back_to_table_names(tmp_path):
    store = LanceVectorStore(db_path=tmp_path)
    store._db = SimpleNamespace(table_names=lambda: ["embeddings"])
    assert store._list_tables() == ["embeddings"]


def test_require_table_raises_when_missing(tmp_path):
    store = LanceVectorStore(db_path=tmp_path)
    store._table = None
    try:
        store._require_table()
    except RuntimeError as exc:
        assert "not initialized" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError when table is missing")


def test_lancedb_table_error_paths_fall_back(tmp_path, monkeypatch):
    store = LanceVectorStore(db_path=tmp_path)
    store._use_fallback = False

    class BrokenTable:
        def add(self, *_args, **_kwargs):
            raise RuntimeError("boom")

        def delete(self, *_args, **_kwargs):
            raise RuntimeError("boom")

        def count_rows(self, *_args, **_kwargs):
            raise RuntimeError("boom")

        def create_index(self, *_args, **_kwargs):
            raise RuntimeError("boom")

        def search(self, *_args, **_kwargs):
            raise RuntimeError("boom")

    store._table = BrokenTable()
    record = VectorRecord(
        id="tool-1",
        namespace=VectorNamespace.TOOLS,
        vector=[0.1] * 768,
        text="tool",
        metadata={},
    )

    assert store.upsert([record]) == 1
    monkeypatch.setattr(store, "_search_fallback", lambda *args, **kwargs: ["fallback"])
    monkeypatch.setattr(store, "_delete_fallback", lambda *args, **kwargs: 1)
    monkeypatch.setattr(store, "_count_fallback", lambda *args, **kwargs: 1)
    monkeypatch.setattr(store, "_clear_fallback", lambda *args, **kwargs: 1)
    assert store.search([0.1] * 768, VectorNamespace.TOOLS) == ["fallback"]
    assert store.delete(["tool-1"], VectorNamespace.TOOLS) == 0
    assert store.count(VectorNamespace.TOOLS) == 1
    assert store.rebuild_index() is False
    assert store.clear(VectorNamespace.TOOLS) == 1
    assert store.get_all_ids(VectorNamespace.TOOLS) == []
    assert store.get_unique_workflow_count() == 0


def test_fallback_weighted_search_and_stats(tmp_path):
    store = LanceVectorStore(db_path=tmp_path)
    store._use_fallback = True
    store._fallback_store["wf:1"] = VectorRecord(
        id="wf_embedding",
        namespace=VectorNamespace.WORKFLOWS,
        vector=[1.0] * 768,
        text="create chair",
        metadata={
            "workflow_id": "chair_workflow",
            "source_type": "sample_prompt",
            "source_weight": 1.0,
            "language": "en",
        },
    )

    results = store.search_workflows_weighted([1.0] * 768, query_language="en", top_k=3, min_score=0.0)
    stats = store.get_stats()

    assert results
    assert results[0].workflow_id == "chair_workflow"
    assert stats["workflows_count"] == 1
    assert store.get_unique_workflow_count() == 1
