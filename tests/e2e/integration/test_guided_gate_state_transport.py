"""Transport-backed TASK-157 gate-state roundtrip regressions."""

from __future__ import annotations

import asyncio
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
    from server.adapters.mcp.context_utils import ctx_session_id, ctx_transport_type
    from server.adapters.mcp.session_capabilities import (
        build_guided_reference_readiness_payload,
        get_session_capability_state_async,
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


    async def _fake_reference_compare_stage_checkpoint(
        ctx,
        target_object=None,
        target_objects=None,
        collection_name=None,
        checkpoint_label=None,
        target_view=None,
        goal_override=None,
        prompt_hint=None,
        preset_profile="compact",
    ):
        session = await get_session_capability_state_async(ctx)
        return reference_area._stage_compare_response(
            session_id=ctx_session_id(ctx),
            transport=ctx_transport_type(ctx),
            goal=goal_override or session.goal,
            guided_flow_state=session.guided_flow_state,
            active_gate_plan=session.gate_plan,
            checkpoint_id=f"transport_{checkpoint_label or 'checkpoint'}",
            checkpoint_label=checkpoint_label,
            target_object=target_object,
            target_objects=list(target_objects or []),
            collection_name=collection_name,
            target_view=target_view,
            preset_profile=preset_profile,
            preset_names=["context_wide"],
            captures=[],
            reference_ids=[],
            reference_labels=[],
            include_captures=False,
            guided_reference_readiness=build_guided_reference_readiness_payload(session),
            message="Synthetic gate-state compare.",
        )


    router_area.get_router_handler = lambda: RouterHandler()
    router_area._should_attach_repair_suggestion = lambda payload: False
    router_area._scene_has_meaningful_guided_objects = lambda: False
    scene_area.get_scene_handler = lambda: SceneHandler()
    modeling_area.get_modeling_handler = lambda: ModelingHandler()
    reference_area.reference_compare_stage_checkpoint = _fake_reference_compare_stage_checkpoint
    di.get_scene_handler = lambda: SceneHandler()
    router_helper.is_router_enabled = lambda: False
    """
)


def _tail_gate(gates: list[dict[str, object]]) -> dict[str, object]:
    return next(gate for gate in gates if gate["gate_id"] == "tail_body_seam")


async def _exercise_gate_state_roundtrip(client) -> None:
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

    async def run() -> None:
        async with stdio_client(script_path) as client:
            await _exercise_gate_state_roundtrip(client)

    asyncio.run(run())


@pytest.mark.slow
def test_guided_gate_state_roundtrip_over_streamable(tmp_path: Path):
    script_path = write_server_script(tmp_path, _PATCHED_GATE_STATE_SERVER)

    async def run(url: str) -> None:
        async with streamable_client(url) as client:
            await _exercise_gate_state_roundtrip(client)

    with run_streamable_server(script_path) as url:
        asyncio.run(run(url))
