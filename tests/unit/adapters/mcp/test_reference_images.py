"""Tests for the goal-scoped reference image MCP surface."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from server.adapters.mcp.areas.reference import (
    reference_compare_checkpoint,
    reference_compare_current_view,
    reference_images,
)
from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantRunResult,
    VisionAssistContract,
)
from server.adapters.mcp.session_capabilities import update_session_from_router_goal


@dataclass
class FakeContext:
    state: dict[str, object] = field(default_factory=dict)

    def get_state(self, key: str):
        return self.state.get(key)

    def set_state(self, key: str, value, *, serializable: bool = True) -> None:
        self.state[key] = value

    def info(self, message, logger_name=None, extra=None):
        return None


def test_reference_images_attach_without_active_goal_is_staged_for_next_goal(tmp_path, monkeypatch):
    image = tmp_path / "ref.png"
    image.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    result = asyncio.run(reference_images(ctx, action="attach", source_path=str(image), label="front_ref"))

    assert result.error is None
    assert result.goal is None
    assert result.reference_count == 1
    assert result.references[0].goal == "__pending_goal__"
    assert "pending reference image" in (result.message or "")

    state = update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    assert state.reference_images is not None
    assert state.reference_images[0]["goal"] == "low poly squirrel"
    assert state.pending_reference_images is None


def test_reference_images_attach_list_remove_and_clear(tmp_path, monkeypatch):
    image = tmp_path / "ref.png"
    image.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "rounded housing", {"status": "ready"})

    attached = asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image),
            label="main_ref",
            notes="front silhouette",
            target_object="Housing",
            target_view="front",
        )
    )

    assert attached.reference_count == 1
    ref = attached.references[0]
    assert ref.goal == "rounded housing"
    assert ref.label == "main_ref"
    assert ref.target_object == "Housing"
    assert ref.stored_path.endswith(".png")

    listed = asyncio.run(reference_images(ctx, action="list"))
    assert listed.reference_count == 1
    assert listed.references[0].reference_id == ref.reference_id

    removed = asyncio.run(reference_images(ctx, action="remove", reference_id=ref.reference_id))
    assert removed.reference_count == 0
    assert removed.removed_reference_id == ref.reference_id

    attached_again = asyncio.run(reference_images(ctx, action="attach", source_path=str(image)))
    assert attached_again.reference_count == 1
    cleared = asyncio.run(reference_images(ctx, action="clear"))
    assert cleared.reference_count == 0


def test_reference_compare_checkpoint_uses_goal_and_matching_references(tmp_path, monkeypatch):
    image = tmp_path / "ref.png"
    image.write_bytes(b"fake")
    checkpoint = tmp_path / "checkpoint.png"
    checkpoint.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image),
            label="front_ref",
            target_object="Squirrel",
            target_view="front",
        )
    )

    captured = {}

    async def _fake_run_vision_assist(ctx, *, request, resolver):
        captured["request"] = request
        return AssistantRunResult(
            status="success",
            assistant_name="vision_assist",
            message="ok",
            budget=AssistantBudgetContract(max_input_chars=1000, max_messages=1, max_tokens=100, tool_budget=0),
            capability_source="local_runtime",
            result=VisionAssistContract(
                backend_kind="mlx_local",
                model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                goal_summary="Closer to the squirrel reference.",
                visible_changes=["Tail arc is still too low."],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())

    result = asyncio.run(
        reference_compare_checkpoint(
            ctx,
            checkpoint_path=str(checkpoint),
            checkpoint_label="stage_2",
            target_object="Squirrel",
            target_view="front",
        )
    )

    assert result.error is None
    assert result.goal == "low poly squirrel"
    assert result.reference_count == 1
    assert result.reference_labels == ["front_ref"]
    assert result.vision_assistant is not None
    assert result.vision_assistant.result is not None
    assert captured["request"].goal == "low poly squirrel"
    assert [image.role for image in captured["request"].images] == ["after", "reference"]


def test_reference_compare_checkpoint_requires_goal_or_override(tmp_path):
    checkpoint = tmp_path / "checkpoint.png"
    checkpoint.write_bytes(b"fake")

    result = asyncio.run(reference_compare_checkpoint(FakeContext(), checkpoint_path=str(checkpoint)))

    assert result.error is not None
    assert "router_set_goal" in result.error


def test_reference_compare_current_view_captures_then_compares(tmp_path, monkeypatch):
    image = tmp_path / "ref.png"
    image.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image),
            label="side_ref",
            target_object="Squirrel",
            target_view="side",
        )
    )

    class SceneHandler:
        def get_viewport(self, **kwargs):
            return "ZmFrZQ=="  # base64("fake")

    captured = {}

    async def _fake_run_vision_assist(ctx, *, request, resolver):
        captured["request"] = request
        return AssistantRunResult(
            status="success",
            assistant_name="vision_assist",
            message="ok",
            budget=AssistantBudgetContract(max_input_chars=1000, max_messages=1, max_tokens=100, tool_budget=0),
            capability_source="local_runtime",
            result=VisionAssistContract(
                backend_kind="mlx_local",
                model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                goal_summary="Current side checkpoint is closer to the squirrel reference.",
                visible_changes=["Tail arc is now more visible."],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())

    result = asyncio.run(
        reference_compare_current_view(
            ctx,
            checkpoint_label="stage_3_side",
            target_object="Squirrel",
            target_view="side",
            camera_name="ShotCam",
        )
    )

    assert result.error is None
    assert result.reference_count == 1
    assert result.vision_assistant is not None
    assert result.vision_assistant.result is not None
    assert result.checkpoint_path.endswith(".jpg")
    assert [image.role for image in captured["request"].images] == ["after", "reference"]
    assert "comparison_mode=current_view_checkpoint" in (captured["request"].prompt_hint or "")
