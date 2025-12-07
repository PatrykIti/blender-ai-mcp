"""
Base Workflow Classes and Interfaces.

Provides abstract base class for workflow definitions.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow.

    Attributes:
        tool: The MCP tool name to call.
        params: Parameters to pass to the tool.
        description: Human-readable description of the step.
        condition: Optional condition expression for conditional execution.
        optional: If True, step can be skipped for low-confidence matches.
        tags: Semantic tags for filtering (e.g., ["bench", "seating"]).
    """

    tool: str
    params: Dict[str, Any]
    description: Optional[str] = None
    condition: Optional[str] = None  # Optional condition expression
    optional: bool = False  # Can be skipped for LOW confidence matches
    tags: List[str] = field(default_factory=list)  # Semantic tags for filtering

    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary representation."""
        return {
            "tool": self.tool,
            "params": dict(self.params),
            "description": self.description,
            "condition": self.condition,
            "optional": self.optional,
            "tags": list(self.tags),
        }


@dataclass
class WorkflowDefinition:
    """Complete workflow definition."""

    name: str
    description: str
    steps: List[WorkflowStep]
    trigger_pattern: Optional[str] = None
    trigger_keywords: List[str] = field(default_factory=list)
    sample_prompts: List[str] = field(default_factory=list)
    category: str = "general"
    author: str = "system"
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "trigger_pattern": self.trigger_pattern,
            "trigger_keywords": self.trigger_keywords,
            "sample_prompts": self.sample_prompts,
            "category": self.category,
            "author": self.author,
            "version": self.version,
            "steps": [step.to_dict() for step in self.steps],
        }


class BaseWorkflow(ABC):
    """Abstract base class for workflow implementations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique workflow name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description."""
        pass

    @property
    @abstractmethod
    def trigger_pattern(self) -> Optional[str]:
        """Pattern name that triggers this workflow."""
        pass

    @property
    @abstractmethod
    def trigger_keywords(self) -> List[str]:
        """Keywords that trigger this workflow."""
        pass

    @property
    def sample_prompts(self) -> List[str]:
        """Sample prompts for semantic matching with LaBSE.

        These prompts are embedded by LaBSE for semantic similarity matching.
        Include variations in multiple languages if needed (LaBSE supports 109 languages).

        Returns:
            List of sample prompts that should trigger this workflow.
        """
        return []

    @abstractmethod
    def get_steps(self, params: Optional[Dict[str, Any]] = None) -> List[WorkflowStep]:
        """Get workflow steps, optionally customized by parameters.

        Args:
            params: Optional parameters to customize the workflow.

        Returns:
            List of workflow steps.
        """
        pass

    def get_definition(self, params: Optional[Dict[str, Any]] = None) -> WorkflowDefinition:
        """Get complete workflow definition.

        Args:
            params: Optional parameters to customize the workflow.

        Returns:
            Complete workflow definition.
        """
        return WorkflowDefinition(
            name=self.name,
            description=self.description,
            steps=self.get_steps(params),
            trigger_pattern=self.trigger_pattern,
            trigger_keywords=self.trigger_keywords,
            sample_prompts=self.sample_prompts,
        )

    def matches_pattern(self, pattern_name: str) -> bool:
        """Check if workflow matches a pattern.

        Args:
            pattern_name: Name of the pattern to match.

        Returns:
            True if workflow matches.
        """
        return self.trigger_pattern == pattern_name

    def matches_keywords(self, text: str) -> bool:
        """Check if workflow matches keywords in text.

        Args:
            text: Text to search for keywords.

        Returns:
            True if any keyword matches.
        """
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in self.trigger_keywords)
