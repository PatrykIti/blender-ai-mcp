"""Blender-backed E2E checks for creature gate-state completion blocking."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest
from fastmcp import Context
from PIL import Image, ImageDraw
from server.adapters.mcp.areas import scene as scene_area
from server.adapters.mcp.areas.reference import reference_images, reference_iterate_stage_checkpoint
from server.adapters.mcp.areas.scene import scene_relation_graph
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantRunResult,
    VisionAssistContract,
)
from server.adapters.mcp.session_capabilities import (
    get_session_capability_state,
    update_session_from_router_goal,
)
from server.application.tool_handlers.macro_handler import MacroToolHandler
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

    async def reset_visibility(self) -> None:
        return None

    async def enable_components(self, **kwargs) -> None:
        return None

    async def disable_components(self, **kwargs) -> None:
        return None


def _skip_if_blender_unavailable(error: RuntimeError) -> None:
    error_msg = str(error).lower()
    if "could not connect" in error_msg or "is blender running" in error_msg:
        pytest.skip(f"Blender not available: {error}")
    raise error


def _skip_if_blender_error_payload(error: str | None) -> None:
    error_msg = str(error or "").lower()
    if "could not connect" in error_msg or "is blender running" in error_msg or "rpc client timeout" in error_msg:
        pytest.skip(f"Blender not available: {error}")


def _write_creature_reference(path: Path) -> None:
    image = Image.new("RGBA", (220, 220), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((72, 84, 148, 180), fill=(0, 0, 0, 255))
    draw.polygon([(82, 84), (96, 36), (110, 84)], fill=(0, 0, 0, 255))
    draw.polygon([(110, 84), (124, 36), (138, 84)], fill=(0, 0, 0, 255))
    draw.rectangle((140, 108, 194, 132), fill=(0, 0, 0, 255))
    image.save(path)


@pytest.fixture(scope="session")
def scene_handler(rpc_client):
    return SceneToolHandler(rpc_client)


@pytest.fixture(scope="session")
def modeling_handler(rpc_client):
    return ModelingToolHandler(rpc_client)


@pytest.fixture(scope="session")
def macro_handler(scene_handler, modeling_handler):
    return MacroToolHandler(scene_handler, modeling_handler)


@pytest.fixture
def clean_scene(scene_handler):
    try:
        scene_handler.clean_scene(keep_lights_and_cameras=False)
    except RuntimeError as error:
        _skip_if_blender_unavailable(error)
    yield
    try:
        scene_handler.clean_scene(keep_lights_and_cameras=False)
    except RuntimeError:
        pass


def _seed_guided_goal(ctx: FakeContext, *, goal: str, gate_proposal: dict[str, object]) -> None:
    update_session_from_router_goal(
        cast(Context, ctx),
        goal,
        {
            "status": "no_match",
            "continuation_mode": "guided_manual_build",
            "workflow": None,
            "resolved": {},
            "unresolved": [],
            "resolution_sources": {},
            "phase_hint": "build",
            "message": "Continue on the guided build surface.",
        },
        gate_proposal=gate_proposal,
        surface_profile="llm-guided",
    )


def _capture_contract(path: Path, *, label: str) -> VisionCaptureImageContract:
    return VisionCaptureImageContract(
        label=label,
        image_path=str(path),
        host_visible_path=str(path),
        preset_name="target_front",
        media_type="image/png",
        view_kind="focus",
    )


def _gate_by_id(result, gate_id: str):
    return next(gate for gate in result.gate_statuses if gate.gate_id == gate_id)


def test_reference_iterate_stage_checkpoint_blocks_primitive_only_creature_gate_completion(
    clean_scene,
    scene_handler,
    modeling_handler,
    tmp_path,
    monkeypatch,
):
    body_name = "CreatureBody"
    head_name = "CreatureHead"
    tail_name = "CreatureTail"
    reference_path = tmp_path / "creature_reference.png"
    capture_path = tmp_path / "creature_capture_front.png"
    _write_creature_reference(reference_path)
    _write_creature_reference(capture_path)
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.0, location=[0.0, 0.0, 0.0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=head_name, size=1.2, location=[-3.6, 0.0, 0.0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=tail_name, size=1.0, location=[4.2, 0.0, 0.0])
        modeling_handler.transform_object(name=tail_name, scale=[0.8, 0.25, 0.25])

        ctx = FakeContext()
        _seed_guided_goal(
            ctx,
            goal="create a low-poly squirrel matching front and side reference images",
            gate_proposal={
                "source": "llm_goal",
                "gates": [
                    {
                        "gate_id": "eye_pair_required",
                        "gate_type": "required_part",
                        "label": "visible eye pair",
                        "target_kind": "reference_part",
                        "target_label": "eye_pair",
                    },
                    {
                        "gate_id": "eye_pair_symmetry",
                        "gate_type": "symmetry_pair",
                        "label": "eye pair stays symmetric",
                        "target_kind": "reference_part",
                        "target_label": "eye_pair",
                    },
                    {
                        "gate_id": "tail_body_seam",
                        "gate_type": "attachment_seam",
                        "label": "tail seated on body",
                        "target_kind": "object_pair",
                        "target_objects": [tail_name, body_name],
                    },
                ],
            },
        )
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
                    goal_summary="The creature is still primitive-only and structurally incomplete.",
                    visible_changes=["Body, head, and tail are visible in the staged capture."],
                    correction_focus=[],
                    next_corrections=[],
                    shape_mismatches=[],
                    proportion_mismatches=[],
                    likely_issues=[],
                    recommended_checks=[],
                ),
            )

        monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: scene_handler)
        monkeypatch.setattr(scene_area, "get_scene_handler", lambda: scene_handler)
        monkeypatch.setattr("server.infrastructure.di.get_scene_handler", lambda: scene_handler)
        monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
        monkeypatch.setattr(
            "server.adapters.mcp.areas.reference.get_vision_backend_resolver",
            lambda: SimpleNamespace(
                runtime_config=SimpleNamespace(max_tokens=400, max_images=8, active_model_name="gate-test-model")
            ),
        )
        monkeypatch.setattr(
            "server.adapters.mcp.areas.reference.capture_stage_images",
            lambda *args, **kwargs: [_capture_contract(capture_path, label="target_front_after")],
        )

        relation = scene_relation_graph(
            ctx,
            target_object=body_name,
            target_objects=[head_name, tail_name],
            goal_hint="assembled creature",
        )
        _skip_if_blender_error_payload(relation.error)
        assert relation.error is None

        session = get_session_capability_state(ctx)
        assert session.gate_plan is not None
        assert any(
            gate["gate_id"] == "tail_body_seam" and gate["status"] == "failed" for gate in session.gate_plan["gates"]
        )

        result = asyncio.run(
            reference_iterate_stage_checkpoint(
                ctx,
                target_object=body_name,
                target_objects=[head_name, tail_name],
                checkpoint_label="creature_gate_blockers",
                target_view="front",
                preset_profile="compact",
            )
        )

        assert result.error is None
        assert result.active_gate_plan is not None
        assert result.loop_disposition == "inspect_validate"
        assert result.completion_blockers

        eye_required = _gate_by_id(result, "eye_pair_required")
        eye_symmetry = _gate_by_id(result, "eye_pair_symmetry")
        tail_seam = _gate_by_id(result, "tail_body_seam")
        final_completion = _gate_by_id(result, "final_completion")

        assert eye_required.status == "failed"
        assert eye_required.status_reason == "missing_required_part"
        assert eye_symmetry.status == "failed"
        assert eye_symmetry.status_reason == "missing_required_part"
        assert tail_seam.status == "failed"
        assert tail_seam.status_reason == "relation_floating_gap"
        assert final_completion.status == "blocked"
        assert any(blocker.gate_id == "tail_body_seam" for blocker in result.completion_blockers)
        assert "resolve_quality_gate_blockers" in result.next_gate_actions
        assert "verify_or_repair_spatial_gate" in result.next_gate_actions
        assert "macro_attach_part_to_surface" in result.recommended_bounded_tools
        assert "Quality gate blockers remain unresolved" in (
            result.message or ""
        ) or "Deterministic truth findings remain high-priority" in (result.message or "")
    except RuntimeError as error:
        _skip_if_blender_unavailable(error)


def test_creature_gate_repair_macro_clears_tail_seam_blocker(
    clean_scene,
    scene_handler,
    modeling_handler,
    macro_handler,
    tmp_path,
    monkeypatch,
):
    body_name = "RepairCreatureBody"
    tail_name = "RepairCreatureTail"
    reference_path = tmp_path / "creature_reference_repair.png"
    capture_path = tmp_path / "creature_capture_repair.png"
    _write_creature_reference(reference_path)
    _write_creature_reference(capture_path)
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.0, location=[0.0, 0.0, 0.0])
        modeling_handler.create_primitive(primitive_type="CUBE", name=tail_name, size=1.0, location=[4.2, 0.0, 0.0])
        modeling_handler.transform_object(name=tail_name, scale=[0.8, 0.25, 0.25])

        ctx = FakeContext()
        _seed_guided_goal(
            ctx,
            goal="create a low-poly squirrel matching front and side reference images",
            gate_proposal={
                "source": "llm_goal",
                "gates": [
                    {
                        "gate_id": "tail_body_seam",
                        "gate_type": "attachment_seam",
                        "label": "tail seated on body",
                        "target_kind": "object_pair",
                        "target_objects": [tail_name, body_name],
                    }
                ],
            },
        )
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
                    goal_summary="The creature tail still needs attachment repair.",
                    visible_changes=["Body and tail are visible in the staged capture."],
                    correction_focus=[],
                    next_corrections=[],
                    shape_mismatches=[],
                    proportion_mismatches=[],
                    likely_issues=[],
                    recommended_checks=[],
                ),
            )

        monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: scene_handler)
        monkeypatch.setattr(scene_area, "get_scene_handler", lambda: scene_handler)
        monkeypatch.setattr("server.infrastructure.di.get_scene_handler", lambda: scene_handler)
        monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
        monkeypatch.setattr(
            "server.adapters.mcp.areas.reference.get_vision_backend_resolver",
            lambda: SimpleNamespace(
                runtime_config=SimpleNamespace(max_tokens=400, max_images=8, active_model_name="gate-test-model")
            ),
        )
        monkeypatch.setattr(
            "server.adapters.mcp.areas.reference.capture_stage_images",
            lambda *args, **kwargs: [_capture_contract(capture_path, label="target_front_after")],
        )

        first_relation = scene_relation_graph(
            ctx,
            target_object=body_name,
            target_objects=[tail_name],
            goal_hint="assembled creature",
        )
        _skip_if_blender_error_payload(first_relation.error)
        assert first_relation.error is None

        first = asyncio.run(
            reference_iterate_stage_checkpoint(
                ctx,
                target_object=body_name,
                target_objects=[tail_name],
                checkpoint_label="creature_repair_before",
                target_view="front",
                preset_profile="compact",
            )
        )
        assert _gate_by_id(first, "tail_body_seam").status == "failed"
        assert any(blocker.gate_id == "tail_body_seam" for blocker in first.completion_blockers)

        macro_result = macro_handler.attach_part_to_surface(
            part_object=tail_name,
            surface_object=body_name,
            surface_axis="X",
            surface_side="positive",
            align_mode="center",
            gap=0.0,
        )
        assert macro_result["status"] == "success"

        second_relation = scene_relation_graph(
            ctx,
            target_object=body_name,
            target_objects=[tail_name],
            goal_hint="assembled creature",
        )
        _skip_if_blender_error_payload(second_relation.error)
        assert second_relation.error is None

        second = asyncio.run(
            reference_iterate_stage_checkpoint(
                ctx,
                target_object=body_name,
                target_objects=[tail_name],
                checkpoint_label="creature_repair_after",
                target_view="front",
                preset_profile="compact",
            )
        )

        tail_seam = _gate_by_id(second, "tail_body_seam")
        final_completion = _gate_by_id(second, "final_completion")
        assert tail_seam.status == "passed"
        assert all(blocker.gate_id != "tail_body_seam" for blocker in second.completion_blockers)
        assert final_completion.status == "passed"
    except RuntimeError as error:
        _skip_if_blender_unavailable(error)
