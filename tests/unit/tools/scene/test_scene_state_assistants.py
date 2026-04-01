"""Tests for assistant_summary support on scene state read tools."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantRunResult,
    InspectionSummaryContract,
)


def _assistant_result(subject: str, overview: str) -> AssistantRunResult[InspectionSummaryContract]:
    return AssistantRunResult(
        status="success",
        assistant_name="inspection_summarizer",
        message="ok",
        budget=AssistantBudgetContract(
            max_input_chars=1000,
            max_messages=1,
            max_tokens=100,
            tool_budget=0,
        ),
        capability_source="client",
        result=InspectionSummaryContract(
            inspection_action=subject,
            overview=overview,
            key_findings=["bounded summary"],
            truth_source="inspection_contract",
        ),
    )


@patch("server.adapters.mcp.areas.scene.run_inspection_summary_assistant")
@patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
def test_scene_snapshot_state_can_attach_assistant_summary(
    mock_router_enabled,
    mock_assistant,
    monkeypatch,
):
    from server.adapters.mcp.areas.scene import scene_snapshot_state

    class Handler:
        def snapshot_state(self, include_mesh_stats=False, include_materials=False):
            return {"snapshot": {"object_count": 1, "mode": "OBJECT"}, "hash": "abc123"}

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)
    mock_assistant.return_value = _assistant_result("scene_snapshot_state", "Snapshot summary")

    result = asyncio.run(scene_snapshot_state(MagicMock(), assistant_summary=True))

    assert result.assistant is not None
    assert result.assistant.result.overview == "Snapshot summary"


@patch("server.adapters.mcp.areas.scene.run_inspection_summary_assistant")
@patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
def test_scene_compare_snapshot_can_attach_assistant_summary(
    mock_router_enabled,
    mock_assistant,
    monkeypatch,
):
    from server.adapters.mcp.areas.scene import scene_compare_snapshot

    class DiffService:
        def compare_snapshots(self, baseline_snapshot, target_snapshot, ignore_minor_transforms=0.0):
            return {
                "objects_added": ["Cube"],
                "objects_removed": [],
                "objects_modified": [],
                "baseline_hash": "base",
                "target_hash": "target",
                "baseline_timestamp": "t1",
                "target_timestamp": "t2",
                "has_changes": True,
            }

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_snapshot_diff_service", lambda: DiffService())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)
    mock_assistant.return_value = _assistant_result("scene_compare_snapshot", "Diff summary")

    result = asyncio.run(
        scene_compare_snapshot(
            MagicMock(),
            baseline_snapshot="{}",
            target_snapshot="{}",
            assistant_summary=True,
        )
    )

    assert result.assistant is not None
    assert result.assistant.result.overview == "Diff summary"


@patch("server.adapters.mcp.areas.scene.run_inspection_summary_assistant")
@patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
def test_scene_get_hierarchy_can_attach_assistant_summary(
    mock_router_enabled,
    mock_assistant,
    monkeypatch,
):
    from server.adapters.mcp.areas.scene import scene_get_hierarchy

    class Handler:
        def get_hierarchy(self, object_name=None, include_transforms=False):
            return {"roots": [{"name": object_name or "Cube"}], "total_objects": 1}

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)
    mock_assistant.return_value = _assistant_result("scene_get_hierarchy", "Hierarchy summary")

    result = asyncio.run(scene_get_hierarchy(MagicMock(), object_name="Cube", assistant_summary=True))

    assert result.assistant is not None
    assert result.assistant.result.overview == "Hierarchy summary"


@patch("server.adapters.mcp.areas.scene.run_inspection_summary_assistant")
@patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
def test_scene_get_bounding_box_can_attach_assistant_summary(
    mock_router_enabled,
    mock_assistant,
    monkeypatch,
):
    from server.adapters.mcp.areas.scene import scene_get_bounding_box

    class Handler:
        def get_bounding_box(self, object_name, world_space=True):
            return {"min": [0, 0, 0], "max": [1, 1, 1], "volume": 1.0}

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)
    mock_assistant.return_value = _assistant_result("scene_get_bounding_box", "Bounding box summary")

    result = asyncio.run(scene_get_bounding_box(MagicMock(), object_name="Cube", assistant_summary=True))

    assert result.assistant is not None
    assert result.assistant.result.overview == "Bounding box summary"


@patch("server.adapters.mcp.areas.scene.run_inspection_summary_assistant")
@patch("server.adapters.mcp.router_helper.is_router_enabled", return_value=False)
def test_scene_get_origin_info_can_attach_assistant_summary(
    mock_router_enabled,
    mock_assistant,
    monkeypatch,
):
    from server.adapters.mcp.areas.scene import scene_get_origin_info

    class Handler:
        def get_origin_info(self, object_name):
            return {"origin_world": [0, 0, 0], "suggestions": ["center"]}

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)
    mock_assistant.return_value = _assistant_result("scene_get_origin_info", "Origin summary")

    result = asyncio.run(scene_get_origin_info(MagicMock(), object_name="Cube", assistant_summary=True))

    assert result.assistant is not None
    assert result.assistant.result.overview == "Origin summary"
