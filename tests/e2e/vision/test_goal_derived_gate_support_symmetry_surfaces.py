"""Blender-backed E2E checks for support and symmetry gate correction surfaces."""

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
from server.adapters.mcp.areas.reference import reference_compare_stage_checkpoint, reference_images
from server.adapters.mcp.areas.scene import scene_relation_graph
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
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


def _write_support_reference(path: Path) -> None:
    image = Image.new("RGBA", (240, 220), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((44, 174, 196, 196), fill=(0, 0, 0, 255))
    draw.rectangle((88, 72, 152, 174), fill=(0, 0, 0, 255))
    image.save(path)


def _write_symmetry_reference(path: Path) -> None:
    image = Image.new("RGBA", (220, 220), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((48, 84, 92, 136), fill=(0, 0, 0, 255))
    draw.rectangle((128, 84, 172, 136), fill=(0, 0, 0, 255))
    image.save(path)


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


def test_reference_compare_stage_checkpoint_surfaces_support_gate_followup(
    clean_scene,
    scene_handler,
    modeling_handler,
    tmp_path,
    monkeypatch,
):
    body_name = "SupportGateBody"
    base_name = "SupportGateBase"
    reference_path = tmp_path / "support_reference.png"
    capture_path = tmp_path / "support_capture_front.png"
    _write_support_reference(reference_path)
    _write_support_reference(capture_path)
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=base_name, size=1.0, location=[0.0, 0.0, 0.0])
        modeling_handler.transform_object(name=base_name, scale=[3.0, 2.0, 0.1])
        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=1.0, location=[0.0, 0.0, 1.3])
        modeling_handler.transform_object(name=body_name, scale=[0.6, 0.5, 0.6])

        ctx = FakeContext()
        _seed_guided_goal(
            ctx,
            goal="support the body on the base",
            gate_proposal={
                "source": "llm_goal",
                "gates": [
                    {
                        "gate_id": "body_base_support",
                        "gate_type": "support_contact",
                        "label": "body supported by base",
                        "target_kind": "object_pair",
                        "target_objects": [body_name, base_name],
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
                    goal_summary="The body is still floating above the base.",
                    visible_changes=["Body and base are visible in the staged capture."],
                    correction_focus=["Seat the body onto the base"],
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
            target_objects=[base_name],
            goal_hint="support the body on the base",
        )
        _skip_if_blender_error_payload(relation.error)
        assert relation.error is None
        assert relation.payload is not None
        assert relation.payload.pairs[0].support_semantics is not None
        assert relation.payload.pairs[0].support_semantics.verdict == "unsupported"

        result = asyncio.run(
            reference_compare_stage_checkpoint(
                ctx,
                target_object=body_name,
                target_objects=[base_name],
                checkpoint_label="support_gate_surfaces",
                target_view="front",
                preset_profile="compact",
            )
        )

        assert result.error is None
        assert result.active_gate_plan is not None
        support_gate = _gate_by_id(result, "body_base_support")
        final_completion = _gate_by_id(result, "final_completion")
        assert support_gate.status == "failed"
        assert final_completion.status == "blocked"
        assert result.truth_bundle is not None
        assert result.truth_bundle.checks[0].support_semantics is not None
        assert result.truth_bundle.checks[0].support_semantics.verdict == "unsupported"
        assert result.truth_followup is not None
        assert any(item.kind == "support" for item in result.truth_followup.items)
        assert any(
            candidate.macro_name == "macro_place_supported_pair" for candidate in result.truth_followup.macro_candidates
        )
        assert result.correction_candidates
        assert any(
            macro.macro_name == "macro_place_supported_pair"
            for candidate in result.correction_candidates
            for macro in (candidate.truth_evidence.macro_candidates if candidate.truth_evidence is not None else [])
        )
    except RuntimeError as error:
        _skip_if_blender_unavailable(error)


def test_reference_compare_stage_checkpoint_surfaces_symmetry_gate_followup(
    clean_scene,
    scene_handler,
    modeling_handler,
    tmp_path,
    monkeypatch,
):
    left_name = "SymmetryGateLeft"
    right_name = "SymmetryGateRight"
    reference_path = tmp_path / "symmetry_reference.png"
    capture_path = tmp_path / "symmetry_capture_front.png"
    _write_symmetry_reference(reference_path)
    _write_symmetry_reference(capture_path)
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=left_name, size=1.0, location=[-1.2, 0.0, 0.8])
        modeling_handler.create_primitive(primitive_type="CUBE", name=right_name, size=1.0, location=[1.2, 0.25, 0.8])
        modeling_handler.transform_object(name=left_name, scale=[0.2, 0.35, 0.4])
        modeling_handler.transform_object(name=right_name, scale=[0.2, 0.35, 0.4])

        ctx = FakeContext()
        _seed_guided_goal(
            ctx,
            goal="keep the wheel pair symmetric",
            gate_proposal={
                "source": "llm_goal",
                "gates": [
                    {
                        "gate_id": "wheel_pair_symmetry",
                        "gate_type": "symmetry_pair",
                        "label": "wheel pair remains symmetric",
                        "target_kind": "object_pair",
                        "target_objects": [left_name, right_name],
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
                target_object=left_name,
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
                    goal_summary="The mirrored pair is still asymmetric.",
                    visible_changes=["Both pair members are visible in the staged capture."],
                    correction_focus=["Re-mirror the pair"],
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
            target_object=left_name,
            target_objects=[right_name],
            goal_hint="keep the wheel pair symmetric",
        )
        _skip_if_blender_error_payload(relation.error)
        assert relation.error is None
        assert relation.payload is not None
        assert relation.payload.pairs[0].symmetry_semantics is not None
        assert relation.payload.pairs[0].symmetry_semantics.verdict == "asymmetric"

        result = asyncio.run(
            reference_compare_stage_checkpoint(
                ctx,
                target_object=left_name,
                target_objects=[right_name],
                checkpoint_label="symmetry_gate_surfaces",
                target_view="front",
                preset_profile="compact",
            )
        )

        assert result.error is None
        assert result.active_gate_plan is not None
        symmetry_gate = _gate_by_id(result, "wheel_pair_symmetry")
        final_completion = _gate_by_id(result, "final_completion")
        assert symmetry_gate.status == "failed"
        assert symmetry_gate.status_reason == "relation_asymmetric"
        assert final_completion.status == "blocked"
        assert result.truth_bundle is not None
        assert result.truth_bundle.checks[0].symmetry_semantics is not None
        assert result.truth_bundle.checks[0].symmetry_semantics.verdict == "asymmetric"
        assert result.truth_followup is not None
        assert any(item.kind == "symmetry" for item in result.truth_followup.items)
        assert any(
            candidate.macro_name == "macro_place_symmetry_pair" for candidate in result.truth_followup.macro_candidates
        )
        assert result.correction_candidates
        assert any(
            macro.macro_name == "macro_place_symmetry_pair"
            for candidate in result.correction_candidates
            for macro in (candidate.truth_evidence.macro_candidates if candidate.truth_evidence is not None else [])
        )
    except RuntimeError as error:
        _skip_if_blender_unavailable(error)
