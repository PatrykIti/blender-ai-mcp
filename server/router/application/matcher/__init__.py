"""
Matcher Module.

Provides semantic matching capabilities for workflows.
TASK-046-3: Legacy SemanticWorkflowMatcher
TASK-053: Ensemble Matching System
"""

from server.router.application.matcher.semantic_workflow_matcher import (
    SemanticWorkflowMatcher,
    MatchResult,
)
from server.router.application.matcher.keyword_matcher import KeywordMatcher
from server.router.application.matcher.semantic_matcher import SemanticMatcher
from server.router.application.matcher.pattern_matcher import PatternMatcher
from server.router.application.matcher.modifier_extractor import ModifierExtractor
from server.router.application.matcher.ensemble_aggregator import EnsembleAggregator
from server.router.application.matcher.ensemble_matcher import EnsembleMatcher

__all__ = [
    # Legacy (TASK-046)
    "SemanticWorkflowMatcher",
    "MatchResult",
    # Ensemble Matching (TASK-053)
    "KeywordMatcher",
    "SemanticMatcher",
    "PatternMatcher",
    "ModifierExtractor",
    "EnsembleAggregator",
    "EnsembleMatcher",
]
