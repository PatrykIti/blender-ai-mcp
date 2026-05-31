"""Blender-backed squirrel regression proof for TASK-169."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field, replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastmcp import Context
from server.adapters.mcp.areas.reference import reference_compare_stage_checkpoint, reference_images
from server.adapters.mcp.areas.scene import scene_relation_graph
from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantRunResult,
    VisionAssistContract,
    VisionPacketStatusContract,
)
from server.adapters.mcp.session_capabilities import (
    get_session_capability_state,
    register_guided_part_role,
    set_session_capability_state,
    update_session_from_router_goal,
)
from server.adapters.mcp.session_state import set_session_value_async
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler

pytestmark = pytest.mark.e2e

REPO_ROOT = Path(__file__).resolve().parents[3]
FRONT_REFERENCE_PATH = REPO_ROOT / "_docs/_TEST_IMAGES/squirrel-front.png"
SIDE_REFERENCE_PATH = REPO_ROOT / "_docs/_TEST_IMAGES/squirrel-side.png"
SQUIRREL_GOAL = "create a low-poly squirrel matching front and side reference images"
_SQUIRREL_LOOP_STATE_KEY = "reference_correction_loop"


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


def _relation_pair(relation, left: str, right: str):
    for pair in relation.pairs:
        if {pair.from_object, pair.to_object} == {left, right}:
            return pair
    raise AssertionError(f"Missing relation pair for {left} and {right}")


def _bbox(scene_handler: SceneToolHandler, object_name: str) -> dict[str, Any]:
    payload = scene_handler.get_bounding_box(object_name)
    assert "center" in payload
    assert "dimensions" in payload
    return payload


def _build_vertical_stack_bad_squirrel(modeling_handler: ModelingToolHandler) -> tuple[str, str, str]:
    body_name = "BadSquirrelBody"
    head_name = "BadSquirrelHead"
    tail_name = "BadSquirrelTail"

    modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.0, location=[0.0, 0.0, 1.6])
    modeling_handler.transform_object(name=body_name, scale=[0.55, 0.55, 2.4])

    modeling_handler.create_primitive(primitive_type="CUBE", name=head_name, size=1.2, location=[0.0, 0.0, 4.42])
    modeling_handler.transform_object(name=head_name, scale=[0.7, 0.7, 0.7])

    modeling_handler.create_primitive(primitive_type="CUBE", name=tail_name, size=1.0, location=[0.0, 0.0, 5.72])
    modeling_handler.transform_object(name=tail_name, scale=[0.32, 0.32, 1.8])

    return body_name, head_name, tail_name


def _build_good_squirrel_with_local_ear_focus(modeling_handler: ModelingToolHandler) -> tuple[str, str, str, str]:
    body_name = "SquirrelBody"
    head_name = "SquirrelHead"
    tail_name = "SquirrelTail"
    ear_name = "SquirrelEar_L"

    modeling_handler.create_primitive(primitive_type="CUBE", name=body_name, size=2.0, location=[0.0, 0.0, 0.8])
    modeling_handler.transform_object(name=body_name, scale=[1.45, 0.85, 0.75])

    modeling_handler.create_primitive(primitive_type="CUBE", name=head_name, size=1.2, location=[-1.96, 0.0, 1.35])
    modeling_handler.transform_object(name=head_name, scale=[0.85, 0.7, 0.75])

    modeling_handler.create_primitive(primitive_type="CUBE", name=tail_name, size=1.0, location=[2.14, 0.0, 1.05])
    modeling_handler.transform_object(name=tail_name, scale=[1.35, 0.32, 0.32])

    modeling_handler.create_primitive(primitive_type="CUBE", name=ear_name, size=0.45, location=[-2.35, 0.0, 2.05])
    modeling_handler.transform_object(name=ear_name, scale=[0.32, 0.18, 0.58])

    return body_name, head_name, tail_name, ear_name


def _squirrel_quality_metrics(
    ctx: FakeContext,
    scene_handler: SceneToolHandler,
    *,
    body_name: str,
    head_name: str,
    tail_name: str,
) -> dict[str, Any]:
    body_ratio = scene_handler.assert_proportion(
        body_name,
        axis_a="Z",
        axis_b="Y",
        expected_ratio=0.9,
        tolerance=0.25,
        world_space=True,
    )

    body_bbox = _bbox(scene_handler, body_name)
    head_bbox = _bbox(scene_handler, head_name)
    tail_bbox = _bbox(scene_handler, tail_name)

    body_center = [float(value) for value in body_bbox["center"]]
    head_center = [float(value) for value in head_bbox["center"]]
    tail_center = [float(value) for value in tail_bbox["center"]]
    body_dimensions = [float(value) for value in body_bbox["dimensions"]]

    head_lateral_offset = abs(head_center[0] - body_center[0])
    head_vertical_delta = abs(head_center[2] - body_center[2])
    head_tower_ratio = head_vertical_delta / max(head_lateral_offset, 0.001)

    relation = scene_relation_graph(
        cast(Context, ctx),
        target_object=body_name,
        target_objects=[head_name, tail_name],
        goal_hint="assembled seated squirrel",
    )
    _skip_if_blender_error_payload(relation.error)
    assert relation.error is None

    head_pair = _relation_pair(relation, body_name, head_name)
    tail_pair = _relation_pair(relation, body_name, tail_name)

    return {
        "body_ratio_passed": bool(body_ratio["passed"]),
        "body_ratio": float(body_ratio["actual"]["ratio"]),
        "head_tower_ratio": head_tower_ratio,
        "tail_rear": tail_center[0] > body_center[0] + 0.3,
        "tail_upward": tail_center[2] >= body_center[2] - 0.1,
        "head_body_verdict": (
            head_pair.attachment_semantics.attachment_verdict if head_pair.attachment_semantics is not None else None
        ),
        "tail_body_verdict": (
            tail_pair.attachment_semantics.attachment_verdict if tail_pair.attachment_semantics is not None else None
        ),
        "body_depth": body_dimensions[1],
    }


def _seed_squirrel_secondary_state(
    ctx: FakeContext,
    *,
    body_name: str,
    head_name: str,
    tail_name: str,
    ear_name: str,
) -> None:
    state = get_session_capability_state(cast(Context, ctx))
    set_session_capability_state(
        cast(Context, ctx),
        replace(
            state,
            surface_profile="llm-guided",
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "create_primary_masses",
                "completed_steps": ["understand_goal", "establish_spatial_context"],
                "active_target_scope": {
                    "scope_kind": "object_set",
                    "primary_target": body_name,
                    "object_names": [body_name, head_name, tail_name],
                    "object_count": 3,
                },
                "required_checks": [],
                "required_prompts": ["guided_session_start", "reference_guided_creature_build"],
                "preferred_prompts": ["workflow_router_first"],
                "next_actions": ["begin_primary_masses"],
                "blocked_families": [],
                "allowed_families": ["primary_masses", "reference_context"],
                "allowed_roles": ["body_core", "head_mass", "tail_mass"],
                "completed_roles": [],
                "missing_roles": ["body_core", "head_mass", "tail_mass"],
                "required_role_groups": ["primary_masses"],
                "step_status": "ready",
            },
        ),
    )
    register_guided_part_role(cast(Context, ctx), object_name=body_name, role="body_core")
    register_guided_part_role(cast(Context, ctx), object_name=head_name, role="head_mass")
    register_guided_part_role(cast(Context, ctx), object_name=tail_name, role="tail_mass")
    register_guided_part_role(cast(Context, ctx), object_name=ear_name, role="ear_pair")


def test_squirrel_quality_oracle_rejects_vertical_blockout_class(clean_scene, scene_handler, modeling_handler):
    try:
        body_name, head_name, tail_name = _build_vertical_stack_bad_squirrel(modeling_handler)
        metrics = _squirrel_quality_metrics(
            FakeContext(),
            scene_handler,
            body_name=body_name,
            head_name=head_name,
            tail_name=tail_name,
        )

        assert metrics["body_ratio_passed"] is False
        assert metrics["head_tower_ratio"] > 1.0
        assert metrics["tail_rear"] is False
    except RuntimeError as error:
        _skip_if_blender_unavailable(error)


def test_reference_compare_stage_checkpoint_keeps_broad_primary_mass_scope_for_squirrel_regression(
    clean_scene,
    scene_handler,
    modeling_handler,
    tmp_path,
    monkeypatch,
):
    assert FRONT_REFERENCE_PATH.exists()
    assert SIDE_REFERENCE_PATH.exists()

    try:
        monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
        monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

        body_name, head_name, tail_name, ear_name = _build_good_squirrel_with_local_ear_focus(modeling_handler)

        ctx = FakeContext()
        update_session_from_router_goal(cast(Context, ctx), SQUIRREL_GOAL, {"status": "no_match"})
        asyncio.run(
            reference_images(
                ctx,
                action="attach",
                source_path=str(FRONT_REFERENCE_PATH),
                label="front_ref",
                target_object=body_name,
                target_view="front",
            )
        )
        asyncio.run(
            reference_images(
                ctx,
                action="attach",
                source_path=str(SIDE_REFERENCE_PATH),
                label="side_ref",
                target_object=body_name,
                target_view="side",
            )
        )
        _seed_squirrel_secondary_state(
            ctx,
            body_name=body_name,
            head_name=head_name,
            tail_name=tail_name,
            ear_name=ear_name,
        )
        asyncio.run(
            set_session_value_async(
                cast(Context, ctx),
                _SQUIRREL_LOOP_STATE_KEY,
                {
                    "goal": SQUIRREL_GOAL,
                    "preset_profile": "compact",
                    "last_focus_pairs": [f"{ear_name} -> {head_name}"],
                },
            )
        )

        captured_requests: list[Any] = []

        async def _fake_run_vision_assist(ctx, *, request, resolver):
            captured_requests.append(request)
            return AssistantRunResult(
                status="success",
                assistant_name="vision_assist",
                message="ok",
                budget=AssistantBudgetContract(max_input_chars=2000, max_messages=1, max_tokens=150, tool_budget=0),
                capability_source="local_runtime",
                result=VisionAssistContract(
                    backend_kind="mlx_local",
                    model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                    goal_summary="Primary masses remain globally readable before local ear repair takes over.",
                    visible_changes=["Front and side squirrel silhouettes are readable."],
                    shape_mismatches=[],
                    proportion_mismatches=[],
                    correction_focus=[],
                    next_corrections=[],
                    likely_issues=[],
                    recommended_checks=[],
                    packet_guidance=VisionPacketStatusContract(
                        packet_status="clean",
                        status_reason=None,
                        ranking_recommendation="skip_clean",
                    ),
                ),
            )

        monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: scene_handler)
        monkeypatch.setattr(
            "server.adapters.mcp.areas.reference.get_vision_backend_resolver",
            lambda: SimpleNamespace(
                runtime_config=SimpleNamespace(
                    max_tokens=400,
                    max_images=8,
                    active_model_name="task-169-squirrel-proof",
                )
            ),
        )
        monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)

        result = asyncio.run(
            reference_compare_stage_checkpoint(
                ctx,
                checkpoint_label="stage_squirrel_quality_regression",
                preset_profile="compact",
            )
        )

        assert result.error is None
        assert result.target_object == body_name
        assert result.target_objects == [body_name, head_name, tail_name]
        assert result.compare_diagnostics is not None
        assert {packet.scope_label for packet in result.compare_diagnostics.packets} == {"Body + Head", "Tail"}
        assert all(packet.scope_label != "Ears" for packet in result.compare_diagnostics.packets)
        assert result.runtime_evidence is not None
        runtime_by_capability = {item.capability: item for item in result.runtime_evidence.capabilities}
        assert runtime_by_capability["vision"].status == "used"
        assert runtime_by_capability["localization"].status == "not_configured"
        assert runtime_by_capability["segmentation"].status == "not_configured"
        assert result.reference_orchestrator_feedback is not None
        assert result.reference_orchestrator_feedback.runtime_evidence is not None
        assert captured_requests
        assert {request.metadata["packet_scope"] for request in captured_requests} == {"Body + Head", "Tail"}
        assert all(ear_name not in list(request.metadata["target_objects"]) for request in captured_requests)

        metrics = _squirrel_quality_metrics(
            ctx,
            scene_handler,
            body_name=body_name,
            head_name=head_name,
            tail_name=tail_name,
        )
        assert metrics["body_ratio_passed"] is True
        assert metrics["head_tower_ratio"] < 0.8
        assert metrics["tail_rear"] is True
        assert metrics["tail_upward"] is True
        assert metrics["head_body_verdict"] == "seated_contact"
        assert metrics["tail_body_verdict"] == "seated_contact"
    except RuntimeError as error:
        _skip_if_blender_unavailable(error)
