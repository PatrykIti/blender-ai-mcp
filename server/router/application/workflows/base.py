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

        id: Optional unique identifier for this step (TASK-056-4).
        depends_on: List of step IDs this step depends on (TASK-056-4).
        timeout: Maximum execution time in seconds (TASK-056-4).
        max_retries: Maximum number of retry attempts on failure (TASK-056-4).
        retry_delay: Delay in seconds between retry attempts (TASK-056-4).
        on_failure: Action on failure: "fail", "skip", "retry" (TASK-056-4).
        priority: Execution priority for parallel steps (higher first) (TASK-056-4).

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

    # TASK-056-4: Execution control and dependencies
    id: Optional[str] = None  # Unique step identifier
    depends_on: List[str] = field(default_factory=list)  # Step ID dependencies
    timeout: Optional[float] = None  # Timeout in seconds
    max_retries: int = 0  # Number of retry attempts
    retry_delay: float = 1.0  # Delay between retries in seconds
    on_failure: str = "fail"  # "fail", "skip", "retry"
    priority: int = 0  # Higher priority executes first in parallel scenarios

    def __post_init__(self):
        """Post-initialization to validate and store dynamic attribute names.

        TASK-055-FIX-6: Track which attributes were dynamically added from YAML
        (beyond the standard dataclass fields) for semantic filtering.

        TASK-056-4: Validate execution control parameters.
        """
        # Store known fields for introspection
        self._known_fields = {
            "tool", "params", "description", "condition",
            "optional", "disable_adaptation", "tags",
            "id", "depends_on", "timeout", "max_retries",
            "retry_delay", "on_failure", "priority"
        }

        # TASK-056-4: Validate on_failure
        valid_on_failure = {"fail", "skip", "retry"}
        if self.on_failure not in valid_on_failure:
            raise ValueError(
                f"Invalid on_failure value '{self.on_failure}'. "
                f"Must be one of: {valid_on_failure}"
            )

        # TASK-056-4: Validate timeout
        if self.timeout is not None and self.timeout <= 0:
            raise ValueError(f"Timeout must be positive, got: {self.timeout}")

        # TASK-056-4: Validate max_retries
        if self.max_retries < 0:
            raise ValueError(f"max_retries must be non-negative, got: {self.max_retries}")

        # TASK-056-4: Validate retry_delay
        if self.retry_delay < 0:
            raise ValueError(f"retry_delay must be non-negative, got: {self.retry_delay}")

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

        # TASK-056-4: Include execution control fields
        if self.id is not None:
            result["id"] = self.id
        if self.depends_on:
            result["depends_on"] = list(self.depends_on)
        if self.timeout is not None:
            result["timeout"] = self.timeout
        if self.max_retries > 0:
            result["max_retries"] = self.max_retries
        if self.retry_delay != 1.0:
            result["retry_delay"] = self.retry_delay
        if self.on_failure != "fail":
            result["on_failure"] = self.on_failure
        if self.priority != 0:
            result["priority"] = self.priority

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
