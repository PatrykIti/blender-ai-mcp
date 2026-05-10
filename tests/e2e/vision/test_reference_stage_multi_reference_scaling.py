"""Blender-runner E2E coverage for staged multi-reference packet scheduling."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image, ImageDraw
from server.adapters.mcp.areas.reference import reference_compare_stage_checkpoint, reference_images
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.sampling.result_types import (
    AssistantBudgetContract,
    AssistantRunResult,
    VisionAssistContract,
    VisionPacketStatusContract,
)
from server.adapters.mcp.session_capabilities import update_session_from_router_goal
from server.application.tool_handlers.modeling_handler import ModelingToolHandler
from server.application.tool_handlers.scene_handler import SceneToolHandler

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


def _skip_if_blender_unavailable(error: RuntimeError) -> None:
    error_msg = str(error).lower()
    if "could not connect" in error_msg or "is blender running" in error_msg:
        pytest.skip(f"Blender not available: {error}")
    raise error


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
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)
    yield
    try:
        scene_handler.clean_scene(keep_lights_and_cameras=False)
    except RuntimeError:
        pass


def _write_reference_silhouette(path: Path, *, shade: int) -> None:
    image = Image.new("RGBA", (180, 180), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((50, 48, 130, 150), fill=(shade, shade, shade, 255))
    draw.polygon([(78, 48), (92, 22), (106, 48)], fill=(shade, shade, shade, 255))
    image.save(path)


def test_reference_stage_compare_splits_six_front_references_under_runtime_image_budget(
    clean_scene,
    scene_handler,
    modeling_handler,
    tmp_path,
    monkeypatch,
):
    target_name = "PacketScalingCreature"
    capture_context_path = tmp_path / "context_wide_after.png"
    capture_front_path = tmp_path / "target_front_after.png"
    _write_reference_silhouette(capture_context_path, shade=0)
    _write_reference_silhouette(capture_front_path, shade=0)
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    try:
        modeling_handler.create_primitive(primitive_type="CUBE", name=target_name, size=2.0, location=[0, 0, 0])

        ctx = FakeContext()
        update_session_from_router_goal(ctx, "low poly creature with multiple front references", {"status": "no_match"})
        expected_reference_ids: list[str] = []
        for index in range(1, 7):
            reference_path = tmp_path / f"front_ref_{index}.png"
            _write_reference_silhouette(reference_path, shade=index * 20)
            attach_result = asyncio.run(
                reference_images(
                    ctx,
                    action="attach",
                    source_path=str(reference_path),
                    label=f"front_ref_{index}",
                    target_object=target_name,
                    target_view="front",
                )
            )
            expected_reference_ids.append(attach_result.references[-1].reference_id)

        captured_requests: list[object] = []

        async def _fake_run_vision_assist(ctx, *, request, resolver):
            captured_requests.append(request)
            assert len(request.images) <= 3
            return AssistantRunResult(
                status="success",
                assistant_name="vision_assist",
                message="ok",
                budget=AssistantBudgetContract(max_input_chars=1000, max_messages=1, max_tokens=100, tool_budget=0),
                capability_source="local_runtime",
                result=VisionAssistContract(
                    backend_kind="mlx_local",
                    model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                    goal_summary="Packet compare completed cleanly.",
                    visible_changes=["Front silhouette is readable."],
                    shape_mismatches=[],
                    correction_focus=[],
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
                    max_images=3,
                    effective_max_images=3,
                    max_input_chars=12000,
                    effective_max_input_chars=12000,
                    max_tokens=400,
                    effective_max_tokens=400,
                    active_model_name="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                    active_segmentation_sidecar=None,
                )
            ),
        )
        monkeypatch.setattr("server.adapters.mcp.areas.reference.run_vision_assist", _fake_run_vision_assist)
        monkeypatch.setattr(
            "server.adapters.mcp.areas.reference.capture_stage_images",
            lambda *args, **kwargs: [
                VisionCaptureImageContract(
                    label="context_wide_after",
                    image_path=str(capture_context_path),
                    host_visible_path=str(capture_context_path),
                    preset_name="context_wide",
                    media_type="image/png",
                    view_kind="wide",
                ),
                VisionCaptureImageContract(
                    label="target_front_after",
                    image_path=str(capture_front_path),
                    host_visible_path=str(capture_front_path),
                    preset_name="target_front",
                    media_type="image/png",
                    view_kind="focus",
                ),
            ],
        )

        result = asyncio.run(
            reference_compare_stage_checkpoint(
                ctx,
                target_object=target_name,
                checkpoint_label="stage_multi_reference_scaling",
                preset_profile="rich",
                target_view="front",
            )
        )

        assert result.error is None
        assert len(captured_requests) == 6
        assert all(len(request.images) <= 3 for request in captured_requests)
        assert result.compare_diagnostics is not None
        assert result.compare_diagnostics.complexity_tier == "super_complex"
        assert result.compare_diagnostics.packet_count == 6
        assert result.compare_diagnostics.synthesis_required is True
        assert result.compare_diagnostics.budget_notes == [
            "Compare packet policy split reference evidence into bounded packet-local slices to stay within "
            "VISION_MAX_IMAGES=3."
        ]
        packet_reference_ids = [
            request.metadata["packet_reference_ids"][0]
            for request in captured_requests
            if len(request.metadata["packet_reference_ids"]) == 1
        ]
        assert packet_reference_ids == expected_reference_ids
        assert len({request.metadata["packet_id"] for request in captured_requests}) == 6
    except RuntimeError as e:
        _skip_if_blender_unavailable(e)
