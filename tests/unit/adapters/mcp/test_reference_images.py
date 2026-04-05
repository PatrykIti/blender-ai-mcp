"""Tests for the goal-scoped reference image MCP surface."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from server.adapters.mcp.areas.reference import (
    _assembled_target_scope,
    _build_correction_candidates,
    _build_truth_followup,
    _effective_candidate_budget,
    _effective_pair_budget,
    _model_budget_bias,
    _select_refinement_route,
    reference_compare_checkpoint,
    reference_compare_current_view,
    reference_compare_stage_checkpoint,
    reference_images,
    reference_iterate_stage_checkpoint,
)
from server.adapters.mcp.contracts.reference import ReferenceCompareStageCheckpointResponseContract
from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneAssertionPayloadContract,
    SceneCorrectionTruthBundleContract,
    SceneCorrectionTruthPairContract,
    SceneCorrectionTruthSummaryContract,
)
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantRunResult,
    VisionAssistContract,
)
from server.adapters.mcp.session_capabilities import update_session_from_router_goal


@dataclass
class FakeContext:
    state: dict[str, object] = field(default_factory=dict)
    session_id: str = "sess_test"
    transport: str = "stdio"

    def get_state(self, key: str):
        return self.state.get(key)

    def set_state(self, key: str, value, *, serializable: bool = True) -> None:
        self.state[key] = value

    def info(self, message, logger_name=None, extra=None):
        return None


def test_truth_followup_emits_cleanup_macro_candidate_for_overlap_pairs():
    bundle = SceneCorrectionTruthBundleContract(
        scope=SceneAssembledTargetScopeContract(
            scope_kind="object_set",
            primary_target="Horn",
            object_names=["Horn", "Head"],
            object_count=2,
        ),
        summary=SceneCorrectionTruthSummaryContract(
            pairing_strategy="primary_to_others",
            pair_count=1,
            evaluated_pairs=1,
            contact_failures=1,
            overlap_pairs=1,
        ),
        checks=[
            SceneCorrectionTruthPairContract(
                from_object="Horn",
                to_object="Head",
                gap={"relation": "overlapping", "gap": 0.0},
                alignment={"is_aligned": True, "axes": ["X", "Y", "Z"]},
                overlap={"overlaps": True, "relation": "overlap", "overlap_dimensions": [0.2, 0.3, 0.4]},
                contact_assertion=SceneAssertionPayloadContract(
                    assertion="scene_assert_contact",
                    passed=False,
                    subject="Horn",
                    target="Head",
                    expected={"max_gap": 0.0001, "allow_overlap": False},
                    actual={"gap": 0.0, "relation": "overlapping"},
                ),
            )
        ],
    )

    followup = _build_truth_followup(bundle)

    assert followup.continue_recommended is True
    assert followup.macro_candidates
    assert followup.macro_candidates[0].macro_name == "macro_cleanup_part_intersections"


def test_truth_followup_explicitly_calls_out_bbox_touching_but_surface_gap():
    bundle = SceneCorrectionTruthBundleContract(
        scope=SceneAssembledTargetScopeContract(
            scope_kind="object_set",
            primary_target="Eye",
            object_names=["Eye", "Head"],
            object_count=2,
        ),
        summary=SceneCorrectionTruthSummaryContract(
            pairing_strategy="primary_to_others",
            pair_count=1,
            evaluated_pairs=1,
            contact_failures=1,
            separated_pairs=1,
        ),
        checks=[
            SceneCorrectionTruthPairContract(
                from_object="Eye",
                to_object="Head",
                gap={
                    "relation": "separated",
                    "gap": 0.051,
                    "measurement_basis": "mesh_surface",
                    "bbox_relation": "contact",
                },
                alignment={"is_aligned": True, "axes": ["X", "Y", "Z"]},
                overlap={"overlaps": False, "relation": "disjoint"},
                contact_assertion=SceneAssertionPayloadContract(
                    assertion="scene_assert_contact",
                    passed=False,
                    subject="Eye",
                    target="Head",
                    expected={"max_gap": 0.0001, "allow_overlap": False},
                    actual={"gap": 0.051, "relation": "separated"},
                    details={
                        "measurement_basis": "mesh_surface",
                        "bbox_relation": "contact",
                    },
                ),
            )
        ],
    )

    followup = _build_truth_followup(bundle)

    assert followup.items
    assert "Bounding boxes touch" in followup.items[0].summary
    assert followup.items[1].summary.startswith("Eye -> Head still has measurable surface separation.")


def test_model_budget_bias_avoids_gemini_name_collision_and_keeps_explicit_mini_bias():
    assert _model_budget_bias("gemini-2.5-pro") == 0
    assert _model_budget_bias("gemini-2.5-flash") == 0
    assert _model_budget_bias("gpt-4.1-mini") == -1
    assert _model_budget_bias("mlx-community/Qwen3-VL-4B-Instruct-4bit") == -1


def test_effective_budgets_do_not_downgrade_gemini_model_names():
    assert _effective_pair_budget(max_tokens=600, model_name="gemini-2.5-flash") == 4
    assert _effective_candidate_budget(pair_budget=4, max_tokens=600, model_name="gemini-2.5-flash") == 5
    assert _effective_pair_budget(max_tokens=600, model_name="gpt-4.1-mini") == 3
    assert _effective_candidate_budget(pair_budget=3, max_tokens=600, model_name="gpt-4.1-mini") == 4


def test_assembled_target_scope_prefers_structural_anchor_over_accessory_first_item(monkeypatch):
    class SceneHandler:
        def get_bounding_box(self, object_name: str, world_space: bool = True):
            dimensions = {
                "EarLeft": [0.2, 0.2, 0.6],
                "EarRight": [0.2, 0.2, 0.6],
                "Head": [1.0, 0.9, 1.2],
            }[object_name]
            return {"object_name": object_name, "dimensions": dimensions}

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())

    scope = _assembled_target_scope(
        target_object=None,
        target_objects=["EarLeft", "EarRight", "Head"],
        collection_name=None,
    )

    assert scope.scope_kind == "object_set"
    assert scope.primary_target == "Head"


def test_build_correction_candidates_merges_truth_macro_and_matching_vision_focus():
    compare = ReferenceCompareStageCheckpointResponseContract.model_validate(
        {
            "action": "compare_stage_checkpoint",
            "goal": "low poly creature",
            "target_object": "TruthHead",
            "target_objects": ["TruthHead", "TruthBody"],
            "checkpoint_id": "checkpoint_merge",
            "checkpoint_label": "stage_merge",
            "preset_profile": "compact",
            "preset_names": ["context_wide"],
            "capture_count": 1,
            "captures": [],
            "reference_count": 1,
            "reference_ids": ["ref_1"],
            "reference_labels": ["front_ref"],
            "truth_followup": {
                "scope": {
                    "scope_kind": "object_set",
                    "primary_target": "TruthHead",
                    "object_names": ["TruthHead", "TruthBody"],
                    "object_count": 2,
                },
                "continue_recommended": True,
                "message": "truth",
                "focus_pairs": ["TruthHead -> TruthBody"],
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
            "vision_assistant": {
                "status": "success",
                "assistant_name": "vision_assist",
                "message": "ok",
                "budget": {"max_input_chars": 1000, "max_messages": 1, "max_tokens": 100, "tool_budget": 0},
                "capability_source": "local_runtime",
                "result": {
                    "backend_kind": "mlx_local",
                    "goal_summary": "The pair still needs correction.",
                    "visible_changes": ["The body is visible."],
                    "shape_mismatches": ["TruthHead -> TruthBody contact is still wrong."],
                    "proportion_mismatches": [],
                    "correction_focus": ["TruthHead -> TruthBody contact", "Head silhouette"],
                    "next_corrections": ["Repair contact first."],
                    "likely_issues": [],
                    "recommended_checks": [],
                    "captures_used": ["target_front_after"],
                },
            },
        }
    )

    candidates = _build_correction_candidates(compare)

    assert [candidate.priority_rank for candidate in candidates] == [1, 2]
    assert candidates[0].candidate_kind == "hybrid"
    assert candidates[0].priority == "high"
    assert candidates[0].focus_pairs == ["TruthHead -> TruthBody"]
    assert candidates[0].source_signals == ["truth", "macro", "vision"]
    assert candidates[0].truth_evidence is not None
    assert candidates[0].truth_evidence.macro_candidates[0].macro_name == "macro_align_part_with_contact"
    assert candidates[0].vision_evidence is not None
    assert candidates[0].vision_evidence.correction_focus == ["TruthHead -> TruthBody contact"]
    assert candidates[1].candidate_kind == "vision_only"
    assert candidates[1].summary == "Head silhouette"


def test_select_refinement_route_prefers_macro_for_assembly_signals():
    compare = ReferenceCompareStageCheckpointResponseContract.model_validate(
        {
            "action": "compare_stage_checkpoint",
            "goal": "assemble a low poly squirrel",
            "target_object": None,
            "target_objects": ["Head", "EarLeft", "EarRight"],
            "collection_name": "Squirrel",
            "checkpoint_id": "checkpoint_macro",
            "checkpoint_label": "stage_macro",
            "preset_profile": "compact",
            "preset_names": [],
            "capture_count": 0,
            "captures": [],
            "reference_count": 0,
            "reference_ids": [],
            "reference_labels": [],
            "truth_followup": {
                "scope": {
                    "scope_kind": "collection",
                    "primary_target": "Head",
                    "object_names": ["Head", "EarLeft", "EarRight"],
                    "object_count": 3,
                    "collection_name": "Squirrel",
                },
                "continue_recommended": True,
                "message": "truth",
                "focus_pairs": ["Head -> EarLeft"],
                "items": [],
                "macro_candidates": [
                    {
                        "macro_name": "macro_align_part_with_contact",
                        "reason": "Repair the pair with a bounded nudge.",
                        "priority": "high",
                        "arguments_hint": {"part_object": "Head", "reference_object": "EarLeft"},
                    }
                ],
            },
            "correction_candidates": [
                {
                    "candidate_id": "pair:head_earleft",
                    "summary": "Head -> EarLeft failed the contact assertion.",
                    "priority_rank": 1,
                    "priority": "high",
                    "candidate_kind": "truth_only",
                    "target_objects": ["Head", "EarLeft"],
                    "focus_pairs": ["Head -> EarLeft"],
                    "source_signals": ["truth", "macro"],
                    "truth_evidence": {
                        "focus_pairs": ["Head -> EarLeft"],
                        "item_kinds": ["contact_failure"],
                        "items": [],
                        "macro_candidates": [
                            {
                                "macro_name": "macro_align_part_with_contact",
                                "reason": "Repair the pair with a bounded nudge.",
                                "priority": "high",
                                "arguments_hint": {"part_object": "Head", "reference_object": "EarLeft"},
                            }
                        ],
                    },
                }
            ],
        }
    )

    route = _select_refinement_route(compare)

    assert route.domain_classification == "assembly"
    assert route.selected_family == "macro"


def test_select_refinement_route_prefers_sculpt_for_non_low_poly_organic_refinement():
    compare = ReferenceCompareStageCheckpointResponseContract.model_validate(
        {
            "action": "compare_stage_checkpoint",
            "goal": "refine the organic heart surface to look softer and more anatomical",
            "target_object": "Heart",
            "target_objects": ["Heart"],
            "checkpoint_id": "checkpoint_sculpt",
            "checkpoint_label": "stage_sculpt",
            "preset_profile": "compact",
            "preset_names": [],
            "capture_count": 0,
            "captures": [],
            "reference_count": 0,
            "reference_ids": [],
            "reference_labels": [],
            "correction_candidates": [
                {
                    "candidate_id": "vision:heart_surface",
                    "summary": "Heart surface still looks too lumpy.",
                    "priority_rank": 1,
                    "priority": "normal",
                    "candidate_kind": "vision_only",
                    "target_object": "Heart",
                    "target_objects": ["Heart"],
                    "focus_pairs": [],
                    "source_signals": ["vision"],
                    "vision_evidence": {
                        "correction_focus": ["Heart surface smoothing"],
                        "shape_mismatches": ["Heart surface still looks too lumpy."],
                        "proportion_mismatches": [],
                        "next_corrections": ["Smooth and slightly inflate the upper chamber area."],
                    },
                }
            ],
        }
    )

    route = _select_refinement_route(compare)

    assert route.domain_classification == "anatomy"
    assert route.selected_family == "sculpt_region"


def test_select_refinement_route_keeps_low_poly_creature_on_modeling_mesh():
    compare = ReferenceCompareStageCheckpointResponseContract.model_validate(
        {
            "action": "compare_stage_checkpoint",
            "goal": "refine the low-poly squirrel silhouette to match references",
            "target_object": "Squirrel",
            "target_objects": ["Squirrel"],
            "checkpoint_id": "checkpoint_lowpoly",
            "checkpoint_label": "stage_lowpoly",
            "preset_profile": "compact",
            "preset_names": [],
            "capture_count": 0,
            "captures": [],
            "reference_count": 0,
            "reference_ids": [],
            "reference_labels": [],
            "correction_candidates": [
                {
                    "candidate_id": "vision:squirrel_silhouette",
                    "summary": "Squirrel silhouette is still too round.",
                    "priority_rank": 1,
                    "priority": "normal",
                    "candidate_kind": "vision_only",
                    "target_object": "Squirrel",
                    "target_objects": ["Squirrel"],
                    "focus_pairs": [],
                    "source_signals": ["vision"],
                    "vision_evidence": {
                        "correction_focus": ["Squirrel silhouette"],
                        "shape_mismatches": ["Squirrel silhouette is still too round."],
                        "proportion_mismatches": [],
                        "next_corrections": ["Sharpen the main silhouette planes."],
                    },
                }
            ],
        }
    )

    route = _select_refinement_route(compare)

    assert route.domain_classification == "organic_form"
    assert route.selected_family == "modeling_mesh"


def test_reference_compare_stage_checkpoint_exposes_sculpt_handoff_without_visibility_unlock(tmp_path, monkeypatch):
    image_front = tmp_path / "front.png"
    image_front.write_bytes(b"front")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "refine the organic heart surface", {"status": "no_match"})
    asyncio.run(reference_images(ctx, action="attach", source_path=str(image_front), label="front_ref"))

    class SceneHandler:
        def get_bounding_box(self, object_name: str, world_space: bool = True):
            return {"object_name": object_name, "dimensions": [1.0, 1.0, 1.0]}

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
                goal_summary="Heart silhouette is still too lumpy.",
                visible_changes=["The full organic form is visible."],
                shape_mismatches=["Heart surface is still too lumpy."],
                correction_focus=["Heart surface smoothing"],
                next_corrections=["Smooth and slightly inflate the upper chamber area."],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.get_vision_backend_resolver",
        lambda: SimpleNamespace(
            runtime_config=SimpleNamespace(
                max_tokens=400,
                max_images=8,
                active_model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
            )
        ),
    )
    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.capture_stage_images",
        lambda *args, **kwargs: [
            VisionCaptureImageContract(
                label="context_wide_after",
                image_path=str(tmp_path / "context.jpg"),
                host_visible_path=str(tmp_path / "context.jpg"),
                preset_name="context_wide",
                media_type="image/jpeg",
                view_kind="wide",
            ),
        ],
    )

    result = asyncio.run(
        reference_compare_stage_checkpoint(
            ctx,
            target_object="Heart",
            checkpoint_label="stage_organic",
            preset_profile="compact",
        )
    )

    assert result.refinement_route is not None
    assert result.refinement_route.selected_family == "sculpt_region"
    assert result.refinement_handoff is not None
    assert result.refinement_handoff.selected_family == "sculpt_region"
    assert [tool.tool_name for tool in result.refinement_handoff.recommended_tools] == [
        "sculpt_deform_region",
        "sculpt_smooth_region",
        "sculpt_inflate_region",
        "sculpt_pinch_region",
    ]


def test_reference_images_attach_without_active_goal_is_staged_for_next_goal(tmp_path, monkeypatch):
    image = tmp_path / "ref.png"
    image.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    result = asyncio.run(reference_images(ctx, action="attach", source_path=str(image), label="front_ref"))

    assert result.error is None
    assert result.goal is None
    assert result.reference_count == 1
    assert result.references[0].goal == "__pending_goal__"
    assert "pending reference image" in (result.message or "")

    state = update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    assert state.reference_images is not None
    assert state.reference_images[0]["goal"] == "low poly squirrel"
    assert state.pending_reference_images is None


def test_reference_images_attach_during_pending_goal_questions_stays_pending_until_ready(tmp_path, monkeypatch):
    image = tmp_path / "ref.png"
    image.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(
        ctx,
        "low poly squirrel",
        {
            "status": "needs_input",
            "workflow": "squirrel_workflow",
            "unresolved": [{"param": "style"}],
        },
    )

    attached = asyncio.run(reference_images(ctx, action="attach", source_path=str(image), label="front_ref"))
    assert ctx.state["pending_reference_images"] is not None
    ready_state = update_session_from_router_goal(
        ctx,
        "low poly squirrel",
        {
            "status": "ready",
            "workflow": "squirrel_workflow",
            "resolved": {"style": "low_poly"},
            "unresolved": [],
            "resolution_sources": {"style": "user"},
            "message": "ok",
            "executed": 0,
        },
    )

    assert attached.error is None
    assert attached.goal == "low poly squirrel"
    assert attached.references[0].goal == "low poly squirrel"
    assert ready_state.reference_images is not None
    assert ready_state.reference_images[0]["goal"] == "low poly squirrel"
    assert ready_state.pending_reference_images is None


def test_reference_images_attach_during_pending_goal_questions_keeps_pending_store_isolated_from_active_refs(
    tmp_path, monkeypatch
):
    image_active = tmp_path / "active.png"
    image_pending = tmp_path / "pending.png"
    image_active.write_bytes(b"active")
    image_pending.write_bytes(b"pending")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "ready"})

    active_attached = asyncio.run(
        reference_images(ctx, action="attach", source_path=str(image_active), label="front_ref")
    )
    active_id = active_attached.references[0].reference_id

    update_session_from_router_goal(
        ctx,
        "low poly squirrel",
        {
            "status": "needs_input",
            "workflow": "squirrel_workflow",
            "unresolved": [{"param": "style"}],
        },
    )

    staged = asyncio.run(reference_images(ctx, action="attach", source_path=str(image_pending), label="side_ref"))
    listed = asyncio.run(reference_images(ctx, action="list"))

    pending_state = ctx.state["pending_reference_images"]
    assert pending_state is not None
    assert len(pending_state) == 1
    assert pending_state[0]["reference_id"] != active_id
    assert ctx.state["reference_images"] is not None
    assert len(ctx.state["reference_images"]) == 1
    assert ctx.state["reference_images"][0]["reference_id"] == active_id
    assert staged.reference_count == 2
    assert [item.reference_id for item in staged.references] == [active_id, pending_state[0]["reference_id"]]
    assert listed.reference_count == 2
    assert [item.reference_id for item in listed.references] == [active_id, pending_state[0]["reference_id"]]


def test_reference_images_remove_during_pending_goal_questions_can_remove_active_ref_without_touching_staged_refs(
    tmp_path, monkeypatch
):
    image_active = tmp_path / "active.png"
    image_pending = tmp_path / "pending.png"
    image_active.write_bytes(b"active")
    image_pending.write_bytes(b"pending")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "ready"})

    active_attached = asyncio.run(
        reference_images(ctx, action="attach", source_path=str(image_active), label="front_ref")
    )
    active_ref = active_attached.references[0]
    active_path = active_ref.stored_path

    update_session_from_router_goal(
        ctx,
        "low poly squirrel",
        {
            "status": "needs_input",
            "workflow": "squirrel_workflow",
            "unresolved": [{"param": "style"}],
        },
    )

    staged = asyncio.run(reference_images(ctx, action="attach", source_path=str(image_pending), label="side_ref"))
    staged_ref = next(item for item in staged.references if item.reference_id != active_ref.reference_id)
    staged_path = staged_ref.stored_path

    removed = asyncio.run(reference_images(ctx, action="remove", reference_id=active_ref.reference_id))

    assert removed.removed_reference_id == active_ref.reference_id
    assert removed.reference_count == 1
    assert removed.references[0].reference_id == staged_ref.reference_id
    assert ctx.state["reference_images"] is None
    assert ctx.state["pending_reference_images"] is not None
    assert len(ctx.state["pending_reference_images"]) == 1
    assert ctx.state["pending_reference_images"][0]["reference_id"] == staged_ref.reference_id
    assert not Path(active_path).exists()
    assert Path(staged_path).exists()


def test_reference_images_clear_during_pending_goal_questions_clears_active_and_pending_reference_files(
    tmp_path, monkeypatch
):
    image_active = tmp_path / "active.png"
    image_pending = tmp_path / "pending.png"
    image_active.write_bytes(b"active")
    image_pending.write_bytes(b"pending")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "ready"})

    active_attached = asyncio.run(
        reference_images(ctx, action="attach", source_path=str(image_active), label="front_ref")
    )
    active_path = active_attached.references[0].stored_path

    update_session_from_router_goal(
        ctx,
        "low poly squirrel",
        {
            "status": "needs_input",
            "workflow": "squirrel_workflow",
            "unresolved": [{"param": "style"}],
        },
    )

    staged = asyncio.run(reference_images(ctx, action="attach", source_path=str(image_pending), label="side_ref"))
    staged_ref = next(item for item in staged.references if item.stored_path != active_path)
    staged_path = staged_ref.stored_path

    cleared = asyncio.run(reference_images(ctx, action="clear"))

    assert cleared.reference_count == 0
    assert cleared.message == "Cleared active and pending reference images."
    assert ctx.state["reference_images"] is None
    assert ctx.state["pending_reference_images"] is None
    assert not Path(active_path).exists()
    assert not Path(staged_path).exists()


def test_reference_images_remove_ready_session_can_remove_explicit_pending_ref_without_touching_active_ref(tmp_path):
    active_path = tmp_path / "active.png"
    pending_path = tmp_path / "pending.png"
    active_path.write_bytes(b"active")
    pending_path.write_bytes(b"pending")

    ctx = FakeContext(
        state={
            "goal": "table",
            "last_router_status": "ready",
            "reference_images": [
                {
                    "reference_id": "ref_active",
                    "goal": "table",
                    "label": "table_ref",
                    "notes": None,
                    "target_object": None,
                    "target_view": None,
                    "stored_path": str(active_path),
                    "host_visible_path": str(active_path),
                    "media_type": "image/png",
                    "source_kind": "local_path",
                    "original_path": str(active_path),
                    "added_at": "2026-04-05T10:00:00Z",
                }
            ],
            "pending_reference_images": [
                {
                    "reference_id": "ref_pending",
                    "goal": "chair",
                    "label": "chair_ref",
                    "notes": None,
                    "target_object": None,
                    "target_view": None,
                    "stored_path": str(pending_path),
                    "host_visible_path": str(pending_path),
                    "media_type": "image/png",
                    "source_kind": "local_path",
                    "original_path": str(pending_path),
                    "added_at": "2026-04-05T10:05:00Z",
                }
            ],
        }
    )

    listed = asyncio.run(reference_images(ctx, action="list"))
    removed = asyncio.run(reference_images(ctx, action="remove", reference_id="ref_pending"))

    assert listed.reference_count == 2
    assert [item.reference_id for item in listed.references] == ["ref_active", "ref_pending"]
    assert removed.removed_reference_id == "ref_pending"
    assert removed.reference_count == 1
    assert removed.references[0].reference_id == "ref_active"
    assert ctx.state["reference_images"] is not None
    assert ctx.state["reference_images"][0]["reference_id"] == "ref_active"
    assert ctx.state["pending_reference_images"] is None
    assert Path(active_path).exists()
    assert not Path(pending_path).exists()


def test_reference_images_clear_ready_session_also_clears_explicit_pending_refs(tmp_path):
    active_path = tmp_path / "active.png"
    pending_path = tmp_path / "pending.png"
    active_path.write_bytes(b"active")
    pending_path.write_bytes(b"pending")

    ctx = FakeContext(
        state={
            "goal": "table",
            "last_router_status": "ready",
            "reference_images": [
                {
                    "reference_id": "ref_active",
                    "goal": "table",
                    "label": "table_ref",
                    "notes": None,
                    "target_object": None,
                    "target_view": None,
                    "stored_path": str(active_path),
                    "host_visible_path": str(active_path),
                    "media_type": "image/png",
                    "source_kind": "local_path",
                    "original_path": str(active_path),
                    "added_at": "2026-04-05T10:00:00Z",
                }
            ],
            "pending_reference_images": [
                {
                    "reference_id": "ref_pending",
                    "goal": "chair",
                    "label": "chair_ref",
                    "notes": None,
                    "target_object": None,
                    "target_view": None,
                    "stored_path": str(pending_path),
                    "host_visible_path": str(pending_path),
                    "media_type": "image/png",
                    "source_kind": "local_path",
                    "original_path": str(pending_path),
                    "added_at": "2026-04-05T10:05:00Z",
                }
            ],
        }
    )

    listed = asyncio.run(reference_images(ctx, action="list"))
    cleared = asyncio.run(reference_images(ctx, action="clear"))

    assert listed.reference_count == 2
    assert [item.reference_id for item in listed.references] == ["ref_active", "ref_pending"]
    assert cleared.reference_count == 0
    assert cleared.message == "Cleared active and pending reference images."
    assert ctx.state["reference_images"] is None
    assert ctx.state["pending_reference_images"] is None
    assert not Path(active_path).exists()
    assert not Path(pending_path).exists()


def test_reference_images_attach_list_remove_and_clear(tmp_path, monkeypatch):
    image = tmp_path / "ref.png"
    image.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "rounded housing", {"status": "ready"})

    attached = asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image),
            label="main_ref",
            notes="front silhouette",
            target_object="Housing",
            target_view="front",
        )
    )

    assert attached.reference_count == 1
    ref = attached.references[0]
    assert ref.goal == "rounded housing"
    assert ref.label == "main_ref"
    assert ref.target_object == "Housing"
    assert ref.stored_path.endswith(".png")

    listed = asyncio.run(reference_images(ctx, action="list"))
    assert listed.reference_count == 1
    assert listed.references[0].reference_id == ref.reference_id

    removed = asyncio.run(reference_images(ctx, action="remove", reference_id=ref.reference_id))
    assert removed.reference_count == 0
    assert removed.removed_reference_id == ref.reference_id

    attached_again = asyncio.run(reference_images(ctx, action="attach", source_path=str(image)))
    assert attached_again.reference_count == 1
    cleared = asyncio.run(reference_images(ctx, action="clear"))
    assert cleared.reference_count == 0


def test_reference_compare_checkpoint_uses_goal_and_matching_references(tmp_path, monkeypatch):
    image = tmp_path / "ref.png"
    image.write_bytes(b"fake")
    checkpoint = tmp_path / "checkpoint.png"
    checkpoint.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image),
            label="front_ref",
            target_object="Squirrel",
            target_view="front",
        )
    )

    captured = {}

    async def _fake_run_vision_assist(ctx, *, request, resolver):
        captured["request"] = request
        return AssistantRunResult(
            status="success",
            assistant_name="vision_assist",
            message="ok",
            budget=AssistantBudgetContract(max_input_chars=1000, max_messages=1, max_tokens=100, tool_budget=0),
            capability_source="local_runtime",
            result=VisionAssistContract(
                backend_kind="mlx_local",
                model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                goal_summary="Closer to the squirrel reference.",
                visible_changes=["Tail arc is still too low."],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())

    result = asyncio.run(
        reference_compare_checkpoint(
            ctx,
            checkpoint_path=str(checkpoint),
            checkpoint_label="stage_2",
            target_object="Squirrel",
            target_view="front",
        )
    )

    assert result.error is None
    assert result.goal == "low poly squirrel"
    assert result.reference_count == 1
    assert result.reference_labels == ["front_ref"]
    assert result.vision_assistant is not None
    assert result.vision_assistant.result is not None
    assert captured["request"].goal == "low poly squirrel"
    assert [image.role for image in captured["request"].images] == ["after", "reference"]


def test_reference_compare_checkpoint_requires_goal_or_override(tmp_path):
    checkpoint = tmp_path / "checkpoint.png"
    checkpoint.write_bytes(b"fake")

    result = asyncio.run(reference_compare_checkpoint(FakeContext(), checkpoint_path=str(checkpoint)))

    assert result.error is not None
    assert "router_set_goal" in result.error


def test_reference_compare_current_view_captures_then_compares(tmp_path, monkeypatch):
    image = tmp_path / "ref.png"
    image.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image),
            label="side_ref",
            target_object="Squirrel",
            target_view="side",
        )
    )

    class SceneHandler:
        def get_viewport(self, **kwargs):
            return "ZmFrZQ=="  # base64("fake")

    captured = {}

    async def _fake_run_vision_assist(ctx, *, request, resolver):
        captured["request"] = request
        return AssistantRunResult(
            status="success",
            assistant_name="vision_assist",
            message="ok",
            budget=AssistantBudgetContract(max_input_chars=1000, max_messages=1, max_tokens=100, tool_budget=0),
            capability_source="local_runtime",
            result=VisionAssistContract(
                backend_kind="mlx_local",
                model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                goal_summary="Current side checkpoint is closer to the squirrel reference.",
                visible_changes=["Tail arc is now more visible."],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())

    result = asyncio.run(
        reference_compare_current_view(
            ctx,
            checkpoint_label="stage_3_side",
            target_object="Squirrel",
            target_view="side",
            camera_name="ShotCam",
        )
    )

    assert result.error is None
    assert result.reference_count == 1
    assert result.vision_assistant is not None
    assert result.vision_assistant.result is not None
    assert result.checkpoint_path.endswith(".jpg")
    assert [image.role for image in captured["request"].images] == ["after", "reference"]
    assert "comparison_mode=current_view_checkpoint" in (captured["request"].prompt_hint or "")


def test_reference_compare_current_view_uses_unique_checkpoint_filename(tmp_path, monkeypatch):
    image = tmp_path / "ref.png"
    image.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image),
            label="side_ref",
            target_object="Squirrel",
            target_view="side",
        )
    )

    class SceneHandler:
        def get_viewport(self, **kwargs):
            return "ZmFrZQ=="  # base64("fake")

    class FixedUuid:
        hex = "deadbeefcafebabe"

    class FixedDatetime:
        @staticmethod
        def now():
            return datetime(2026, 4, 1, 12, 34, 56)

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
                goal_summary="Current side checkpoint is closer to the squirrel reference.",
                visible_changes=["Tail arc is now more visible."],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.uuid4", lambda: FixedUuid())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.datetime", FixedDatetime)

    result = asyncio.run(
        reference_compare_current_view(
            ctx,
            checkpoint_label="stage_3_side",
            target_object="Squirrel",
            target_view="side",
        )
    )

    assert result.error is None
    assert result.checkpoint_path.endswith("checkpoint_compare_20260401_123456_deadbeef.jpg")
    assert result.checkpoint_path != ""


def test_reference_compare_current_view_requires_goal_before_capture(monkeypatch):
    class SceneHandler:
        def get_viewport(self, **kwargs):
            raise AssertionError("get_viewport should not be called without an active goal")

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())

    result = asyncio.run(reference_compare_current_view(FakeContext(), checkpoint_label="no_goal"))

    assert result.error is not None
    assert "router_set_goal" in result.error
    assert result.checkpoint_path == ""


def test_reference_compare_stage_checkpoint_captures_deterministic_stage_set(tmp_path, monkeypatch):
    image_front = tmp_path / "front.png"
    image_side = tmp_path / "side.png"
    image_front.write_bytes(b"front")
    image_side.write_bytes(b"side")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image_front),
            label="front_ref",
            target_object="Squirrel",
            target_view="front",
        )
    )
    asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image_side),
            label="side_ref",
            target_object="Squirrel",
            target_view="side",
        )
    )

    class SceneHandler:
        def measure_gap(self, from_object: str, to_object: str, tolerance: float = 0.0001):
            return {"from_object": from_object, "to_object": to_object, "relation": "contact", "gap": 0.0}

        def measure_alignment(self, from_object: str, to_object: str, axes=None, reference="CENTER", tolerance=0.0001):
            return {
                "from_object": from_object,
                "to_object": to_object,
                "is_aligned": True,
                "axes": axes or ["X", "Y", "Z"],
            }

        def measure_overlap(self, from_object: str, to_object: str, tolerance: float = 0.0001):
            return {"from_object": from_object, "to_object": to_object, "overlaps": False, "relation": "disjoint"}

        def assert_contact(
            self, from_object: str, to_object: str, max_gap: float = 0.0001, allow_overlap: bool = False
        ):
            return {
                "assertion": "scene_assert_contact",
                "passed": True,
                "subject": from_object,
                "target": to_object,
                "expected": {"max_gap": max_gap, "allow_overlap": allow_overlap},
                "actual": {"gap": 0.0, "relation": "contact"},
            }

    class CollectionHandler:
        def list_objects(self, collection_name: str, recursive: bool = True, include_hidden: bool = False):
            return {"objects": []}

    captured = {}

    async def _fake_run_vision_assist(ctx, *, request, resolver):
        captured["request"] = request
        return AssistantRunResult(
            status="success",
            assistant_name="vision_assist",
            message="ok",
            budget=AssistantBudgetContract(max_input_chars=1000, max_messages=1, max_tokens=100, tool_budget=0),
            capability_source="local_runtime",
            result=VisionAssistContract(
                backend_kind="mlx_local",
                model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                goal_summary="Stage checkpoint is moving closer to the squirrel references.",
                visible_changes=["The tail arc is more readable from side and front views."],
                shape_mismatches=["Head silhouette is still too spherical."],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_collection_handler", lambda: CollectionHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.capture_stage_images",
        lambda *args, **kwargs: [
            VisionCaptureImageContract(
                label="context_wide_after",
                image_path=str(tmp_path / "context.jpg"),
                host_visible_path=str(tmp_path / "context.jpg"),
                preset_name="context_wide",
                media_type="image/jpeg",
                view_kind="wide",
            ),
            VisionCaptureImageContract(
                label="target_front_after",
                image_path=str(tmp_path / "front.jpg"),
                host_visible_path=str(tmp_path / "front.jpg"),
                preset_name="target_front",
                media_type="image/jpeg",
                view_kind="focus",
            ),
            VisionCaptureImageContract(
                label="target_side_after",
                image_path=str(tmp_path / "side.jpg"),
                host_visible_path=str(tmp_path / "side.jpg"),
                preset_name="target_side",
                media_type="image/jpeg",
                view_kind="focus",
            ),
        ],
    )

    result = asyncio.run(
        reference_compare_stage_checkpoint(
            ctx,
            target_object="Squirrel",
            checkpoint_label="stage_3",
            preset_profile="compact",
        )
    )

    assert result.error is None
    assert result.reference_count == 2
    assert result.capture_count == 3
    assert result.preset_profile == "compact"
    assert result.preset_names == ["context_wide", "target_front", "target_side"]
    assert result.vision_assistant is not None
    assert result.assembled_target_scope is not None
    assert result.assembled_target_scope.scope_kind == "single_object"
    assert result.assembled_target_scope.primary_target == "Squirrel"
    assert result.assembled_target_scope.object_names == ["Squirrel"]
    assert result.truth_bundle is not None
    assert result.truth_bundle.summary.pairing_strategy == "none"
    assert result.truth_followup is not None
    assert result.truth_followup.continue_recommended is False
    assert captured["request"].truth_summary["scope"]["scope_kind"] == "single_object"
    assert [image.role for image in captured["request"].images] == [
        "after",
        "after",
        "after",
        "reference",
        "reference",
    ]
    assert "comparison_mode=stage_checkpoint_vs_reference" in (captured["request"].prompt_hint or "")


def test_reference_compare_stage_checkpoint_requires_goal_or_override():
    result = asyncio.run(reference_compare_stage_checkpoint(FakeContext(), target_object="Squirrel"))

    assert result.error is not None
    assert result.session_id == "sess_test"
    assert result.transport == "stdio"
    assert result.guided_reference_readiness is not None
    assert result.guided_reference_readiness.blocking_reason == "active_goal_required"
    assert result.guided_reference_readiness.next_action == "call_router_set_goal"
    assert "router_set_goal" in result.error


def test_reference_compare_stage_checkpoint_does_not_use_goal_override_as_session_substitute():
    result = asyncio.run(
        reference_compare_stage_checkpoint(
            FakeContext(),
            target_object="Squirrel",
            goal_override="low poly squirrel",
        )
    )

    assert result.error is not None
    assert result.guided_reference_readiness is not None
    assert result.guided_reference_readiness.blocking_reason == "active_goal_required"


def test_reference_compare_stage_checkpoint_can_hint_mcp_session_reconnect_when_scene_scope_exists(monkeypatch):
    class SceneHandler:
        def list_objects(self):
            return [
                {"name": "Squirrel_Head"},
                {"name": "Squirrel_Snout"},
                {"name": "Squirrel_Eye_L"},
            ]

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())

    result = asyncio.run(
        reference_compare_stage_checkpoint(
            FakeContext(),
            target_objects=["Squirrel_Head", "Squirrel_Snout", "Squirrel_Eye_L"],
            checkpoint_label="recovery_probe",
        )
    )

    assert result.error is not None
    assert "guided MCP session state was reset or reconnected" in result.error
    assert "router_set_goal" in result.error


def test_reference_compare_stage_checkpoint_fail_fast_exposes_pending_goal_readiness(tmp_path, monkeypatch):
    image = tmp_path / "ref.png"
    image.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(
        ctx,
        "low poly squirrel",
        {
            "status": "needs_input",
            "workflow": "squirrel_workflow",
            "unresolved": [{"param": "style"}],
        },
    )
    asyncio.run(reference_images(ctx, action="attach", source_path=str(image), label="front_ref"))

    result = asyncio.run(reference_compare_stage_checkpoint(ctx, target_object="Squirrel"))

    assert result.error is not None
    assert result.session_id == "sess_test"
    assert result.transport == "stdio"
    assert result.guided_reference_readiness is not None
    assert result.guided_reference_readiness.blocking_reason == "goal_input_pending"
    assert result.guided_reference_readiness.next_action == "answer_pending_goal_questions"


def test_reference_compare_stage_checkpoint_can_compare_full_scene_when_target_object_is_omitted(tmp_path, monkeypatch):
    image_front = tmp_path / "front.png"
    image_side = tmp_path / "side.png"
    image_front.write_bytes(b"front")
    image_side.write_bytes(b"side")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(reference_images(ctx, action="attach", source_path=str(image_front), label="front_ref"))
    asyncio.run(reference_images(ctx, action="attach", source_path=str(image_side), label="side_ref"))

    captured = {}

    class SceneHandler:
        def measure_gap(self, from_object: str, to_object: str, tolerance: float = 0.0001):
            raise AssertionError("measure_gap should not be called for scene-wide scope")

        def measure_alignment(self, from_object: str, to_object: str, axes=None, reference="CENTER", tolerance=0.0001):
            raise AssertionError("measure_alignment should not be called for scene-wide scope")

        def measure_overlap(self, from_object: str, to_object: str, tolerance: float = 0.0001):
            raise AssertionError("measure_overlap should not be called for scene-wide scope")

        def assert_contact(
            self, from_object: str, to_object: str, max_gap: float = 0.0001, allow_overlap: bool = False
        ):
            raise AssertionError("assert_contact should not be called for scene-wide scope")

    class CollectionHandler:
        def list_objects(self, collection_name: str, recursive: bool = True, include_hidden: bool = False):
            return {"objects": []}

    async def _fake_run_vision_assist(ctx, *, request, resolver):
        captured["request"] = request
        return AssistantRunResult(
            status="success",
            assistant_name="vision_assist",
            message="ok",
            budget=AssistantBudgetContract(max_input_chars=1000, max_messages=1, max_tokens=100, tool_budget=0),
            capability_source="local_runtime",
            result=VisionAssistContract(
                backend_kind="mlx_local",
                model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                goal_summary="The full squirrel scene is closer to the references.",
                visible_changes=["The full silhouette is visible across the deterministic views."],
                correction_focus=["Tail arc visibility"],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_collection_handler", lambda: CollectionHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.capture_stage_images",
        lambda *args, **kwargs: [
            VisionCaptureImageContract(
                label="context_wide_after",
                image_path=str(tmp_path / "context.jpg"),
                host_visible_path=str(tmp_path / "context.jpg"),
                preset_name="context_wide",
                media_type="image/jpeg",
                view_kind="wide",
            ),
            VisionCaptureImageContract(
                label="target_front_after",
                image_path=str(tmp_path / "front.jpg"),
                host_visible_path=str(tmp_path / "front.jpg"),
                preset_name="target_front",
                media_type="image/jpeg",
                view_kind="focus",
            ),
        ],
    )

    result = asyncio.run(
        reference_compare_stage_checkpoint(
            ctx,
            checkpoint_label="stage_full_scene",
            preset_profile="compact",
        )
    )

    assert result.error is None
    assert result.target_object is None
    assert result.reference_count == 2
    assert result.assembled_target_scope is not None
    assert result.assembled_target_scope.scope_kind == "scene"
    assert result.assembled_target_scope.object_names == []
    assert result.truth_bundle is not None
    assert result.truth_bundle.summary.pairing_strategy == "none"
    assert result.truth_followup is not None
    assert result.truth_followup.continue_recommended is False
    assert captured["request"].target_object is None


def test_reference_compare_stage_checkpoint_can_expand_collection_scope(tmp_path, monkeypatch):
    image_front = tmp_path / "front.png"
    image_side = tmp_path / "side.png"
    image_front.write_bytes(b"front")
    image_side.write_bytes(b"side")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(reference_images(ctx, action="attach", source_path=str(image_front), label="front_ref"))
    asyncio.run(reference_images(ctx, action="attach", source_path=str(image_side), label="side_ref"))

    captured = {}

    class CollectionHandler:
        def list_objects(self, collection_name: str, recursive: bool = True, include_hidden: bool = False):
            assert collection_name == "Squirrel"
            return {
                "objects": [
                    {"name": "Squirrel_Head"},
                    {"name": "Squirrel_Body"},
                    {"name": "Squirrel_Tail"},
                ]
            }

    class SceneHandler:
        def measure_gap(self, from_object: str, to_object: str, tolerance: float = 0.0001):
            return {"from_object": from_object, "to_object": to_object, "relation": "separated", "gap": 0.05}

        def measure_alignment(self, from_object: str, to_object: str, axes=None, reference="CENTER", tolerance=0.0001):
            return {
                "from_object": from_object,
                "to_object": to_object,
                "is_aligned": False,
                "axes": axes or ["X", "Y", "Z"],
            }

        def measure_overlap(self, from_object: str, to_object: str, tolerance: float = 0.0001):
            return {"from_object": from_object, "to_object": to_object, "overlaps": False, "relation": "disjoint"}

        def assert_contact(
            self, from_object: str, to_object: str, max_gap: float = 0.0001, allow_overlap: bool = False
        ):
            return {
                "assertion": "scene_assert_contact",
                "passed": False,
                "subject": from_object,
                "target": to_object,
                "expected": {"max_gap": max_gap, "allow_overlap": allow_overlap},
                "actual": {"gap": 0.05, "relation": "separated"},
            }

    async def _fake_run_vision_assist(ctx, *, request, resolver):
        captured["request"] = request
        return AssistantRunResult(
            status="success",
            assistant_name="vision_assist",
            message="ok",
            budget=AssistantBudgetContract(max_input_chars=1000, max_messages=1, max_tokens=100, tool_budget=0),
            capability_source="local_runtime",
            result=VisionAssistContract(
                backend_kind="mlx_local",
                model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                goal_summary="The squirrel collection is closer to the references.",
                visible_changes=["The full squirrel silhouette is visible."],
                correction_focus=["Tail/body ratio"],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_collection_handler", lambda: CollectionHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_collection_handler", lambda: CollectionHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.capture_stage_images",
        lambda *args, **kwargs: [
            VisionCaptureImageContract(
                label="context_wide_after",
                image_path=str(tmp_path / "context.jpg"),
                host_visible_path=str(tmp_path / "context.jpg"),
                preset_name="context_wide",
                media_type="image/jpeg",
                view_kind="wide",
            ),
        ],
    )

    result = asyncio.run(
        reference_compare_stage_checkpoint(
            ctx,
            collection_name="Squirrel",
            checkpoint_label="stage_full_collection",
            preset_profile="compact",
        )
    )

    assert result.error is None
    assert result.collection_name == "Squirrel"
    assert result.target_objects == ["Squirrel_Head", "Squirrel_Body", "Squirrel_Tail"]
    assert result.assembled_target_scope is not None
    assert result.assembled_target_scope.scope_kind == "collection"
    assert result.assembled_target_scope.collection_name == "Squirrel"
    assert result.assembled_target_scope.object_count == 3
    assert result.truth_bundle is not None
    assert result.truth_bundle.summary.pairing_strategy == "primary_to_others"
    assert result.truth_bundle.summary.pair_count == 2
    assert result.truth_followup is not None
    assert result.truth_followup.continue_recommended is True
    assert result.truth_followup.focus_pairs == [
        "Squirrel_Head -> Squirrel_Body",
        "Squirrel_Head -> Squirrel_Tail",
    ]
    assert result.truth_followup.macro_candidates
    assert result.truth_followup.macro_candidates[0].macro_name == "macro_align_part_with_contact"
    assert result.correction_candidates
    assert result.correction_candidates[0].priority_rank == 1
    assert result.correction_candidates[0].candidate_kind == "truth_only"
    assert result.correction_candidates[0].truth_evidence is not None
    assert captured["request"].truth_summary["summary"]["pair_count"] == 2
    assert captured["request"].metadata["collection_name"] == "Squirrel"


def test_reference_compare_stage_checkpoint_can_track_explicit_object_set_scope(tmp_path, monkeypatch):
    image_front = tmp_path / "front.png"
    image_front.write_bytes(b"front")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(reference_images(ctx, action="attach", source_path=str(image_front), label="front_ref"))

    class CollectionHandler:
        def list_objects(self, collection_name: str, recursive: bool = True, include_hidden: bool = False):
            return {"objects": []}

    class SceneHandler:
        def measure_gap(self, from_object: str, to_object: str, tolerance: float = 0.0001):
            return {"from_object": from_object, "to_object": to_object, "relation": "contact", "gap": 0.0}

        def measure_alignment(self, from_object: str, to_object: str, axes=None, reference="CENTER", tolerance=0.0001):
            return {
                "from_object": from_object,
                "to_object": to_object,
                "is_aligned": True,
                "axes": axes or ["X", "Y", "Z"],
            }

        def measure_overlap(self, from_object: str, to_object: str, tolerance: float = 0.0001):
            return {"from_object": from_object, "to_object": to_object, "overlaps": False, "relation": "disjoint"}

        def assert_contact(
            self, from_object: str, to_object: str, max_gap: float = 0.0001, allow_overlap: bool = False
        ):
            return {
                "assertion": "scene_assert_contact",
                "passed": True,
                "subject": from_object,
                "target": to_object,
                "expected": {"max_gap": max_gap, "allow_overlap": allow_overlap},
                "actual": {"gap": 0.0, "relation": "contact"},
            }

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
                goal_summary="ok",
                visible_changes=[],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_collection_handler", lambda: CollectionHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.capture_stage_images",
        lambda *args, **kwargs: [
            VisionCaptureImageContract(
                label="context_wide_after",
                image_path=str(tmp_path / "context.jpg"),
                host_visible_path=str(tmp_path / "context.jpg"),
                preset_name="context_wide",
                media_type="image/jpeg",
                view_kind="wide",
            ),
        ],
    )

    result = asyncio.run(
        reference_compare_stage_checkpoint(
            ctx,
            target_objects=["Squirrel_Head", "Squirrel_Tail"],
            checkpoint_label="stage_object_set",
            preset_profile="compact",
        )
    )

    assert result.error is None
    assert result.target_object is None
    assert result.target_objects == ["Squirrel_Head", "Squirrel_Tail"]
    assert result.assembled_target_scope is not None
    assert result.assembled_target_scope.scope_kind == "object_set"
    assert result.assembled_target_scope.object_names == ["Squirrel_Head", "Squirrel_Tail"]
    assert result.assembled_target_scope.object_count == 2
    assert result.truth_bundle is not None
    assert result.truth_bundle.summary.pairing_strategy == "primary_to_others"
    assert result.truth_bundle.summary.pair_count == 1
    assert result.truth_followup is not None
    assert result.truth_followup.continue_recommended is False
    assert result.correction_candidates == []


def test_reference_compare_stage_checkpoint_trims_truth_bundle_for_low_budget(tmp_path, monkeypatch):
    image_front = tmp_path / "front.png"
    image_front.write_bytes(b"front")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(reference_images(ctx, action="attach", source_path=str(image_front), label="front_ref"))

    class CollectionHandler:
        def list_objects(self, collection_name: str, recursive: bool = True, include_hidden: bool = False):
            assert collection_name == "Squirrel"
            return {
                "objects": [
                    {"name": "Body"},
                    {"name": "Head"},
                    {"name": "Tail"},
                    {"name": "BackPawLeft"},
                    {"name": "BackPawRight"},
                ]
            }

    class SceneHandler:
        def get_bounding_box(self, object_name: str, world_space: bool = True):
            dimensions = {
                "Body": [1.2, 0.9, 1.0],
                "Head": [0.7, 0.7, 0.8],
                "Tail": [0.5, 0.3, 1.1],
                "BackPawLeft": [0.2, 0.2, 0.25],
                "BackPawRight": [0.2, 0.2, 0.25],
            }[object_name]
            return {"object_name": object_name, "dimensions": dimensions}

        def measure_gap(self, from_object: str, to_object: str, tolerance: float = 0.0001):
            relation_map = {
                ("Body", "Head"): ("contact", 0.0),
                ("Body", "Tail"): ("overlapping", 0.0),
                ("Body", "BackPawLeft"): ("separated", 0.18),
                ("Body", "BackPawRight"): ("separated", 0.19),
            }
            relation, gap = relation_map[(from_object, to_object)]
            return {
                "from_object": from_object,
                "to_object": to_object,
                "relation": relation,
                "gap": gap,
                "axis_gap": {"x": gap, "y": 0.0, "z": 0.0},
            }

        def measure_alignment(self, from_object: str, to_object: str, axes=None, reference="CENTER", tolerance=0.0001):
            misaligned = (from_object, to_object) in {
                ("Body", "BackPawLeft"),
                ("Body", "BackPawRight"),
            }
            return {
                "from_object": from_object,
                "to_object": to_object,
                "is_aligned": not misaligned,
                "axes": axes or ["X", "Y", "Z"],
            }

        def measure_overlap(self, from_object: str, to_object: str, tolerance: float = 0.0001):
            overlaps = (from_object, to_object) == ("Body", "Tail")
            return {
                "from_object": from_object,
                "to_object": to_object,
                "overlaps": overlaps,
                "relation": "overlap" if overlaps else "disjoint",
            }

        def assert_contact(
            self, from_object: str, to_object: str, max_gap: float = 0.0001, allow_overlap: bool = False
        ):
            passed = (from_object, to_object) == ("Body", "Head")
            return {
                "assertion": "scene_assert_contact",
                "passed": passed,
                "subject": from_object,
                "target": to_object,
                "expected": {"max_gap": max_gap, "allow_overlap": allow_overlap},
                "actual": {"gap": 0.0 if passed else 0.18, "relation": "contact" if passed else "separated"},
            }

    captured = {}

    async def _fake_run_vision_assist(ctx, *, request, resolver):
        captured["request"] = request
        return AssistantRunResult(
            status="success",
            assistant_name="vision_assist",
            message="ok",
            budget=AssistantBudgetContract(max_input_chars=1000, max_messages=1, max_tokens=100, tool_budget=0),
            capability_source="local_runtime",
            result=VisionAssistContract(
                backend_kind="mlx_local",
                model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                goal_summary="The body still needs contact fixes.",
                visible_changes=["Rear paws are visible."],
                correction_focus=["Connect rear paws to body"],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_collection_handler", lambda: CollectionHandler())
    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.get_vision_backend_resolver",
        lambda: SimpleNamespace(
            runtime_config=SimpleNamespace(
                max_tokens=200,
                max_images=8,
                active_model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
            )
        ),
    )
    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.capture_stage_images",
        lambda *args, **kwargs: [
            VisionCaptureImageContract(
                label="context_wide_after",
                image_path=str(tmp_path / "context.jpg"),
                host_visible_path=str(tmp_path / "context.jpg"),
                preset_name="context_wide",
                media_type="image/jpeg",
                view_kind="wide",
            ),
        ],
    )

    result = asyncio.run(
        reference_compare_stage_checkpoint(
            ctx,
            collection_name="Squirrel",
            checkpoint_label="stage_budgeted",
            preset_profile="compact",
        )
    )

    assert result.budget_control is not None
    assert result.budget_control.trimming_applied is True
    assert result.budget_control.scope_trimmed is True
    assert result.budget_control.model_name == "mlx-community/Qwen3-VL-4B-Instruct-4bit"
    assert result.budget_control.original_pair_count == 4
    assert result.budget_control.emitted_pair_count == 2
    assert result.truth_bundle is not None
    assert result.truth_bundle.summary.pair_count == 2
    assert captured["request"].truth_summary["summary"]["pair_count"] == 2


def test_reference_compare_stage_checkpoint_sanitizes_checkpoint_id_target_token(tmp_path, monkeypatch):
    image_front = tmp_path / "front.png"
    image_front.write_bytes(b"front")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(reference_images(ctx, action="attach", source_path=str(image_front), label="front_ref"))

    class SceneHandler:
        pass

    class CollectionHandler:
        def list_objects(self, collection_name: str, recursive: bool = True, include_hidden: bool = False):
            return {"objects": []}

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
                goal_summary="ok",
                visible_changes=[],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_collection_handler", lambda: CollectionHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.get_vision_backend_resolver", lambda: object())
    monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.capture_stage_images",
        lambda *args, **kwargs: [
            VisionCaptureImageContract(
                label="context_wide_after",
                image_path=str(tmp_path / "context.jpg"),
                host_visible_path=str(tmp_path / "context.jpg"),
                preset_name="context_wide",
                media_type="image/jpeg",
                view_kind="wide",
            ),
        ],
    )

    result = asyncio.run(
        reference_compare_stage_checkpoint(
            ctx,
            collection_name="Squirrel/Head",
            checkpoint_label="unsafe_target",
            preset_profile="compact",
        )
    )

    assert result.error is None
    assert "/" not in result.checkpoint_id
    assert "\\" not in result.checkpoint_id
    assert "Squirrel_Head" in result.checkpoint_id


def test_reference_iterate_stage_checkpoint_tracks_previous_focus_and_iteration(tmp_path, monkeypatch):
    image_front = tmp_path / "front.png"
    image_side = tmp_path / "side.png"
    image_front.write_bytes(b"front")
    image_side.write_bytes(b"side")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image_front),
            label="front_ref",
            target_object="Squirrel",
            target_view="front",
        )
    )
    asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image_side),
            label="side_ref",
            target_object="Squirrel",
            target_view="side",
        )
    )

    # use the public helper via monkeypatching the internal compare call site
    first_compare = ReferenceCompareStageCheckpointResponseContract.model_validate(
        {
            "action": "compare_stage_checkpoint",
            "session_id": "sess_test",
            "transport": "stdio",
            "goal": "low poly squirrel",
            "target_object": "Squirrel",
            "checkpoint_id": "checkpoint_1",
            "checkpoint_label": "stage_1",
            "preset_profile": "compact",
            "preset_names": ["context_wide", "target_front"],
            "capture_count": 2,
            "captures": [],
            "reference_count": 2,
            "reference_ids": ["ref_1", "ref_2"],
            "reference_labels": ["front_ref", "side_ref"],
            "correction_candidates": [
                {
                    "candidate_id": "vision:head_silhouette",
                    "summary": "Head silhouette",
                    "priority_rank": 1,
                    "priority": "normal",
                    "candidate_kind": "vision_only",
                    "target_object": "Squirrel",
                    "target_objects": ["Squirrel"],
                    "focus_pairs": [],
                    "source_signals": ["vision"],
                    "vision_evidence": {
                        "correction_focus": ["Head silhouette"],
                        "shape_mismatches": ["Head silhouette is still too spherical."],
                        "proportion_mismatches": [],
                        "next_corrections": ["Flatten the head silhouette slightly."],
                    },
                }
            ],
            "vision_assistant": {
                "status": "success",
                "assistant_name": "vision_assist",
                "message": "ok",
                "budget": {"max_input_chars": 1000, "max_messages": 1, "max_tokens": 100, "tool_budget": 0},
                "capability_source": "local_runtime",
                "result": {
                    "backend_kind": "mlx_local",
                    "goal_summary": "Closer to the squirrel reference.",
                    "visible_changes": ["Tail arc is larger."],
                    "shape_mismatches": ["Head silhouette is still too spherical."],
                    "proportion_mismatches": [],
                    "correction_focus": ["Head silhouette"],
                    "next_corrections": ["Flatten the head silhouette slightly."],
                    "likely_issues": [],
                    "recommended_checks": [],
                    "captures_used": ["target_front_after"],
                },
            },
        }
    )
    second_compare = ReferenceCompareStageCheckpointResponseContract.model_validate(
        {
            **first_compare.model_dump(mode="json"),
            "checkpoint_id": "checkpoint_2",
            "checkpoint_label": "stage_2",
            "vision_assistant": {
                **first_compare.vision_assistant.model_dump(mode="json"),
                "result": {
                    **first_compare.vision_assistant.result.model_dump(mode="json"),
                    "correction_focus": ["Head silhouette", "Tail/body ratio"],
                },
            },
        }
    )
    compares = [first_compare, second_compare]

    async def _fake_reference_compare_stage_checkpoint(*args, **kwargs):
        return compares.pop(0)

    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.reference_compare_stage_checkpoint",
        _fake_reference_compare_stage_checkpoint,
    )

    first = asyncio.run(
        reference_iterate_stage_checkpoint(
            ctx,
            target_object="Squirrel",
            checkpoint_label="stage_1",
        )
    )
    second = asyncio.run(
        reference_iterate_stage_checkpoint(
            ctx,
            target_object="Squirrel",
            checkpoint_label="stage_2",
        )
    )

    assert first.session_id == "sess_test"
    assert first.transport == "stdio"
    assert first.iteration_index == 1
    assert first.loop_disposition == "continue_build"
    assert first.prior_correction_focus == []
    assert first.correction_candidates
    assert first.correction_candidates[0].summary == "Head silhouette"
    assert second.iteration_index == 2
    assert second.prior_checkpoint_id == "checkpoint_1"
    assert second.prior_correction_focus == ["Head silhouette"]
    assert second.repeated_correction_focus == ["Head silhouette"]
    assert second.loop_disposition == "continue_build"


def test_reference_iterate_stage_checkpoint_escalates_after_repeated_focus(monkeypatch):
    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})

    compare = ReferenceCompareStageCheckpointResponseContract.model_validate(
        {
            "action": "compare_stage_checkpoint",
            "goal": "low poly squirrel",
            "target_object": "Squirrel",
            "checkpoint_id": "checkpoint_repeat",
            "checkpoint_label": "stage_repeat",
            "preset_profile": "compact",
            "preset_names": ["context_wide"],
            "capture_count": 1,
            "captures": [],
            "reference_count": 0,
            "reference_ids": [],
            "reference_labels": [],
            "vision_assistant": {
                "status": "success",
                "assistant_name": "vision_assist",
                "message": "ok",
                "budget": {"max_input_chars": 1000, "max_messages": 1, "max_tokens": 100, "tool_budget": 0},
                "capability_source": "local_runtime",
                "result": {
                    "backend_kind": "mlx_local",
                    "goal_summary": "Still off from the squirrel reference.",
                    "visible_changes": ["The body is a bit fuller."],
                    "shape_mismatches": ["Head silhouette is still too spherical."],
                    "proportion_mismatches": [],
                    "correction_focus": ["Head silhouette"],
                    "next_corrections": ["Flatten the head silhouette slightly."],
                    "likely_issues": [],
                    "recommended_checks": [],
                    "captures_used": ["target_front_after"],
                },
            },
        }
    )

    async def _fake_reference_compare_stage_checkpoint(*args, **kwargs):
        return compare

    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.reference_compare_stage_checkpoint",
        _fake_reference_compare_stage_checkpoint,
    )

    first = asyncio.run(reference_iterate_stage_checkpoint(ctx, target_object="Squirrel", checkpoint_label="stage_1"))
    second = asyncio.run(reference_iterate_stage_checkpoint(ctx, target_object="Squirrel", checkpoint_label="stage_2"))
    third = asyncio.run(reference_iterate_stage_checkpoint(ctx, target_object="Squirrel", checkpoint_label="stage_3"))

    assert first.loop_disposition == "continue_build"
    assert second.loop_disposition == "continue_build"
    assert third.loop_disposition == "inspect_validate"
    assert third.stagnation_count >= 2


def test_reference_iterate_stage_checkpoint_uses_truth_integrated_candidates_for_focus(monkeypatch):
    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly creature", {"status": "no_match"})

    compare = ReferenceCompareStageCheckpointResponseContract.model_validate(
        {
            "action": "compare_stage_checkpoint",
            "goal": "low poly creature",
            "target_object": "TruthHead",
            "target_objects": ["TruthHead", "TruthBody"],
            "checkpoint_id": "checkpoint_truth_only",
            "checkpoint_label": "stage_truth_only",
            "preset_profile": "compact",
            "preset_names": ["context_wide"],
            "capture_count": 1,
            "captures": [],
            "reference_count": 0,
            "reference_ids": [],
            "reference_labels": [],
            "truth_followup": {
                "scope": {
                    "scope_kind": "object_set",
                    "primary_target": "TruthHead",
                    "object_names": ["TruthHead", "TruthBody"],
                    "object_count": 2,
                },
                "continue_recommended": True,
                "message": "truth",
                "focus_pairs": ["TruthHead -> TruthBody"],
                "items": [
                    {
                        "kind": "gap",
                        "summary": "TruthHead -> TruthBody still has measurable separation.",
                        "priority": "normal",
                        "from_object": "TruthHead",
                        "to_object": "TruthBody",
                        "tool_name": "scene_measure_gap",
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
            "correction_candidates": [
                {
                    "candidate_id": "pair:truthhead_truthbody",
                    "summary": "TruthHead -> TruthBody still has measurable separation.",
                    "priority_rank": 1,
                    "priority": "high",
                    "candidate_kind": "truth_only",
                    "target_object": "TruthHead",
                    "target_objects": ["TruthHead", "TruthBody"],
                    "focus_pairs": ["TruthHead -> TruthBody"],
                    "source_signals": ["truth", "macro"],
                    "truth_evidence": {
                        "focus_pairs": ["TruthHead -> TruthBody"],
                        "item_kinds": ["gap"],
                        "items": [
                            {
                                "kind": "gap",
                                "summary": "TruthHead -> TruthBody still has measurable separation.",
                                "priority": "normal",
                                "from_object": "TruthHead",
                                "to_object": "TruthBody",
                                "tool_name": "scene_measure_gap",
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
            "budget_control": {
                "model_name": "mlx-community/Qwen3-VL-4B-Instruct-4bit",
                "max_input_chars": 12000,
                "max_output_tokens": 400,
                "max_images": 8,
                "original_pair_count": 1,
                "emitted_pair_count": 1,
                "original_candidate_count": 1,
                "emitted_candidate_count": 1,
                "trimming_applied": False,
                "scope_trimmed": False,
                "detail_trimmed": False,
                "selected_focus_pairs": ["TruthHead -> TruthBody"],
            },
        }
    )

    async def _fake_reference_compare_stage_checkpoint(*args, **kwargs):
        return compare

    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.reference_compare_stage_checkpoint",
        _fake_reference_compare_stage_checkpoint,
    )

    result = asyncio.run(
        reference_iterate_stage_checkpoint(
            ctx,
            target_object="TruthHead",
            target_objects=["TruthBody"],
            checkpoint_label="stage_truth_only",
        )
    )

    assert result.correction_focus == ["TruthHead -> TruthBody still has measurable separation."]
    assert result.loop_disposition == "continue_build"
    assert result.correction_candidates
    assert result.correction_candidates[0].candidate_kind == "truth_only"
    assert result.budget_control is not None
    assert result.budget_control.selected_focus_pairs == ["TruthHead -> TruthBody"]


def test_reference_iterate_stage_checkpoint_escalates_when_truth_signal_is_high_priority(monkeypatch):
    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly creature", {"status": "no_match"})

    compare = ReferenceCompareStageCheckpointResponseContract.model_validate(
        {
            "action": "compare_stage_checkpoint",
            "goal": "low poly creature",
            "target_object": "TruthHead",
            "target_objects": ["TruthHead", "TruthBody"],
            "checkpoint_id": "checkpoint_truth_inspect",
            "checkpoint_label": "stage_truth_inspect",
            "preset_profile": "compact",
            "preset_names": ["context_wide"],
            "capture_count": 1,
            "captures": [],
            "reference_count": 0,
            "reference_ids": [],
            "reference_labels": [],
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

    async def _fake_reference_compare_stage_checkpoint(*args, **kwargs):
        return compare

    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.reference_compare_stage_checkpoint",
        _fake_reference_compare_stage_checkpoint,
    )

    result = asyncio.run(
        reference_iterate_stage_checkpoint(
            ctx,
            target_object="TruthHead",
            target_objects=["TruthBody"],
            checkpoint_label="stage_truth_inspect",
        )
    )

    assert result.loop_disposition == "inspect_validate"
    assert result.correction_focus == ["TruthHead -> TruthBody failed the contact assertion."]
    assert "Deterministic truth findings remain high-priority" in (result.message or "")


def test_reference_iterate_stage_checkpoint_does_not_reuse_state_across_target_view_or_profile(monkeypatch):
    ctx = FakeContext()
    update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})

    compare = ReferenceCompareStageCheckpointResponseContract.model_validate(
        {
            "action": "compare_stage_checkpoint",
            "goal": "low poly squirrel",
            "target_object": "Squirrel",
            "target_view": "front",
            "checkpoint_id": "checkpoint_front",
            "checkpoint_label": "stage_front",
            "preset_profile": "compact",
            "preset_names": ["context_wide"],
            "capture_count": 1,
            "captures": [],
            "reference_count": 0,
            "reference_ids": [],
            "reference_labels": [],
            "vision_assistant": {
                "status": "success",
                "assistant_name": "vision_assist",
                "message": "ok",
                "budget": {"max_input_chars": 1000, "max_messages": 1, "max_tokens": 100, "tool_budget": 0},
                "capability_source": "local_runtime",
                "result": {
                    "backend_kind": "mlx_local",
                    "goal_summary": "Still off from the squirrel reference.",
                    "visible_changes": ["The head is visible."],
                    "shape_mismatches": ["Head silhouette is still too spherical."],
                    "proportion_mismatches": [],
                    "correction_focus": ["Head silhouette"],
                    "next_corrections": ["Flatten the head silhouette slightly."],
                    "likely_issues": [],
                    "recommended_checks": [],
                    "captures_used": ["target_front_after"],
                },
            },
        }
    )
    compare_side = ReferenceCompareStageCheckpointResponseContract.model_validate(
        {
            **compare.model_dump(mode="json"),
            "checkpoint_id": "checkpoint_side",
            "checkpoint_label": "stage_side",
            "target_view": "side",
        }
    )

    compares = [compare, compare_side]

    async def _fake_reference_compare_stage_checkpoint(*args, **kwargs):
        return compares.pop(0)

    monkeypatch.setattr(
        "server.adapters.mcp.areas.reference.reference_compare_stage_checkpoint",
        _fake_reference_compare_stage_checkpoint,
    )

    first = asyncio.run(
        reference_iterate_stage_checkpoint(
            ctx,
            target_object="Squirrel",
            checkpoint_label="stage_front",
            target_view="front",
            preset_profile="compact",
        )
    )
    second = asyncio.run(
        reference_iterate_stage_checkpoint(
            ctx,
            target_object="Squirrel",
            checkpoint_label="stage_side",
            target_view="side",
            preset_profile="compact",
        )
    )

    assert first.iteration_index == 1
    assert second.iteration_index == 1
    assert second.prior_correction_focus == []
    assert second.repeated_correction_focus == []
