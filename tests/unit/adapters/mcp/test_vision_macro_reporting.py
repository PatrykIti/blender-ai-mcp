"""Tests for attaching capture/vision artifacts to macro reports."""

from __future__ import annotations

from server.adapters.mcp.contracts.macro import (
    MacroActionRecordContract,
    MacroExecutionReportContract,
)
from server.adapters.mcp.contracts.vision import (
    VisionCaptureBundleContract,
    VisionCaptureImageContract,
)
from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantRunResult,
    VisionAssistContract,
    to_vision_assistant_contract,
)
from server.adapters.mcp.vision import attach_vision_artifacts


def test_attach_vision_artifacts_enriches_macro_report():
    report = MacroExecutionReportContract(
        status="success",
        macro_name="macro_finish_form",
        actions_taken=[
            MacroActionRecordContract(
                status="applied",
                action="add_bevel_finish",
                tool_name="modeling_add_modifier",
            )
        ],
    )
    bundle = VisionCaptureBundleContract(
        bundle_id="bundle_1",
        target_object="Housing",
        preset_names=["context_wide", "target_focus"],
        captures_before=[
            VisionCaptureImageContract(label="context_wide_before", image_path="/tmp/before.jpg", media_type="image/jpeg")
        ],
        captures_after=[
            VisionCaptureImageContract(label="context_wide_after", image_path="/tmp/after.jpg", media_type="image/jpeg")
        ],
    )
    vision_assistant = to_vision_assistant_contract(
        AssistantRunResult(
            status="success",
            assistant_name="vision_assist",
            message="ok",
            budget=AssistantBudgetContract(max_input_chars=1000, max_messages=1, max_tokens=100, tool_budget=0),
            capability_source="external_runtime",
            result=VisionAssistContract(
                backend_kind="openai_compatible_external",
                model_name="gemma-3-27b-vision",
                goal_summary="Closer to the reference silhouette.",
                visible_changes=["Front profile is softer."],
                shape_mismatches=["Front silhouette still looks too boxy."],
                next_corrections=["Round the front silhouette more aggressively."],
            ),
        )
    )

    enriched = attach_vision_artifacts(
        report,
        capture_bundle=bundle,
        vision_assistant=vision_assistant,
    )

    assert enriched.capture_bundle is not None
    assert enriched.capture_bundle.bundle_id == "bundle_1"
    assert enriched.vision_assistant is not None
    assert enriched.vision_assistant.result is not None
    assert enriched.vision_assistant.result.backend_kind == "openai_compatible_external"
    assert enriched.requires_followup is True
    assert enriched.verification_recommended is not None
    assert any(item.tool_name == "inspect_scene" for item in enriched.verification_recommended)
