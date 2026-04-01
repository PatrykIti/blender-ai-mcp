"""Tests for the goal-scoped reference image MCP surface."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from server.adapters.mcp.areas.reference import (
    reference_compare_checkpoint,
    reference_compare_current_view,
    reference_compare_stage_checkpoint,
    reference_images,
    reference_iterate_stage_checkpoint,
)
from server.adapters.mcp.contracts.reference import ReferenceCompareStageCheckpointResponseContract
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
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


def test_reference_compare_current_view_requires_goal_before_capture(monkeypatch):
    class SceneHandler:
        def get_viewport(self, **kwargs):
            raise AssertionError("get_viewport should not be called without an active goal")

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())

    result = asyncio.run(reference_compare_current_view(FakeContext(), checkpoint_label="no_goal"))

    assert result.error is not None
    assert "router_set_goal" in result.error
    assert result.checkpoint_path == ""


def test_reference_compare_stage_checkpoint_captures_deterministic_stage_set(tmp_path, monkeypatch):
    image_front = tmp_path / "front.png"
    image_side = tmp_path / "side.png"
    image_front.write_bytes(b"front")
    image_side.write_bytes(b"side")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image_front),
            label="front_ref",
            target_object="Squirrel",
            target_view="front",
        )
    )
    asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image_side),
            label="side_ref",
            target_object="Squirrel",
            target_view="side",
        )
    )

    class SceneHandler:
        pass

    class CollectionHandler:
        def list_objects(self, collection_name: str, recursive: bool = True, include_hidden: bool = False):
            return {"objects": []}

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
                goal_summary="Stage checkpoint is moving closer to the squirrel references.",
                visible_changes=["The tail arc is more readable from side and front views."],
                shape_mismatches=["Head silhouette is still too spherical."],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_collection_handler", lambda: CollectionHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.capture_stage_images",
        lambda *args, **kwargs: [
            VisionCaptureImageContract(
                label="context_wide_after",
                image_path=str(tmp_path / "context.jpg"),
                host_visible_path=str(tmp_path / "context.jpg"),
                preset_name="context_wide",
                media_type="image/jpeg",
                view_kind="wide",
            ),
            VisionCaptureImageContract(
                label="target_front_after",
                image_path=str(tmp_path / "front.jpg"),
                host_visible_path=str(tmp_path / "front.jpg"),
                preset_name="target_front",
                media_type="image/jpeg",
                view_kind="focus",
            ),
            VisionCaptureImageContract(
                label="target_side_after",
                image_path=str(tmp_path / "side.jpg"),
                host_visible_path=str(tmp_path / "side.jpg"),
                preset_name="target_side",
                media_type="image/jpeg",
                view_kind="focus",
            ),
        ],
    )

    result = asyncio.run(
        reference_compare_stage_checkpoint(
            ctx,
            target_object="Squirrel",
            checkpoint_label="stage_3",
            preset_profile="compact",
        )
    )

    assert result.error is None
    assert result.reference_count == 2
    assert result.capture_count == 3
    assert result.preset_profile == "compact"
    assert result.preset_names == ["context_wide", "target_front", "target_side"]
    assert result.vision_assistant is not None
    assert [image.role for image in captured["request"].images] == [
        "after",
        "after",
        "after",
        "reference",
        "reference",
    ]
    assert "comparison_mode=stage_checkpoint_vs_reference" in (captured["request"].prompt_hint or "")


def test_reference_compare_stage_checkpoint_requires_goal_or_override():
    result = asyncio.run(reference_compare_stage_checkpoint(FakeContext(), target_object="Squirrel"))

    assert result.error is not None
    assert "router_set_goal" in result.error


def test_reference_compare_stage_checkpoint_can_compare_full_scene_when_target_object_is_omitted(tmp_path, monkeypatch):
    image_front = tmp_path / "front.png"
    image_side = tmp_path / "side.png"
    image_front.write_bytes(b"front")
    image_side.write_bytes(b"side")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(reference_images(ctx, action="attach", source_path=str(image_front), label="front_ref"))
    asyncio.run(reference_images(ctx, action="attach", source_path=str(image_side), label="side_ref"))

    captured = {}

    class SceneHandler:
        pass

    class CollectionHandler:
        def list_objects(self, collection_name: str, recursive: bool = True, include_hidden: bool = False):
            return {"objects": []}

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
                goal_summary="The full squirrel scene is closer to the references.",
                visible_changes=["The full silhouette is visible across the deterministic views."],
                correction_focus=["Tail arc visibility"],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_collection_handler", lambda: CollectionHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.capture_stage_images",
        lambda *args, **kwargs: [
            VisionCaptureImageContract(
                label="context_wide_after",
                image_path=str(tmp_path / "context.jpg"),
                host_visible_path=str(tmp_path / "context.jpg"),
                preset_name="context_wide",
                media_type="image/jpeg",
                view_kind="wide",
            ),
            VisionCaptureImageContract(
                label="target_front_after",
                image_path=str(tmp_path / "front.jpg"),
                host_visible_path=str(tmp_path / "front.jpg"),
                preset_name="target_front",
                media_type="image/jpeg",
                view_kind="focus",
            ),
        ],
    )

    result = asyncio.run(
        reference_compare_stage_checkpoint(
            ctx,
            checkpoint_label="stage_full_scene",
            preset_profile="compact",
        )
    )

    assert result.error is None
    assert result.target_object is None
    assert result.reference_count == 2
    assert captured["request"].target_object is None


def test_reference_compare_stage_checkpoint_can_expand_collection_scope(tmp_path, monkeypatch):
    image_front = tmp_path / "front.png"
    image_side = tmp_path / "side.png"
    image_front.write_bytes(b"front")
    image_side.write_bytes(b"side")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(reference_images(ctx, action="attach", source_path=str(image_front), label="front_ref"))
    asyncio.run(reference_images(ctx, action="attach", source_path=str(image_side), label="side_ref"))

    captured = {}

    class CollectionHandler:
        def list_objects(self, collection_name: str, recursive: bool = True, include_hidden: bool = False):
            assert collection_name == "Squirrel"
            return {
                "objects": [
                    {"name": "Squirrel_Head"},
                    {"name": "Squirrel_Body"},
                    {"name": "Squirrel_Tail"},
                ]
            }

    class SceneHandler:
        pass

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
                goal_summary="The squirrel collection is closer to the references.",
                visible_changes=["The full squirrel silhouette is visible."],
                correction_focus=["Tail/body ratio"],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_collection_handler", lambda: CollectionHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_collection_handler", lambda: CollectionHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.capture_stage_images",
        lambda *args, **kwargs: [
            VisionCaptureImageContract(
                label="context_wide_after",
                image_path=str(tmp_path / "context.jpg"),
                host_visible_path=str(tmp_path / "context.jpg"),
                preset_name="context_wide",
                media_type="image/jpeg",
                view_kind="wide",
            ),
        ],
    )

    result = asyncio.run(
        reference_compare_stage_checkpoint(
            ctx,
            collection_name="Squirrel",
            checkpoint_label="stage_full_collection",
            preset_profile="compact",
        )
    )

    assert result.error is None
    assert result.collection_name == "Squirrel"
    assert result.target_objects == ["Squirrel_Head", "Squirrel_Body", "Squirrel_Tail"]
    assert captured["request"].metadata["collection_name"] == "Squirrel"


def test_reference_compare_stage_checkpoint_sanitizes_checkpoint_id_target_token(tmp_path, monkeypatch):
    image_front = tmp_path / "front.png"
    image_front.write_bytes(b"front")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(reference_images(ctx, action="attach", source_path=str(image_front), label="front_ref"))

    class SceneHandler:
        pass

    class CollectionHandler:
        def list_objects(self, collection_name: str, recursive: bool = True, include_hidden: bool = False):
            return {"objects": []}

    async def _fake_run_vision_assist(ctx, *, request, resolver):
        return AssistantRunResult(
            status="success",
            assistant_name="vision_assist",
            message="ok",
            budget=AssistantBudgetContract(max_input_chars=1000, max_messages=1, max_tokens=100, tool_budget=0),
            capability_source="local_runtime",
            result=VisionAssistContract(
                backend_kind="mlx_local",
                model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                goal_summary="ok",
                visible_changes=[],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_collection_handler", lambda: CollectionHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.capture_stage_images",
        lambda *args, **kwargs: [
            VisionCaptureImageContract(
                label="context_wide_after",
                image_path=str(tmp_path / "context.jpg"),
                host_visible_path=str(tmp_path / "context.jpg"),
                preset_name="context_wide",
                media_type="image/jpeg",
                view_kind="wide",
            ),
        ],
    )

    result = asyncio.run(
        reference_compare_stage_checkpoint(
            ctx,
            collection_name="Squirrel/Head",
            checkpoint_label="unsafe_target",
            preset_profile="compact",
        )
    )

    assert result.error is None
    assert "/" not in result.checkpoint_id
    assert "\\" not in result.checkpoint_id
    assert "Squirrel_Head" in result.checkpoint_id


def test_reference_iterate_stage_checkpoint_tracks_previous_focus_and_iteration(tmp_path, monkeypatch):
    image_front = tmp_path / "front.png"
    image_side = tmp_path / "side.png"
    image_front.write_bytes(b"front")
    image_side.write_bytes(b"side")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image_front),
            label="front_ref",
            target_object="Squirrel",
            target_view="front",
        )
    )
    asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image_side),
            label="side_ref",
            target_object="Squirrel",
            target_view="side",
        )
    )

    # use the public helper via monkeypatching the internal compare call site
    first_compare = ReferenceCompareStageCheckpointResponseContract.model_validate(
        {
            "action": "compare_stage_checkpoint",
            "goal": "low poly squirrel",
            "target_object": "Squirrel",
            "checkpoint_id": "checkpoint_1",
            "checkpoint_label": "stage_1",
            "preset_profile": "compact",
            "preset_names": ["context_wide", "target_front"],
            "capture_count": 2,
            "captures": [],
            "reference_count": 2,
            "reference_ids": ["ref_1", "ref_2"],
            "reference_labels": ["front_ref", "side_ref"],
            "vision_assistant": {
                "status": "success",
                "assistant_name": "vision_assist",
                "message": "ok",
                "budget": {"max_input_chars": 1000, "max_messages": 1, "max_tokens": 100, "tool_budget": 0},
                "capability_source": "local_runtime",
                "result": {
                    "backend_kind": "mlx_local",
                    "goal_summary": "Closer to the squirrel reference.",
                    "visible_changes": ["Tail arc is larger."],
                    "shape_mismatches": ["Head silhouette is still too spherical."],
                    "proportion_mismatches": [],
                    "correction_focus": ["Head silhouette"],
                    "next_corrections": ["Flatten the head silhouette slightly."],
                    "likely_issues": [],
                    "recommended_checks": [],
                    "captures_used": ["target_front_after"],
                },
            },
        }
    )
    second_compare = ReferenceCompareStageCheckpointResponseContract.model_validate(
        {
            **first_compare.model_dump(mode="json"),
            "checkpoint_id": "checkpoint_2",
            "checkpoint_label": "stage_2",
            "vision_assistant": {
                **first_compare.vision_assistant.model_dump(mode="json"),
                "result": {
                    **first_compare.vision_assistant.result.model_dump(mode="json"),
                    "correction_focus": ["Head silhouette", "Tail/body ratio"],
                },
            },
        }
    )
    compares = [first_compare, second_compare]

    async def _fake_reference_compare_stage_checkpoint(*args, **kwargs):
        return compares.pop(0)

    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.reference_compare_stage_checkpoint",
        _fake_reference_compare_stage_checkpoint,
    )

    first = asyncio.run(
        reference_iterate_stage_checkpoint(
            ctx,
            target_object="Squirrel",
            checkpoint_label="stage_1",
        )
    )
    second = asyncio.run(
        reference_iterate_stage_checkpoint(
            ctx,
            target_object="Squirrel",
            checkpoint_label="stage_2",
        )
    )

    assert first.iteration_index == 1
    assert first.loop_disposition == "continue_build"
    assert first.prior_correction_focus == []
    assert second.iteration_index == 2
    assert second.prior_checkpoint_id == "checkpoint_1"
    assert second.prior_correction_focus == ["Head silhouette"]
    assert second.repeated_correction_focus == ["Head silhouette"]
    assert second.loop_disposition == "continue_build"


def test_reference_iterate_stage_checkpoint_escalates_after_repeated_focus(monkeypatch):
    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})

    compare = ReferenceCompareStageCheckpointResponseContract.model_validate(
        {
            "action": "compare_stage_checkpoint",
            "goal": "low poly squirrel",
            "target_object": "Squirrel",
            "checkpoint_id": "checkpoint_repeat",
            "checkpoint_label": "stage_repeat",
            "preset_profile": "compact",
            "preset_names": ["context_wide"],
            "capture_count": 1,
            "captures": [],
            "reference_count": 0,
            "reference_ids": [],
            "reference_labels": [],
            "vision_assistant": {
                "status": "success",
                "assistant_name": "vision_assist",
                "message": "ok",
                "budget": {"max_input_chars": 1000, "max_messages": 1, "max_tokens": 100, "tool_budget": 0},
                "capability_source": "local_runtime",
                "result": {
                    "backend_kind": "mlx_local",
                    "goal_summary": "Still off from the squirrel reference.",
                    "visible_changes": ["The body is a bit fuller."],
                    "shape_mismatches": ["Head silhouette is still too spherical."],
                    "proportion_mismatches": [],
                    "correction_focus": ["Head silhouette"],
                    "next_corrections": ["Flatten the head silhouette slightly."],
                    "likely_issues": [],
                    "recommended_checks": [],
                    "captures_used": ["target_front_after"],
                },
            },
        }
    )

    async def _fake_reference_compare_stage_checkpoint(*args, **kwargs):
        return compare

    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.reference_compare_stage_checkpoint",
        _fake_reference_compare_stage_checkpoint,
    )

    first = asyncio.run(reference_iterate_stage_checkpoint(ctx, target_object="Squirrel", checkpoint_label="stage_1"))
    second = asyncio.run(reference_iterate_stage_checkpoint(ctx, target_object="Squirrel", checkpoint_label="stage_2"))
    third = asyncio.run(reference_iterate_stage_checkpoint(ctx, target_object="Squirrel", checkpoint_label="stage_3"))

    assert first.loop_disposition == "continue_build"
    assert second.loop_disposition == "continue_build"
    assert third.loop_disposition == "inspect_validate"
    assert third.stagnation_count >= 2
