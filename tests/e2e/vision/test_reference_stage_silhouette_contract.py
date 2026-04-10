"""E2E-style staged reference coverage for deterministic silhouette/action-hint payloads."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image, ImageDraw
from server.adapters.mcp.areas.reference import (
    reference_compare_stage_checkpoint,
    reference_images,
    reference_iterate_stage_checkpoint,
)
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantRunResult,
    VisionAssistContract,
)
from server.adapters.mcp.session_capabilities import update_session_from_router_goal

pytestmark = pytest.mark.e2e


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


def _write_creature_silhouette(path: Path, *, with_ears: bool) -> None:
    image = Image.new("RGBA", (220, 220), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((70, 70, 150, 190), fill=(0, 0, 0, 255))
    if with_ears:
        draw.polygon([(78, 70), (95, 22), (112, 70)], fill=(0, 0, 0, 255))
        draw.polygon([(108, 70), (125, 22), (142, 70)], fill=(0, 0, 0, 255))
    image.save(path)


def test_reference_stage_compare_and_iterate_expose_silhouette_metrics_and_action_hints(tmp_path, monkeypatch):
    reference_path = tmp_path / "reference_front.png"
    capture_path = tmp_path / "capture_front.png"
    _write_creature_silhouette(reference_path, with_ears=True)
    _write_creature_silhouette(capture_path, with_ears=False)

    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(
        ctx,
        "create a low-poly creature matching front and side reference images",
        {"status": "no_match"},
    )
    asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(reference_path),
            label="front_ref",
            target_object="Creature",
            target_view="front",
        )
    )

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
                goal_summary="The creature still needs upper silhouette corrections.",
                visible_changes=["The front creature profile is visible."],
                shape_mismatches=["The ears are still missing from the silhouette."],
                correction_focus=[],
                next_corrections=["Build the upper silhouette before detail cleanup."],
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
                label="target_front_after",
                image_path=str(capture_path),
                host_visible_path=str(capture_path),
                preset_name="target_front",
                media_type="image/png",
                view_kind="focus",
            )
        ],
    )

    compare_result = asyncio.run(
        reference_compare_stage_checkpoint(
            ctx,
            target_object="Creature",
            checkpoint_label="stage_ears",
            target_view="front",
            preset_profile="compact",
        )
    )

    assert compare_result.error is None
    assert compare_result.silhouette_analysis is not None
    assert compare_result.silhouette_analysis.status == "available"
    assert any(metric.metric_id == "upper_band_width_delta" for metric in compare_result.silhouette_analysis.metrics)
    assert compare_result.action_hints
    assert any(hint.hint_type == "widen_upper_profile" for hint in compare_result.action_hints)
    assert compare_result.part_segmentation is not None
    assert compare_result.part_segmentation.status == "disabled"

    iterate_result = asyncio.run(
        reference_iterate_stage_checkpoint(
            ctx,
            target_object="Creature",
            checkpoint_label="stage_ears_iterate",
            target_view="front",
            preset_profile="compact",
        )
    )

    assert iterate_result.error is None
    assert iterate_result.continue_recommended is True
    assert iterate_result.loop_disposition == "continue_build"
    assert iterate_result.silhouette_analysis is not None
    assert iterate_result.silhouette_analysis.status == "available"
    assert iterate_result.action_hints
    assert any(hint.hint_type == "widen_upper_profile" for hint in iterate_result.action_hints)
    assert iterate_result.part_segmentation is not None
    assert iterate_result.part_segmentation.status == "disabled"
