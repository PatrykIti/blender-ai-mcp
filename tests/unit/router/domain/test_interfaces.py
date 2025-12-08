"""
Tests for Router Domain Interfaces.

Task: TASK-039-3

These tests verify that interfaces are properly defined and can be implemented.
"""

import pytest
from abc import ABC
from typing import Dict, Any, List, Tuple, Optional

from server.router.domain.interfaces import (
    IToolInterceptor,
    ISceneAnalyzer,
    IPatternDetector,
    ICorrectionEngine,
    IOverrideEngine,
    IExpansionEngine,
    IFirewall,
    IIntentClassifier,
    # Ensemble Matcher (TASK-053)
    IMatcher,
    IModifierExtractor,
)
from server.router.domain.entities import (
    InterceptedToolCall,
    CorrectedToolCall,
    SceneContext,
    PatternType,
    DetectedPattern,
    PatternMatchResult,
    OverrideDecision,
    FirewallResult,
    # Ensemble (TASK-053)
    MatcherResult,
    ModifierResult,
)


class TestIToolInterceptor:
    """Tests for IToolInterceptor interface."""

    def test_is_abstract(self):
        """Verify interface is abstract."""
        assert issubclass(IToolInterceptor, ABC)

    def test_has_required_methods(self):
        """Verify interface has all required methods."""
        assert hasattr(IToolInterceptor, "intercept")
        assert hasattr(IToolInterceptor, "get_history")
        assert hasattr(IToolInterceptor, "clear_history")
        assert hasattr(IToolInterceptor, "get_session_calls")

    def test_can_implement(self):
        """Verify interface can be implemented."""

        class MockInterceptor(IToolInterceptor):
            def intercept(self, tool_name, params, prompt=None):
                return InterceptedToolCall(tool_name=tool_name, params=params)

            def get_history(self, limit=10):
                return []

            def clear_history(self):
                pass

            def get_session_calls(self, session_id):
                return []

        interceptor = MockInterceptor()
        result = interceptor.intercept("test_tool", {"a": 1})
        assert isinstance(result, InterceptedToolCall)


class TestISceneAnalyzer:
    """Tests for ISceneAnalyzer interface."""

    def test_is_abstract(self):
        """Verify interface is abstract."""
        assert issubclass(ISceneAnalyzer, ABC)

    def test_has_required_methods(self):
        """Verify interface has all required methods."""
        assert hasattr(ISceneAnalyzer, "analyze")
        assert hasattr(ISceneAnalyzer, "get_cached")
        assert hasattr(ISceneAnalyzer, "invalidate_cache")
        assert hasattr(ISceneAnalyzer, "get_mode")
        assert hasattr(ISceneAnalyzer, "has_selection")

    def test_can_implement(self):
        """Verify interface can be implemented."""

        class MockAnalyzer(ISceneAnalyzer):
            def analyze(self, object_name=None):
                return SceneContext()

            def get_cached(self):
                return None

            def invalidate_cache(self):
                pass

            def get_mode(self):
                return "OBJECT"

            def has_selection(self):
                return False

        analyzer = MockAnalyzer()
        result = analyzer.analyze()
        assert isinstance(result, SceneContext)


class TestIPatternDetector:
    """Tests for IPatternDetector interface."""

    def test_is_abstract(self):
        """Verify interface is abstract."""
        assert issubclass(IPatternDetector, ABC)

    def test_has_required_methods(self):
        """Verify interface has all required methods."""
        assert hasattr(IPatternDetector, "detect")
        assert hasattr(IPatternDetector, "detect_pattern")
        assert hasattr(IPatternDetector, "get_best_match")
        assert hasattr(IPatternDetector, "get_supported_patterns")

    def test_can_implement(self):
        """Verify interface can be implemented."""

        class MockDetector(IPatternDetector):
            def detect(self, context):
                return PatternMatchResult()

            def detect_pattern(self, context, pattern_type):
                return DetectedPattern.unknown()

            def get_best_match(self, context, threshold=0.5):
                return None

            def get_supported_patterns(self):
                return [PatternType.TOWER_LIKE, PatternType.PHONE_LIKE]

        detector = MockDetector()
        patterns = detector.get_supported_patterns()
        assert PatternType.TOWER_LIKE in patterns


class TestICorrectionEngine:
    """Tests for ICorrectionEngine interface."""

    def test_is_abstract(self):
        """Verify interface is abstract."""
        assert issubclass(ICorrectionEngine, ABC)

    def test_has_required_methods(self):
        """Verify interface has all required methods."""
        assert hasattr(ICorrectionEngine, "correct")
        assert hasattr(ICorrectionEngine, "clamp_parameters")
        assert hasattr(ICorrectionEngine, "get_required_mode")
        assert hasattr(ICorrectionEngine, "requires_selection")
        assert hasattr(ICorrectionEngine, "get_mode_switch_call")
        assert hasattr(ICorrectionEngine, "get_selection_call")

    def test_can_implement(self):
        """Verify interface can be implemented."""

        class MockCorrection(ICorrectionEngine):
            def correct(self, tool_name, params, context):
                return CorrectedToolCall(tool_name=tool_name, params=params), []

            def clamp_parameters(self, tool_name, params, context):
                return params, []

            def get_required_mode(self, tool_name):
                return "EDIT" if tool_name.startswith("mesh_") else "OBJECT"

            def requires_selection(self, tool_name):
                return tool_name in ["mesh_extrude", "mesh_bevel"]

            def get_mode_switch_call(self, target_mode):
                return CorrectedToolCall(
                    tool_name="system_set_mode",
                    params={"mode": target_mode},
                    is_injected=True,
                )

            def get_selection_call(self, selection_type="all"):
                return CorrectedToolCall(
                    tool_name="mesh_select",
                    params={"action": selection_type},
                    is_injected=True,
                )

        engine = MockCorrection()
        assert engine.get_required_mode("mesh_extrude") == "EDIT"
        assert engine.requires_selection("mesh_extrude")


class TestIOverrideEngine:
    """Tests for IOverrideEngine interface."""

    def test_is_abstract(self):
        """Verify interface is abstract."""
        assert issubclass(IOverrideEngine, ABC)

    def test_has_required_methods(self):
        """Verify interface has all required methods."""
        assert hasattr(IOverrideEngine, "check_override")
        assert hasattr(IOverrideEngine, "get_override_rules")
        assert hasattr(IOverrideEngine, "register_rule")
        assert hasattr(IOverrideEngine, "remove_rule")

    def test_can_implement(self):
        """Verify interface can be implemented."""

        class MockOverride(IOverrideEngine):
            def __init__(self):
                self.rules = {}

            def check_override(self, tool_name, params, context, pattern=None):
                return OverrideDecision.no_override()

            def get_override_rules(self):
                return list(self.rules.values())

            def register_rule(self, rule_name, trigger_tool, trigger_pattern, replacement_tools):
                self.rules[rule_name] = {
                    "trigger_tool": trigger_tool,
                    "replacement_tools": replacement_tools,
                }

            def remove_rule(self, rule_name):
                if rule_name in self.rules:
                    del self.rules[rule_name]
                    return True
                return False

        engine = MockOverride()
        result = engine.check_override("test", {}, SceneContext())
        assert not result.should_override


class TestIExpansionEngine:
    """Tests for IExpansionEngine interface."""

    def test_is_abstract(self):
        """Verify interface is abstract."""
        assert issubclass(IExpansionEngine, ABC)

    def test_has_required_methods(self):
        """Verify interface has all required methods."""
        assert hasattr(IExpansionEngine, "expand")
        assert hasattr(IExpansionEngine, "get_workflow")
        assert hasattr(IExpansionEngine, "register_workflow")
        assert hasattr(IExpansionEngine, "get_available_workflows")
        assert hasattr(IExpansionEngine, "expand_workflow")

    def test_can_implement(self):
        """Verify interface can be implemented."""

        class MockExpansion(IExpansionEngine):
            def __init__(self):
                self.workflows = {}

            def expand(self, tool_name, params, context, pattern=None):
                return None

            def get_workflow(self, workflow_name):
                return self.workflows.get(workflow_name)

            def register_workflow(self, name, steps, trigger_pattern=None, trigger_keywords=None):
                self.workflows[name] = steps

            def get_available_workflows(self):
                return list(self.workflows.keys())

            def expand_workflow(self, workflow_name, params):
                return []

        engine = MockExpansion()
        engine.register_workflow("test_workflow", [{"tool": "step1"}])
        assert "test_workflow" in engine.get_available_workflows()


class TestIFirewall:
    """Tests for IFirewall interface."""

    def test_is_abstract(self):
        """Verify interface is abstract."""
        assert issubclass(IFirewall, ABC)

    def test_has_required_methods(self):
        """Verify interface has all required methods."""
        assert hasattr(IFirewall, "validate")
        assert hasattr(IFirewall, "validate_sequence")
        assert hasattr(IFirewall, "can_auto_fix")
        assert hasattr(IFirewall, "get_firewall_rules")
        assert hasattr(IFirewall, "register_rule")
        assert hasattr(IFirewall, "enable_rule")
        assert hasattr(IFirewall, "disable_rule")

    def test_can_implement(self):
        """Verify interface can be implemented."""

        class MockFirewall(IFirewall):
            def validate(self, tool_call, context):
                return FirewallResult.allow()

            def validate_sequence(self, calls, context):
                return [self.validate(call, context) for call in calls]

            def can_auto_fix(self, tool_call, context):
                return True

            def get_firewall_rules(self):
                return []

            def register_rule(self, rule_name, tool_pattern, condition, action, fix_description=""):
                pass

            def enable_rule(self, rule_name):
                return True

            def disable_rule(self, rule_name):
                return True

        firewall = MockFirewall()
        call = CorrectedToolCall(tool_name="test", params={})
        result = firewall.validate(call, SceneContext())
        assert result.allowed


class TestIIntentClassifier:
    """Tests for IIntentClassifier interface."""

    def test_is_abstract(self):
        """Verify interface is abstract."""
        assert issubclass(IIntentClassifier, ABC)

    def test_has_required_methods(self):
        """Verify interface has all required methods."""
        assert hasattr(IIntentClassifier, "predict")
        assert hasattr(IIntentClassifier, "predict_top_k")
        assert hasattr(IIntentClassifier, "load_tool_embeddings")
        assert hasattr(IIntentClassifier, "is_loaded")
        assert hasattr(IIntentClassifier, "get_embedding")
        assert hasattr(IIntentClassifier, "similarity")

    def test_can_implement(self):
        """Verify interface can be implemented."""

        class MockClassifier(IIntentClassifier):
            def __init__(self):
                self._loaded = False

            def predict(self, prompt):
                return ("mesh_extrude", 0.9)

            def predict_top_k(self, prompt, k=5):
                return [("mesh_extrude", 0.9), ("mesh_bevel", 0.7)]

            def load_tool_embeddings(self, metadata):
                self._loaded = True

            def is_loaded(self):
                return self._loaded

            def get_embedding(self, text):
                return [0.1, 0.2, 0.3]

            def similarity(self, text1, text2):
                return 0.8

        classifier = MockClassifier()
        tool, confidence = classifier.predict("extrude")
        assert tool == "mesh_extrude"
        assert confidence > 0.5


class TestIMatcher:
    """Tests for IMatcher interface (TASK-053-2)."""

    def test_is_abstract(self):
        """Verify interface is abstract."""
        assert issubclass(IMatcher, ABC)

    def test_has_required_properties(self):
        """Verify interface has all required properties."""
        assert hasattr(IMatcher, "name")
        assert hasattr(IMatcher, "weight")

    def test_has_required_methods(self):
        """Verify interface has all required methods."""
        assert hasattr(IMatcher, "match")

    def test_can_implement(self):
        """Verify interface can be implemented."""

        class MockMatcher(IMatcher):
            @property
            def name(self) -> str:
                return "test_matcher"

            @property
            def weight(self) -> float:
                return 0.40

            def match(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> MatcherResult:
                return MatcherResult(
                    matcher_name=self.name,
                    workflow_name="test_workflow",
                    confidence=0.85,
                    weight=self.weight,
                )

        matcher = MockMatcher()
        assert matcher.name == "test_matcher"
        assert matcher.weight == 0.40

        result = matcher.match("create a test")
        assert isinstance(result, MatcherResult)
        assert result.matcher_name == "test_matcher"
        assert result.workflow_name == "test_workflow"
        assert result.confidence == 0.85

    def test_can_implement_no_match(self):
        """Verify interface can return no match."""

        class MockMatcher(IMatcher):
            @property
            def name(self) -> str:
                return "keyword"

            @property
            def weight(self) -> float:
                return 0.40

            def match(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> MatcherResult:
                # No keyword match
                return MatcherResult(
                    matcher_name=self.name,
                    workflow_name=None,
                    confidence=0.0,
                    weight=self.weight,
                )

        matcher = MockMatcher()
        result = matcher.match("some prompt")
        assert result.workflow_name is None
        assert result.confidence == 0.0


class TestIModifierExtractor:
    """Tests for IModifierExtractor interface (TASK-053-2)."""

    def test_is_abstract(self):
        """Verify interface is abstract."""
        assert issubclass(IModifierExtractor, ABC)

    def test_has_required_methods(self):
        """Verify interface has all required methods."""
        assert hasattr(IModifierExtractor, "extract")

    def test_can_implement(self):
        """Verify interface can be implemented."""

        class MockExtractor(IModifierExtractor):
            def extract(self, prompt: str, workflow_name: str) -> ModifierResult:
                # Simple mock: extract "straight" keyword
                modifiers = {}
                matched = []
                confidence = {}

                if "straight" in prompt.lower():
                    modifiers = {"leg_angle_left": 0, "leg_angle_right": 0}
                    matched = ["straight"]
                    confidence = {"straight": 1.0}

                return ModifierResult(
                    modifiers=modifiers,
                    matched_keywords=matched,
                    confidence_map=confidence,
                )

        extractor = MockExtractor()
        result = extractor.extract("create straight table", "picnic_table_workflow")
        assert isinstance(result, ModifierResult)
        assert result.modifiers["leg_angle_left"] == 0
        assert "straight" in result.matched_keywords

    def test_can_implement_no_modifiers(self):
        """Verify interface can return no modifiers."""

        class MockExtractor(IModifierExtractor):
            def extract(self, prompt: str, workflow_name: str) -> ModifierResult:
                # No modifiers found
                return ModifierResult(
                    modifiers={},
                    matched_keywords=[],
                    confidence_map={},
                )

        extractor = MockExtractor()
        result = extractor.extract("create table", "picnic_table_workflow")
        assert not result.has_modifiers()
        assert len(result.matched_keywords) == 0
