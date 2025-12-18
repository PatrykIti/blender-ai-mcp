"""
Geometry Pattern Detector Implementation.

Detects patterns like tower_like, phone_like, table_like in object geometry.
"""

from typing import Optional, List

from server.router.domain.interfaces.i_pattern_detector import IPatternDetector
from server.router.domain.entities.scene_context import SceneContext, ProportionInfo
from server.router.domain.entities.pattern import (
    PatternType,
    DetectedPattern,
    PatternMatchResult,
    PATTERN_RULES,
)
from server.router.application.analyzers.proportion_calculator import calculate_proportions


class GeometryPatternDetector(IPatternDetector):
    """Implementation of geometry pattern detection.

    Detects patterns like tower_like, phone_like, table_like
    based on object proportions and geometry.
    """

    def __init__(self, default_threshold: float = 0.5):
        """Initialize detector.

        Args:
            default_threshold: Default confidence threshold.
        """
        self._default_threshold = default_threshold

    def detect(self, context: SceneContext) -> PatternMatchResult:
        """Detect patterns in the given scene context.

        Args:
            context: Scene context with object information.

        Returns:
            PatternMatchResult with all detected patterns.
        """
        patterns = []

        # Check all known patterns
        for pattern_type in self.get_supported_patterns():
            detected = self.detect_pattern(context, pattern_type)
            if detected.confidence > 0:
                patterns.append(detected)

        # Sort by confidence (highest first)
        patterns.sort(key=lambda p: p.confidence, reverse=True)

        # Find best match above threshold
        best_match = None
        for pattern in patterns:
            if pattern.confidence >= self._default_threshold:
                best_match = pattern
                break

        return PatternMatchResult(
            patterns=patterns,
            best_match=best_match,
            threshold=self._default_threshold,
        )

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
        # Get proportions
        proportions = context.proportions
        if not proportions:
            # Try to calculate from dimensions
            dims = context.get_active_dimensions()
            if dims:
                proportions = calculate_proportions(dims)
            else:
                return DetectedPattern.unknown()

        # Detect based on pattern type
        if pattern_type == PatternType.TOWER_LIKE:
            return self._detect_tower_like(proportions)
        elif pattern_type == PatternType.PHONE_LIKE:
            return self._detect_phone_like(proportions)
        elif pattern_type == PatternType.TABLE_LIKE:
            return self._detect_table_like(proportions)
        elif pattern_type == PatternType.PILLAR_LIKE:
            return self._detect_pillar_like(proportions)
        elif pattern_type == PatternType.WHEEL_LIKE:
            return self._detect_wheel_like(proportions)
        elif pattern_type == PatternType.BOX_LIKE:
            return self._detect_box_like(proportions)
        else:
            return DetectedPattern.unknown()

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
        result = self.detect(context)
        if result.best_match and result.best_match.confidence >= threshold:
            return result.best_match
        return None

    def get_supported_patterns(self) -> List[PatternType]:
        """Get list of patterns this detector can identify.

        Returns:
            List of supported PatternType values.
        """
        return [
            PatternType.TOWER_LIKE,
            PatternType.PHONE_LIKE,
            PatternType.TABLE_LIKE,
            PatternType.PILLAR_LIKE,
            PatternType.WHEEL_LIKE,
            PatternType.BOX_LIKE,
        ]

    def _detect_tower_like(self, proportions: ProportionInfo) -> DetectedPattern:
        """Detect tower-like pattern.

        Rules:
        - height > width * 3
        - height > depth * 3
        """
        rules_matched = []
        confidence = 0.0

        # Check if tall
        if proportions.is_tall:
            rules_matched.append("is_tall")
            confidence += 0.4

        # Check aspect ratios (height = z, width = x, depth = y)
        if proportions.aspect_xz < 0.33:  # x/z < 0.33 means z > x*3
            rules_matched.append("height > width * 3")
            confidence += 0.3

        if proportions.aspect_yz < 0.33:  # y/z < 0.33 means z > y*3
            rules_matched.append("height > depth * 3")
            confidence += 0.3

        return DetectedPattern(
            pattern_type=PatternType.TOWER_LIKE,
            confidence=min(confidence, 1.0),
            suggested_workflow=PATTERN_RULES.get(PatternType.TOWER_LIKE, {}).get("suggested_workflow"),
            detection_rules=rules_matched,
            metadata={"proportions": proportions.to_dict()},
        )

    def _detect_phone_like(self, proportions: ProportionInfo) -> DetectedPattern:
        """Detect phone-like pattern.

        Rules:
        - is_flat
        - 0.4 < aspect_xy < 0.7
        - z < 0.15 (thin)
        """
        rules_matched = []
        confidence = 0.0

        # Check if flat
        if proportions.is_flat:
            rules_matched.append("is_flat")
            confidence += 0.4

        # Check aspect ratio (phone-like rectangle)
        if 0.4 < proportions.aspect_xy < 0.7:
            rules_matched.append("0.4 < aspect_xy < 0.7")
            confidence += 0.4

        # Check if thin (using aspect ratios as proxy)
        # If z is dominant, it's not phone-like
        if proportions.dominant_axis != "z" and proportions.is_flat:
            rules_matched.append("thin")
            confidence += 0.2

        return DetectedPattern(
            pattern_type=PatternType.PHONE_LIKE,
            confidence=min(confidence, 1.0),
            suggested_workflow=PATTERN_RULES.get(PatternType.PHONE_LIKE, {}).get("suggested_workflow"),
            detection_rules=rules_matched,
            metadata={"proportions": proportions.to_dict()},
        )

    def _detect_table_like(self, proportions: ProportionInfo) -> DetectedPattern:
        """Detect table-like pattern.

        Rules:
        - is_flat
        - not is_tall
        """
        rules_matched = []
        confidence = 0.0

        if proportions.is_flat:
            rules_matched.append("is_flat")
            confidence += 0.5

        if not proportions.is_tall:
            rules_matched.append("not is_tall")
            confidence += 0.3

        # Bonus for wider shapes
        if proportions.is_wide or proportions.aspect_xy > 0.8:
            rules_matched.append("wide surface")
            confidence += 0.2

        return DetectedPattern(
            pattern_type=PatternType.TABLE_LIKE,
            confidence=min(confidence, 1.0),
            suggested_workflow=PATTERN_RULES.get(PatternType.TABLE_LIKE, {}).get("suggested_workflow"),
            detection_rules=rules_matched,
            metadata={"proportions": proportions.to_dict()},
        )

    def _detect_pillar_like(self, proportions: ProportionInfo) -> DetectedPattern:
        """Detect pillar-like pattern.

        Rules:
        - is_tall
        - is_cubic (in x-y plane)
        """
        rules_matched = []
        confidence = 0.0

        if proportions.is_tall:
            rules_matched.append("is_tall")
            confidence += 0.5

        # Check if x and y are similar (cubic in horizontal plane)
        if 0.7 < proportions.aspect_xy < 1.3:
            rules_matched.append("cubic in x-y plane")
            confidence += 0.5

        return DetectedPattern(
            pattern_type=PatternType.PILLAR_LIKE,
            confidence=min(confidence, 1.0),
            suggested_workflow=PATTERN_RULES.get(PatternType.PILLAR_LIKE, {}).get("suggested_workflow"),
            detection_rules=rules_matched,
            metadata={"proportions": proportions.to_dict()},
        )

    def _detect_wheel_like(self, proportions: ProportionInfo) -> DetectedPattern:
        """Detect wheel-like pattern.

        Rules:
        - is_flat
        - aspect_xy ≈ 1.0 (circular in x-y)
        """
        rules_matched = []
        confidence = 0.0

        if proportions.is_flat:
            rules_matched.append("is_flat")
            confidence += 0.4

        # Check if circular (x ≈ y)
        if 0.9 < proportions.aspect_xy < 1.1:
            rules_matched.append("0.9 < aspect_xy < 1.1")
            confidence += 0.6

        return DetectedPattern(
            pattern_type=PatternType.WHEEL_LIKE,
            confidence=min(confidence, 1.0),
            suggested_workflow=PATTERN_RULES.get(PatternType.WHEEL_LIKE, {}).get("suggested_workflow"),
            detection_rules=rules_matched,
            metadata={"proportions": proportions.to_dict()},
        )

    def _detect_box_like(self, proportions: ProportionInfo) -> DetectedPattern:
        """Detect box-like pattern.

        Rules:
        - is_cubic
        - not is_flat
        - not is_tall
        """
        rules_matched = []
        confidence = 0.0

        if proportions.is_cubic:
            rules_matched.append("is_cubic")
            confidence += 0.5

        if not proportions.is_flat:
            rules_matched.append("not is_flat")
            confidence += 0.25

        if not proportions.is_tall:
            rules_matched.append("not is_tall")
            confidence += 0.25

        return DetectedPattern(
            pattern_type=PatternType.BOX_LIKE,
            confidence=min(confidence, 1.0),
            suggested_workflow=PATTERN_RULES.get(PatternType.BOX_LIKE, {}).get("suggested_workflow"),
            detection_rules=rules_matched,
            metadata={"proportions": proportions.to_dict()},
        )
