import difflib
import logging
import uuid
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
        self._import_sessions: Dict[str, Dict[str, Any]] = {}

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

        suffix = path.suffix.lower()
        format_hint = "json" if suffix == ".json" else "yaml"
        result = self._import_loaded_workflow(
            workflow=workflow,
            overwrite=overwrite,
            format_hint=format_hint,
            source_path=str(path),
        )
        result["source_type"] = "file"
        return result

    def import_workflow_content(
        self,
        content: str,
        content_type: Optional[str] = None,
        overwrite: Optional[bool] = None,
        source_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not content:
            return {"status": "error", "message": "content is required for import"}

        try:
            workflow, resolved_format = self._workflow_loader.load_content(
                content=content,
                source_name=source_name,
                format_hint=content_type,
            )
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to load workflow content: {e}",
                "source_name": source_name or "inline",
            }

        result = self._import_loaded_workflow(
            workflow=workflow,
            overwrite=overwrite,
            format_hint=resolved_format,
            source_path=source_name or "inline",
        )
        result["source_type"] = "inline"
        result["content_type"] = resolved_format
        return result

    def begin_import_session(
        self,
        content_type: Optional[str] = None,
        source_name: Optional[str] = None,
        total_chunks: Optional[int] = None,
    ) -> Dict[str, Any]:
        session_id = uuid.uuid4().hex
        normalized_type = (content_type or "").strip().lower() or None
        if normalized_type in {"yml", "yaml", "text/yaml", "application/x-yaml"}:
            normalized_type = "yaml"
        elif normalized_type in {"json", "application/json"}:
            normalized_type = "json"
        elif normalized_type:
            return {
                "status": "error",
                "message": f"Unsupported content_type: {content_type}",
            }

        self._import_sessions[session_id] = {
            "chunks": [],
            "indexed_chunks": {},
            "use_indexed": False,
            "bytes_received": 0,
            "content_type": normalized_type,
            "source_name": source_name,
            "total_chunks": total_chunks,
        }

        return {
            "status": "ready",
            "session_id": session_id,
            "content_type": normalized_type,
            "source_name": source_name,
            "total_chunks": total_chunks,
        }

    def append_import_chunk(
        self,
        session_id: str,
        chunk_data: str,
        chunk_index: Optional[int] = None,
        total_chunks: Optional[int] = None,
    ) -> Dict[str, Any]:
        session = self._import_sessions.get(session_id)
        if session is None:
            return {"status": "error", "message": "Unknown session_id"}
        if chunk_data is None:
            return {"status": "error", "message": "chunk_data is required"}

        if total_chunks is not None:
            session["total_chunks"] = total_chunks

        if session["use_indexed"]:
            if chunk_index is None:
                return {"status": "error", "message": "chunk_index required for indexed session"}
            session["indexed_chunks"][int(chunk_index)] = chunk_data
        else:
            if chunk_index is None:
                session["chunks"].append(chunk_data)
            else:
                indexed = {}
                for idx, data in enumerate(session["chunks"]):
                    indexed[idx] = data
                session["chunks"] = []
                session["indexed_chunks"] = indexed
                session["use_indexed"] = True
                session["indexed_chunks"][int(chunk_index)] = chunk_data

        session["bytes_received"] += len(chunk_data)
        received = (
            len(session["indexed_chunks"])
            if session["use_indexed"]
            else len(session["chunks"])
        )

        return {
            "status": "chunk_received",
            "session_id": session_id,
            "received_chunks": received,
            "total_chunks": session.get("total_chunks"),
            "bytes_received": session["bytes_received"],
        }

    def finalize_import_session(
        self,
        session_id: str,
        overwrite: Optional[bool] = None,
    ) -> Dict[str, Any]:
        session = self._import_sessions.get(session_id)
        if session is None:
            return {"status": "error", "message": "Unknown session_id"}

        total_chunks = session.get("total_chunks")
        if session["use_indexed"]:
            if total_chunks is not None and len(session["indexed_chunks"]) < total_chunks:
                missing = sorted(
                    set(range(int(total_chunks))) - set(session["indexed_chunks"].keys())
                )
                return {
                    "status": "error",
                    "message": "Missing chunks for session",
                    "missing_indices": missing,
                }
            chunks = [session["indexed_chunks"][idx] for idx in sorted(session["indexed_chunks"])]
        else:
            if total_chunks is not None and len(session["chunks"]) < total_chunks:
                return {
                    "status": "error",
                    "message": "Missing chunks for session",
                }
            chunks = list(session["chunks"])

        content = "".join(chunks)
        result = self.import_workflow_content(
            content=content,
            content_type=session.get("content_type"),
            overwrite=overwrite,
            source_name=session.get("source_name") or f"session:{session_id}",
        )
        result["source_type"] = "chunked"
        result["session_id"] = session_id
        result["received_chunks"] = len(chunks)
        result["bytes_received"] = session["bytes_received"]

        if result.get("status") != "needs_input":
            self._import_sessions.pop(session_id, None)
        return result

    def abort_import_session(self, session_id: str) -> Dict[str, Any]:
        if session_id in self._import_sessions:
            self._import_sessions.pop(session_id, None)
            return {"status": "aborted", "session_id": session_id}
        return {"status": "error", "message": "Unknown session_id"}

    def _import_loaded_workflow(
        self,
        workflow: Any,
        overwrite: Optional[bool],
        format_hint: str,
        source_path: str,
    ) -> Dict[str, Any]:
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
            "source_path": source_path,
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
