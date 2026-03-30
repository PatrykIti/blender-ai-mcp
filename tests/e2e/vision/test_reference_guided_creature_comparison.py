"""Opt-in real-model reference-guided creature comparison smoke coverage."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from types import SimpleNamespace

import pytest
from server.adapters.mcp.vision import (
    VisionImageInput,
    VisionRequest,
    build_vision_runtime_config,
    create_vision_backend,
)

from scripts import vision_harness as harness

CHECKPOINT_IMAGES = (
    ("stage_face_camera", "_docs/_TESTS/_TEST_4/2-squirrel_face_features-camera-perspective.png"),
    ("stage_full_body_camera", "_docs/_TESTS/_TEST_4/3-squirrel_full_body-camera-perspective.png"),
)


def _require_env_path(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.skip(f"set {name} to run real reference-guided creature comparison")
    path = Path(value).expanduser().resolve()
    if not path.exists():
        pytest.skip(f"{name} does not exist: {path}")
    return str(path)


async def _run_model(model_name: str, *, front_reference: str, side_reference: str) -> list[dict[str, object]]:
    args = SimpleNamespace(
        max_images=8,
        max_tokens=600,
        timeout_seconds=120.0,
        transformers_model="Qwen/Qwen2.5-VL-3B-Instruct",
        local_device="mps",
        local_dtype="float16",
        mlx_model=model_name,
        external_base_url=None,
        external_model=None,
        external_api_key=None,
        external_api_key_env=None,
        goal=None,
        target_object=None,
        prompt_hint=None,
        bundle_json=None,
        references_json=None,
        before=None,
        after=None,
        reference=None,
        truth_json=None,
    )
    runtime = build_vision_runtime_config(harness._config_for_backend(args, "mlx_local"))
    backend = create_vision_backend(runtime)
    rows: list[dict[str, object]] = []

    for label, relative_path in CHECKPOINT_IMAGES:
        checkpoint = Path(relative_path).resolve()
        request = VisionRequest(
            goal=(
                "Compare the current low-poly squirrel stage against the front and side squirrel reference images "
                "and report the highest-priority visible mismatches to fix next."
            ),
            target_object="Squirrel",
            prompt_hint=f"comparison_mode=checkpoint_vs_reference | creature_type=squirrel | checkpoint_label={label}",
            images=(
                VisionImageInput(path=str(checkpoint), role="after", label=label, media_type="image/png"),
                VisionImageInput(path=front_reference, role="reference", label="reference_front", media_type="image/png"),
                VisionImageInput(path=side_reference, role="reference", label="reference_side", media_type="image/png"),
            ),
        )
        result = await backend.analyze(request)
        rows.append(
            {
                "label": label,
                "reference_match_summary": result.get("reference_match_summary"),
                "shape_mismatches": list(result.get("shape_mismatches") or []),
                "proportion_mismatches": list(result.get("proportion_mismatches") or []),
                "correction_focus": list(result.get("correction_focus") or []),
                "next_corrections": list(result.get("next_corrections") or []),
                "likely_issues": list(result.get("likely_issues") or []),
                "recommended_checks": list(result.get("recommended_checks") or []),
            }
        )
    return rows


@pytest.mark.slow
@pytest.mark.skipif(
    os.getenv("RUN_REAL_REFERENCE_GUIDED_CREATURE_EVAL") != "1",
    reason="set RUN_REAL_REFERENCE_GUIDED_CREATURE_EVAL=1 to run real reference-guided creature comparison",
)
def test_real_reference_guided_creature_comparison_returns_correction_guidance():
    """Real MLX creature/reference comparison should return bounded correction guidance."""

    front_reference = _require_env_path("VISION_REFERENCE_FRONT_PATH")
    side_reference = _require_env_path("VISION_REFERENCE_SIDE_PATH")
    model_name = os.getenv("VISION_REFERENCE_CREATURE_MODEL") or "mlx-community/Qwen3-VL-4B-Instruct-4bit"

    try:
        rows = asyncio.run(
            _run_model(
                model_name,
                front_reference=front_reference,
                side_reference=side_reference,
            )
        )
    except Exception as exc:  # pragma: no cover - opt-in runtime guard
        pytest.skip(f"real reference-guided creature comparison unavailable in this environment: {exc}")

    assert rows
    for row in rows:
        assert row["reference_match_summary"]
        assert len(row["shape_mismatches"]) <= 3
        assert len(row["proportion_mismatches"]) <= 3
        assert len(row["correction_focus"]) <= 3
        assert len(row["next_corrections"]) <= 3
        assert len(row["likely_issues"]) <= 2
        assert len(row["recommended_checks"]) <= 2
        assert bool(
            row["correction_focus"]
            or row["shape_mismatches"]
            or row["proportion_mismatches"]
            or row["next_corrections"]
        )
