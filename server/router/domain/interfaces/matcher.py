"""
Matcher Interfaces for Ensemble Matching System.

TASK-053-2: Abstract interfaces for workflow matchers and modifier extractors.

These interfaces enable the ensemble matcher to run multiple matchers
(keyword, semantic, pattern) in parallel and aggregate their results.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from server.router.domain.entities.ensemble import MatcherResult, ModifierResult


class IMatcher(ABC):
    """Abstract interface for workflow matchers.

    All matchers implement this interface to enable ensemble matching.
    Each matcher runs independently and returns a MatcherResult.

    Matchers:
    - KeywordMatcher: Exact keyword matching from workflow definitions
    - SemanticMatcher: LaBSE embedding-based semantic similarity
    - PatternMatcher: Geometry pattern detection (tower_like, phone_like, etc.)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Matcher name for logging and aggregation.

        Returns:
            Matcher identifier (e.g., "keyword", "semantic", "pattern").
        """
        pass

    @property
    @abstractmethod
    def weight(self) -> float:
        """Weight for score aggregation (0.0-1.0).

        Higher weight = more influence on final decision.
        Sum of all weights should be ~1.0 for normalized scores.

        Standard weights (TASK-053):
        - KeywordMatcher: 0.40 (most precise, low false positive rate)
        - SemanticMatcher: 0.40 (most flexible, context-aware)
        - PatternMatcher: 0.15 (geometry-aware, very confident when triggered)

        Returns:
            Weight value between 0.0 and 1.0.
        """
        pass

    @abstractmethod
    def match(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> MatcherResult:
        """Match prompt to workflow.

        Args:
            prompt: User prompt/goal (e.g., "create a smartphone", "prosty stół").
            context: Optional scene context dict (used by PatternMatcher).
                    Contains: mode, active_object, selected_objects, topology, etc.
                    PatternMatcher requires 'detected_pattern' key.

        Returns:
            MatcherResult with workflow name and confidence.
            If no match, returns MatcherResult with workflow_name=None, confidence=0.0.
        """
        pass


class IModifierExtractor(ABC):
    """Interface for modifier/tag extraction.

    Extracts parametric modifiers from user prompt for a given workflow.
    Always runs regardless of which matcher "wins" the workflow selection.

    This is CRITICAL for TASK-053: The bug fix ensures modifiers like
    "proste nogi" (straight legs) are always extracted and applied,
    even if semantic matcher wins over keyword matcher.

    Example:
        Prompt: "prosty stół z prostymi nogami"
        Workflow: picnic_table_workflow
        Modifiers: {"leg_angle_left": 0, "leg_angle_right": 0}
    """

    @abstractmethod
    def extract(self, prompt: str, workflow_name: str) -> ModifierResult:
        """Extract modifiers from prompt for given workflow.

        Scans prompt for modifier keywords defined in workflow definition.
        Returns all matching variable overrides.

        Args:
            prompt: User prompt (e.g., "prosty stół z prostymi nogami").
            workflow_name: Target workflow to check modifiers for.

        Returns:
            ModifierResult with extracted parameters.
            If no modifiers found, returns ModifierResult with empty dicts.

        Example:
            >>> extractor.extract("prosty stół z prostymi nogami", "picnic_table_workflow")
            ModifierResult(
                modifiers={"leg_angle_left": 0, "leg_angle_right": 0},
                matched_keywords=["prosty", "proste nogi"],
                confidence_map={"prosty": 1.0, "proste nogi": 1.0}
            )
        """
        pass
