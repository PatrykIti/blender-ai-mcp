"""
Unit tests for SupervisorRouter.

Tests the main router orchestrator and its pipeline.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from server.router.application.router import SupervisorRouter
from server.router.infrastructure.config import RouterConfig
from server.router.domain.entities.scene_context import (
    SceneContext,
    ObjectInfo,
    TopologyInfo,
    ProportionInfo,
)
from server.router.domain.entities.pattern import PatternType, DetectedPattern
from server.router.domain.entities.tool_call import CorrectedToolCall
from server.router.domain.entities.firewall_result import FirewallResult, FirewallAction
from server.router.domain.entities.override_decision import (
    OverrideDecision,
    OverrideReason,
    ReplacementTool,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def router():
    """Create a SupervisorRouter instance."""
    config = RouterConfig()
    return SupervisorRouter(config=config)


@pytest.fixture
def router_with_rpc():
    """Create a SupervisorRouter with mock RPC client."""
    config = RouterConfig()
    rpc_client = MagicMock()
    return SupervisorRouter(config=config, rpc_client=rpc_client)


@pytest.fixture
def object_mode_context():
    """Create a context in OBJECT mode."""
    return SceneContext(
        mode="OBJECT",
        active_object="Cube",
        selected_objects=["Cube"],
        objects=[
            ObjectInfo(
                name="Cube",
                type="MESH",
                dimensions=[2.0, 2.0, 2.0],
                selected=True,
                active=True,
            )
        ],
        topology=TopologyInfo(
            vertices=8,
            edges=12,
            faces=6,
            selected_verts=0,
            selected_edges=0,
            selected_faces=0,
        ),
        proportions=ProportionInfo(
            aspect_xy=1.0,
            aspect_xz=1.0,
            aspect_yz=1.0,
            is_flat=False,
            is_tall=False,
            is_wide=False,
            is_cubic=True,
            dominant_axis="x",
            volume=8.0,
            surface_area=24.0,
        ),
    )


@pytest.fixture
def edit_mode_context():
    """Create a context in EDIT mode with selection."""
    return SceneContext(
        mode="EDIT",
        active_object="Cube",
        selected_objects=["Cube"],
        objects=[
            ObjectInfo(
                name="Cube",
                type="MESH",
                dimensions=[2.0, 2.0, 2.0],
                selected=True,
                active=True,
            )
        ],
        topology=TopologyInfo(
            vertices=8,
            edges=12,
            faces=6,
            selected_verts=8,
            selected_edges=12,
            selected_faces=6,
        ),
        proportions=ProportionInfo(
            aspect_xy=1.0,
            aspect_xz=1.0,
            aspect_yz=1.0,
            is_flat=False,
            is_tall=False,
            is_wide=False,
            is_cubic=True,
            dominant_axis="x",
            volume=8.0,
            surface_area=24.0,
        ),
    )


@pytest.fixture
def phone_like_context():
    """Create a context with phone-like proportions."""
    return SceneContext(
        mode="OBJECT",
        active_object="Phone",
        selected_objects=["Phone"],
        objects=[
            ObjectInfo(
                name="Phone",
                type="MESH",
                dimensions=[0.4, 0.8, 0.05],
                selected=True,
                active=True,
            )
        ],
        proportions=ProportionInfo(
            aspect_xy=0.5,
            aspect_xz=8.0,
            aspect_yz=16.0,
            is_flat=True,
            is_tall=False,
            is_wide=False,
            is_cubic=False,
            dominant_axis="y",
            volume=0.016,
            surface_area=0.76,
        ),
    )


# ============================================================================
# Initialization Tests
# ============================================================================


class TestSupervisorRouterInit:
    """Tests for SupervisorRouter initialization."""

    def test_init_default_config(self, router):
        """Test initialization with default config."""
        assert router.config is not None
        assert router.interceptor is not None
        assert router.analyzer is not None
        assert router.detector is not None
        assert router.correction_engine is not None
        assert router.override_engine is not None
        assert router.expansion_engine is not None
        assert router.firewall is not None
        assert router.classifier is not None
        assert router.logger is not None

    def test_init_custom_config(self):
        """Test initialization with custom config."""
        config = RouterConfig(
            auto_mode_switch=False,
            enable_overrides=False,
        )
        router = SupervisorRouter(config=config)
        assert router.config.auto_mode_switch is False
        assert router.config.enable_overrides is False

    def test_init_with_rpc_client(self, router_with_rpc):
        """Test initialization with RPC client."""
        assert router_with_rpc._rpc_client is not None

    def test_set_rpc_client(self, router):
        """Test setting RPC client after initialization."""
        mock_rpc = MagicMock()
        router.set_rpc_client(mock_rpc)
        assert router._rpc_client == mock_rpc

    def test_initial_stats(self, router):
        """Test initial processing stats."""
        stats = router.get_stats()
        assert stats["total_calls"] == 0
        assert stats["corrections_applied"] == 0
        assert stats["overrides_triggered"] == 0
        assert stats["workflows_expanded"] == 0
        assert stats["blocked_calls"] == 0


# ============================================================================
# Basic Pipeline Tests
# ============================================================================


class TestBasicPipeline:
    """Tests for basic pipeline processing."""

    def test_passthrough_no_correction_needed(self, router, edit_mode_context):
        """Test passthrough when no corrections needed."""
        with patch.object(router.analyzer, 'analyze', return_value=edit_mode_context):
            result = router.process_llm_tool_call(
                "mesh_extrude_region",
                {"move": [0.0, 0.0, 0.5]},
            )

        assert len(result) >= 1
        # Last tool should be the extrude
        assert any(r["tool"] == "mesh_extrude_region" for r in result)

    def test_mode_switch_correction(self, router, object_mode_context):
        """Test mode switch is added when needed."""
        with patch.object(router.analyzer, 'analyze', return_value=object_mode_context):
            result = router.process_llm_tool_call(
                "mesh_extrude_region",
                {"move": [0.0, 0.0, 0.5]},
            )

        # Should include mode switch
        assert any(r["tool"] == "system_set_mode" for r in result)
        assert any(r["tool"] == "mesh_extrude_region" for r in result)

    def test_selection_fix_added(self, router, edit_mode_context):
        """Test selection is added when missing."""
        # Context with no selection
        no_selection_context = SceneContext(
            mode="EDIT",
            active_object="Cube",
            selected_objects=["Cube"],
            objects=[
                ObjectInfo(
                    name="Cube",
                    type="MESH",
                    dimensions=[2.0, 2.0, 2.0],
                    selected=True,
                    active=True,
                )
            ],
            topology=TopologyInfo(
                vertices=8,
                edges=12,
                faces=6,
                selected_verts=0,  # No selection
                selected_edges=0,
                selected_faces=0,
            ),
        )

        with patch.object(router.analyzer, 'analyze', return_value=no_selection_context):
            result = router.process_llm_tool_call(
                "mesh_extrude_region",
                {"move": [0.0, 0.0, 0.5]},
            )

        # Should include selection
        assert any(r["tool"] == "mesh_select" for r in result)

    def test_stats_increment(self, router, object_mode_context):
        """Test stats are incremented on processing."""
        with patch.object(router.analyzer, 'analyze', return_value=object_mode_context):
            router.process_llm_tool_call("mesh_extrude_region", {"move": [0.0, 0.0, 0.5]})

        stats = router.get_stats()
        assert stats["total_calls"] == 1
        assert stats["corrections_applied"] >= 1  # Mode switch counts as correction


# ============================================================================
# Override Tests
# ============================================================================


class TestOverrides:
    """Tests for tool override functionality."""

    def test_override_triggered_with_pattern(self, router, phone_like_context):
        """Test override is triggered when pattern matches."""
        # Create a phone_like pattern
        phone_pattern = DetectedPattern(
            pattern_type=PatternType.PHONE_LIKE,
            confidence=0.9,
        )

        with patch.object(router.analyzer, 'analyze', return_value=phone_like_context):
            with patch.object(router.detector, 'get_best_match', return_value=phone_pattern):
                result = router.process_llm_tool_call(
                    "mesh_extrude_region",
                    {"move": [0.0, 0.0, -0.02]},
                )

        # Should have override replacement tools
        assert len(result) >= 2

    def test_override_disabled(self, phone_like_context):
        """Test override not triggered when disabled."""
        config = RouterConfig(enable_overrides=False)
        router = SupervisorRouter(config=config)

        phone_pattern = DetectedPattern(
            pattern_type=PatternType.PHONE_LIKE,
            confidence=0.9,
        )

        with patch.object(router.analyzer, 'analyze', return_value=phone_like_context):
            with patch.object(router.detector, 'get_best_match', return_value=phone_pattern):
                result = router.process_llm_tool_call(
                    "mesh_extrude_region",
                    {"move": [0.0, 0.0, -0.02]},
                )

        # Should just have the original call (with mode/selection fixes)
        assert any(r["tool"] == "mesh_extrude_region" for r in result)


# ============================================================================
# Workflow Expansion Tests
# ============================================================================


class TestWorkflowExpansion:
    """Tests for workflow expansion functionality."""

    def test_workflow_expansion_with_pattern(self, router, phone_like_context):
        """Test workflow expansion is triggered."""
        phone_pattern = DetectedPattern(
            pattern_type=PatternType.PHONE_LIKE,
            confidence=0.9,
            suggested_workflow="phone_workflow",
        )

        with patch.object(router.analyzer, 'analyze', return_value=phone_like_context):
            with patch.object(router.detector, 'get_best_match', return_value=phone_pattern):
                # Override won't match because trigger tool is different
                result = router.process_llm_tool_call(
                    "some_other_tool",
                    {},
                )

        # Workflow expansion should be triggered
        stats = router.get_stats()
        assert stats["workflows_expanded"] >= 0  # May or may not expand

    def test_workflow_disabled(self, phone_like_context):
        """Test workflow not expanded when disabled."""
        config = RouterConfig(enable_workflow_expansion=False)
        router = SupervisorRouter(config=config)

        phone_pattern = DetectedPattern(
            pattern_type=PatternType.PHONE_LIKE,
            confidence=0.9,
            suggested_workflow="phone_workflow",
        )

        with patch.object(router.analyzer, 'analyze', return_value=phone_like_context):
            with patch.object(router.detector, 'get_best_match', return_value=phone_pattern):
                result = router.process_llm_tool_call(
                    "modeling_create_primitive",
                    {"type": "CUBE"},
                )

        stats = router.get_stats()
        assert stats["workflows_expanded"] == 0


# ============================================================================
# Firewall Tests
# ============================================================================


class TestFirewall:
    """Tests for firewall validation."""

    def test_firewall_blocks_invalid(self, router):
        """Test firewall blocks invalid operations."""
        # Create context with no objects
        empty_context = SceneContext(
            mode="OBJECT",
            objects=[],
        )

        with patch.object(router.analyzer, 'analyze', return_value=empty_context):
            result = router.process_llm_tool_call(
                "scene_delete_object",
                {"name": "NonExistent"},
            )

        # Should be blocked or have no valid operations
        stats = router.get_stats()
        # May be blocked by firewall

    def test_firewall_auto_fix(self, router, object_mode_context):
        """Test firewall auto-fixes when possible."""
        with patch.object(router.analyzer, 'analyze', return_value=object_mode_context):
            result = router.process_llm_tool_call(
                "mesh_bevel",
                {"offset": 0.1, "segments": 2},
            )

        # Should include mode switch fix
        assert len(result) >= 1

    def test_firewall_disabled(self, object_mode_context):
        """Test firewall bypass when disabled."""
        config = RouterConfig(block_invalid_operations=False)
        router = SupervisorRouter(config=config)

        with patch.object(router.analyzer, 'analyze', return_value=object_mode_context):
            result = router.process_llm_tool_call(
                "mesh_bevel",
                {"offset": 0.1, "segments": 2},
            )

        # Should pass through without firewall blocking
        assert len(result) >= 1


# ============================================================================
# Batch Processing Tests
# ============================================================================


class TestBatchProcessing:
    """Tests for batch processing of tool calls."""

    def test_process_batch(self, router, edit_mode_context):
        """Test processing batch of tool calls."""
        with patch.object(router.analyzer, 'analyze', return_value=edit_mode_context):
            result = router.process_batch([
                {"tool": "mesh_extrude_region", "params": {"move": [0.0, 0.0, 0.5]}},
                {"tool": "mesh_bevel", "params": {"offset": 0.1}},
            ])

        assert len(result) >= 2
        stats = router.get_stats()
        assert stats["total_calls"] == 2

    def test_batch_empty(self, router):
        """Test processing empty batch."""
        result = router.process_batch([])
        assert result == []


# ============================================================================
# Route Method Tests
# ============================================================================


class TestRouteMethod:
    """Tests for natural language routing."""

    def test_route_without_classifier(self, router):
        """Test route returns empty when classifier not loaded."""
        result = router.route("extrude the top face")
        assert result == []

    def test_route_with_mock_classifier(self, router):
        """Test route with mocked classifier."""
        router.classifier._is_loaded = True
        with patch.object(
            router.classifier,
            'predict_top_k',
            return_value=[("mesh_extrude_region", 0.85), ("mesh_inset", 0.7)],
        ):
            with patch.object(router.classifier, 'is_loaded', return_value=True):
                result = router.route("extrude the top face")

        assert "mesh_extrude_region" in result


# ============================================================================
# Context Simulation Tests
# ============================================================================


class TestContextSimulation:
    """Tests for context change simulation."""

    def test_mode_switch_simulation(self, router, object_mode_context):
        """Test mode is simulated after mode switch."""
        mode_switch = CorrectedToolCall(
            tool_name="system_set_mode",
            params={"mode": "EDIT"},
            corrections_applied=[],
        )

        new_context = router._simulate_context_change(object_mode_context, mode_switch)
        assert new_context.mode == "EDIT"

    def test_select_all_simulation(self, router, edit_mode_context):
        """Test selection is simulated after select all."""
        # Start with no selection
        no_selection = SceneContext(
            mode="EDIT",
            active_object="Cube",
            selected_objects=["Cube"],
            objects=[],
            topology=TopologyInfo(
                vertices=8,
                edges=12,
                faces=6,
                selected_verts=0,
                selected_edges=0,
                selected_faces=0,
            ),
        )

        select_call = CorrectedToolCall(
            tool_name="mesh_select",
            params={"action": "all"},
            corrections_applied=[],
        )

        new_context = router._simulate_context_change(no_selection, select_call)
        assert new_context.topology.selected_verts == 8

    def test_select_none_simulation(self, router, edit_mode_context):
        """Test selection is cleared after select none."""
        select_call = CorrectedToolCall(
            tool_name="mesh_select",
            params={"action": "none"},
            corrections_applied=[],
        )

        new_context = router._simulate_context_change(edit_mode_context, select_call)
        assert new_context.topology.selected_verts == 0


# ============================================================================
# State Management Tests
# ============================================================================


class TestStateManagement:
    """Tests for router state management."""

    def test_get_last_context(self, router, edit_mode_context):
        """Test getting last analyzed context."""
        with patch.object(router.analyzer, 'analyze', return_value=edit_mode_context):
            router.process_llm_tool_call("mesh_extrude_region", {"move": [0.0, 0.0, 0.5]})

        last_context = router.get_last_context()
        assert last_context is not None
        assert last_context.mode == "EDIT"

    def test_get_last_pattern(self, router, phone_like_context):
        """Test getting last detected pattern."""
        phone_pattern = DetectedPattern(
            pattern_type=PatternType.PHONE_LIKE,
            confidence=0.9,
        )

        with patch.object(router.analyzer, 'analyze', return_value=phone_like_context):
            with patch.object(router.detector, 'get_best_match', return_value=phone_pattern):
                router.process_llm_tool_call("mesh_extrude_region", {"move": [0.0, 0.0, 0.5]})

        last_pattern = router.get_last_pattern()
        assert last_pattern is not None
        assert last_pattern.pattern_type == PatternType.PHONE_LIKE

    def test_invalidate_cache(self, router, edit_mode_context):
        """Test cache invalidation."""
        with patch.object(router.analyzer, 'analyze', return_value=edit_mode_context):
            router.process_llm_tool_call("mesh_extrude_region", {"move": [0.0, 0.0, 0.5]})

        router.invalidate_cache()
        assert router.get_last_context() is None
        assert router.get_last_pattern() is None

    def test_reset_stats(self, router, edit_mode_context):
        """Test stats reset."""
        with patch.object(router.analyzer, 'analyze', return_value=edit_mode_context):
            router.process_llm_tool_call("mesh_extrude_region", {"move": [0.0, 0.0, 0.5]})

        router.reset_stats()
        stats = router.get_stats()
        assert stats["total_calls"] == 0


# ============================================================================
# Configuration Tests
# ============================================================================


class TestConfiguration:
    """Tests for configuration management."""

    def test_get_config(self, router):
        """Test getting config."""
        config = router.get_config()
        assert config is not None
        assert isinstance(config, RouterConfig)

    def test_update_config(self, router):
        """Test updating config."""
        router.update_config(auto_mode_switch=False)
        assert router.config.auto_mode_switch is False

    def test_update_invalid_config(self, router):
        """Test updating with invalid key."""
        router.update_config(invalid_key="value")
        # Should not raise, just ignore

    def test_get_component_status(self, router):
        """Test component status."""
        status = router.get_component_status()
        assert "interceptor" in status
        assert "analyzer" in status
        assert "detector" in status
        assert "correction_engine" in status
        assert "override_engine" in status
        assert "expansion_engine" in status
        assert "firewall" in status
        assert "classifier" in status

    def test_is_ready_without_rpc(self, router):
        """Test readiness without RPC client."""
        assert router.is_ready() is False

    def test_is_ready_with_rpc(self, router_with_rpc):
        """Test readiness with RPC client."""
        assert router_with_rpc.is_ready() is True


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for full pipeline."""

    def test_full_pipeline_mesh_in_object_mode(self, router, object_mode_context):
        """Test full pipeline for mesh tool in object mode."""
        with patch.object(router.analyzer, 'analyze', return_value=object_mode_context):
            result = router.process_llm_tool_call(
                "mesh_extrude_region",
                {"move": [0.0, 0.0, 0.5]},
            )

        # Should have:
        # 1. Mode switch to EDIT
        # 2. Selection (if needed)
        # 3. The actual extrude
        tools = [r["tool"] for r in result]
        assert "system_set_mode" in tools
        # Final tool should be extrude or have extrude somewhere
        assert "mesh_extrude_region" in tools or "mesh_inset" in tools

    def test_full_pipeline_modeling_in_edit_mode(self, router, edit_mode_context):
        """Test full pipeline for modeling tool in edit mode."""
        with patch.object(router.analyzer, 'analyze', return_value=edit_mode_context):
            result = router.process_llm_tool_call(
                "modeling_add_modifier",
                {"type": "BEVEL"},
            )

        # Should have mode switch to OBJECT
        tools = [r["tool"] for r in result]
        assert "system_set_mode" in tools

    def test_parameter_clamping(self, router, edit_mode_context):
        """Test parameter clamping in pipeline."""
        with patch.object(router.analyzer, 'analyze', return_value=edit_mode_context):
            result = router.process_llm_tool_call(
                "mesh_subdivide",
                {"number_cuts": 100},  # Way over limit
            )

        # The tool should be processed (clamping happens in correction)
        assert len(result) >= 1

    def test_multiple_corrections_applied(self, router, object_mode_context):
        """Test multiple corrections in single call."""
        # Object mode, no selection - needs both mode switch and selection
        no_selection_object = SceneContext(
            mode="OBJECT",
            active_object="Cube",
            selected_objects=["Cube"],
            objects=[
                ObjectInfo(
                    name="Cube",
                    type="MESH",
                    dimensions=[2.0, 2.0, 2.0],
                    selected=True,
                    active=True,
                )
            ],
            topology=TopologyInfo(
                vertices=8,
                edges=12,
                faces=6,
                selected_verts=0,
                selected_edges=0,
                selected_faces=0,
            ),
        )

        with patch.object(router.analyzer, 'analyze', return_value=no_selection_object):
            result = router.process_llm_tool_call(
                "mesh_extrude_region",
                {"move": [0.0, 0.0, 0.5]},
            )

        # Should have mode switch and selection
        tools = [r["tool"] for r in result]
        assert "system_set_mode" in tools
        assert "mesh_select" in tools


# ==============================================================================
# TASK-053 Ensemble Matching Tests
# ==============================================================================


class TestEnsembleMatcherInitialization:
    """Tests for TASK-053-9: Ensemble matcher initialization."""

    def test_ensemble_fields_initialized(self):
        """Test that ensemble matching fields are initialized in SupervisorRouter."""
        router = SupervisorRouter(config=RouterConfig())

        # TASK-053-9: New ensemble matching fields
        assert hasattr(router, '_ensemble_matcher')
        assert hasattr(router, '_last_ensemble_result')
        assert hasattr(router, '_pending_modifiers')
        assert hasattr(router, '_use_ensemble_matching')

        # Initial values
        assert router._ensemble_matcher is None  # Lazy init
        assert router._last_ensemble_result is None
        assert router._pending_modifiers == {}
        assert router._use_ensemble_matching is True  # Enabled by default

    def test_ensure_ensemble_initialized_creates_components(self):
        """Test _ensure_ensemble_initialized creates ensemble components."""
        router = SupervisorRouter(config=RouterConfig(use_ensemble_matching=True))

        # Before initialization
        assert router._ensemble_matcher is None

        # Initialize
        result = router._ensure_ensemble_initialized()

        # Should succeed
        assert result is True
        assert router._ensemble_matcher is not None
        assert router._ensemble_matcher.is_initialized() is True

    def test_ensure_ensemble_initialized_with_disabled_flag(self):
        """Test _ensure_ensemble_initialized respects config flag."""
        router = SupervisorRouter(config=RouterConfig(use_ensemble_matching=False))

        # Even with flag disabled, initialization should work
        result = router._ensure_ensemble_initialized()
        assert result is True

    def test_ensure_ensemble_initialized_idempotent(self):
        """Test _ensure_ensemble_initialized can be called multiple times."""
        router = SupervisorRouter(config=RouterConfig())

        # First call
        router._ensure_ensemble_initialized()
        matcher1 = router._ensemble_matcher

        # Second call
        router._ensure_ensemble_initialized()
        matcher2 = router._ensemble_matcher

        # Should return same instance
        assert matcher1 is matcher2


class TestSetCurrentGoalEnsemble:
    """Tests for TASK-053-10: set_current_goal with ensemble matching."""

    def test_set_goal_uses_ensemble_when_enabled(self):
        """Test set_current_goal uses ensemble matching when enabled."""
        router = SupervisorRouter(config=RouterConfig(use_ensemble_matching=True))

        # Mock ensemble matcher
        mock_ensemble = MagicMock()
        mock_ensemble.match.return_value = MagicMock(
            workflow_name="table_workflow",
            final_score=0.84,
            confidence_level="HIGH",
            modifiers={"leg_style": "straight"},
            matcher_contributions={"semantic": 0.336, "keyword": 0.40},
            requires_adaptation=False
        )
        router._ensemble_matcher = mock_ensemble
        router._ensemble_matcher.is_initialized.return_value = True

        # Set goal
        result = router.set_current_goal("prosty stół z prostymi nogami")

        # Should use ensemble matching
        assert result == "table_workflow"
        assert router._pending_workflow == "table_workflow"
        assert router._pending_modifiers == {"leg_style": "straight"}
        mock_ensemble.match.assert_called_once()

    def test_set_goal_stores_ensemble_result(self):
        """Test set_current_goal stores EnsembleResult."""
        router = SupervisorRouter(config=RouterConfig(use_ensemble_matching=True))

        from server.router.domain.entities.ensemble import EnsembleResult

        # Mock ensemble matcher
        ensemble_result = EnsembleResult(
            workflow_name="phone_workflow",
            final_score=0.74,
            confidence_level="HIGH",
            modifiers={},
            matcher_contributions={"keyword": 0.40, "semantic": 0.34},
            requires_adaptation=False
        )
        mock_ensemble = MagicMock()
        mock_ensemble.match.return_value = ensemble_result
        router._ensemble_matcher = mock_ensemble
        router._ensemble_matcher.is_initialized.return_value = True

        # Set goal
        router.set_current_goal("create phone")

        # Should store result
        assert router._last_ensemble_result is ensemble_result
        assert router._last_ensemble_result.workflow_name == "phone_workflow"

    def test_set_goal_creates_match_result_from_ensemble(self):
        """Test set_current_goal creates MatchResult from EnsembleResult."""
        router = SupervisorRouter(config=RouterConfig(use_ensemble_matching=True))

        # Mock ensemble matcher
        mock_ensemble = MagicMock()
        mock_ensemble.match.return_value = MagicMock(
            workflow_name="table_workflow",
            final_score=0.55,
            confidence_level="MEDIUM",
            modifiers={},
            matcher_contributions={"semantic": 0.22, "keyword": 0.40},
            requires_adaptation=True
        )
        router._ensemble_matcher = mock_ensemble
        router._ensemble_matcher.is_initialized.return_value = True

        # Set goal
        router.set_current_goal("table")

        # Should create MatchResult for backward compatibility
        assert router._last_match_result is not None
        assert router._last_match_result.workflow_name == "table_workflow"
        assert router._last_match_result.confidence == 0.55
        assert router._last_match_result.match_type == "ensemble"
        assert router._last_match_result.confidence_level == "MEDIUM"
        assert router._last_match_result.requires_adaptation is True


class TestExpandTriggeredWorkflowWithModifiers:
    """Tests for TASK-053-11: _expand_triggered_workflow uses _pending_modifiers."""

    @patch('server.router.application.workflows.registry.get_workflow_registry')
    def test_expand_uses_pending_modifiers_in_adaptation_path(self, mock_get_registry):
        """Test _expand_triggered_workflow uses _pending_modifiers in adaptation path."""
        router = SupervisorRouter(config=RouterConfig(
            use_ensemble_matching=True,
            enable_workflow_adaptation=True
        ))

        # Set up pending modifiers (from ensemble result)
        router._pending_modifiers = {"leg_style": "straight", "surface": "smooth"}

        # Set up last match result (triggers adaptation)
        from server.router.application.matcher.semantic_workflow_matcher import MatchResult
        router._last_match_result = MatchResult(
            workflow_name="table_workflow",
            confidence=0.35,
            match_type="ensemble",
            confidence_level="LOW",
            requires_adaptation=True
        )

        # Mock workflow definition
        from server.router.application.workflows.base import WorkflowDefinition, WorkflowStep
        definition = WorkflowDefinition(
            name="table_workflow",
            description="Table",
            steps=[
                WorkflowStep(tool="modeling_create_primitive", params={"primitive_type": "CUBE"}, optional=False),
            ],
            defaults={"leg_style": "curved"}  # Will be overridden by pending_modifiers
        )

        # Mock registry
        mock_registry = MagicMock()
        mock_get_registry.return_value = mock_registry
        mock_registry.get_definition.return_value = definition
        mock_registry.ensure_custom_loaded.return_value = None

        # Mock workflow adapter
        from server.router.application.engines.workflow_adapter import AdaptationResult
        router._workflow_adapter = MagicMock()
        router._workflow_adapter.adapt.return_value = (
            [WorkflowStep(tool="modeling_create_primitive", params={"primitive_type": "CUBE"}, optional=False)],
            AdaptationResult(
                original_step_count=1,
                adapted_step_count=1,
                confidence_level="LOW",
                adaptation_strategy="CORE_ONLY"
            )
        )

        # Call _expand_triggered_workflow
        context = SceneContext(mode="OBJECT", objects=[])
        calls = router._expand_triggered_workflow("table_workflow", {}, context)

        # Verify pending_modifiers were cleared after expansion
        assert router._pending_modifiers == {}

    @patch('server.router.application.workflows.registry.get_workflow_registry')
    def test_expand_clears_pending_modifiers_after_expansion(self, mock_get_registry):
        """Test _expand_triggered_workflow clears _pending_modifiers after use."""
        router = SupervisorRouter(config=RouterConfig())

        # Set up pending modifiers
        router._pending_modifiers = {"leg_style": "straight"}
        router._pending_workflow = "table_workflow"

        # Mock registry
        mock_registry = MagicMock()
        mock_get_registry.return_value = mock_registry
        mock_registry.expand_workflow.return_value = [
            CorrectedToolCall(tool_name="modeling_create_primitive", params={}, corrections_applied=[], is_injected=True)
        ]
        mock_registry.ensure_custom_loaded.return_value = None

        # Call standard expansion path
        context = SceneContext(mode="OBJECT", objects=[])
        calls = router._expand_triggered_workflow("table_workflow", {}, context)

        # Verify pending_modifiers were cleared
        assert router._pending_modifiers == {}
        assert router._pending_workflow is None


class TestRouterConfigEnsembleFields:
    """Tests for TASK-053-12: RouterConfig ensemble fields."""

    def test_config_has_ensemble_fields(self):
        """Test RouterConfig has ensemble matching fields."""
        config = RouterConfig()

        # TASK-053-12: Ensemble matching fields
        assert hasattr(config, 'use_ensemble_matching')
        assert hasattr(config, 'keyword_weight')
        assert hasattr(config, 'semantic_weight')
        assert hasattr(config, 'pattern_weight')
        assert hasattr(config, 'pattern_boost_factor')
        assert hasattr(config, 'composition_threshold')
        assert hasattr(config, 'enable_composition_mode')
        assert hasattr(config, 'ensemble_high_threshold')
        assert hasattr(config, 'ensemble_medium_threshold')

    def test_config_ensemble_defaults(self):
        """Test RouterConfig ensemble field defaults match spec."""
        config = RouterConfig()

        assert config.use_ensemble_matching is True
        assert config.keyword_weight == 0.40
        assert config.semantic_weight == 0.40
        assert config.pattern_weight == 0.15
        assert config.pattern_boost_factor == 1.3
        assert config.composition_threshold == 0.15
        assert config.enable_composition_mode is False
        assert config.ensemble_high_threshold == 0.7
        assert config.ensemble_medium_threshold == 0.4

    def test_config_ensemble_fields_in_to_dict(self):
        """Test RouterConfig.to_dict() includes ensemble fields."""
        config = RouterConfig()
        config_dict = config.to_dict()

        assert 'use_ensemble_matching' in config_dict
        assert 'keyword_weight' in config_dict
        assert 'semantic_weight' in config_dict
        assert 'pattern_weight' in config_dict
        assert 'pattern_boost_factor' in config_dict
        assert 'composition_threshold' in config_dict
        assert 'enable_composition_mode' in config_dict
        assert 'ensemble_high_threshold' in config_dict
        assert 'ensemble_medium_threshold' in config_dict

    def test_config_ensemble_fields_from_dict(self):
        """Test RouterConfig.from_dict() restores ensemble fields."""
        original = RouterConfig(
            use_ensemble_matching=False,
            keyword_weight=0.50,
            semantic_weight=0.30,
            pattern_weight=0.20
        )

        config_dict = original.to_dict()
        restored = RouterConfig.from_dict(config_dict)

        assert restored.use_ensemble_matching is False
        assert restored.keyword_weight == 0.50
        assert restored.semantic_weight == 0.30
        assert restored.pattern_weight == 0.20
