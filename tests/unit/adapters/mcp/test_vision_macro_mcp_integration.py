"""Tests for attaching bounded vision output on macro MCP paths."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

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


def _capture_bundle() -> dict:
    return VisionCaptureBundleContract(
        bundle_id="bundle_1",
        target_object="Housing",
        preset_names=["context_wide", "target_focus"],
        captures_before=[
            VisionCaptureImageContract(label="context_wide_before", image_path="/tmp/before.jpg", media_type="image/jpeg")
        ],
        captures_after=[
            VisionCaptureImageContract(label="context_wide_after", image_path="/tmp/after.jpg", media_type="image/jpeg")
        ],
    ).model_dump(exclude_none=True)


def _vision_contract():
    return to_vision_assistant_contract(
        AssistantRunResult(
            status="success",
            assistant_name="vision_assist",
            message="ok",
            budget=AssistantBudgetContract(max_input_chars=1000, max_messages=1, max_tokens=100, tool_budget=0),
            capability_source="external_runtime",
            result=VisionAssistContract(
                backend_kind="openai_compatible_external",
                model_name="gemma-3-27b-vision",
                goal_summary="Closer to the target.",
                visible_changes=["Front profile changed."],
            ),
        )
    )


def test_macro_finish_form_mcp_can_attach_vision_assistant(monkeypatch):
    from server.adapters.mcp.areas.modeling import _macro_finish_form_impl

    class Handler:
        def finish_form(self, **kwargs):
            return {
                "status": "success",
                "macro_name": "macro_finish_form",
                "actions_taken": [{"status": "applied", "action": "add_bevel_finish"}],
                "capture_bundle": _capture_bundle(),
            }

    captured = {}

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_macro_handler", lambda: Handler())
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling._resolve_macro_capture_profile",
        lambda ctx: asyncio.sleep(0, result="compact"),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.maybe_attach_macro_vision",
        lambda ctx, report: asyncio.sleep(
            0,
            result=report.model_copy(update={"vision_assistant": _vision_contract()}),
        ),
    )

    result = asyncio.run(_macro_finish_form_impl(MagicMock(), target_object="Housing"))

    assert result.capture_bundle is not None
    assert result.vision_assistant is not None
    assert result.vision_assistant.result is not None
    assert result.vision_assistant.result.backend_kind == "openai_compatible_external"


def test_macro_finish_form_mcp_passes_capture_profile_into_handler(monkeypatch):
    from server.adapters.mcp.areas.modeling import _macro_finish_form_impl

    observed = {}

    class Handler:
        def finish_form(self, **kwargs):
            observed.update(kwargs)
            return {
                "status": "success",
                "macro_name": "macro_finish_form",
                "actions_taken": [{"status": "applied", "action": "add_bevel_finish"}],
            }

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_macro_handler", lambda: Handler())
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling._resolve_macro_capture_profile",
        lambda ctx: asyncio.sleep(0, result="rich"),
    )

    result = asyncio.run(_macro_finish_form_impl(MagicMock(), target_object="Housing"))

    assert result.status == "success"
    assert observed["capture_profile"] == "rich"


def test_macro_relative_layout_mcp_can_attach_vision_assistant(monkeypatch):
    from server.adapters.mcp.areas.scene import macro_relative_layout

    class Handler:
        def relative_layout(self, **kwargs):
            return {
                "status": "success",
                "macro_name": "macro_relative_layout",
                "actions_taken": [{"status": "applied", "action": "apply_relative_layout"}],
                "capture_bundle": _capture_bundle(),
            }

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: Handler())
    monkeypatch.setattr(
        "server.adapters.mcp.areas.scene._resolve_macro_capture_profile",
        lambda ctx: asyncio.sleep(0, result="compact"),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.scene.maybe_attach_macro_vision",
        lambda ctx, report: asyncio.sleep(0, result=report.model_copy(update={"vision_assistant": _vision_contract()})),
    )

    result = asyncio.run(macro_relative_layout(MagicMock(), moving_object="Panel", reference_object="Housing"))

    assert result.capture_bundle is not None
    assert result.vision_assistant is not None
    assert result.vision_assistant.result is not None
    assert result.vision_assistant.result.backend_kind == "openai_compatible_external"
