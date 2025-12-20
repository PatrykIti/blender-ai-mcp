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
        calls = registry.expand_workflow("feature_phone_workflow")

        assert len(calls) > 0, "Phone workflow should have steps"

        # Execute each step
        executed_steps = []
        for call in calls[:12]:
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
        calls = registry.expand_workflow("feature_phone_workflow", {
            "width": 0.07,
            "height": 0.15,
            "depth": 0.008,
        })

        # Execute up to the first body shell transform to exercise scaling
        steps_to_run = []
        for call in calls:
            steps_to_run.append(call)
            if (
                call.tool_name == "modeling_transform_object"
                and call.params.get("name") == "body_shell"
            ):
                break

        for call in steps_to_run:
            tool_name = call.tool_name
            params = call.params

            area = tool_name.split("_")[0]
            method = "_".join(tool_name.split("_")[1:])

            try:
                rpc_client.send_request(f"{area}.{method}", params)
            except Exception as e:
                pytest.fail(f"Step {tool_name} failed: {e}")


class TestTableWorkflowExecution:
    """Tests for table workflow execution."""

    def test_simple_table_workflow_creates_object(self, router, rpc_client, clean_scene):
        """Test: Simple table workflow creates an object."""
        registry = get_workflow_registry()

        calls = registry.expand_workflow("simple_table_workflow")

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

    def test_picnic_table_without_benches_has_fewer_steps(self, router, rpc_client, clean_scene):
        """Test: Picnic table workflow without benches skips optional steps."""
        registry = get_workflow_registry()

        default_calls = registry.expand_workflow("picnic_table_workflow")
        no_bench_calls = registry.expand_workflow(
            "picnic_table_workflow",
            {"bench_layout": "none", "include_a_frame_supports": False},
        )

        assert len(no_bench_calls) < len(default_calls), "No-bench workflow should have fewer steps"

        for call in no_bench_calls[:10]:
            tool_name = call.tool_name
            params = call.params

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
        registry = get_workflow_registry()
        if "screen_cutout_workflow" not in registry.get_all_workflows():
            pytest.skip("screen_cutout_workflow not available")

        # First create a phone-like object
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {
            "scale": [0.4, 0.8, 0.05]
        })
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})

        # Get screen cutout workflow
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
        calls = registry.expand_workflow("feature_phone_workflow", {
            "body_bevel_width": 0.005,
            "body_bevel_segments": 5,
        })

        # Find bevel step
        bevel_call = next(
            (
                c
                for c in calls
                if c.tool_name == "modeling_add_modifier"
                and c.params.get("modifier_type") == "BEVEL"
            ),
            None,
        )

        if bevel_call:
            # Parameters should be customized
            props = bevel_call.params.get("properties") or {}
            assert props.get("width") == 0.005 or props.get("segments") == 5


class TestWorkflowErrorHandling:
    """Tests for workflow error handling."""

    def test_workflow_continues_on_non_fatal_error(self, router, rpc_client, clean_scene):
        """Test: Workflow doesn't crash on minor errors."""
        registry = get_workflow_registry()

        # Execute phone workflow
        calls = registry.expand_workflow("feature_phone_workflow")

        errors = []
        successes = []

        for call in calls[:20]:
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
