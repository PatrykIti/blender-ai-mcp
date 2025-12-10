"""
Base Workflow Classes and Interfaces.

Provides abstract base class for workflow definitions.

TASK-055: Added parameters field for interactive parameter resolution.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from server.router.domain.entities.parameter import ParameterSchema


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow.

    Attributes:
        tool: The MCP tool name to call.
        params: Parameters to pass to the tool.
        description: Human-readable description of the step.
        condition: Optional condition expression for conditional execution.
        optional: If True, step can be skipped for low-confidence matches.
        disable_adaptation: If True, skip semantic filtering (treat as core step).
        tags: Semantic tags for filtering (e.g., ["bench", "seating"]).

    Dynamic Attributes (TASK-055-FIX-6 Phase 2):
        Custom boolean parameters loaded from YAML are set as instance attributes.
        These act as semantic filters (e.g., add_bench=True, include_stretchers=False).
    """

    tool: str
    params: Dict[str, Any]
    description: Optional[str] = None
    condition: Optional[str] = None  # Optional condition expression
    optional: bool = False  # Can be skipped for LOW confidence matches
    disable_adaptation: bool = False  # TASK-055-FIX-5: Skip adaptation filtering
    tags: List[str] = field(default_factory=list)  # Semantic tags for filtering

    def __post_init__(self):
        """Post-initialization to store dynamic attribute names.

        TASK-055-FIX-6: Track which attributes were dynamically added from YAML
        (beyond the standard dataclass fields) for semantic filtering.
        """
        # Store known fields for introspection
        self._known_fields = {
            "tool", "params", "description", "condition",
            "optional", "disable_adaptation", "tags"
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary representation.

        Includes both standard fields and dynamic semantic filter attributes.
        """
        result = {
            "tool": self.tool,
            "params": dict(self.params),
            "description": self.description,
            "condition": self.condition,
            "optional": self.optional,
            "disable_adaptation": self.disable_adaptation,
            "tags": list(self.tags),
        }

        # TASK-055-FIX-6: Include dynamic attributes
        for attr_name in dir(self):
            if (not attr_name.startswith("_") and
                attr_name not in self._known_fields and
                attr_name not in {"to_dict"} and
                not callable(getattr(self, attr_name))):
                result[attr_name] = getattr(self, attr_name)

        return result


@dataclass
class WorkflowDefinition:
    """Complete workflow definition.

    Attributes:
        name: Unique workflow identifier.
        description: Human-readable description.
        steps: List of workflow steps.
        trigger_pattern: Pattern name that triggers this workflow.
        trigger_keywords: Keywords that trigger this workflow.
        sample_prompts: Sample prompts for LaBSE semantic matching.
        category: Workflow category (e.g., "furniture", "architecture").
        author: Author name.
        version: Version string.
        defaults: Default variable values for $variable substitution.
        modifiers: Keyword → variable mappings for parametric adaptation.
        parameters: Parameter schemas for interactive LLM resolution (TASK-055).
            Maps parameter names to ParameterSchema objects defining constraints,
            semantic hints, and defaults for three-tier resolution.
    """

    name: str
    description: str
    steps: List[WorkflowStep]
    trigger_pattern: Optional[str] = None
    trigger_keywords: List[str] = field(default_factory=list)
    sample_prompts: List[str] = field(default_factory=list)
    category: str = "general"
    author: str = "system"
    version: str = "1.0.0"
    defaults: Dict[str, Any] = field(default_factory=dict)
    modifiers: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)  # TASK-055: ParameterSchema dict

    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary representation."""
        result = {
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
        if self.defaults:
            result["defaults"] = dict(self.defaults)
        if self.modifiers:
            result["modifiers"] = {k: dict(v) for k, v in self.modifiers.items()}
        if self.parameters:
            # Convert ParameterSchema objects to dicts if needed
            result["parameters"] = {
                k: (v.to_dict() if hasattr(v, "to_dict") else v)
                for k, v in self.parameters.items()
            }
        return result


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
