"""Blender-backed E2E checks for multi-pair assembled-creature attachment truth."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from types import SimpleNamespace

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


def test_reference_compare_stage_checkpoint_surfaces_required_creature_seams_together(
    clean_scene,
    scene_handler,
    modeling_handler,
    tmp_path,
    monkeypatch,
):
    head_name = "AssembledHead"
    body_name = "AssembledBody"
    tail_name = "AssembledTail"
    snout_name = "AssembledSnout"
    nose_name = "AssembledNose"
    forelimb_name = "AssembledForelimb"
    reference_path = tmp_path / "assembled_creature_ref.png"
    reference_path.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.0, location=[0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=head_name, size=1.2, location=[-4.0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=tail_name, size=1.0, location=[4.0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=snout_name, size=1.0, location=[-6.0, 0, 0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=nose_name, size=1.0, location=[-7.0, 0, 0])
        modeling_handler.create_primitive(
            primitive_type="CUBE", name=forelimb_name, size=1.0, location=[2.0, 0.0, -2.5]
        )
        modeling_handler.transform_object(name=tail_name, scale=[0.8, 0.25, 0.25])
        modeling_handler.transform_object(name=snout_name, scale=[0.8, 0.5, 0.4])
        modeling_handler.transform_object(name=nose_name, scale=[0.16, 0.16, 0.16])
        modeling_handler.transform_object(name=forelimb_name, scale=[0.6, 0.3, 0.3])

        ctx = FakeContext()
        update_session_from_router_goal(ctx, "low poly creature", {"status": "no_match"})
        asyncio.run(reference_images(ctx, action="attach", source_path=str(reference_path), label="front_ref"))

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
                    goal_summary="Several required creature seams are still detached in the assembled stage.",
                    visible_changes=["Head, body, tail, snout, nose, and forelimb are visible in the staged capture."],
                    correction_focus=[
                        f"{head_name} -> {body_name} contact",
                        f"{snout_name} -> {head_name} seating",
                        f"{forelimb_name} -> {body_name} contact",
                    ],
                ),
            )

        monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
        monkeypatch.setattr(
            "server.adapters.mcp.areas.reference.get_vision_backend_resolver",
            lambda: SimpleNamespace(
                runtime_config=SimpleNamespace(max_tokens=1000, max_images=8, active_model_name="gpt-4.1")
            ),
        )
        monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: scene_handler)

        result = asyncio.run(
            reference_compare_stage_checkpoint(
                ctx,
                target_objects=[head_name, body_name, tail_name, snout_name, nose_name, forelimb_name],
                checkpoint_label="stage_assembled_creature",
                target_view="front",
                preset_profile="compact",
            )
        )

        assert result.error is None
        assert result.truth_bundle is not None
        assert result.truth_bundle.summary.pairing_strategy == "required_creature_seams"
        assert result.truth_bundle.summary.pair_count == 5

        pair_labels = [f"{item.from_object} -> {item.to_object}" for item in result.truth_bundle.checks]
        assert pair_labels == [
            f"{head_name} -> {body_name}",
            f"{tail_name} -> {body_name}",
            f"{forelimb_name} -> {body_name}",
            f"{snout_name} -> {head_name}",
            f"{nose_name} -> {snout_name}",
        ]

        semantics_by_pair = {
            f"{item.from_object} -> {item.to_object}": item.attachment_semantics for item in result.truth_bundle.checks
        }
        assert semantics_by_pair[f"{head_name} -> {body_name}"] is not None
        assert semantics_by_pair[f"{head_name} -> {body_name}"].preferred_macro == "macro_align_part_with_contact"
        assert semantics_by_pair[f"{forelimb_name} -> {body_name}"] is not None
        assert semantics_by_pair[f"{forelimb_name} -> {body_name}"].seam_kind == "limb_body"
        assert semantics_by_pair[f"{snout_name} -> {head_name}"] is not None
        assert semantics_by_pair[f"{snout_name} -> {head_name}"].preferred_macro == "macro_attach_part_to_surface"
        assert semantics_by_pair[f"{nose_name} -> {snout_name}"] is not None
        assert semantics_by_pair[f"{nose_name} -> {snout_name}"].seam_kind == "nose_snout"

        assert result.truth_followup is not None
        assert result.truth_followup.focus_pairs == pair_labels
        assert [candidate.macro_name for candidate in result.truth_followup.macro_candidates] == [
            "macro_align_part_with_contact",
            "macro_align_part_with_contact",
            "macro_align_part_with_contact",
            "macro_attach_part_to_surface",
            "macro_attach_part_to_surface",
        ]

        assert result.correction_candidates
        assert [candidate.focus_pairs[0] for candidate in result.correction_candidates] == pair_labels
        assert any(pair.endswith(f"-> {body_name}") for pair in result.truth_followup.focus_pairs)
        assert any(pair.endswith(f"-> {head_name}") for pair in result.truth_followup.focus_pairs)
        assert any(pair.startswith(f"{forelimb_name} -> ") for pair in result.truth_followup.focus_pairs)
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)
