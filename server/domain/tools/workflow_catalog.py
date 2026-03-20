from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IWorkflowCatalogTool(ABC):
    """Access to workflow definitions (no execution).

    Intended for:
    - Listing available workflows
    - Inspecting workflow metadata and steps
    - Searching for similar workflows (semantic/keyword) to guide manual modeling
    - Importing workflows from YAML/JSON files
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

    @abstractmethod
    def import_workflow(
        self,
        filepath: str,
        overwrite: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Import a workflow from a YAML/JSON file path."""
        raise NotImplementedError

    @abstractmethod
    def import_workflow_content(
        self,
        content: str,
        content_type: Optional[str] = None,
        overwrite: Optional[bool] = None,
        source_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Import a workflow from inline YAML/JSON content."""
        raise NotImplementedError

    @abstractmethod
    def begin_import_session(
        self,
        content_type: Optional[str] = None,
        source_name: Optional[str] = None,
        total_chunks: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Start a chunked workflow import session."""
        raise NotImplementedError

    @abstractmethod
    def append_import_chunk(
        self,
        session_id: str,
        chunk_data: str,
        chunk_index: Optional[int] = None,
        total_chunks: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Append a chunk to a workflow import session."""
        raise NotImplementedError

    @abstractmethod
    def finalize_import_session(
        self,
        session_id: str,
        overwrite: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Finalize a chunked workflow import session."""
        raise NotImplementedError

    @abstractmethod
    def abort_import_session(self, session_id: str) -> Dict[str, Any]:
        """Abort a chunked workflow import session."""
        raise NotImplementedError
