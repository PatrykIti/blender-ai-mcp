"""
E2E tests for Router Supervisor scenarios.

Tests real-world scenarios where the router corrects LLM mistakes.
Requires running Blender instance.

TASK-039-23
"""

import pytest

from server.router.application.router import SupervisorRouter
from server.router.infrastructure.config import RouterConfig


class TestModeCorrection:
    """Tests for automatic mode correction."""

    def test_mesh_tool_in_object_mode_adds_mode_switch(self, router, rpc_client, clean_scene):
        """Test: mesh_extrude in OBJECT mode → Router adds mode switch."""
        # Create a cube (starts in OBJECT mode)
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})

        # Ensure we're in OBJECT mode
        rpc_client.send_request("system.set_mode", {"mode": "OBJECT"})

        # Invalidate router's scene context cache to get fresh state
        router.invalidate_cache()

        # LLM tries to extrude without switching to EDIT mode
        tools = router.process_llm_tool_call("mesh_extrude_region", {"depth": 0.5})

        # Router should add mode switch before extrude
        tool_names = [t["tool"] for t in tools]

        # Should have mode switch
        assert "system_set_mode" in tool_names, f"Router should add mode switch, got: {tool_names}"

        # Mode switch should come before extrude
        mode_idx = tool_names.index("system_set_mode")
        extrude_idx = tool_names.index("mesh_extrude_region")
        assert mode_idx < extrude_idx, "Mode switch should come before extrude"

    def test_modeling_tool_in_edit_mode_adds_mode_switch(self, router, rpc_client, clean_scene):
        """Test: modeling_add_modifier in EDIT mode → Router adds mode switch."""
        # Create a cube and enter EDIT mode
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})

        # Invalidate router's scene context cache to get fresh state
        router.invalidate_cache()

        # LLM tries to add modifier while in EDIT mode
        tools = router.process_llm_tool_call(
            "modeling_add_modifier",
            {"modifier_type": "SUBSURF", "name": "Subdivision"}
        )

        # Router should add mode switch to OBJECT
        tool_names = [t["tool"] for t in tools]
        assert "system_set_mode" in tool_names, f"Expected mode switch for EDIT->OBJECT, got: {tool_names}"


class TestParameterClamping:
    """Tests for parameter clamping."""

    def test_bevel_width_clamped(self, router, rpc_client, clean_scene):
        """Test: Excessive bevel width is clamped."""
        # Create a small cube
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # LLM tries to bevel with huge width
        tools = router.process_llm_tool_call("mesh_bevel", {"width": 1000.0, "segments": 3})

        # Find the bevel call
        bevel_tool = next((t for t in tools if t["tool"] == "mesh_bevel"), None)
        assert bevel_tool is not None

        # Offset should be clamped (width alias normalized to offset)
        assert "offset" in bevel_tool["params"]
        assert bevel_tool["params"]["offset"] <= 10.0, "Bevel width should be clamped"

    def test_subdivide_cuts_clamped(self, router, rpc_client, clean_scene):
        """Test: Excessive subdivide cuts are clamped."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})

        # LLM tries too many subdivisions
        tools = router.process_llm_tool_call("mesh_subdivide", {"number_cuts": 100})

        subdivide_tool = next((t for t in tools if t["tool"] == "mesh_subdivide"), None)
        assert subdivide_tool is not None

        # Cuts should be clamped to max 6
        assert subdivide_tool["params"]["number_cuts"] <= 6


class TestSelectionHandling:
    """Tests for automatic selection handling."""

    def test_extrude_without_selection_adds_select_all(self, router, rpc_client, clean_scene):
        """Test: Extrude without selection → Router adds select all."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})

        # Deselect all
        rpc_client.send_request("mesh.select", {"action": "none"})

        # LLM tries to extrude with nothing selected
        tools = router.process_llm_tool_call("mesh_extrude_region", {"depth": 0.5})

        tool_names = [t["tool"] for t in tools]

        # Should have selection before extrude
        has_selection = any("select" in name for name in tool_names)
        assert has_selection, "Router should add selection step"


class TestFullPipelineExecution:
    """Tests for executing the full corrected pipeline."""

    def test_corrected_extrude_executes_successfully(self, router, rpc_client, clean_scene):
        """Test: Corrected extrude pipeline executes without errors."""
        # Create cube in OBJECT mode
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})

        # Get corrected tools (should add mode switch, selection)
        tools = router.process_llm_tool_call("mesh_extrude_region", {"depth": 0.3})

        # Execute each tool
        results = []
        for tool in tools:
            tool_name = tool["tool"]
            params = tool["params"]

            # Map to RPC method
            area = tool_name.split("_")[0]
            method = "_".join(tool_name.split("_")[1:])
            rpc_method = f"{area}.{method}"

            try:
                result = rpc_client.send_request(rpc_method, params)
                results.append({"tool": tool_name, "result": result, "success": True})
            except Exception as e:
                results.append({"tool": tool_name, "error": str(e), "success": False})

        # All tools should succeed
        failed = [r for r in results if not r["success"]]
        assert len(failed) == 0, f"Some tools failed: {failed}"

    def test_bevel_after_mode_switch_works(self, router, rpc_client, clean_scene):
        """Test: Bevel with mode correction executes correctly."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "OBJECT"})

        # Stay in OBJECT mode, try to bevel
        tools = router.process_llm_tool_call("mesh_bevel", {"width": 0.1, "segments": 2})

        # Should have mode switch
        assert any(t["tool"] == "system_set_mode" for t in tools)

        # Execute and verify no errors
        for tool in tools:
            area = tool["tool"].split("_")[0]
            method = "_".join(tool["tool"].split("_")[1:])
            try:
                rpc_client.send_request(f"{area}.{method}", tool["params"])
            except Exception as e:
                pytest.fail(f"Tool {tool['tool']} failed: {e}")
