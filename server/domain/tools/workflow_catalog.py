from abc import ABC, abstractmethod
from typing import Any, Dict


class IWorkflowCatalogTool(ABC):
    """Read-only access to workflow definitions (no execution).

    Intended for:
    - Listing available workflows
    - Inspecting workflow metadata and steps
    - Searching for similar workflows (semantic/keyword) to guide manual modeling
    """

    @abstractmethod
    def list_workflows(self) -> Dict[str, Any]:
        """List all available workflows with summary metadata."""
        raise NotImplementedError

    @abstractmethod
    def get_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Get a workflow definition (including steps) by name."""
        raise NotImplementedError

    @abstractmethod
    def search_workflows(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.0,
    ) -> Dict[str, Any]:
        """Search for workflows similar to a query (no execution)."""
        raise NotImplementedError

