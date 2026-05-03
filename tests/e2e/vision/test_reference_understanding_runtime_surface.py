"""Blender-backed E2E checks for the TASK-158 reference-understanding surface."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

import pytest
from fastmcp import Context
from PIL import Image, ImageDraw
from server.adapters.mcp.areas import scene as scene_area
from server.adapters.mcp.areas.reference import (
    reference_compare_stage_checkpoint,
    reference_images,
    reference_iterate_stage_checkpoint,
)
from server.adapters.mcp.areas.router import router_get_status, router_set_goal
from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantRunResult,
    VisionAssistContract,
)
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler

pytestmark = pytest.mark.e2e


@dataclass
class FakeContext:
    state: dict[str, object] = field(default_factory=dict)
    session_id: str = "sess_task_158"
    transport: str = "stdio"

    def get_state(self, key: str):
        return self.state.get(key)

    def set_state(self, key: str, value, *, serializable: bool = True) -> None:
        self.state[key] = value

    def info(self, message, logger_name=None, extra=None):
        return None

    def warning(self, message, logger_name=None, extra=None):
        return None

    async def reset_visibility(self) -> None:
        self.state["_visibility_calls"] = [("reset_visibility", {})]

    async def enable_components(self, **kwargs) -> None:
        calls = self.state.setdefault("_visibility_calls", [])
        assert isinstance(calls, list)
        calls.append(("enable_components", kwargs))

    async def disable_components(self, **kwargs) -> None:
        calls = self.state.setdefault("_visibility_calls", [])
        assert isinstance(calls, list)
        calls.append(("disable_components", kwargs))


def _skip_if_blender_unavailable(error: RuntimeError) -> None:
    error_msg = str(error).lower()
    if "could not connect" in error_msg or "is blender running" in error_msg or "rpc client timeout" in error_msg:
        pytest.skip(f"Blender not available: {error}")
    raise error


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


class _ReferenceUnderstandingBackend:
    async def analyze(self, request):
        assert request.metadata["mode"] == "reference_understanding"
        return {
            "status": "available",
            "understanding_id": "understanding_blender_surface",
            "goal": request.goal,
            "reference_ids": list(request.metadata.get("reference_ids") or []),
            "subject": {
                "label": "low poly squirrel",
                "category": "creature",
                "confidence": 0.9,
                "uncertainty_notes": [],
            },
            "style": {
                "style_label": "low_poly_faceted",
                "confidence": 0.9,
                "notes": ["faceted silhouette"],
            },
            "required_parts": [
                {
                    "part_label": "visible eye pair",
                    "target_label": "eye_pair",
                    "construction_hint": "Keep both eyes readable in the blockout.",
                    "priority": "high",
                    "source_reference_ids": list(request.metadata.get("reference_ids") or []),
                }
            ],
            "non_goals": ["Do not smooth the build into an organic sculpt pass."],
            "construction_strategy": {
                "construction_path": "low_poly_facet",
                "primary_family": "modeling_mesh",
                "allowed_families": ["macro", "modeling_mesh", "inspect_only"],
                "stage_sequence": ["primary_masses", "secondary_parts", "inspect_validate"],
                "finish_policy": "preserve_facets",
            },
            "router_handoff_hints": {
                "preferred_family": "modeling_mesh",
                "allowed_guided_families": [
                    "reference_context",
                    "primary_masses",
                    "secondary_parts",
                    "inspect_validate",
                ],
                "sculpt_policy": "hidden",
            },
            "gate_proposals": [
                {
                    "gate_type": "required_part",
                    "label": "visible eye pair",
                    "target_kind": "reference_part",
                    "target_label": "eye_pair",
                }
            ],
            "visual_evidence_refs": [
                {
                    "evidence_id": "ref_front_subject",
                    "source_class": "reference_image",
                    "summary": "The reference depicts a faceted squirrel blockout.",
                    "reference_id": (request.metadata.get("reference_ids") or ["ref_front"])[0],
                }
            ],
            "verification_requirements": [
                {
                    "tool_name": "scene_view_diagnostics",
                    "reason": "Confirm the front silhouette framing before detail edits.",
                    "priority": "high",
                }
            ],
            "classification_scores": [],
            "segmentation_artifacts": [],
            "source_provenance": [{"source": "reference_understanding"}],
            "boundary_policy": {
                "advisory_only": True,
                "not_truth_source": True,
                "may_unlock_tools": False,
                "may_pass_gates": False,
                "may_propose_gates": True,
            },
        }


class _Resolver:
    def __init__(self):
        self.runtime_config = type(
            "RuntimeCfg",
            (),
            {
                "max_tokens": 400,
                "max_images": 8,
                "active_model_name": "blender-reference-understanding-model",
                "active_segmentation_sidecar": None,
            },
        )()

    def resolve_default(self):
        return _ReferenceUnderstandingBackend()


async def _fake_run_vision_assist(ctx, *, request, resolver):
    return AssistantRunResult(
        status="success",
        assistant_name="vision_assist",
        message="ok",
        budget=AssistantBudgetContract(max_input_chars=1000, max_messages=1, max_tokens=100, tool_budget=0),
        capability_source="local_runtime",
        result=VisionAssistContract(
            backend_kind="mlx_local",
            model_name="blender-reference-understanding-model",
            goal_summary="The blockout still needs visible eye detail and seam refinement.",
            visible_changes=["The body blockout is visible in the staged capture."],
            correction_focus=["Eye pair readability", "Tail/body seam"],
        ),
    )


def test_router_status_and_stage_checkpoint_surface_reference_understanding_with_real_blender_capture(
    clean_scene,
    scene_handler,
    modeling_handler,
    tmp_path,
    monkeypatch,
):
    body_name = "Squirrel_Body"
    reference_path = tmp_path / "creature_reference_front.png"
    _write_creature_reference(reference_path)
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.0, location=[0.0, 0.0, 0.0])
    except RuntimeError as error:
        _skip_if_blender_unavailable(error)

    class Handler:
        def set_goal(self, goal, resolved_params=None):
            return {
                "status": "no_match",
                "continuation_mode": "guided_manual_build",
                "workflow": None,
                "resolved": {},
                "unresolved": [],
                "resolution_sources": {},
                "phase_hint": "build",
                "message": "Continue on the guided build surface.",
            }

        def clear_goal(self):
            return "cleared"

    monkeypatch.setattr("server.adapters.mcp.areas.router.get_router_handler", lambda: Handler())
    monkeypatch.setattr(
        "server.adapters.mcp.areas.router.get_config",
        lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})(),
    )
    monkeypatch.setattr("server.adapters.mcp.areas.router._should_attach_repair_suggestion", lambda payload: False)
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: scene_handler)
    monkeypatch.setattr(scene_area, "get_scene_handler", lambda: scene_handler)
    monkeypatch.setattr("server.infrastructure.di.get_scene_handler", lambda: scene_handler)
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: _Resolver())
    monkeypatch.setattr("server.infrastructure.di.get_vision_backend_resolver", lambda: _Resolver())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)

    ctx = FakeContext()

    attach_result = asyncio.run(
        reference_images(
            cast(Context, ctx),
            action="attach",
            source_path=str(reference_path),
            label="front_ref",
            target_object=body_name,
            target_view="front",
        )
    )
    assert attach_result.reference_count == 1
    assert "pending" in str(attach_result.message).lower()

    goal_result = asyncio.run(
        router_set_goal(
            cast(Context, ctx),
            goal="create a low-poly squirrel matching front and side reference images",
        )
    )
    assert goal_result.reference_understanding_summary is not None
    assert goal_result.reference_understanding_summary.understanding_id == "understanding_blender_surface"
    assert goal_result.reference_understanding_summary.construction_strategy is not None
    assert goal_result.reference_understanding_summary.construction_strategy.primary_family == "modeling_mesh"
    assert goal_result.reference_understanding_gate_ids

    status_result = asyncio.run(router_get_status(cast(Context, ctx)))
    assert status_result.reference_understanding_summary is not None
    assert status_result.reference_understanding_summary.understanding_id == "understanding_blender_surface"
    assert status_result.reference_understanding_gate_ids == goal_result.reference_understanding_gate_ids

    compare_result = asyncio.run(
        reference_compare_stage_checkpoint(
            cast(Context, ctx),
            target_object=body_name,
            checkpoint_label="task_158_reference_understanding_compare",
            target_view="front",
            preset_profile="compact",
        )
    )
    assert compare_result.error is None
    assert compare_result.reference_understanding_summary is not None
    assert compare_result.reference_understanding_summary.understanding_id == "understanding_blender_surface"
    assert compare_result.reference_understanding_gate_ids == goal_result.reference_understanding_gate_ids
    assert compare_result.part_segmentation is not None
    assert compare_result.part_segmentation.status == "disabled"

    iterate_result = asyncio.run(
        reference_iterate_stage_checkpoint(
            cast(Context, ctx),
            target_object=body_name,
            checkpoint_label="task_158_reference_understanding_iterate",
            target_view="front",
            preset_profile="compact",
        )
    )
    assert iterate_result.error is None
    assert iterate_result.reference_understanding_summary is not None
    assert iterate_result.reference_understanding_summary.understanding_id == "understanding_blender_surface"
    assert iterate_result.reference_understanding_gate_ids == goal_result.reference_understanding_gate_ids
    assert iterate_result.part_segmentation is not None
    assert iterate_result.part_segmentation.status == "disabled"


def test_reference_understanding_refresh_clear_reapplies_visibility_immediately(tmp_path, monkeypatch):
    reference_path = tmp_path / "creature_reference_front.png"
    _write_creature_reference(reference_path)
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    class Handler:
        def set_goal(self, goal, resolved_params=None):
            return {
                "status": "no_match",
                "continuation_mode": "guided_manual_build",
                "workflow": None,
                "resolved": {},
                "unresolved": [],
                "resolution_sources": {},
                "phase_hint": "build",
                "message": "Continue on the guided build surface.",
            }

        def clear_goal(self):
            return "cleared"

    class VisibilityBackend:
        async def analyze(self, request):
            return {
                "status": "available",
                "understanding_id": "understanding_visibility_refresh",
                "goal": request.goal,
                "reference_ids": list(request.metadata.get("reference_ids") or []),
                "subject": {
                    "label": "low poly squirrel",
                    "category": "creature",
                    "confidence": 0.9,
                    "uncertainty_notes": [],
                },
                "style": {
                    "style_label": "low_poly_faceted",
                    "confidence": 0.9,
                    "notes": [],
                },
                "required_parts": [],
                "non_goals": [],
                "construction_strategy": {
                    "construction_path": "low_poly_facet",
                    "primary_family": "modeling_mesh",
                    "allowed_families": ["macro", "modeling_mesh", "inspect_only"],
                    "stage_sequence": ["primary_masses"],
                    "finish_policy": "preserve_facets",
                },
                "router_handoff_hints": {
                    "preferred_family": "modeling_mesh",
                    "allowed_guided_families": [
                        "reference_context",
                        "primary_masses",
                        "secondary_parts",
                        "inspect_validate",
                    ],
                    "sculpt_policy": "hidden",
                },
                "gate_proposals": [
                    {
                        "gate_type": "support_contact",
                        "label": "body supported by base",
                        "target_kind": "object_pair",
                        "target_objects": ["Body", "Base"],
                    }
                ],
                "visual_evidence_refs": [],
                "verification_requirements": [],
                "classification_scores": [],
                "segmentation_artifacts": [],
                "source_provenance": [{"source": "reference_understanding"}],
                "boundary_policy": {
                    "advisory_only": True,
                    "not_truth_source": True,
                    "may_unlock_tools": False,
                    "may_pass_gates": False,
                    "may_propose_gates": True,
                },
            }

    class VisibilityResolver:
        def __init__(self):
            self.runtime_config = type(
                "RuntimeCfg",
                (),
                {
                    "max_tokens": 400,
                    "max_images": 8,
                    "active_model_name": "blender-reference-understanding-model",
                    "active_segmentation_sidecar": None,
                },
            )()

        def resolve_default(self):
            return VisibilityBackend()

    monkeypatch.setattr("server.adapters.mcp.areas.router.get_router_handler", lambda: Handler())
    monkeypatch.setattr(
        "server.adapters.mcp.areas.router.get_config",
        lambda: type("Cfg", (), {"MCP_SURFACE_PROFILE": "llm-guided"})(),
    )
    monkeypatch.setattr("server.adapters.mcp.areas.router._should_attach_repair_suggestion", lambda payload: False)
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: VisibilityResolver())
    monkeypatch.setattr("server.infrastructure.di.get_vision_backend_resolver", lambda: VisibilityResolver())

    ctx = FakeContext()

    attach_result = asyncio.run(
        reference_images(
            cast(Context, ctx),
            action="attach",
            source_path=str(reference_path),
            label="front_ref",
            target_object="Squirrel_Body",
            target_view="front",
        )
    )
    assert attach_result.reference_count == 1

    goal_result = asyncio.run(
        router_set_goal(
            cast(Context, ctx),
            goal="create a low-poly squirrel matching front and side reference images",
        )
    )
    assert goal_result.reference_understanding_gate_ids
    visibility_after_goal = list(cast(list[tuple[str, dict[str, object]]], ctx.state.get("_visibility_calls") or []))
    assert visibility_after_goal
    assert visibility_after_goal[0] == ("reset_visibility", {})
    assert any(
        name == "enable_components" and "macro_place_supported_pair" in set(call.get("names") or ())
        for name, call in visibility_after_goal[1:]
    )

    clear_result = asyncio.run(reference_images(cast(Context, ctx), action="clear"))
    assert clear_result.reference_count == 0

    visibility_after_clear = list(cast(list[tuple[str, dict[str, object]]], ctx.state.get("_visibility_calls") or []))
    assert visibility_after_clear
    assert visibility_after_clear[0] == ("reset_visibility", {})
    assert all(
        not (name == "enable_components" and "macro_place_supported_pair" in set(call.get("names") or ()))
        for name, call in visibility_after_clear[1:]
    )

    status_after_clear = asyncio.run(router_get_status(cast(Context, ctx)))
    assert status_after_clear.reference_understanding_gate_ids is None
