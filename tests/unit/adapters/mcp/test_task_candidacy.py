"""Tests for TASK-088 execution-mode candidacy inventory."""

from server.adapters.mcp.tasks.candidacy import (
    TASK_CANDIDACY_MATRIX,
    get_task_candidacy,
    get_tool_task_config,
)


def test_task_candidacy_matrix_classifies_initial_heavy_operations():
    """Heavy operations should have an explicit candidacy entry before rollout."""

    operation_keys = {entry.operation_key for entry in TASK_CANDIDACY_MATRIX}

    assert "scene_get_viewport" in operation_keys
    assert "extraction_render_angles" in operation_keys
    assert "workflow_catalog.import_finalize" in operation_keys
    assert "import.glb" in operation_keys
    assert "export.obj" in operation_keys

    assert get_task_candidacy("scene_get_viewport").adopted is True
    assert get_task_candidacy("workflow_catalog.import_finalize").backend_kind == "server_local"


def test_adopted_tools_expose_explicit_optional_task_configs():
    """Adopted MCP endpoints should carry a concrete TaskConfig, not implicit booleans."""

    scene_config = get_tool_task_config("scene_get_viewport")
    extraction_config = get_tool_task_config("extraction_render_angles")
    workflow_config = get_tool_task_config("workflow_catalog")

    assert scene_config is not None
    assert extraction_config is not None
    assert workflow_config is not None

    assert scene_config.mode == "optional"
    assert extraction_config.mode == "optional"
    assert workflow_config.mode == "optional"

    assert int(scene_config.poll_interval.total_seconds()) == 1
