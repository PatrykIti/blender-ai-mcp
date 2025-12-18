import difflib
import logging
from typing import Any, Dict, List, Optional, Tuple

from server.domain.tools.workflow_catalog import IWorkflowCatalogTool
from server.router.domain.interfaces.i_workflow_intent_classifier import (
    IWorkflowIntentClassifier,
)
from server.router.infrastructure.workflow_loader import WorkflowLoader

logger = logging.getLogger(__name__)


class WorkflowCatalogToolHandler(IWorkflowCatalogTool):
    """Read-only workflow exploration (no Router execution)."""

    def __init__(
        self,
        workflow_loader: WorkflowLoader,
        workflow_classifier: Optional[IWorkflowIntentClassifier] = None,
    ):
        self._workflow_loader = workflow_loader
        self._workflow_classifier = workflow_classifier

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

