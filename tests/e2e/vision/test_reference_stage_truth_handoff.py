"""Blender-backed E2E checks for stage compare truth bundle / followup handoff."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

import pytest
from server.adapters.mcp.areas.reference import reference_compare_stage_checkpoint, reference_images
from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantRunResult,
    VisionAssistContract,
)
from server.adapters.mcp.session_capabilities import update_session_from_router_goal
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler

pytestmark = pytest.mark.e2e


@dataclass
class FakeContext:
    state: dict[str, object] = field(default_factory=dict)

    def get_state(self, key: str):
        return self.state.get(key)

    def set_state(self, key: str, value, *, serializable: bool = True) -> None:
        self.state[key] = value

    def info(self, message, logger_name=None, extra=None):
        return None


def _skip_if_blender_unavailable(error: RuntimeError) -> None:
    error_msg = str(error).lower()
    if "could not connect" in error_msg or "is blender running" in error_msg:
        pytest.skip(f"Blender not available: {error}")
    raise error


@pytest.fixture(scope="session")
def scene_handler(rpc_client):
    return SceneToolHandler(rpc_client)


@pytest.fixture(scope="session")
def modeling_handler(rpc_client):
    return ModelingToolHandler(rpc_client)


@pytest.fixture
def clean_scene(scene_handler):
    try:
        scene_handler.clean_scene(keep_lights_and_cameras=False)
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)
    yield
    try:
        scene_handler.clean_scene(keep_lights_and_cameras=False)
    except RuntimeError:
        pass


def test_reference_compare_stage_checkpoint_exposes_truth_bundle_and_followup(
    clean_scene,
    scene_handler,
    modeling_handler,
    tmp_path,
    monkeypatch,
):
    head_name = "TruthHead"
    body_name = "TruthBody"
    reference_path = tmp_path / "truth_ref.png"
    reference_path.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=head_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.0, location=[4, 0, 0])

        ctx = FakeContext()
        update_session_from_router_goal(ctx, "low poly creature", {"status": "no_match"})
        asyncio.run(
            reference_images(
                ctx,
                action="attach",
                source_path=str(reference_path),
                label="front_ref",
                target_object=head_name,
                target_view="front",
            )
        )

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
                    goal_summary="The head/body stage still needs assembly corrections.",
                    visible_changes=["The head and body are both visible in the staged capture."],
                    correction_focus=["TruthHead -> TruthBody contact"],
                ),
            )

        monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
        monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())
        monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: scene_handler)

        result = asyncio.run(
            reference_compare_stage_checkpoint(
                ctx,
                target_object=head_name,
                target_objects=[body_name],
                checkpoint_label="stage_truth",
                target_view="front",
                preset_profile="compact",
            )
        )

        assert result.error is None
        assert result.assembled_target_scope is not None
        assert result.assembled_target_scope.scope_kind == "object_set"
        assert result.assembled_target_scope.object_names == [head_name, body_name]
        assert result.truth_bundle is not None
        assert result.truth_bundle.summary.pair_count == 1
        assert result.truth_bundle.summary.contact_failures == 1
        assert result.truth_bundle.summary.separated_pairs == 1
        assert result.truth_followup is not None
        assert result.truth_followup.continue_recommended is True
        assert result.truth_followup.focus_pairs == [f"{head_name} -> {body_name}"]
        assert any(item.tool_name == "scene_assert_contact" for item in result.truth_followup.items)
        assert any(item.tool_name == "scene_measure_gap" for item in result.truth_followup.items)
        assert result.correction_candidates
        assert result.correction_candidates[0].focus_pairs == [f"{head_name} -> {body_name}"]
        assert "truth" in result.correction_candidates[0].source_signals
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)


def test_reference_compare_stage_checkpoint_prefers_body_anchor_for_multi_part_creature_scope(
    clean_scene,
    scene_handler,
    modeling_handler,
    tmp_path,
    monkeypatch,
):
    head_name = "TruthBodyAnchorHead"
    body_name = "TruthBodyAnchorBody"
    tail_name = "TruthBodyAnchorTail"
    reference_path = tmp_path / "truth_body_anchor_ref.png"
    reference_path.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=head_name, size=1.5, location=[-4, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.5, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=tail_name, size=1.0, location=[4, 0, 0])
        modeling_handler.transform_object(name=tail_name, scale=[0.8, 0.25, 0.25])

        ctx = FakeContext()
        update_session_from_router_goal(ctx, "low poly creature", {"status": "no_match"})
        asyncio.run(
            reference_images(
                ctx,
                action="attach",
                source_path=str(reference_path),
                label="front_ref",
                target_object=body_name,
                target_view="front",
            )
        )

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
                    goal_summary="The body remains the structural anchor for the current creature stage.",
                    visible_changes=["Head, body, and tail are visible in the staged capture."],
                    correction_focus=["TruthBodyAnchorBody -> TruthBodyAnchorTail contact"],
                ),
            )

        monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
        monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())
        monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: scene_handler)

        result = asyncio.run(
            reference_compare_stage_checkpoint(
                ctx,
                target_objects=[head_name, body_name, tail_name],
                checkpoint_label="stage_truth_body_anchor",
                target_view="front",
                preset_profile="compact",
            )
        )

        assert result.error is None
        assert result.assembled_target_scope is not None
        assert result.assembled_target_scope.primary_target == body_name
        assert result.truth_bundle is not None
        assert result.truth_bundle.summary.pair_count == 2
        assert result.truth_followup is not None
        assert result.truth_followup.focus_pairs == [
            f"{body_name} -> {head_name}",
            f"{body_name} -> {tail_name}",
        ]
        assert result.correction_candidates
        assert result.correction_candidates[0].focus_pairs[0].startswith(f"{body_name} -> ")
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)
