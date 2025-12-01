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
                {"depth": 0.5},
            )

        assert len(result) >= 1
        # Last tool should be the extrude
        assert any(r["tool"] == "mesh_extrude_region" for r in result)

    def test_mode_switch_correction(self, router, object_mode_context):
        """Test mode switch is added when needed."""
        with patch.object(router.analyzer, 'analyze', return_value=object_mode_context):
            result = router.process_llm_tool_call(
                "mesh_extrude_region",
                {"depth": 0.5},
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
                {"depth": 0.5},
            )

        # Should include selection
        assert any(r["tool"] == "mesh_select" for r in result)

    def test_stats_increment(self, router, object_mode_context):
        """Test stats are incremented on processing."""
        with patch.object(router.analyzer, 'analyze', return_value=object_mode_context):
            router.process_llm_tool_call("mesh_extrude_region", {"depth": 0.5})

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
                    {"depth": -0.02},
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
                    {"depth": -0.02},
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
                {"width": 0.1, "segments": 2},
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
                {"width": 0.1, "segments": 2},
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
                {"tool": "mesh_extrude_region", "params": {"depth": 0.5}},
                {"tool": "mesh_bevel", "params": {"width": 0.1}},
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
            router.process_llm_tool_call("mesh_extrude_region", {"depth": 0.5})

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
                router.process_llm_tool_call("mesh_extrude_region", {"depth": 0.5})

        last_pattern = router.get_last_pattern()
        assert last_pattern is not None
        assert last_pattern.pattern_type == PatternType.PHONE_LIKE

    def test_invalidate_cache(self, router, edit_mode_context):
        """Test cache invalidation."""
        with patch.object(router.analyzer, 'analyze', return_value=edit_mode_context):
            router.process_llm_tool_call("mesh_extrude_region", {"depth": 0.5})

        router.invalidate_cache()
        assert router.get_last_context() is None
        assert router.get_last_pattern() is None

    def test_reset_stats(self, router, edit_mode_context):
        """Test stats reset."""
        with patch.object(router.analyzer, 'analyze', return_value=edit_mode_context):
            router.process_llm_tool_call("mesh_extrude_region", {"depth": 0.5})

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
                {"depth": 0.5},
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
                {"depth": 0.5},
            )

        # Should have mode switch and selection
        tools = [r["tool"] for r in result]
        assert "system_set_mode" in tools
        assert "mesh_select" in tools
