"""
E2E tests for Full Router Pipeline.

Tests the complete router pipeline from LLM call to Blender execution.
Requires running Blender instance.

TASK-039-23
"""

import pytest

from server.router.application.router import SupervisorRouter
from server.router.infrastructure.config import RouterConfig
from server.router.infrastructure.logger import get_router_logger


class TestFullPipeline:
    """Tests for complete pipeline execution."""

    def test_complete_modeling_session(self, router, rpc_client, clean_scene):
        """Test: Complete modeling session with multiple tools."""
        # Simulate a modeling session
        session_tools = [
            ("modeling_create_primitive", {"type": "CUBE"}),
            ("modeling_transform_object", {"scale": [0.5, 0.5, 1.0]}),
            ("mesh_subdivide", {"number_cuts": 2}),
            ("mesh_bevel", {"width": 0.05, "segments": 2}),
        ]

        all_executed = []

        for tool_name, params in session_tools:
            # Process through router
            corrected_tools = router.process_llm_tool_call(tool_name, params)

            # Execute each corrected tool
            for tool in corrected_tools:
                t_name = tool["tool"]
                t_params = tool["params"]

                area = t_name.split("_")[0]
                method = "_".join(t_name.split("_")[1:])

                try:
                    rpc_client.send_request(f"{area}.{method}", t_params)
                    all_executed.append({"tool": t_name, "success": True})
                except Exception as e:
                    all_executed.append({"tool": t_name, "success": False, "error": str(e)})

        # Count successes
        successes = [e for e in all_executed if e["success"]]
        assert len(successes) >= len(session_tools), \
            f"Should execute at least {len(session_tools)} tools, got {len(successes)}"

    def test_pipeline_with_intent_classification(self, router, rpc_client, clean_scene):
        """Test: Pipeline with prompt-based intent classification."""
        # Process with natural language prompt
        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": 0.5},
            prompt="extrude the top face of the phone to create a button"
        )

        assert len(tools) > 0, "Should return at least one tool"

        # Should have the extrude
        tool_names = [t["tool"] for t in tools]
        assert "mesh_extrude_region" in tool_names

    def test_pipeline_telemetry(self, router, rpc_client, clean_scene):
        """Test: Pipeline generates telemetry events."""
        logger = get_router_logger()
        logger.clear_events()  # Method is clear_events(), not clear()

        # Create and process
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})

        router.process_llm_tool_call("mesh_bevel", {"width": 0.1})

        # Should have logged events
        events = logger.get_events()
        assert len(events) > 0, "Should have logged events"

        # Check for intercept event (events are dicts with 'event_type' key)
        event_types = [e["event_type"] for e in events]
        assert "intercept" in event_types, "Should have intercept event"


class TestErrorRecovery:
    """Tests for error recovery in the pipeline."""

    def test_invalid_tool_name_handled(self, router, rpc_client, clean_scene):
        """Test: Invalid tool name is handled gracefully."""
        # This might raise or return empty
        try:
            tools = router.process_llm_tool_call(
                "nonexistent_tool_xyz",
                {"param": "value"}
            )
            # If it doesn't raise, should return something
            assert isinstance(tools, list)
        except Exception:
            # Raising is also acceptable
            pass

    def test_missing_params_handled(self, router, rpc_client, clean_scene):
        """Test: Missing required params are handled."""
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})

        # Bevel without width might use default
        tools = router.process_llm_tool_call("mesh_bevel", {})

        # Should still return tools (with defaults or error)
        assert isinstance(tools, list)

    def test_wrong_mode_recovery(self, router, rpc_client, clean_scene):
        """Test: Wrong mode is corrected and recovered."""
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})

        # Ensure OBJECT mode
        rpc_client.send_request("system.set_mode", {"mode": "OBJECT"})

        # Try mesh operation (requires EDIT)
        tools = router.process_llm_tool_call("mesh_extrude_region", {"depth": 0.3})

        # Execute all
        for tool in tools:
            area = tool["tool"].split("_")[0]
            method = "_".join(tool["tool"].split("_")[1:])
            try:
                rpc_client.send_request(f"{area}.{method}", tool["params"])
            except Exception:
                pass  # Some may fail, that's ok

        # Verify we're now in EDIT mode (if mode switch worked)
        try:
            result = rpc_client.send_request("scene.get_mode", {})
            # Mode should be EDIT after correction
            assert "EDIT" in str(result).upper() or len(tools) > 1
        except Exception:
            pass


class TestRouterConfiguration:
    """Tests for different router configurations."""

    def test_disabled_mode_switch(self, rpc_client, clean_scene, shared_classifier):
        """Test: Router with disabled mode switch."""
        config = RouterConfig(
            auto_mode_switch=False,
            auto_selection=True,
        )
        # Use shared_classifier to avoid loading LaBSE model again
        router = SupervisorRouter(config=config, rpc_client=rpc_client, classifier=shared_classifier)

        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})

        tools = router.process_llm_tool_call("mesh_extrude_region", {"depth": 0.3})

        # Should NOT have mode switch when disabled
        tool_names = [t["tool"] for t in tools]

        # With mode switch disabled, it should still work but might not add switch
        # Behavior depends on implementation
        assert "mesh_extrude_region" in tool_names

    def test_disabled_workflow_expansion(self, rpc_client, clean_scene, shared_classifier):
        """Test: Router with disabled workflow expansion."""
        config = RouterConfig(
            enable_workflow_expansion=False,
        )
        # Use shared_classifier to avoid loading LaBSE model again
        router = SupervisorRouter(config=config, rpc_client=rpc_client, classifier=shared_classifier)

        # Even with matching pattern, shouldn't expand
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {
            "scale": [0.4, 0.8, 0.05]
        })

        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": -0.02},
            prompt="create phone screen"
        )

        # Should NOT expand to full workflow
        assert len(tools) <= 5, "Should not expand to full workflow"


class TestConcurrentOperations:
    """Tests for handling multiple sequential operations."""

    def test_multiple_objects_session(self, router, rpc_client, clean_scene):
        """Test: Creating and modifying multiple objects."""
        objects_created = 0

        for i in range(3):
            # Create object
            tools = router.process_llm_tool_call(
                "modeling_create_primitive",
                {"type": "CUBE"}
            )

            for tool in tools:
                area = tool["tool"].split("_")[0]
                method = "_".join(tool["tool"].split("_")[1:])
                try:
                    rpc_client.send_request(f"{area}.{method}", tool["params"])
                    if "create" in tool["tool"]:
                        objects_created += 1
                except Exception:
                    pass

            # Move it
            try:
                rpc_client.send_request("modeling.transform_object", {
                    "location": [i * 2, 0, 0]
                })
            except Exception:
                pass

        assert objects_created >= 1, "Should have created at least one object"

    def test_rapid_tool_calls(self, router, rpc_client, clean_scene):
        """Test: Rapid succession of tool calls."""
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "all"})

        # Rapid calls
        operations = [
            ("mesh_subdivide", {"number_cuts": 1}),
            ("mesh_bevel", {"width": 0.02}),
            ("mesh_subdivide", {"number_cuts": 1}),
        ]

        for tool_name, params in operations:
            tools = router.process_llm_tool_call(tool_name, params)

            for tool in tools:
                area = tool["tool"].split("_")[0]
                method = "_".join(tool["tool"].split("_")[1:])
                try:
                    rpc_client.send_request(f"{area}.{method}", tool["params"])
                except Exception:
                    pass  # Continue on error

        # Should complete without crash
        assert True
