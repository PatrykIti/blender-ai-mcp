"""Blender-backed E2E checks for building/facade gate-state completion blocking."""

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


def _write_building_reference(path: Path) -> None:
    image = Image.new("RGBA", (240, 220), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((56, 78, 184, 188), fill=(0, 0, 0, 255))
    draw.polygon([(48, 78), (120, 28), (192, 78)], fill=(0, 0, 0, 255))
    draw.rectangle((88, 122, 112, 168), fill=(255, 255, 255, 255))
    draw.rectangle((136, 122, 160, 168), fill=(255, 255, 255, 255))
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


def test_reference_iterate_stage_checkpoint_blocks_building_gate_completion(
    clean_scene,
    scene_handler,
    modeling_handler,
    tmp_path,
    monkeypatch,
):
    wall_name = "FacadeMainVolume"
    roof_name = "FacadeRoofMass"
    reference_path = tmp_path / "building_reference.png"
    capture_path = tmp_path / "building_capture_front.png"
    _write_building_reference(reference_path)
    _write_building_reference(capture_path)
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=wall_name, size=2.0, location=[0.0, 0.0, 0.0])
        modeling_handler.transform_object(name=wall_name, scale=[1.8, 1.0, 1.4])
        modeling_handler.create_primitive(primitive_type="CUBE", name=roof_name, size=1.0, location=[0.0, 0.0, 3.0])
        modeling_handler.transform_object(name=roof_name, scale=[2.0, 1.2, 0.25])

        ctx = FakeContext()
        _seed_guided_goal(
            ctx,
            goal="create a small building facade matching the front reference",
            gate_proposal={
                "source": "llm_goal",
                "gates": [
                    {
                        "gate_id": "roof_wall_seam",
                        "gate_type": "attachment_seam",
                        "label": "roof seated on wall volume",
                        "target_kind": "object_pair",
                        "target_objects": [roof_name, wall_name],
                    },
                    {
                        "gate_id": "front_window_opening",
                        "gate_type": "opening_or_cut",
                        "label": "front window opening is cut into the facade",
                        "target_kind": "object",
                        "target_label": wall_name,
                        "target_objects": [wall_name],
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
                target_object=wall_name,
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
                    goal_summary="The facade shell is still structurally incomplete.",
                    visible_changes=["Main volume and roof are visible in the staged capture."],
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
            target_object=wall_name,
            target_objects=[roof_name],
            goal_hint="building facade roof wall",
        )
        _skip_if_blender_error_payload(relation.error)
        assert relation.error is None

        session = get_session_capability_state(ctx)
        assert session.gate_plan is not None

        result = asyncio.run(
            reference_iterate_stage_checkpoint(
                ctx,
                target_object=wall_name,
                target_objects=[roof_name],
                checkpoint_label="building_gate_blockers",
                target_view="front",
                preset_profile="compact",
            )
        )

        assert result.error is None
        assert result.active_gate_plan is not None
        assert result.loop_disposition == "inspect_validate"
        assert result.completion_blockers

        roof_seam = _gate_by_id(result, "roof_wall_seam")
        opening = _gate_by_id(result, "front_window_opening")
        final_completion = _gate_by_id(result, "final_completion")

        assert roof_seam.status == "failed"
        assert roof_seam.status_reason == "relation_floating_gap"
        assert opening.status == "pending"
        assert final_completion.status == "blocked"
        assert any(blocker.gate_id == "roof_wall_seam" for blocker in result.completion_blockers)
        assert any(blocker.gate_id == "front_window_opening" for blocker in result.completion_blockers)
        assert "resolve_quality_gate_blockers" in result.next_gate_actions
        assert "macro_attach_part_to_surface" in result.recommended_bounded_tools
        assert "macro_cutout_recess" in result.recommended_bounded_tools
    except RuntimeError as error:
        _skip_if_blender_unavailable(error)
