"""
Router Domain Entities.

Pure data classes with no external dependencies.
"""

from server.router.domain.entities.tool_call import (
    InterceptedToolCall,
    CorrectedToolCall,
    ToolCallSequence,
)
from server.router.domain.entities.scene_context import (
    ObjectInfo,
    TopologyInfo,
    ProportionInfo,
    SceneContext,
)
from server.router.domain.entities.pattern import (
    PatternType,
    DetectedPattern,
    PatternMatchResult,
    PATTERN_RULES,
)
from server.router.domain.entities.firewall_result import (
    FirewallAction,
    FirewallRuleType,
    FirewallViolation,
    FirewallResult,
)
from server.router.domain.entities.override_decision import (
    OverrideReason,
    ReplacementTool,
    OverrideDecision,
)
from server.router.domain.entities.ensemble import (
    MatcherResult,
    ModifierResult,
    EnsembleResult,
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
]
