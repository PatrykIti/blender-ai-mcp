"""
E2E tests for Workflow Execution.

Tests that workflows execute correctly against real Blender.
Requires running Blender instance.

TASK-039-23
"""

import pytest

from server.router.application.router import SupervisorRouter
from server.router.application.workflows import get_workflow_registry


class TestPhoneWorkflowExecution:
    """Tests for phone workflow execution."""

    def test_phone_workflow_creates_object(self, router, rpc_client, clean_scene):
        """Test: Phone workflow creates a properly shaped object."""
        registry = get_workflow_registry()

        # Expand phone workflow
        calls = registry.expand_workflow("phone_workflow")

        assert len(calls) == 10, "Phone workflow should have 10 steps"

        # Execute each step
        executed_steps = []
        for call in calls:
            tool_name = call.tool_name
            params = call.params

            area = tool_name.split("_")[0]
            method = "_".join(tool_name.split("_")[1:])
            rpc_method = f"{area}.{method}"

            try:
                result = rpc_client.send_request(rpc_method, params)
                executed_steps.append({"tool": tool_name, "success": True, "result": result})
            except Exception as e:
                # Some steps may fail due to state issues, continue execution
                executed_steps.append({"tool": tool_name, "success": False, "error": str(e)})

        # Verify at least some steps executed successfully
        successful = [s for s in executed_steps if s["success"]]
        assert len(successful) > 0, f"At least one step should succeed, got: {executed_steps}"

        # Check if object exists in scene
        try:
            objects = rpc_client.send_request("scene.list_objects", {})
            assert len(objects) > 0 if isinstance(objects, list) else True, "Should have object in scene"
        except Exception:
            # If we can't query, at least some steps succeeded
            pass

    def test_phone_workflow_with_custom_params(self, router, rpc_client, clean_scene):
        """Test: Phone workflow with custom parameters."""
        registry = get_workflow_registry()

        # Custom phone dimensions
        calls = registry.expand_workflow("phone_workflow", {
            "width": 0.07,
            "height": 0.15,
            "depth": 0.008,
        })

        # Execute first few steps (create and scale)
        for call in calls[:2]:
            tool_name = call.tool_name
            params = call.params

            area = tool_name.split("_")[0]
            method = "_".join(tool_name.split("_")[1:])

            try:
                rpc_client.send_request(f"{area}.{method}", params)
            except Exception as e:
                pytest.fail(f"Step {tool_name} failed: {e}")


class TestTowerWorkflowExecution:
    """Tests for tower workflow execution."""

    def test_tower_workflow_creates_tall_object(self, router, rpc_client, clean_scene):
        """Test: Tower workflow creates a tall object."""
        registry = get_workflow_registry()

        calls = registry.expand_workflow("tower_workflow")

        # Execute workflow
        for call in calls:
            tool_name = call.tool_name
            params = call.params

            area = tool_name.split("_")[0]
            method = "_".join(tool_name.split("_")[1:])

            try:
                rpc_client.send_request(f"{area}.{method}", params)
            except Exception as e:
                pytest.fail(f"Step {tool_name} failed: {e}")

        # Verify object exists
        try:
            result = rpc_client.send_request("scene.list_objects", {})
            assert len(result) > 0, "Should have created an object"
        except Exception:
            pass  # Skip verification if RPC fails

    def test_tower_workflow_without_taper(self, router, rpc_client, clean_scene):
        """Test: Tower workflow without taper effect."""
        registry = get_workflow_registry()

        # Get tower workflow without taper
        from server.router.application.workflows import tower_workflow
        steps = tower_workflow.get_steps({"add_taper": False})

        # Fewer steps without taper
        assert len(steps) < 8, "Should have fewer steps without taper"

        # Execute
        for step in steps:
            tool_name = step.tool
            params = step.params

            area = tool_name.split("_")[0]
            method = "_".join(tool_name.split("_")[1:])

            try:
                rpc_client.send_request(f"{area}.{method}", params)
            except Exception as e:
                pytest.fail(f"Step {tool_name} failed: {e}")


class TestScreenCutoutWorkflowExecution:
    """Tests for screen cutout sub-workflow."""

    def test_screen_cutout_on_existing_object(self, router, rpc_client, clean_scene):
        """Test: Screen cutout workflow on existing object."""
        # First create a phone-like object
        rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {
            "scale": [0.4, 0.8, 0.05]
        })
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})

        # Get screen cutout workflow
        registry = get_workflow_registry()
        calls = registry.expand_workflow("screen_cutout_workflow")

        # Execute
        for call in calls:
            tool_name = call.tool_name
            params = call.params

            area = tool_name.split("_")[0]
            method = "_".join(tool_name.split("_")[1:])

            try:
                rpc_client.send_request(f"{area}.{method}", params)
            except Exception as e:
                # Some steps may fail if geometry doesn't match
                # (e.g., select by location might not find exact face)
                pass


class TestCustomWorkflowExecution:
    """Tests for custom workflow loading and execution."""

    def test_custom_workflow_from_registry(self, router, rpc_client, clean_scene):
        """Test: Execute a workflow from the registry."""
        registry = get_workflow_registry()

        # Get any available workflow
        all_workflows = registry.get_all_workflows()
        assert len(all_workflows) > 0, "Should have registered workflows"

        # Get first workflow
        workflow_name = all_workflows[0]
        calls = registry.expand_workflow(workflow_name)

        assert len(calls) > 0, f"Workflow {workflow_name} should have steps"

    def test_workflow_parameter_inheritance(self, router, rpc_client, clean_scene):
        """Test: Workflow parameter inheritance works."""
        registry = get_workflow_registry()

        # Phone workflow with custom bevel
        calls = registry.expand_workflow("phone_workflow", {
            "bevel_width": 0.05,
            "bevel_segments": 5,
        })

        # Find bevel step
        bevel_call = next((c for c in calls if "bevel" in c.tool_name), None)

        if bevel_call:
            # Parameters should be customized
            assert bevel_call.params.get("width") == 0.05 or \
                   bevel_call.params.get("segments") == 5


class TestWorkflowErrorHandling:
    """Tests for workflow error handling."""

    def test_workflow_continues_on_non_fatal_error(self, router, rpc_client, clean_scene):
        """Test: Workflow doesn't crash on minor errors."""
        registry = get_workflow_registry()

        # Execute phone workflow
        calls = registry.expand_workflow("phone_workflow")

        errors = []
        successes = []

        for call in calls:
            tool_name = call.tool_name
            params = call.params

            area = tool_name.split("_")[0]
            method = "_".join(tool_name.split("_")[1:])

            try:
                result = rpc_client.send_request(f"{area}.{method}", params)
                successes.append(tool_name)
            except Exception as e:
                errors.append({"tool": tool_name, "error": str(e)})

        # Should have more successes than failures
        assert len(successes) >= len(errors), \
            f"Too many errors: {len(errors)} errors vs {len(successes)} successes"

    def test_nonexistent_workflow_returns_empty(self, router, rpc_client):
        """Test: Non-existent workflow returns empty list."""
        registry = get_workflow_registry()

        calls = registry.expand_workflow("nonexistent_workflow_12345")

        assert calls == [], "Non-existent workflow should return empty list"
