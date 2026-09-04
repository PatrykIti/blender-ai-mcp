"""
Router Domain Entities.

Pure data classes with no external dependencies.
"""

from server.router.domain.entities.ensemble import (
    EnsembleResult,
    MatcherResult,
    ModifierResult,
)
from server.router.domain.entities.firewall_result import (
    FirewallAction,
    FirewallResult,
    FirewallRuleType,
    FirewallViolation,
)
from server.router.domain.entities.override_decision import (
    OverrideDecision,
    OverrideReason,
    ReplacementTool,
)
from server.router.domain.entities.parameter import (
    ParameterResolutionResult,
    ParameterSchema,
    StoredMapping,
    UnresolvedParameter,
)
from server.router.domain.entities.pattern import (
    PATTERN_RULES,
    DetectedPattern,
    PatternMatchResult,
    PatternType,
)
from server.router.domain.entities.scene_context import (
    ObjectInfo,
    ProportionInfo,
    SceneContext,
    TopologyInfo,
)
from server.router.domain.entities.tool_call import (
    CorrectedToolCall,
    InterceptedToolCall,
    ToolCallSequence,
)

__all__ = [
    # Tool Call
    "InterceptedToolCall",
    "CorrectedToolCall",
    "ToolCallSequence",
    # Scene Context
    "ObjectInfo",
    "TopologyInfo",
    "ProportionInfo",
    "SceneContext",
    # Pattern
    "PatternType",
    "DetectedPattern",
    "PatternMatchResult",
    "PATTERN_RULES",
    # Firewall
    "FirewallAction",
    "FirewallRuleType",
    "FirewallViolation",
    "FirewallResult",
    # Override
    "OverrideReason",
    "ReplacementTool",
    "OverrideDecision",
    # Ensemble (TASK-053)
    "MatcherResult",
    "ModifierResult",
    "EnsembleResult",
    # Parameter Resolution (TASK-055)
    "ParameterSchema",
    "StoredMapping",
    "UnresolvedParameter",
    "ParameterResolutionResult",
]
