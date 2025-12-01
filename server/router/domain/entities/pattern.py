"""
Pattern Entity.

Data classes for geometry pattern detection.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


class PatternType(Enum):
    """Known geometry pattern types."""

    TOWER_LIKE = "tower_like"
    PHONE_LIKE = "phone_like"
    TABLE_LIKE = "table_like"
    PILLAR_LIKE = "pillar_like"
    WHEEL_LIKE = "wheel_like"
    SCREEN_AREA = "screen_area"
    BOX_LIKE = "box_like"
    SPHERE_LIKE = "sphere_like"
    CYLINDER_LIKE = "cylinder_like"
    UNKNOWN = "unknown"


@dataclass
class DetectedPattern:
    """Represents a detected geometry pattern.

    Attributes:
        pattern_type: Type of pattern detected.
        confidence: Confidence score (0.0 to 1.0).
        suggested_workflow: Name of suggested workflow for this pattern.
        metadata: Additional pattern-specific data.
        detection_rules: Rules that triggered this detection.
    """

    pattern_type: PatternType
    confidence: float
    suggested_workflow: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    detection_rules: List[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        """Get pattern name as string."""
        return self.pattern_type.value

    @property
    def is_confident(self) -> bool:
        """Check if detection is confident (> 0.7)."""
        return self.confidence > 0.7

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pattern_type": self.pattern_type.value,
            "confidence": self.confidence,
            "suggested_workflow": self.suggested_workflow,
            "metadata": self.metadata,
            "detection_rules": self.detection_rules,
        }

    @classmethod
    def unknown(cls) -> "DetectedPattern":
        """Create unknown pattern result."""
        return cls(
            pattern_type=PatternType.UNKNOWN,
            confidence=0.0,
        )


@dataclass
class PatternMatchResult:
    """Result of pattern matching against multiple patterns.

    Attributes:
        patterns: List of detected patterns, sorted by confidence.
        best_match: Pattern with highest confidence (if any above threshold).
        threshold: Confidence threshold used for matching.
    """

    patterns: List[DetectedPattern] = field(default_factory=list)
    best_match: Optional[DetectedPattern] = None
    threshold: float = 0.5

    @property
    def has_match(self) -> bool:
        """Check if any pattern matched above threshold."""
        return self.best_match is not None and self.best_match.confidence >= self.threshold

    @property
    def best_pattern_name(self) -> Optional[str]:
        """Get name of best matching pattern."""
        if self.best_match:
            return self.best_match.name
        return None

    def get_pattern(self, pattern_type: PatternType) -> Optional[DetectedPattern]:
        """Get specific pattern by type."""
        for pattern in self.patterns:
            if pattern.pattern_type == pattern_type:
                return pattern
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "patterns": [p.to_dict() for p in self.patterns],
            "best_match": self.best_match.to_dict() if self.best_match else None,
            "threshold": self.threshold,
            "has_match": self.has_match,
        }


# Pattern detection rules (used by GeometryPatternDetector)
PATTERN_RULES: Dict[PatternType, Dict[str, Any]] = {
    PatternType.TOWER_LIKE: {
        "description": "Tall vertical structure",
        "rules": ["height > width * 3", "height > depth * 3"],
        "suggested_workflow": "tower_workflow",
    },
    PatternType.PHONE_LIKE: {
        "description": "Flat rectangular thin object",
        "rules": ["is_flat", "0.4 < aspect_xy < 0.7", "z < 0.15"],
        "suggested_workflow": "phone_workflow",
    },
    PatternType.TABLE_LIKE: {
        "description": "Flat horizontal surface",
        "rules": ["is_flat", "not is_tall"],
        "suggested_workflow": "table_workflow",
    },
    PatternType.PILLAR_LIKE: {
        "description": "Tall cubic structure",
        "rules": ["is_tall", "is_cubic"],
        "suggested_workflow": "pillar_workflow",
    },
    PatternType.WHEEL_LIKE: {
        "description": "Flat circular object",
        "rules": ["is_flat", "0.9 < aspect_xy < 1.1"],
        "suggested_workflow": "wheel_workflow",
    },
    PatternType.SCREEN_AREA: {
        "description": "Inset face area (screen/display)",
        "rules": ["has_inset_face", "face_on_top"],
        "suggested_workflow": "screen_cutout_workflow",
    },
    PatternType.BOX_LIKE: {
        "description": "Roughly cubic shape",
        "rules": ["is_cubic", "not is_flat", "not is_tall"],
        "suggested_workflow": None,
    },
    PatternType.SPHERE_LIKE: {
        "description": "Spherical shape",
        "rules": ["is_cubic", "high_face_count", "smooth_normals"],
        "suggested_workflow": None,
    },
    PatternType.CYLINDER_LIKE: {
        "description": "Cylindrical shape",
        "rules": ["circular_cross_section", "extruded"],
        "suggested_workflow": None,
    },
}
