"""Transport-backed inspect/validate handoff regressions for TASK-141."""

from __future__ import annotations

import asyncio
import textwrap
from pathlib import Path

import pytest

from ._guided_surface_harness import result_payload, stdio_client, write_server_script

_PATCHED_HANDOFF_SERVER = textwrap.dedent(
    """
    from dataclasses import replace
    from fastmcp import Context
    from server.adapters.mcp.areas import router as router_area
    import server.adapters.mcp.areas.reference as reference_area
    import server.adapters.mcp.areas.scene as scene_area
    from server.adapters.mcp.contracts.reference import ReferenceCompareStageCheckpointResponseContract
    import server.adapters.mcp.router_helper as router_helper
    import server.adapters.mcp.session_capabilities as session_caps


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


    def _ready_payload():
        return {
            "status": "ready",
            "goal": "low poly creature",
            "has_active_goal": True,
            "goal_input_pending": False,
            "attached_reference_count": 2,
            "pending_reference_count": 0,
            "compare_ready": True,
            "iterate_ready": True,
            "blocking_reason": None,
            "next_action": None,
        }


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
        if checkpoint_label == "degraded_truth":
            return ReferenceCompareStageCheckpointResponseContract.model_validate(
                {
                    "action": "compare_stage_checkpoint",
                    "goal": "low poly creature",
                    "target_object": "TruthHead",
                    "target_objects": ["TruthHead", "TruthBody"],
                    "checkpoint_id": "checkpoint_truth_error",
                    "checkpoint_label": checkpoint_label,
                    "preset_profile": preset_profile,
                    "preset_names": ["context_wide"],
                    "capture_count": 1,
                    "captures": [],
                    "reference_count": 1,
                    "reference_ids": ["ref_1"],
                    "reference_labels": ["front_ref"],
                    "error": "Vision endpoint request failed: synthetic degraded compare",
                    "guided_reference_readiness": _ready_payload(),
                    "correction_candidates": [
                        {
                            "candidate_id": "pair:truthhead_truthbody",
                            "summary": "TruthHead -> TruthBody still has wrong organic attachment semantics.",
                            "priority_rank": 1,
                            "priority": "high",
                            "candidate_kind": "truth_only",
                            "target_object": "TruthHead",
                            "target_objects": ["TruthHead", "TruthBody"],
                            "focus_pairs": ["TruthHead -> TruthBody"],
                            "source_signals": ["truth", "macro"],
                            "truth_evidence": {
                                "focus_pairs": ["TruthHead -> TruthBody"],
                                "item_kinds": ["attachment", "contact_failure"],
                                "items": [
                                    {
                                        "kind": "attachment",
                                        "summary": "TruthHead -> TruthBody still has wrong organic attachment semantics.",
                                        "priority": "high",
                                        "from_object": "TruthHead",
                                        "to_object": "TruthBody",
                                        "tool_name": "scene_assert_contact",
                                    }
                                ],
                                "macro_candidates": [
                                    {
                                        "macro_name": "macro_align_part_with_contact",
                                        "reason": "Use a bounded attachment/contact repair.",
                                        "priority": "high",
                                        "arguments_hint": {
                                            "part_object": "TruthHead",
                                            "reference_object": "TruthBody",
                                        },
                                    }
                                ],
                            },
                        }
                    ],
                }
            )

        return ReferenceCompareStageCheckpointResponseContract.model_validate(
            {
                "action": "compare_stage_checkpoint",
                "goal": "low poly creature",
                "target_object": "TruthHead",
                "target_objects": ["TruthHead", "TruthBody"],
                "checkpoint_id": "checkpoint_truth_inspect",
                "checkpoint_label": checkpoint_label,
                "preset_profile": preset_profile,
                "preset_names": ["context_wide"],
                "capture_count": 1,
                "captures": [],
                "reference_count": 1,
                "reference_ids": ["ref_1"],
                "reference_labels": ["front_ref"],
                "guided_reference_readiness": _ready_payload(),
                "correction_candidates": [
                    {
                        "candidate_id": "pair:truthhead_truthbody",
                        "summary": "TruthHead -> TruthBody failed the contact assertion.",
                        "priority_rank": 1,
                        "priority": "high",
                        "candidate_kind": "truth_only",
                        "target_object": "TruthHead",
                        "target_objects": ["TruthHead", "TruthBody"],
                        "focus_pairs": ["TruthHead -> TruthBody"],
                        "source_signals": ["truth", "macro"],
                        "truth_evidence": {
                            "focus_pairs": ["TruthHead -> TruthBody"],
                            "item_kinds": ["contact_failure"],
                            "items": [
                                {
                                    "kind": "contact_failure",
                                    "summary": "TruthHead -> TruthBody failed the contact assertion.",
                                    "priority": "high",
                                    "from_object": "TruthHead",
                                    "to_object": "TruthBody",
                                    "tool_name": "scene_assert_contact",
                                }
                            ],
                            "macro_candidates": [
                                {
                                    "macro_name": "macro_align_part_with_contact",
                                    "reason": "Repair the pair with a bounded nudge.",
                                    "priority": "high",
                                    "arguments_hint": {
                                        "part_object": "TruthHead",
                                        "reference_object": "TruthBody",
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        )


    router_area.get_router_handler = lambda: RouterHandler()
    router_area._should_attach_repair_suggestion = lambda payload: False
    reference_area.reference_compare_stage_checkpoint = _fake_reference_compare_stage_checkpoint


    async def _fake_macro_align_part_with_contact(
        ctx: Context,
        part_object,
        reference_object,
        target_relation="contact",
        gap=0.0,
        align_mode="none",
        normal_axis=None,
        preserve_side=True,
        max_nudge=0.5,
        offset=None,
    ):
        current = await session_caps.get_session_capability_state_async(ctx)
        flow_state = dict(current.guided_flow_state or {})
        flow_state["current_step"] = "inspect_validate"
        flow_state["spatial_refresh_required"] = True
        flow_state["required_checks"] = [
            {"check_id": "scope", "tool_name": "scene_scope_graph", "reason": "refresh scope", "status": "pending"},
            {"check_id": "relation", "tool_name": "scene_relation_graph", "reason": "refresh relations", "status": "pending"},
            {"check_id": "view", "tool_name": "scene_view_diagnostics", "reason": "refresh view", "status": "pending"},
        ]
        flow_state["next_actions"] = ["refresh_spatial_context"]
        flow_state["allowed_families"] = ["spatial_context", "checkpoint_iterate", "inspect_validate"]
        await session_caps.set_session_capability_state_async(
            ctx,
            replace(current, guided_flow_state=flow_state),
        )
        return {
            "status": "success",
            "macro_name": "macro_align_part_with_contact",
            "intent": f"repair '{part_object}' relative to '{reference_object}'",
            "actions_taken": [
                {
                    "status": "applied",
                    "action": "nudge_pair_contact",
                    "tool_name": "modeling_transform_object",
                    "summary": "Synthetic bounded contact repair.",
                }
            ],
            "objects_modified": [part_object],
            "requires_followup": False,
        }


    scene_area.macro_align_part_with_contact = _fake_macro_align_part_with_contact
    router_helper.is_router_enabled = lambda: False
    """
)


async def _call_iterate(script_path: Path, checkpoint_label: str) -> dict[str, object]:
    async with stdio_client(script_path) as client:
        await client.call_tool(
            "router_set_goal",
            {"goal": "create a low-poly squirrel matching front and side reference images"},
        )
        result = await client.call_tool(
            "reference_iterate_stage_checkpoint",
            {"target_object": "TruthHead", "target_objects": ["TruthBody"], "checkpoint_label": checkpoint_label},
        )
        payload = result_payload(result)
        assert isinstance(payload, dict)
        return payload


async def _iterate_and_collect_visibility(
    script_path: Path, checkpoint_label: str
) -> tuple[dict[str, object], dict[str, object]]:
    async with stdio_client(script_path) as client:
        await client.call_tool(
            "router_set_goal",
            {"goal": "create a low-poly squirrel matching front and side reference images"},
        )
        result = await client.call_tool(
            "reference_iterate_stage_checkpoint",
            {"target_object": "TruthHead", "target_objects": ["TruthBody"], "checkpoint_label": checkpoint_label},
        )
        payload = result_payload(result)
        assert isinstance(payload, dict)
        status_result = result_payload(await client.call_tool("router_get_status", {}))
        assert isinstance(status_result, dict)
        return payload, status_result


async def _iterate_repair_and_collect_visibility(
    script_path: Path, checkpoint_label: str
) -> tuple[dict[str, object], dict[str, object], dict[str, object], set[str], set[str]]:
    async with stdio_client(script_path) as client:
        await client.call_tool(
            "router_set_goal",
            {"goal": "create a low-poly squirrel matching front and side reference images"},
        )
        await client.call_tool(
            "reference_iterate_stage_checkpoint",
            {"target_object": "TruthHead", "target_objects": ["TruthBody"], "checkpoint_label": checkpoint_label},
        )
        before_status = result_payload(await client.call_tool("router_get_status", {}))
        repair_result = result_payload(
            await client.call_tool(
                "macro_align_part_with_contact",
                {"part_object": "TruthHead", "reference_object": "TruthBody"},
            )
        )
        after_status = result_payload(await client.call_tool("router_get_status", {}))
        tool_names_after_repair = {tool.name for tool in await client.list_tools()}
        repair_search = result_payload(
            await client.call_tool("search_tools", {"query": "contact repair nudge pair alignment"})
        )
        assert isinstance(before_status, dict)
        assert isinstance(repair_result, dict)
        assert isinstance(after_status, dict)
        assert isinstance(repair_search, list)
        repair_search_names = {
            item["name"] for item in repair_search if isinstance(item, dict) and isinstance(item.get("name"), str)
        }
        return before_status, repair_result, after_status, tool_names_after_repair, repair_search_names


def _visible_tool_names_from_status(status: dict[str, object]) -> set[str]:
    visible_names: set[str] = set()
    raw_rules = status.get("visibility_rules")
    if not isinstance(raw_rules, list):
        return visible_names
    for raw_rule in raw_rules:
        if not isinstance(raw_rule, dict):
            continue
        components = raw_rule.get("components")
        if components != ["tool"] and components != {"tool"}:
            continue
        for raw_name in raw_rule.get("names") or []:
            if isinstance(raw_name, str):
                visible_names.add(raw_name)
    return visible_names


@pytest.mark.slow
def test_guided_inspect_validate_handoff_is_truth_first_on_active_stdio_surface(tmp_path: Path):
    """High-priority truth findings should force a stop-and-check branch on the active client path."""

    script_path = write_server_script(tmp_path, _PATCHED_HANDOFF_SERVER)
    payload = asyncio.run(_call_iterate(script_path, "truth_first"))

    assert payload["loop_disposition"] == "inspect_validate"
    assert payload["correction_focus"] == ["TruthHead -> TruthBody failed the contact assertion."]
    assert "Stop free-form modeling" in str(payload["message"])
    assert "inspect/measure/assert" in str(payload["message"])


@pytest.mark.slow
def test_guided_degraded_compare_handoff_keeps_same_truth_first_story(tmp_path: Path):
    """Degraded compare should still hand the operator off to inspect/measure/assert when truth remains strong."""

    script_path = write_server_script(tmp_path, _PATCHED_HANDOFF_SERVER)
    payload = asyncio.run(_call_iterate(script_path, "degraded_truth"))

    assert payload["loop_disposition"] == "inspect_validate"
    assert payload["continue_recommended"] is True
    assert "Vision compare did not complete successfully" in str(payload["message"])
    assert "Stop free-form modeling" in str(payload["message"])
    assert "synthetic degraded compare" in str(payload["stop_reason"])


@pytest.mark.slow
def test_guided_inspect_validate_surface_exposes_spatial_and_attachment_tools_consistently(tmp_path: Path):
    """The inspect phase should expose the same bounded repair surface implied by guided family policy."""

    script_path = write_server_script(tmp_path, _PATCHED_HANDOFF_SERVER)
    payload, status = asyncio.run(_iterate_and_collect_visibility(script_path, "truth_first"))
    visibility_rules = status.get("visibility_rules")
    assert isinstance(visibility_rules, list)
    visible_tool_names = {
        name
        for rule in visibility_rules
        if isinstance(rule, dict)
        for name in (rule.get("names") or [])
        if rule.get("components") == ["tool"] or rule.get("components") == {"tool"}
    }

    assert payload["loop_disposition"] == "inspect_validate"
    assert status["current_phase"] == "inspect_validate"
    assert "scene_scope_graph" in visible_tool_names
    assert "scene_relation_graph" in visible_tool_names
    assert "scene_view_diagnostics" in visible_tool_names
    assert "macro_attach_part_to_surface" in visible_tool_names
    assert "macro_align_part_with_contact" in visible_tool_names
    assert "macro_cleanup_part_intersections" in visible_tool_names


@pytest.mark.slow
def test_guided_inspect_validate_refresh_barrier_hides_attachment_macros_after_repair_mutation(tmp_path: Path):
    """Once inspect/validate re-arms spatial refresh, attachment mutators should disappear from the shaped surface."""

    script_path = write_server_script(tmp_path, _PATCHED_HANDOFF_SERVER)
    before_status, repair_result, after_status, tool_names_after_repair, repair_search_names = asyncio.run(
        _iterate_repair_and_collect_visibility(script_path, "truth_first")
    )

    before_visible_tool_names = _visible_tool_names_from_status(before_status)
    after_visible_tool_names = _visible_tool_names_from_status(after_status)
    after_flow_state = after_status.get("guided_flow_state")
    assert isinstance(after_flow_state, dict)

    assert before_status["current_phase"] == "inspect_validate"
    assert "macro_align_part_with_contact" in before_visible_tool_names
    assert repair_result["status"] == "success"
    assert repair_result["macro_name"] == "macro_align_part_with_contact"
    assert after_status["current_phase"] == "inspect_validate"
    assert after_flow_state["current_step"] == "inspect_validate"
    assert after_flow_state["spatial_refresh_required"] is True
    assert after_flow_state["next_actions"] == ["refresh_spatial_context"]
    assert "macro_align_part_with_contact" not in tool_names_after_repair
    assert "scene_scope_graph" in after_visible_tool_names
    assert "scene_relation_graph" in after_visible_tool_names
    assert "scene_view_diagnostics" in after_visible_tool_names
    assert "macro_align_part_with_contact" not in repair_search_names
    assert "macro_attach_part_to_surface" not in after_visible_tool_names
    assert "macro_align_part_with_contact" not in after_visible_tool_names
    assert "macro_cleanup_part_intersections" not in after_visible_tool_names
