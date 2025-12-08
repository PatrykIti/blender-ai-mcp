"""
Parameter Resolution Domain Entities.

Entities for interactive parameter resolution system that enables
LLM-driven parameter value discovery with semantic learning.

TASK-055
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass
class ParameterSchema:
    """Schema definition for a workflow parameter.

    Defines the structure, constraints, and semantic hints for a parameter
    that can be interactively resolved via LLM when not specified in YAML.

    Attributes:
        name: Parameter name (e.g., "leg_angle_left").
        type: Parameter type ("float", "int", "bool", "string").
        range: Optional min/max range for numeric types.
        default: Default value if not resolved.
        description: Human-readable description for LLM context.
        semantic_hints: Keywords that relate to this parameter for matching.
        group: Optional group name for related parameters (e.g., "leg_angles").
    """

    name: str
    type: str  # "float", "int", "bool", "string"
    range: Optional[Tuple[float, float]] = None
    default: Any = None
    description: str = ""
    semantic_hints: List[str] = field(default_factory=list)
    group: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate parameter schema."""
        valid_types = {"float", "int", "bool", "string"}
        if self.type not in valid_types:
            raise ValueError(
                f"Invalid parameter type '{self.type}'. "
                f"Must be one of: {valid_types}"
            )

        if self.range is not None:
            if len(self.range) != 2:
                raise ValueError(
                    f"Range must be a tuple of (min, max), got: {self.range}"
                )
            if self.range[0] > self.range[1]:
                raise ValueError(
                    f"Range min ({self.range[0]}) must be <= max ({self.range[1]})"
                )

    def validate_value(self, value: Any) -> bool:
        """Check if a value is valid for this parameter.

        Args:
            value: The value to validate.

        Returns:
            True if value is valid, False otherwise.
        """
        if self.type == "float":
            if not isinstance(value, (int, float)):
                return False
            if self.range is not None:
                return self.range[0] <= float(value) <= self.range[1]
            return True

        elif self.type == "int":
            if not isinstance(value, int) or isinstance(value, bool):
                return False
            if self.range is not None:
                return self.range[0] <= value <= self.range[1]
            return True

        elif self.type == "bool":
            return isinstance(value, bool)

        elif self.type == "string":
            return isinstance(value, str)

        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "type": self.type,
            "range": list(self.range) if self.range else None,
            "default": self.default,
            "description": self.description,
            "semantic_hints": self.semantic_hints,
            "group": self.group,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParameterSchema":
        """Create from dictionary.

        Args:
            data: Dictionary with parameter schema fields.

        Returns:
            ParameterSchema instance.
        """
        range_value = data.get("range")
        if range_value is not None:
            range_value = tuple(range_value)

        return cls(
            name=data["name"],
            type=data.get("type", "float"),
            range=range_value,
            default=data.get("default"),
            description=data.get("description", ""),
            semantic_hints=data.get("semantic_hints", []),
            group=data.get("group"),
        )


@dataclass
class StoredMapping:
    """A learned parameter mapping from LLM interaction.

    Represents a semantic association between a natural language context
    and a parameter value, stored for future reuse via LaBSE similarity.

    Attributes:
        context: Original prompt fragment that triggered the mapping.
        value: The resolved parameter value.
        similarity: How well this mapping matched the query (0.0-1.0).
        workflow_name: Name of the workflow this mapping belongs to.
        parameter_name: Name of the parameter this value applies to.
        usage_count: Number of times this mapping has been reused.
        created_at: Timestamp when mapping was first created.
    """

    context: str
    value: Any
    similarity: float
    workflow_name: str
    parameter_name: str
    usage_count: int = 1
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate stored mapping."""
        if not self.context:
            raise ValueError("Context cannot be empty")
        if not 0.0 <= self.similarity <= 1.0:
            raise ValueError(
                f"Similarity must be between 0.0 and 1.0, got: {self.similarity}"
            )
        if not self.workflow_name:
            raise ValueError("Workflow name cannot be empty")
        if not self.parameter_name:
            raise ValueError("Parameter name cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "context": self.context,
            "value": self.value,
            "similarity": self.similarity,
            "workflow_name": self.workflow_name,
            "parameter_name": self.parameter_name,
            "usage_count": self.usage_count,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
        }


@dataclass
class UnresolvedParameter:
    """Parameter that needs LLM input for resolution.

    Created when a parameter is mentioned in the prompt but cannot be
    resolved via YAML modifiers or learned mappings.

    Attributes:
        name: Parameter name.
        schema: Full parameter schema with constraints.
        context: Extracted prompt fragment related to this parameter.
        relevance: LaBSE similarity score indicating how strongly
            the prompt relates to this parameter (0.0-1.0).
    """

    name: str
    schema: ParameterSchema
    context: str
    relevance: float

    def __post_init__(self) -> None:
        """Validate unresolved parameter."""
        if not 0.0 <= self.relevance <= 1.0:
            raise ValueError(
                f"Relevance must be between 0.0 and 1.0, got: {self.relevance}"
            )

    def to_question_dict(self) -> Dict[str, Any]:
        """Convert to question format for LLM interaction.

        Returns:
            Dictionary with question fields for needs_parameter_input response.
        """
        return {
            "parameter": self.name,
            "context": self.context,
            "description": self.schema.description,
            "range": list(self.schema.range) if self.schema.range else None,
            "default": self.schema.default,
            "type": self.schema.type,
            "group": self.schema.group,
        }


@dataclass
class ParameterResolutionResult:
    """Result of parameter resolution attempt.

    Contains both resolved parameters (from YAML, learned, or defaults)
    and unresolved parameters that need LLM input.

    Attributes:
        resolved: Dictionary of parameter names to resolved values.
        unresolved: List of parameters needing LLM input.
        resolution_sources: Maps parameter names to resolution source
            ("yaml_modifier", "learned", "default").
    """

    resolved: Dict[str, Any] = field(default_factory=dict)
    unresolved: List[UnresolvedParameter] = field(default_factory=list)
    resolution_sources: Dict[str, str] = field(default_factory=dict)

    @property
    def needs_llm_input(self) -> bool:
        """True if there are unresolved parameters needing LLM input."""
        return len(self.unresolved) > 0

    @property
    def is_complete(self) -> bool:
        """True if all parameters are resolved."""
        return len(self.unresolved) == 0

    def get_questions(self) -> List[Dict[str, Any]]:
        """Get list of questions for LLM interaction.

        Returns:
            List of question dictionaries for needs_parameter_input response.
        """
        return [p.to_question_dict() for p in self.unresolved]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "resolved": self.resolved,
            "unresolved": [
                {
                    "name": p.name,
                    "context": p.context,
                    "relevance": p.relevance,
                    "schema": p.schema.to_dict(),
                }
                for p in self.unresolved
            ],
            "resolution_sources": self.resolution_sources,
            "needs_llm_input": self.needs_llm_input,
            "is_complete": self.is_complete,
        }
