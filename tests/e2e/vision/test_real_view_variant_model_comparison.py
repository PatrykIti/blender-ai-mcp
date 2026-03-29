"""Opt-in real-model comparison for the new real viewport view variants."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from types import SimpleNamespace

import pytest
from server.adapters.mcp.vision import (
    build_vision_runtime_config,
    create_vision_backend,
    evaluate_vision_result,
    load_golden_scenario,
)

from scripts import vision_harness as harness

SCENARIOS = (
    "tests/fixtures/vision_eval/squirrel_head_to_face_user_top/golden.json",
    "tests/fixtures/vision_eval/squirrel_face_to_body_user_top/golden.json",
    "tests/fixtures/vision_eval/squirrel_head_to_body_user_top/golden.json",
    "tests/fixtures/vision_eval/squirrel_head_to_face_camera_perspective/golden.json",
    "tests/fixtures/vision_eval/squirrel_face_to_body_camera_perspective/golden.json",
    "tests/fixtures/vision_eval/squirrel_head_to_body_camera_perspective/golden.json",
)


async def _run_model(model_name: str) -> list[dict[str, object]]:
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
    for scenario_path in SCENARIOS:
        golden = load_golden_scenario(Path(scenario_path))
        request = harness._build_request_from_args(args, golden)
        result = await backend.analyze(request)
        summary = evaluate_vision_result(
            {
                "backend": "mlx_local",
                "model_name": runtime.active_model_name,
                "status": "success",
                "result": result,
            },
            golden,
        )
        rows.append(
            {
                "scenario_id": golden.scenario.scenario_id,
                "verdict": summary.verdict,
                "normalized_score": summary.normalized_score,
                "noise_count": len(result.get("likely_issues") or [])
                + len(result.get("recommended_checks") or []),
            }
        )
    return rows


@pytest.mark.slow
@pytest.mark.skipif(
    os.getenv("RUN_REAL_VISION_MODEL_COMPARISON") != "1",
    reason="set RUN_REAL_VISION_MODEL_COMPARISON=1 to run real MLX model comparison",
)
def test_real_view_variant_models_remain_strong_and_clean():
    """Both local MLX baselines should stay strong and avoid noisy extra analysis on the new variants."""

    try:
        results_2b = asyncio.run(_run_model("mlx-community/Qwen3-VL-2B-Instruct-4bit"))
        results_4b = asyncio.run(_run_model("mlx-community/Qwen3-VL-4B-Instruct-4bit"))
    except Exception as exc:  # pragma: no cover - opt-in runtime guard
        pytest.skip(f"real MLX comparison unavailable in this environment: {exc}")

    assert all(str(row["verdict"]) == "strong" for row in results_2b)
    assert all(str(row["verdict"]) == "strong" for row in results_4b)

    total_noise_2b = sum(int(row["noise_count"]) for row in results_2b)
    total_noise_4b = sum(int(row["noise_count"]) for row in results_4b)
    total_score_2b = sum(float(row["normalized_score"] or 0.0) for row in results_2b)
    total_score_4b = sum(float(row["normalized_score"] or 0.0) for row in results_4b)

    assert total_noise_2b == 0
    assert total_noise_4b == 0
    assert total_score_4b >= total_score_2b
