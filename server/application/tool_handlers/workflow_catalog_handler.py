import difflib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from server.domain.tools.workflow_catalog import IWorkflowCatalogTool
from server.router.domain.interfaces.i_workflow_intent_classifier import (
    IWorkflowIntentClassifier,
)
from server.router.domain.interfaces.i_vector_store import VectorNamespace
from server.router.infrastructure.workflow_loader import WorkflowLoader

logger = logging.getLogger(__name__)


class WorkflowCatalogToolHandler(IWorkflowCatalogTool):
    """Workflow exploration and import (no Router execution)."""

    def __init__(
        self,
        workflow_loader: WorkflowLoader,
        workflow_classifier: Optional[IWorkflowIntentClassifier] = None,
        vector_store: Optional[Any] = None,
    ):
        self._workflow_loader = workflow_loader
        self._workflow_classifier = workflow_classifier
        self._vector_store = vector_store

    def list_workflows(self) -> Dict[str, Any]:
        workflows = self._workflow_loader.load_all()
        items: List[Dict[str, Any]] = []

        for workflow_name in sorted(workflows.keys()):
            workflow = workflows[workflow_name]
            items.append(
                {
                    "name": workflow.name,
                    "description": workflow.description,
                    "category": workflow.category,
                    "version": workflow.version,
                    "steps_count": len(workflow.steps),
                    "trigger_keywords_count": len(getattr(workflow, "trigger_keywords", []) or []),
                    "sample_prompts_count": len(getattr(workflow, "sample_prompts", []) or []),
                    "parameters_count": len(getattr(workflow, "parameters", {}) or {}),
                }
            )

        return {
            "workflows_dir": str(self._workflow_loader.workflows_dir),
            "count": len(items),
            "workflows": items,
        }

    def get_workflow(self, workflow_name: str) -> Dict[str, Any]:
        workflows = self._workflow_loader.load_all()

        workflow = workflows.get(workflow_name)
        if workflow is None:
            available = sorted(workflows.keys())
            suggestions = difflib.get_close_matches(workflow_name, available, n=5, cutoff=0.35)
            return {
                "error": f"Workflow not found: {workflow_name}",
                "available": available,
                "suggestions": suggestions,
            }

        return {
            "workflow_name": workflow.name,
            "steps_count": len(workflow.steps),
            "workflow": workflow.to_dict(),
        }

    def search_workflows(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.0,
    ) -> Dict[str, Any]:
        workflows = self._workflow_loader.load_all()
        if not workflows:
            return {"error": "No workflows available", "count": 0, "results": []}

        semantic_results: List[Tuple[str, float]] = []
        search_type = "keyword"

        if self._workflow_classifier is not None:
            try:
                self._workflow_classifier.load_workflow_embeddings(workflows)
                effective_threshold = 0.000001 if threshold == 0.0 else threshold
                semantic_results = self._workflow_classifier.find_similar(
                    query,
                    top_k=top_k,
                    threshold=effective_threshold,
                )
                if semantic_results:
                    search_type = "semantic"
            except Exception as e:
                logger.warning(f"Semantic workflow search failed, falling back to keyword search: {e}")

        results: List[Dict[str, Any]] = []

        if semantic_results:
            for workflow_name, score in semantic_results:
                wf = workflows.get(workflow_name)
                results.append(
                    {
                        "workflow_name": workflow_name,
                        "score": round(float(score), 4),
                        "description": getattr(wf, "description", None) if wf else None,
                        "category": getattr(wf, "category", None) if wf else None,
                        "steps_count": len(getattr(wf, "steps", []) or []) if wf else None,
                    }
                )
        else:
            results = self._search_workflows_keyword(workflows, query, top_k)

        return {
            "query": query,
            "search_type": search_type,
            "count": len(results),
            "results": results,
        }

    def _search_workflows_keyword(
        self,
        workflows: Dict[str, Any],
        query: str,
        top_k: int,
    ) -> List[Dict[str, Any]]:
        query_lower = query.strip().lower()
        tokens = [t for t in query_lower.split() if t]

        scored: List[Tuple[float, str]] = []
        for workflow_name, wf in workflows.items():
            name = (getattr(wf, "name", workflow_name) or "").lower()
            description = (getattr(wf, "description", "") or "").lower()
            keywords = [str(k).lower() for k in (getattr(wf, "trigger_keywords", []) or [])]
            text = " ".join([name, description, *keywords])

            score = 0.0
            if query_lower and query_lower in text:
                score += 1.0

            for token in tokens:
                if token in text:
                    score += 0.2

            if score > 0:
                scored.append((score, workflow_name))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[: max(top_k, 0)]

        results: List[Dict[str, Any]] = []
        for score, workflow_name in top:
            wf = workflows[workflow_name]
            results.append(
                {
                    "workflow_name": workflow_name,
                    "score": round(score, 4),
                    "description": getattr(wf, "description", ""),
                    "category": getattr(wf, "category", None),
                    "steps_count": len(getattr(wf, "steps", []) or []),
                }
            )

        return results

    def import_workflow(
        self,
        filepath: str,
        overwrite: Optional[bool] = None,
    ) -> Dict[str, Any]:
        if not filepath:
            return {"status": "error", "message": "filepath is required for import"}

        path = Path(filepath).expanduser()
        try:
            workflow = self._workflow_loader.load_file(path)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to load workflow file: {e}",
                "filepath": str(path),
            }

        workflow_name = workflow.name
        existing_definition = self._workflow_loader.get_workflow(workflow_name)
        existing_files = self._find_existing_workflow_files(workflow_name)
        vector_ids = self._get_vector_workflow_ids(workflow_name)

        conflicts = {
            "definition_loaded": existing_definition is not None,
            "files": [str(p) for p in existing_files],
            "vector_store_records": len(vector_ids),
        }
        has_conflict = bool(
            conflicts["definition_loaded"]
            or conflicts["files"]
            or conflicts["vector_store_records"]
        )

        overwrite_value = self._coerce_overwrite(overwrite)
        if has_conflict and overwrite_value is None:
            return {
                "status": "needs_input",
                "workflow_name": workflow_name,
                "message": (
                    f"Workflow '{workflow_name}' already exists. "
                    "Set overwrite=true to replace or overwrite=false to skip."
                ),
                "conflicts": conflicts,
            }

        if has_conflict and overwrite_value is False:
            return {
                "status": "skipped",
                "workflow_name": workflow_name,
                "message": "Import skipped by user",
                "conflicts": conflicts,
            }

        format_hint = "yaml"
        suffix = path.suffix.lower()
        if suffix == ".json":
            format_hint = "json"

        saved_path = self._workflow_loader.save_workflow(
            workflow=workflow,
            filename=workflow_name,
            format=format_hint,
        )

        removed_files: List[str] = []
        removed_embeddings = 0
        if has_conflict and overwrite_value is True:
            removed_files = self._remove_existing_workflow_files(
                workflow_name,
                keep_path=Path(saved_path),
            )
            removed_embeddings = self._delete_vector_workflow_records(vector_ids)

        workflows = self._workflow_loader.reload()

        try:
            from server.router.application.workflows.registry import get_workflow_registry

            registry = get_workflow_registry()
            registry.load_custom_workflows(reload=True)
        except Exception as e:
            logger.warning(f"Failed to reload workflow registry: {e}")

        embeddings_reloaded = False
        if self._workflow_classifier is not None:
            try:
                self._workflow_classifier.load_workflow_embeddings(workflows)
                embeddings_reloaded = True
            except Exception as e:
                logger.warning(f"Failed to reload workflow embeddings: {e}")

        return {
            "status": "imported",
            "workflow_name": workflow_name,
            "saved_path": str(saved_path),
            "source_path": str(path),
            "overwritten": has_conflict,
            "removed_files": removed_files,
            "removed_embeddings": removed_embeddings,
            "workflows_dir": str(self._workflow_loader.workflows_dir),
            "embeddings_reloaded": embeddings_reloaded,
        }

    def _coerce_overwrite(self, overwrite: Optional[bool]) -> Optional[bool]:
        if overwrite is None or isinstance(overwrite, bool):
            return overwrite
        if isinstance(overwrite, str):
            normalized = overwrite.strip().lower()
            if normalized in {"true", "1", "yes", "y", "tak"}:
                return True
            if normalized in {"false", "0", "no", "n", "nie"}:
                return False
        return None

    def _find_existing_workflow_files(self, workflow_name: str) -> List[Path]:
        workflows_dir = self._workflow_loader.workflows_dir
        extensions = (".yaml", ".yml", ".json")
        matches = []
        for ext in extensions:
            candidate = workflows_dir / f"{workflow_name}{ext}"
            if candidate.exists():
                matches.append(candidate)
        return matches

    def _remove_existing_workflow_files(
        self,
        workflow_name: str,
        keep_path: Optional[Path] = None,
    ) -> List[str]:
        removed = []
        for path in self._find_existing_workflow_files(workflow_name):
            if keep_path and path.resolve() == keep_path.resolve():
                continue
            try:
                path.unlink()
                removed.append(str(path))
            except Exception as e:
                logger.warning(f"Failed to remove workflow file {path}: {e}")
        return removed

    def _get_vector_workflow_ids(self, workflow_name: str) -> List[str]:
        store = self._vector_store
        if store is None:
            return []
        get_ids = getattr(store, "get_all_ids", None)
        if not callable(get_ids):
            return []
        try:
            ids = get_ids(VectorNamespace.WORKFLOWS)
        except Exception as e:
            logger.warning(f"Failed to read workflow IDs from vector store: {e}")
            return []

        matched = []
        for record_id in ids:
            if self._workflow_id_matches(record_id, workflow_name):
                matched.append(record_id)
        return matched

    def _delete_vector_workflow_records(self, ids: List[str]) -> int:
        store = self._vector_store
        if store is None or not ids:
            return 0
        try:
            return store.delete(ids, VectorNamespace.WORKFLOWS)
        except Exception as e:
            logger.warning(f"Failed to delete workflow embeddings: {e}")
            return 0

    @staticmethod
    def _workflow_id_matches(record_id: str, workflow_name: str) -> bool:
        if record_id == workflow_name:
            return True
        return record_id.split("__", 1)[0] == workflow_name
