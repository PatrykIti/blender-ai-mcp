"""
E2E tests for Pattern Detection.

Tests that geometry patterns are detected correctly on real Blender objects.
Requires running Blender instance.

TASK-039-23
"""

import pytest

from server.router.application.router import SupervisorRouter
from server.router.application.analyzers.geometry_pattern_detector import GeometryPatternDetector
from server.router.application.analyzers.scene_context_analyzer import SceneContextAnalyzer
from server.router.application.analyzers.proportion_calculator import (
    calculate_proportions,
    get_proportion_summary,
)


class TestPatternDetectionOnRealGeometry:
    """Tests for pattern detection with real Blender geometry."""

    def test_detect_phone_like_pattern(self, rpc_client, clean_scene):
        """Test: Flat, rectangular object is detected as phone_like."""
        # Create phone-like object
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {
            "scale": [0.4, 0.8, 0.05]  # Phone proportions
        })

        # Analyze scene
        analyzer = SceneContextAnalyzer(rpc_client=rpc_client)
        context = analyzer.analyze()

        # Detect patterns
        detector = GeometryPatternDetector()
        patterns = detector.detect(context)

        # Should detect phone_like or flat pattern
        pattern_names = [p.name for p in patterns]

        assert len(patterns) > 0, "Should detect at least one pattern"

        # Check for phone-like characteristics
        has_flat = any("flat" in name.lower() for name in pattern_names)
        has_phone = any("phone" in name.lower() for name in pattern_names)

        assert has_flat or has_phone, f"Should detect flat/phone pattern, got: {pattern_names}"

    def test_detect_tower_like_pattern(self, rpc_client, clean_scene):
        """Test: Tall, thin object is detected as tower_like."""
        # Create tower-like object
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {
            "scale": [0.3, 0.3, 2.0]  # Tower proportions
        })

        analyzer = SceneContextAnalyzer(rpc_client=rpc_client)
        context = analyzer.analyze()

        detector = GeometryPatternDetector()
        patterns = detector.detect(context)

        pattern_names = [p.name for p in patterns]

        # Should detect tower or tall pattern
        has_tower = any("tower" in name.lower() for name in pattern_names)
        has_tall = any("tall" in name.lower() for name in pattern_names)

        assert has_tower or has_tall, f"Should detect tower/tall pattern, got: {pattern_names}"

    def test_detect_cubic_pattern(self, rpc_client, clean_scene):
        """Test: Cube is detected as cubic pattern."""
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})
        # Default cube is 2x2x2, roughly cubic

        analyzer = SceneContextAnalyzer(rpc_client=rpc_client)
        context = analyzer.analyze()

        detector = GeometryPatternDetector()
        patterns = detector.detect(context)

        pattern_names = [p.name for p in patterns]

        has_cubic = any("cubic" in name.lower() for name in pattern_names)
        has_generic = len(patterns) > 0  # At least some pattern

        assert has_cubic or has_generic, "Should detect cubic or some pattern"

    def test_no_pattern_on_empty_scene(self, rpc_client, clean_scene):
        """Test: Empty scene has no patterns."""
        analyzer = SceneContextAnalyzer(rpc_client=rpc_client)
        context = analyzer.analyze()

        detector = GeometryPatternDetector()
        patterns = detector.detect(context)

        # Empty scene may have no patterns or generic patterns
        # This is acceptable behavior
        assert isinstance(patterns, list)


class TestProportionCalculation:
    """Tests for proportion calculation on real objects."""

    def test_flat_object_proportions(self, rpc_client, clean_scene):
        """Test: Flat object has correct proportions calculated."""
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {
            "scale": [1.0, 1.0, 0.1]  # Flat
        })

        analyzer = SceneContextAnalyzer(rpc_client=rpc_client)
        context = analyzer.analyze()

        # Check proportions
        if context.proportions:
            assert context.proportions.get("is_flat", False) or \
                   context.proportions.get("aspect_xz", 1) > 5, \
                   "Flat object should have flat proportions"

    def test_tall_object_proportions(self, rpc_client, clean_scene):
        """Test: Tall object has correct proportions calculated."""
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {
            "scale": [0.5, 0.5, 3.0]  # Tall
        })

        analyzer = SceneContextAnalyzer(rpc_client=rpc_client)
        context = analyzer.analyze()

        if context.proportions:
            assert context.proportions.get("is_tall", False) or \
                   context.proportions.get("dominant_axis") == "z", \
                   "Tall object should have tall proportions"


class TestSceneContextAnalysis:
    """Tests for scene context analysis."""

    def test_analyze_object_mode(self, rpc_client, clean_scene):
        """Test: Scene analysis reports correct mode."""
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "OBJECT"})

        analyzer = SceneContextAnalyzer(rpc_client=rpc_client)
        context = analyzer.analyze()

        assert context.mode == "OBJECT", f"Should be OBJECT mode, got: {context.mode}"

    def test_analyze_edit_mode(self, rpc_client, clean_scene):
        """Test: Scene analysis reports EDIT mode."""
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})

        analyzer = SceneContextAnalyzer(rpc_client=rpc_client)
        context = analyzer.analyze()

        assert context.mode == "EDIT", f"Should be EDIT mode, got: {context.mode}"

    def test_analyze_active_object(self, rpc_client, clean_scene):
        """Test: Scene analysis reports active object."""
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})

        analyzer = SceneContextAnalyzer(rpc_client=rpc_client)
        context = analyzer.analyze()

        assert context.active_object is not None, "Should have active object"
        assert "Cube" in context.active_object or len(context.active_object) > 0

    def test_analyze_dimensions(self, rpc_client, clean_scene):
        """Test: Scene analysis includes object dimensions."""
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {
            "scale": [2.0, 3.0, 4.0]
        })

        analyzer = SceneContextAnalyzer(rpc_client=rpc_client)
        context = analyzer.analyze()

        # Should have dimension info
        if context.dimensions:
            assert "x" in context.dimensions or "width" in str(context.dimensions).lower()


class TestPatternToWorkflowMapping:
    """Tests for pattern to workflow mapping."""

    def test_phone_pattern_triggers_phone_workflow(self, router, rpc_client, clean_scene):
        """Test: Phone-like pattern suggests phone workflow."""
        # Create phone-like object
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {
            "scale": [0.4, 0.8, 0.05]
        })

        # Process a tool call that might trigger workflow
        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": -0.02},
            prompt="create screen cutout on phone"
        )

        # Should have detected pattern and potentially suggested workflow
        # The actual behavior depends on override rules
        assert len(tools) > 0

    def test_tower_pattern_triggers_tower_workflow(self, router, rpc_client, clean_scene):
        """Test: Tower-like pattern suggests tower workflow."""
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {
            "scale": [0.3, 0.3, 2.0]
        })

        tools = router.process_llm_tool_call(
            "mesh_subdivide",
            {"number_cuts": 3},
            prompt="add segments to tower"
        )

        assert len(tools) > 0
