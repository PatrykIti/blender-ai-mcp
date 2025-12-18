"""
Unit tests for Geometry Pattern Detector.

Tests for GeometryPatternDetector implementation.
"""

import pytest

from server.router.application.analyzers.geometry_pattern_detector import GeometryPatternDetector
from server.router.application.analyzers.proportion_calculator import calculate_proportions
from server.router.domain.entities.scene_context import SceneContext, ObjectInfo, ProportionInfo
from server.router.domain.entities.pattern import PatternType, DetectedPattern, PatternMatchResult


class TestGeometryPatternDetectorBasic:
    """Test basic detector functionality."""

    def test_create_detector(self):
        """Test creating detector."""
        detector = GeometryPatternDetector()

        assert detector is not None

    def test_get_supported_patterns(self):
        """Test listing supported patterns."""
        detector = GeometryPatternDetector()

        patterns = detector.get_supported_patterns()

        assert PatternType.TOWER_LIKE in patterns
        assert PatternType.PHONE_LIKE in patterns
        assert PatternType.TABLE_LIKE in patterns
        assert PatternType.BOX_LIKE in patterns

    def test_detect_empty_context(self):
        """Test detection on empty context."""
        detector = GeometryPatternDetector()
        context = SceneContext.empty()

        result = detector.detect(context)

        assert isinstance(result, PatternMatchResult)


class TestTowerLikeDetection:
    """Test tower-like pattern detection."""

    def test_detect_tower(self):
        """Test detecting tower-like shape."""
        detector = GeometryPatternDetector()

        # Tower dimensions: 0.3 x 0.3 x 3.0
        proportions = calculate_proportions([0.3, 0.3, 3.0])
        context = SceneContext(proportions=proportions)

        pattern = detector.detect_pattern(context, PatternType.TOWER_LIKE)

        assert pattern.pattern_type == PatternType.TOWER_LIKE
        assert pattern.confidence > 0.7  # High confidence

    def test_cube_not_tower(self):
        """Test that cube is not tower-like."""
        detector = GeometryPatternDetector()

        proportions = calculate_proportions([1.0, 1.0, 1.0])
        context = SceneContext(proportions=proportions)

        pattern = detector.detect_pattern(context, PatternType.TOWER_LIKE)

        assert pattern.confidence < 0.5  # Low confidence

    def test_tower_suggested_workflow(self):
        """Test tower pattern has suggested workflow."""
        detector = GeometryPatternDetector()

        proportions = calculate_proportions([0.3, 0.3, 3.0])
        context = SceneContext(proportions=proportions)

        pattern = detector.detect_pattern(context, PatternType.TOWER_LIKE)

        assert pattern.suggested_workflow == "tower_workflow"


class TestPhoneLikeDetection:
    """Test phone-like pattern detection."""

    def test_detect_phone(self):
        """Test detecting phone-like shape."""
        detector = GeometryPatternDetector()

        # Phone dimensions: 0.4 x 0.8 x 0.05
        proportions = calculate_proportions([0.4, 0.8, 0.05])
        context = SceneContext(proportions=proportions)

        pattern = detector.detect_pattern(context, PatternType.PHONE_LIKE)

        assert pattern.pattern_type == PatternType.PHONE_LIKE
        assert pattern.confidence > 0.7

    def test_cube_not_phone(self):
        """Test that cube is not phone-like."""
        detector = GeometryPatternDetector()

        proportions = calculate_proportions([1.0, 1.0, 1.0])
        context = SceneContext(proportions=proportions)

        pattern = detector.detect_pattern(context, PatternType.PHONE_LIKE)

        assert pattern.confidence < 0.5

    def test_phone_suggested_workflow(self):
        """Test phone pattern has suggested workflow."""
        detector = GeometryPatternDetector()

        proportions = calculate_proportions([0.4, 0.8, 0.05])
        context = SceneContext(proportions=proportions)

        pattern = detector.detect_pattern(context, PatternType.PHONE_LIKE)

        assert pattern.suggested_workflow == "phone_workflow"


class TestTableLikeDetection:
    """Test table-like pattern detection."""

    def test_detect_table(self):
        """Test detecting table-like shape."""
        detector = GeometryPatternDetector()

        # Table dimensions: 2.0 x 1.5 x 0.1
        proportions = calculate_proportions([2.0, 1.5, 0.1])
        context = SceneContext(proportions=proportions)

        pattern = detector.detect_pattern(context, PatternType.TABLE_LIKE)

        assert pattern.pattern_type == PatternType.TABLE_LIKE
        assert pattern.confidence > 0.5

    def test_tall_object_not_table(self):
        """Test that tall object is not table-like."""
        detector = GeometryPatternDetector()

        proportions = calculate_proportions([1.0, 1.0, 5.0])
        context = SceneContext(proportions=proportions)

        pattern = detector.detect_pattern(context, PatternType.TABLE_LIKE)

        assert pattern.confidence < 0.5


class TestWheelLikeDetection:
    """Test wheel-like pattern detection."""

    def test_detect_wheel(self):
        """Test detecting wheel-like shape."""
        detector = GeometryPatternDetector()

        # Wheel: circular and flat
        proportions = calculate_proportions([1.0, 1.0, 0.1])
        context = SceneContext(proportions=proportions)

        pattern = detector.detect_pattern(context, PatternType.WHEEL_LIKE)

        assert pattern.pattern_type == PatternType.WHEEL_LIKE
        assert pattern.confidence > 0.7

    def test_rectangular_not_wheel(self):
        """Test that rectangular shape is not wheel-like."""
        detector = GeometryPatternDetector()

        proportions = calculate_proportions([2.0, 1.0, 0.1])
        context = SceneContext(proportions=proportions)

        pattern = detector.detect_pattern(context, PatternType.WHEEL_LIKE)

        assert pattern.confidence < 0.7


class TestBoxLikeDetection:
    """Test box-like pattern detection."""

    def test_detect_box(self):
        """Test detecting box-like shape."""
        detector = GeometryPatternDetector()

        # Cube is box-like
        proportions = calculate_proportions([1.0, 1.0, 1.0])
        context = SceneContext(proportions=proportions)

        pattern = detector.detect_pattern(context, PatternType.BOX_LIKE)

        assert pattern.pattern_type == PatternType.BOX_LIKE
        assert pattern.confidence > 0.7

    def test_flat_not_box(self):
        """Test that flat shape is not box-like."""
        detector = GeometryPatternDetector()

        proportions = calculate_proportions([2.0, 2.0, 0.1])
        context = SceneContext(proportions=proportions)

        pattern = detector.detect_pattern(context, PatternType.BOX_LIKE)

        assert pattern.confidence < 0.7


class TestPatternMatchResult:
    """Test full pattern matching."""

    def test_detect_returns_all_patterns(self):
        """Test that detect returns all patterns."""
        detector = GeometryPatternDetector()
        proportions = calculate_proportions([1.0, 1.0, 1.0])
        context = SceneContext(proportions=proportions)

        result = detector.detect(context)

        assert len(result.patterns) > 0

    def test_patterns_sorted_by_confidence(self):
        """Test that patterns are sorted by confidence."""
        detector = GeometryPatternDetector()
        proportions = calculate_proportions([1.0, 1.0, 1.0])
        context = SceneContext(proportions=proportions)

        result = detector.detect(context)

        # Check sorted descending
        for i in range(len(result.patterns) - 1):
            assert result.patterns[i].confidence >= result.patterns[i + 1].confidence

    def test_best_match_above_threshold(self):
        """Test best_match is above threshold."""
        detector = GeometryPatternDetector(default_threshold=0.5)
        proportions = calculate_proportions([1.0, 1.0, 1.0])  # Box-like
        context = SceneContext(proportions=proportions)

        result = detector.detect(context)

        if result.best_match:
            assert result.best_match.confidence >= 0.5


class TestGetBestMatch:
    """Test get_best_match method."""

    def test_get_best_match_tower(self):
        """Test getting best match for tower shape."""
        detector = GeometryPatternDetector()
        proportions = calculate_proportions([0.3, 0.3, 3.0])
        context = SceneContext(proportions=proportions)

        best = detector.get_best_match(context, threshold=0.5)

        assert best is not None
        assert best.pattern_type == PatternType.TOWER_LIKE

    def test_get_best_match_no_match(self):
        """Test get_best_match with high threshold."""
        detector = GeometryPatternDetector()
        proportions = calculate_proportions([1.0, 1.0, 1.0])
        context = SceneContext(proportions=proportions)

        best = detector.get_best_match(context, threshold=0.99)

        # May or may not have a match depending on exact confidence
        if best:
            assert best.confidence >= 0.99

    def test_get_best_match_from_dimensions(self):
        """Test get_best_match calculates proportions from dimensions."""
        detector = GeometryPatternDetector()
        context = SceneContext(
            objects=[
                ObjectInfo(
                    name="Phone",
                    type="MESH",
                    dimensions=[0.4, 0.8, 0.05],
                    active=True,
                )
            ]
        )

        best = detector.get_best_match(context, threshold=0.5)

        assert best is not None
        assert best.pattern_type == PatternType.PHONE_LIKE


class TestPatternMetadata:
    """Test pattern detection metadata."""

    def test_pattern_includes_rules(self):
        """Test that detected patterns include matched rules."""
        detector = GeometryPatternDetector()
        proportions = calculate_proportions([0.3, 0.3, 3.0])
        context = SceneContext(proportions=proportions)

        pattern = detector.detect_pattern(context, PatternType.TOWER_LIKE)

        assert len(pattern.detection_rules) > 0
        assert "is_tall" in pattern.detection_rules

    def test_pattern_includes_proportions_metadata(self):
        """Test that patterns include proportions in metadata."""
        detector = GeometryPatternDetector()
        proportions = calculate_proportions([1.0, 1.0, 1.0])
        context = SceneContext(proportions=proportions)

        pattern = detector.detect_pattern(context, PatternType.BOX_LIKE)

        assert "proportions" in pattern.metadata
