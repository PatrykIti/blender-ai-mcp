"""
Override Decision Entity.

Data class for tool override decisions.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class OverrideReason:
    """Reason for an override decision.

    Attributes:
        rule_name: Name of the override rule that triggered.
        description: Human-readable description of why.
        pattern_match: Pattern that triggered override (if applicable).
        confidence: Confidence in the override decision.
    """

    rule_name: str
    description: str
    pattern_match: Optional[str] = None
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_name": self.rule_name,
            "description": self.description,
            "pattern_match": self.pattern_match,
            "confidence": self.confidence,
        }


@dataclass
class ReplacementTool:
    """A replacement tool in an override.

    Attributes:
        tool_name: Name of the replacement tool.
        params: Parameters for the tool.
        inherit_params: List of param names to inherit from original.
        description: What this tool does in the workflow.
    """

    tool_name: str
    params: Dict[str, Any] = field(default_factory=dict)
    inherit_params: List[str] = field(default_factory=list)
    description: str = ""

    def resolve_params(self, original_params: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameters, inheriting from original where specified.

        Args:
            original_params: Original parameters from LLM call.

        Returns:
            Resolved parameters dictionary.
        """
        resolved = dict(self.params)

        # Inherit specified parameters from original
        for param_name in self.inherit_params:
            if param_name in original_params:
                resolved[param_name] = original_params[param_name]

        # Also handle $param_name syntax in values
        for key, value in list(resolved.items()):
            if isinstance(value, str) and value.startswith("$"):
                orig_key = value[1:]
                if orig_key in original_params:
                    resolved[key] = original_params[orig_key]

        return resolved

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tool_name": self.tool_name,
            "params": self.params,
            "inherit_params": self.inherit_params,
            "description": self.description,
        }


@dataclass
class OverrideDecision:
    """Decision about whether to override a tool call.

    Attributes:
        should_override: Whether the tool should be overridden.
        reasons: List of reasons for the override.
        replacement_tools: List of replacement tools.
        is_workflow_expansion: Whether this expands to a workflow.
        workflow_name: Name of the workflow if expanded.
    """

    should_override: bool
    reasons: List[OverrideReason] = field(default_factory=list)
    replacement_tools: List[ReplacementTool] = field(default_factory=list)
    is_workflow_expansion: bool = False
    workflow_name: Optional[str] = None

    @property
    def reason_summary(self) -> str:
        """Get summary of override reasons."""
        if not self.reasons:
            return "No override"
        return "; ".join(r.description for r in self.reasons)

    @property
    def replacement_count(self) -> int:
        """Number of replacement tools."""
        return len(self.replacement_tools)

    def get_resolved_tools(self, original_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of resolved tool calls for execution.

        Args:
            original_params: Original parameters from LLM call.

        Returns:
            List of tool call dictionaries.
        """
        return [
            {
                "tool": tool.tool_name,
                "params": tool.resolve_params(original_params),
            }
            for tool in self.replacement_tools
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "should_override": self.should_override,
            "reasons": [r.to_dict() for r in self.reasons],
            "replacement_tools": [t.to_dict() for t in self.replacement_tools],
            "is_workflow_expansion": self.is_workflow_expansion,
            "workflow_name": self.workflow_name,
        }

    @classmethod
    def no_override(cls) -> "OverrideDecision":
        """Create a no-override decision."""
        return cls(should_override=False)

    @classmethod
    def override_with_tools(
        cls,
        tools: List[ReplacementTool],
        reasons: List[OverrideReason],
    ) -> "OverrideDecision":
        """Create an override decision with replacement tools."""
        return cls(
            should_override=True,
            reasons=reasons,
            replacement_tools=tools,
        )

    @classmethod
    def expand_to_workflow(
        cls,
        workflow_name: str,
        tools: List[ReplacementTool],
        reason: str,
    ) -> "OverrideDecision":
        """Create a workflow expansion decision."""
        return cls(
            should_override=True,
            reasons=[OverrideReason(
                rule_name="workflow_expansion",
                description=reason,
            )],
            replacement_tools=tools,
            is_workflow_expansion=True,
            workflow_name=workflow_name,
        )
