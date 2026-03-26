"""Tests for goal-scoped reference images in macro vision attachment."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract
from server.adapters.mcp.contracts.vision import (
    VisionCaptureBundleContract,
    VisionCaptureImageContract,
)
from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantRunResult,
    VisionAssistContract,
)
from server.adapters.mcp.vision.integration import maybe_attach_macro_vision


def _report() -> MacroExecutionReportContract:
    return MacroExecutionReportContract(
        status="success",
        macro_name="macro_finish_form",
        intent="apply rounded housing finish",
        actions_taken=[],
        capture_bundle=VisionCaptureBundleContract(
            bundle_id="bundle_1",
            target_object="Housing",
            preset_names=["context_wide", "target_focus"],
            captures_before=[
                VisionCaptureImageContract(label="before", image_path="/tmp/before.jpg", media_type="image/jpeg")
            ],
            captures_after=[
                VisionCaptureImageContract(label="after", image_path="/tmp/after.jpg", media_type="image/jpeg")
            ],
        ),
    )


class _Ctx:
    def __init__(self) -> None:
        self.state = {
            "goal": "rounded housing",
            "reference_images": [
                {
                    "reference_id": "ref_1",
                    "goal": "rounded housing",
                    "label": "front_reference",
                    "media_type": "image/png",
                    "source_kind": "local_path",
                    "original_path": "/tmp/ref.png",
                    "stored_path": "/tmp/ref_stored.png",
                    "added_at": "2026-03-26T00:00:00Z",
                }
            ],
        }

    def get_state(self, key):
        return self.state.get(key)

    def set_state(self, key, value, *, serializable=True):
        self.state[key] = value


def test_maybe_attach_macro_vision_uses_goal_scoped_reference_images(monkeypatch):
    captured = {}

    async def _fake_run_vision_assist(ctx, *, request, resolver):
        captured["request"] = request
        return AssistantRunResult(
            status="success",
            assistant_name="vision_assist",
            message="ok",
            budget=AssistantBudgetContract(max_input_chars=1000, max_messages=1, max_tokens=100, tool_budget=0),
            capability_source="external_runtime",
            result=VisionAssistContract(
                backend_kind="openai_compatible_external",
                model_name="gemma-3-27b-vision",
                goal_summary="Closer to the goal.",
                visible_changes=["Front silhouette changed."],
            ),
        )

    monkeypatch.setattr("server.adapters.mcp.vision.integration.run_vision_assist", _fake_run_vision_assist)
    monkeypatch.setattr("server.adapters.mcp.vision.integration.get_vision_backend_resolver", lambda: MagicMock())

    result = asyncio.run(maybe_attach_macro_vision(_Ctx(), _report()))

    assert result.vision_assistant is not None
    assert captured["request"].goal == "rounded housing"
    assert [image.role for image in captured["request"].images] == ["before", "after", "reference"]
    assert "front_reference" in (captured["request"].prompt_hint or "")
