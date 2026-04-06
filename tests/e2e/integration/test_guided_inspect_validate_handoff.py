"""Transport-backed inspect/validate handoff regressions for TASK-141."""

from __future__ import annotations

import asyncio
import textwrap
from pathlib import Path

import pytest

from ._guided_surface_harness import result_payload, stdio_client, write_server_script

_PATCHED_HANDOFF_SERVER = textwrap.dedent(
    """
    from server.adapters.mcp.areas import router as router_area
    import server.adapters.mcp.areas.reference as reference_area
    from server.adapters.mcp.contracts.reference import ReferenceCompareStageCheckpointResponseContract


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
