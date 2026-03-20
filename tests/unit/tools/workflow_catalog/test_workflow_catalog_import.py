import json
from pathlib import Path

import pytest

from server.application.tool_handlers.workflow_catalog_handler import (
    WorkflowCatalogToolHandler,
)
from server.router.infrastructure.workflow_loader import WorkflowLoader
from server.router.domain.interfaces.i_vector_store import VectorNamespace


class DummyWorkflowClassifier:
    def __init__(self):
        self.called = False
        self.workflows = None

    def load_workflow_embeddings(self, workflows):
        self.called = True
        self.workflows = workflows


class DummyVectorStore:
    def __init__(self, ids=None):
        self.ids = list(ids or [])
        self.deleted_ids = []
        self.deleted_namespace = None

    def get_all_ids(self, namespace):
        return list(self.ids)

    def delete(self, ids, namespace):
        self.deleted_ids = list(ids)
        self.deleted_namespace = namespace
        return len(ids)


class DummyRegistry:
    def __init__(self):
        self.reload_calls = 0

    def load_custom_workflows(self, reload=False):
        self.reload_calls += 1


def _write_workflow_json(path: Path, name: str) -> None:
    data = {
        "name": name,
        "steps": [
            {
                "tool": "modeling_create_primitive",
                "params": {"primitive_type": "Cube"},
            }
        ],
    }
    path.write_text(json.dumps(data), encoding="utf-8")


def _write_workflow_yaml(path: Path, name: str) -> None:
    content = (
        f"name: {name}\n"
        "steps:\n"
        "  - tool: modeling_create_primitive\n"
        "    params:\n"
        "      primitive_type: Cube\n"
    )
    path.write_text(content, encoding="utf-8")


@pytest.fixture()
def workflow_setup(tmp_path, monkeypatch):
    workflows_dir = tmp_path / "workflows"
    incoming_dir = tmp_path / "incoming"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    incoming_dir.mkdir(parents=True, exist_ok=True)

    loader = WorkflowLoader(workflows_dir)
    registry = DummyRegistry()
    monkeypatch.setattr(
        "server.router.application.workflows.registry.get_workflow_registry",
        lambda: registry,
    )

    return workflows_dir, incoming_dir, loader, registry


def test_import_workflow_success(workflow_setup):
    workflows_dir, incoming_dir, loader, registry = workflow_setup
    incoming_file = incoming_dir / "chair.json"
    _write_workflow_json(incoming_file, "chair_workflow")

    classifier = DummyWorkflowClassifier()
    vector_store = DummyVectorStore()
    handler = WorkflowCatalogToolHandler(
        workflow_loader=loader,
        workflow_classifier=classifier,
        vector_store=vector_store,
    )

    result = handler.import_workflow(str(incoming_file))

    assert result["status"] == "imported"
    assert result["workflow_name"] == "chair_workflow"
    assert result["overwritten"] is False
    assert Path(result["saved_path"]).exists()
    assert Path(result["saved_path"]).parent == workflows_dir
    assert classifier.called is True
    assert "chair_workflow" in (classifier.workflows or {})
    assert registry.reload_calls == 1


def test_import_workflow_conflict_needs_input(workflow_setup):
    workflows_dir, incoming_dir, loader, registry = workflow_setup
    existing_file = workflows_dir / "chair_workflow.json"
    _write_workflow_json(existing_file, "chair_workflow")

    incoming_file = incoming_dir / "chair.json"
    _write_workflow_json(incoming_file, "chair_workflow")

    vector_store = DummyVectorStore(ids=["chair_workflow__name__0"])
    handler = WorkflowCatalogToolHandler(
        workflow_loader=loader,
        workflow_classifier=DummyWorkflowClassifier(),
        vector_store=vector_store,
    )

    result = handler.import_workflow(str(incoming_file))

    assert result["status"] == "needs_input"
    assert result["workflow_name"] == "chair_workflow"
    assert result["conflicts"]["definition_loaded"] is True
    assert result["conflicts"]["files"]
    assert result["conflicts"]["vector_store_records"] == 1
    assert registry.reload_calls == 0


def test_import_workflow_conflict_skip(workflow_setup):
    workflows_dir, incoming_dir, loader, registry = workflow_setup
    existing_file = workflows_dir / "chair_workflow.json"
    _write_workflow_json(existing_file, "chair_workflow")

    incoming_file = incoming_dir / "chair.json"
    _write_workflow_json(incoming_file, "chair_workflow")

    vector_store = DummyVectorStore(ids=["chair_workflow__name__0"])
    handler = WorkflowCatalogToolHandler(
        workflow_loader=loader,
        workflow_classifier=DummyWorkflowClassifier(),
        vector_store=vector_store,
    )

    result = handler.import_workflow(str(incoming_file), overwrite=False)

    assert result["status"] == "skipped"
    assert result["workflow_name"] == "chair_workflow"
    assert vector_store.deleted_ids == []
    assert registry.reload_calls == 0


def test_import_workflow_overwrite_removes_files_and_embeddings(workflow_setup):
    workflows_dir, incoming_dir, loader, registry = workflow_setup
    existing_yaml = workflows_dir / "chair_workflow.yaml"
    _write_workflow_yaml(existing_yaml, "chair_workflow")

    incoming_file = incoming_dir / "chair.json"
    _write_workflow_json(incoming_file, "chair_workflow")

    vector_store = DummyVectorStore(
        ids=["chair_workflow", "chair_workflow__sample_prompt__0"]
    )
    handler = WorkflowCatalogToolHandler(
        workflow_loader=loader,
        workflow_classifier=DummyWorkflowClassifier(),
        vector_store=vector_store,
    )

    result = handler.import_workflow(str(incoming_file), overwrite=True)

    assert result["status"] == "imported"
    assert result["overwritten"] is True
    assert not existing_yaml.exists()
    assert vector_store.deleted_ids == [
        "chair_workflow",
        "chair_workflow__sample_prompt__0",
    ]
    assert vector_store.deleted_namespace == VectorNamespace.WORKFLOWS
    assert result["removed_embeddings"] == 2
    assert registry.reload_calls == 1


def test_import_workflow_content_json(workflow_setup):
    workflows_dir, _incoming_dir, loader, registry = workflow_setup
    content = json.dumps(
        {
            "name": "inline_workflow",
            "steps": [
                {
                    "tool": "modeling_create_primitive",
                    "params": {"primitive_type": "Cube"},
                }
            ],
        }
    )

    handler = WorkflowCatalogToolHandler(
        workflow_loader=loader,
        workflow_classifier=DummyWorkflowClassifier(),
        vector_store=DummyVectorStore(),
    )

    result = handler.import_workflow_content(content=content, content_type="json")

    assert result["status"] == "imported"
    assert result["workflow_name"] == "inline_workflow"
    assert result["source_type"] == "inline"
    assert Path(result["saved_path"]).exists()
    assert Path(result["saved_path"]).parent == workflows_dir
    assert registry.reload_calls == 1


def test_import_workflow_chunked_json(workflow_setup):
    workflows_dir, _incoming_dir, loader, registry = workflow_setup
    content = json.dumps(
        {
            "name": "chunked_workflow",
            "steps": [
                {
                    "tool": "modeling_create_primitive",
                    "params": {"primitive_type": "Cube"},
                }
            ],
        }
    )

    handler = WorkflowCatalogToolHandler(
        workflow_loader=loader,
        workflow_classifier=DummyWorkflowClassifier(),
        vector_store=DummyVectorStore(),
    )

    init = handler.begin_import_session(content_type="json", source_name="chunked.json")
    session_id = init["session_id"]

    midpoint = len(content) // 2
    first_chunk = content[:midpoint]
    second_chunk = content[midpoint:]

    handler.append_import_chunk(session_id=session_id, chunk_data=first_chunk, chunk_index=0)
    handler.append_import_chunk(session_id=session_id, chunk_data=second_chunk, chunk_index=1)

    result = handler.finalize_import_session(session_id=session_id)

    assert result["status"] == "imported"
    assert result["workflow_name"] == "chunked_workflow"
    assert result["source_type"] == "chunked"
    assert result["session_id"] == session_id
    assert Path(result["saved_path"]).exists()
    assert Path(result["saved_path"]).parent == workflows_dir
    assert registry.reload_calls == 1
