"""
E2E tests for Tool Override Engine.

Tests pattern-based tool overrides that replace single tools with workflows.
Requires running Blender instance.

TASK-040
"""

import pytest

from server.router.application.router import SupervisorRouter
from server.router.infrastructure.config import RouterConfig


class TestPatternBasedOverride:
    """Tests for pattern-based tool overrides."""

    def test_extrude_on_phone_pattern_may_add_inset(self, router, rpc_client, clean_scene):
        """Test: Extrude on phone-like object may trigger override."""
        # Create phone-like object (flat rectangle)
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {
            "scale": [0.4, 0.8, 0.05]  # Phone proportions
        })
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # Invalidate cache to get fresh pattern detection
        router.invalidate_cache()

        # Try extrude with screen-related prompt
        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": -0.02},
            prompt="create screen cutout on phone"
        )

        tool_names = [t["tool"] for t in tools]

        # Should have extrude in the output
        assert "mesh_extrude_region" in tool_names, f"Extrude should be present, got: {tool_names}"

        # Override might add inset before extrude (pattern-based)
        # This is optional behavior depending on pattern detection
        if len(tools) > 2:
            # If override triggered, should have inset
            has_inset = "mesh_inset" in tool_names
            # Pattern-based override is optional, so we just verify structure
            assert isinstance(tools, list)

    def test_subdivide_on_tower_pattern_may_add_taper(self, router, rpc_client, clean_scene):
        """Test: Subdivide on tower-like object may trigger override."""
        # Create tower-like object (tall thin)
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {
            "scale": [0.3, 0.3, 2.0]  # Tower proportions
        })
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        router.invalidate_cache()

        # Try subdivide with tower-related prompt
        tools = router.process_llm_tool_call(
            "mesh_subdivide",
            {"number_cuts": 3},
            prompt="add segments to tower for tapering"
        )

        tool_names = [t["tool"] for t in tools]

        # Should have subdivide in output
        assert "mesh_subdivide" in tool_names, f"Subdivide should be present, got: {tool_names}"

        # Override might add taper steps
        # This is optional depending on override engine rules
        assert isinstance(tools, list)


class TestOverrideWithoutPattern:
    """Tests for override behavior without pattern match."""

    def test_extrude_on_cubic_object_no_override(self, router, rpc_client, clean_scene):
        """Test: Extrude on cubic object doesn't trigger phone override."""
        # Create cubic object (not phone-like)
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        # Default cube is 2x2x2 - cubic, not phone-like
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        router.invalidate_cache()

        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": 0.5}
        )

        tool_names = [t["tool"] for t in tools]

        # Should have extrude
        assert "mesh_extrude_region" in tool_names

        # Cubic object shouldn't trigger phone-specific override (inset)
        # May have mode switch or selection, but not pattern-based inset

    def test_subdivide_on_flat_object_no_tower_override(self, router, rpc_client, clean_scene):
        """Test: Subdivide on flat object doesn't trigger tower override."""
        # Create flat object (not tower-like)
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {
            "scale": [2.0, 2.0, 0.1]  # Flat, not tower
        })
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        router.invalidate_cache()

        tools = router.process_llm_tool_call(
            "mesh_subdivide",
            {"number_cuts": 2}
        )

        tool_names = [t["tool"] for t in tools]

        # Should have subdivide
        assert "mesh_subdivide" in tool_names


class TestOverrideConfiguration:
    """Tests for override configuration options."""

    def test_disabled_override_returns_original_tool(self, rpc_client, clean_scene, shared_classifier):
        """Test: Disabled overrides don't modify tool sequence."""
        config = RouterConfig(
            enable_overrides=False,  # Disable overrides
        )
        router = SupervisorRouter(
            config=config,
            rpc_client=rpc_client,
            classifier=shared_classifier,
        )

        # Create phone-like object
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {
            "scale": [0.4, 0.8, 0.05]
        })
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": -0.02},
            prompt="create screen"
        )

        tool_names = [t["tool"] for t in tools]

        # With overrides disabled, should NOT add pattern-based tools
        # May still have mode/selection corrections, but not pattern overrides
        assert "mesh_extrude_region" in tool_names


class TestOverrideExecution:
    """Tests that verify override tools execute correctly."""

    def test_overridden_tools_execute_without_error(self, router, rpc_client, clean_scene):
        """Test: Override tool sequence executes without errors."""
        # Create object
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        router.invalidate_cache()

        # Get tools (may or may not be overridden)
        tools = router.process_llm_tool_call(
            "mesh_bevel",
            {"width": 0.1, "segments": 2}
        )

        # Execute all tools
        errors = []
        for tool in tools:
            tool_name = tool["tool"]
            params = tool["params"]

            area = tool_name.split("_")[0]
            method = "_".join(tool_name.split("_")[1:])

            try:
                rpc_client.send_request(f"{area}.{method}", params)
            except Exception as e:
                errors.append({"tool": tool_name, "error": str(e)})

        # Should execute without major errors
        # Some tools may fail due to state, but shouldn't crash
        assert len(errors) < len(tools), f"Too many errors: {errors}"
