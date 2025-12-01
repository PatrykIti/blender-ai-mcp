"""
Pattern Detector Interface.

Abstract interface for detecting geometry patterns.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from server.router.domain.entities.scene_context import SceneContext
from server.router.domain.entities.pattern import (
    PatternType,
    DetectedPattern,
    PatternMatchResult,
)


class IPatternDetector(ABC):
    """Abstract interface for geometry pattern detection.

    Detects patterns like tower_like, phone_like, table_like in object geometry.
    """

    @abstractmethod
    def detect(self, context: SceneContext) -> PatternMatchResult:
        """Detect patterns in the given scene context.

        Args:
            context: Scene context with object information.

        Returns:
            PatternMatchResult with all detected patterns.
        """
        pass

    @abstractmethod
    def detect_pattern(
        self,
        context: SceneContext,
        pattern_type: PatternType,
    ) -> DetectedPattern:
        """Check for a specific pattern type.

        Args:
            context: Scene context with object information.
            pattern_type: Specific pattern to check for.

        Returns:
            DetectedPattern with confidence score.
        """
        pass

    @abstractmethod
    def get_best_match(
        self,
        context: SceneContext,
        threshold: float = 0.5,
    ) -> Optional[DetectedPattern]:
        """Get the best matching pattern above threshold.

        Args:
            context: Scene context with object information.
            threshold: Minimum confidence threshold.

        Returns:
            Best matching DetectedPattern or None.
        """
        pass

    @abstractmethod
    def get_supported_patterns(self) -> List[PatternType]:
        """Get list of patterns this detector can identify.

        Returns:
            List of supported PatternType values.
        """
        pass
