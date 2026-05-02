"""Transport-backed TASK-157 gate-state roundtrip regressions."""

from __future__ import annotations

import asyncio
import base64
import textwrap
from pathlib import Path

import pytest

from ._guided_surface_harness import (
    result_payload,
    run_streamable_server,
    stdio_client,
    streamable_client,
    write_server_script,
)

_PATCHED_GATE_STATE_SERVER = textwrap.dedent(
    """
    from server.adapters.mcp.areas import router as router_area
    import server.adapters.mcp.areas.modeling as modeling_area
    import server.adapters.mcp.areas.reference as reference_area
    import server.adapters.mcp.areas.scene as scene_area
    import server.adapters.mcp.router_helper as router_helper
    import server.infrastructure.di as di
    from pathlib import Path
    from types import SimpleNamespace
    from server.adapters.mcp.context_utils import ctx_session_id, ctx_transport_type
    from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
    from server.adapters.mcp.sampling.result_types import (
        AssistantBudgetContract,
        AssistantRunResult,
        VisionAssistContract,
    )
    from server.adapters.mcp.session_capabilities import (
        build_guided_reference_readiness_payload,
    )


    class RouterHandler:
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


    class SceneHandler:
        def list_objects(self):
            return [
                {"name": "Squirrel_Body", "type": "MESH"},
                {"name": "Squirrel_Tail", "type": "MESH"},
            ]

        def get_bounding_box(self, object_name, world_space=True):
            payload = {
                "Squirrel_Body": {
                    "min": [-1.0, -1.0, 0.0],
                    "max": [1.0, 1.0, 2.0],
                    "center": [0.0, 0.0, 1.0],
                    "dimensions": [2.0, 2.0, 2.0],
                },
                "Squirrel_Tail": {
                    "min": [2.3, -0.2, 0.75],
                    "max": [3.1, 0.2, 1.0],
                    "center": [2.7, 0.0, 0.875],
                    "dimensions": [0.8, 0.4, 0.25],
                },
            }[object_name]
            return {"object_name": object_name, **payload}

        def get_scope_graph(self, target_object=None, target_objects=None, collection_name=None):
            names = [name for name in [target_object, *(target_objects or [])] if name]
            primary = target_object or (names[0] if names else None)
            return {
                "scope_kind": "object_set" if len(names) > 1 else "single_object",
                "primary_target": primary,
                "object_names": names,
                "object_count": len(names),
                "object_roles": [],
            }

        def get_relation_graph(
            self,
            target_object=None,
            target_objects=None,
            collection_name=None,
            goal_hint=None,
            include_truth_payloads=False,
        ):
            names = [name for name in [target_object, *(target_objects or [])] if name]
            primary = target_object or (names[0] if names else None)
            return {
                "scope": {
                    "scope_kind": "object_set" if len(names) > 1 else "single_object",
                    "primary_target": primary,
                    "object_names": names,
                    "object_count": len(names),
                    "object_roles": [],
                },
                "summary": {
                    "pairing_strategy": "guided_spatial_pairs",
                    "pair_count": 1,
                    "evaluated_pairs": 1,
                    "failing_pairs": 1,
                    "attachment_pairs": 1,
                    "support_pairs": 0,
                    "symmetry_pairs": 0,
                },
                "pairs": [
                    {
                        "pair_id": "squirrel_tail__squirrel_body",
                        "from_object": "Squirrel_Tail",
                        "to_object": "Squirrel_Body",
                        "pair_source": "required_creature_seam",
                        "relation_kinds": ["contact", "gap", "alignment", "attachment"],
                        "relation_verdicts": ["floating_gap"],
                        "gap_relation": "separated",
                        "gap_distance": 0.35,
                        "contact_passed": False,
                        "alignment_status": "aligned",
                        "aligned_axes": ["X", "Y", "Z"],
                        "measurement_basis": "bounding_box",
                        "attachment_semantics": {
                            "relation_kind": "segment_attachment",
                            "seam_kind": "tail_body",
                            "part_object": "Squirrel_Tail",
                            "anchor_object": "Squirrel_Body",
                            "required_seam": True,
                            "preferred_macro": "macro_attach_part_to_surface",
                            "attachment_verdict": "floating_gap",
                        },
                    }
                ],
            }

        def measure_gap(self, from_object, to_object, tolerance=0.0001):
            return {
                "from_object": from_object,
                "to_object": to_object,
                "gap": 0.35,
                "axis_gap": {"x": 0.35, "y": 0.0, "z": 0.0},
                "relation": "separated",
                "tolerance": tolerance,
                "units": "blender_units",
            }

        def measure_alignment(self, from_object, to_object, axes=None, reference="CENTER", tolerance=0.0001):
            return {
                "from_object": from_object,
                "to_object": to_object,
                "reference": reference,
                "axes": axes or ["X", "Y", "Z"],
                "deltas": {"x": 0.35, "y": 0.0, "z": 0.0},
                "aligned_axes": ["Y", "Z"],
                "misaligned_axes": ["X"],
                "is_aligned": False,
                "tolerance": tolerance,
                "units": "blender_units",
            }

        def measure_overlap(self, from_object, to_object, tolerance=0.0001):
            return {
                "from_object": from_object,
                "to_object": to_object,
                "overlaps": False,
                "relation": "disjoint",
                "tolerance": tolerance,
                "units": "blender_units",
            }

        def assert_contact(self, from_object, to_object, max_gap=0.0001, allow_overlap=False):
            return {
                "assertion": "scene_assert_contact",
                "passed": False,
                "subject": from_object,
                "target": to_object,
                "expected": {"max_gap": max_gap, "allow_overlap": allow_overlap},
                "actual": {"gap": 0.35, "relation": "separated"},
            }

        def assert_symmetry(self, left_object, right_object, axis="X", mirror_coordinate=0.0, tolerance=0.0001):
            return {
                "assertion": "scene_assert_symmetry",
                "passed": True,
                "subject_left": left_object,
                "subject_right": right_object,
                "axis": axis,
                "mirror_coordinate": mirror_coordinate,
                "tolerance": tolerance,
            }

        def get_view_diagnostics(
            self,
            target_object=None,
            target_objects=None,
            camera_name=None,
            focus_target=None,
            view_name=None,
            orbit_horizontal=0.0,
            orbit_vertical=0.0,
            zoom_factor=None,
            persist_view=False,
        ):
            names = [name for name in [target_object, *(target_objects or [])] if name]
            return {
                "view_query": {
                    "requested_view_source": "user_perspective",
                    "resolved_view_source": "user_perspective",
                    "analysis_backend": "mirrored_user_perspective",
                    "available": True,
                    "state_restored": True,
                },
                "summary": {
                    "target_count": len(names),
                    "visible_count": len(names),
                    "partially_visible_count": 0,
                    "fully_occluded_count": 0,
                    "outside_frame_count": 0,
                    "unavailable_count": 0,
                    "centered_target_count": len(names),
                    "framing_issue_count": 0,
                },
                "targets": [],
            }


    class ModelingHandler:
        def transform_object(self, name, location=None, rotation=None, scale=None):
            return f"Transformed object '{name}'"


    async def _fake_run_vision_assist(ctx, *, request, resolver):
        return AssistantRunResult(
            status="success",
            assistant_name="vision_assist",
            message="ok",
            budget=AssistantBudgetContract(max_input_chars=1000, max_messages=1, max_tokens=100, tool_budget=0),
            capability_source="local_runtime",
            result=VisionAssistContract(
                backend_kind="mlx_local",
                model_name="transport-gate-model",
                goal_summary="The tail/body seam is still floating.",
                visible_changes=["Body and tail are visible in the staged capture."],
                correction_focus=["Tail/body seam"],
            ),
        )


    _transport_capture = Path("/tmp/transport_gate_capture.png")
    _transport_capture.write_bytes(b"transport-capture")


    router_area.get_router_handler = lambda: RouterHandler()
    router_area._should_attach_repair_suggestion = lambda payload: False
    router_area._scene_has_meaningful_guided_objects = lambda: False
    scene_area.get_scene_handler = lambda: SceneHandler()
    modeling_area.get_modeling_handler = lambda: ModelingHandler()
    reference_area.get_scene_handler = lambda: SceneHandler()
    reference_area.run_vision_assist = _fake_run_vision_assist
    reference_area.get_vision_backend_resolver = lambda: SimpleNamespace(
        runtime_config=SimpleNamespace(max_tokens=200, max_images=8, active_model_name="transport-gate-model")
    )
    reference_area.capture_stage_images = lambda *args, **kwargs: [
        VisionCaptureImageContract(
            label="context_wide_after",
            image_path=str(_transport_capture),
            host_visible_path=str(_transport_capture),
            preset_name="context_wide",
            media_type="image/png",
            view_kind="wide",
        )
    ]
    di.get_scene_handler = lambda: SceneHandler()
    router_helper.is_router_enabled = lambda: False
    """
)

_TRANSPORT_REFERENCE_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4////fwAJ+wP9KobjigAAAABJRU5ErkJggg=="
)


def _tail_gate(gates: list[dict[str, object]]) -> dict[str, object]:
    return next(gate for gate in gates if gate["gate_id"] == "tail_body_seam")


async def _exercise_gate_state_roundtrip(client, reference_path: Path) -> None:
    gate_proposal = {
        "source": "llm_goal",
        "gates": [
            {
                "gate_id": "tail_body_seam",
                "gate_type": "attachment_seam",
                "label": "tail seated on body",
                "target_kind": "object_pair",
                "target_objects": ["Squirrel_Tail", "Squirrel_Body"],
            },
            {
                "gate_id": "tail_profile_segmentation",
                "gate_type": "shape_profile",
                "label": "tail follows segmented reference profile",
                "target_kind": "reference_part",
                "target_label": "tail_profile",
                "evidence_requirements": [{"evidence_kind": "part_segmentation", "required": True}],
            },
        ],
    }

    goal_result = result_payload(
        await client.call_tool(
            "router_set_goal",
            {
                "goal": "create a low-poly squirrel matching front and side reference images",
                "gate_proposal": gate_proposal,
            },
        )
    )

    assert goal_result["active_gate_plan"] is not None
    assert _tail_gate(goal_result["active_gate_plan"]["gates"])["status"] == "pending"
    assert goal_result["gate_intake_result"]["policy_warnings"]
    assert any(
        warning["code"] == "unavailable_required_evidence"
        for warning in goal_result["gate_intake_result"]["policy_warnings"]
    )

    attach_result = result_payload(
        await client.call_tool(
            "reference_images",
            {
                "action": "attach",
                "source_path": str(reference_path),
                "label": "front_ref",
                "target_object": "Squirrel_Body",
                "target_view": "front",
            },
        )
    )
    assert attach_result["reference_count"] == 1

    mutation_result = result_payload(
        await client.call_tool(
            "modeling_transform_object",
            {
                "name": "Squirrel_Body",
                "location": [0.0, 0.0, 0.0],
                "guided_role": "body_core",
            },
        )
    )
    assert "Transformed object" in str(mutation_result)

    relation_result = result_payload(
        await client.call_tool(
            "scene_relation_graph",
            {
                "target_object": "Squirrel_Body",
                "target_objects": ["Squirrel_Tail"],
                "goal_hint": "assembled creature",
            },
        )
    )
    assert relation_result["payload"]["pairs"][0]["attachment_semantics"]["attachment_verdict"] == "floating_gap"

    status_result = result_payload(await client.call_tool("router_get_status", {}))
    active_gate_plan = status_result["active_gate_plan"]
    assert active_gate_plan is not None
    tail_gate = _tail_gate(active_gate_plan["gates"])
    assert tail_gate["status"] == "failed"
    assert tail_gate["status_reason"] == "relation_floating_gap"
    assert any(blocker["gate_id"] == "tail_body_seam" for blocker in active_gate_plan["completion_blockers"])

    compare_result = result_payload(
        await client.call_tool(
            "reference_compare_stage_checkpoint",
            {
                "target_object": "Squirrel_Body",
                "target_objects": ["Squirrel_Tail"],
                "checkpoint_label": "gate_transport_compare",
                "target_view": "front",
                "preset_profile": "compact",
            },
        )
    )

    assert compare_result["active_gate_plan"] is not None
    assert _tail_gate(compare_result["active_gate_plan"]["gates"])["status"] == "failed"
    assert any(blocker["gate_id"] == "tail_body_seam" for blocker in compare_result["completion_blockers"])

    iterate_result = result_payload(
        await client.call_tool(
            "reference_iterate_stage_checkpoint",
            {
                "target_object": "Squirrel_Body",
                "target_objects": ["Squirrel_Tail"],
                "checkpoint_label": "gate_transport",
            },
        )
    )

    assert iterate_result["loop_disposition"] == "inspect_validate"
    assert iterate_result["active_gate_plan"] is not None
    assert _tail_gate(iterate_result["active_gate_plan"]["gates"])["status"] == "failed"
    assert any(blocker["gate_id"] == "tail_body_seam" for blocker in iterate_result["completion_blockers"])
    assert any(
        gate["gate_id"] == "tail_body_seam" and gate["status"] == "failed" for gate in iterate_result["gate_statuses"]
    )
    assert "resolve_quality_gate_blockers" in iterate_result["next_gate_actions"]
    assert "verify_or_repair_spatial_gate" in iterate_result["next_gate_actions"]
    assert "macro_attach_part_to_surface" in iterate_result["recommended_bounded_tools"]


@pytest.mark.slow
def test_guided_gate_state_roundtrip_over_stdio(tmp_path: Path):
    script_path = write_server_script(tmp_path, _PATCHED_GATE_STATE_SERVER)
    reference_path = tmp_path / "transport_front.png"
    reference_path.write_bytes(_TRANSPORT_REFERENCE_PNG)

    async def run() -> None:
        async with stdio_client(script_path) as client:
            await _exercise_gate_state_roundtrip(client, reference_path)

    asyncio.run(run())


@pytest.mark.slow
def test_guided_gate_state_roundtrip_over_streamable(tmp_path: Path):
    script_path = write_server_script(tmp_path, _PATCHED_GATE_STATE_SERVER)
    reference_path = tmp_path / "transport_front.png"
    reference_path.write_bytes(_TRANSPORT_REFERENCE_PNG)

    async def run(url: str) -> None:
        async with streamable_client(url) as client:
            await _exercise_gate_state_roundtrip(client, reference_path)

    with run_streamable_server(script_path) as url:
        asyncio.run(run(url))
