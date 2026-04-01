"""Real-model comparison for the new real viewport view variants."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCENARIOS = (
    "tests/fixtures/vision_eval/squirrel_head_to_face_user_top/golden.json",
    "tests/fixtures/vision_eval/squirrel_face_to_body_user_top/golden.json",
    "tests/fixtures/vision_eval/squirrel_head_to_body_user_top/golden.json",
    "tests/fixtures/vision_eval/squirrel_head_to_face_camera_perspective/golden.json",
    "tests/fixtures/vision_eval/squirrel_face_to_body_camera_perspective/golden.json",
    "tests/fixtures/vision_eval/squirrel_head_to_body_camera_perspective/golden.json",
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def _run_model(model_name: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for scenario_path in SCENARIOS:
        cmd = [
            sys.executable,
            "scripts/vision_harness.py",
            "--backend",
            "mlx_local",
            "--golden-json",
            scenario_path,
            "--mlx-model",
            model_name,
            "--max-images",
            "8",
            "--max-tokens",
            "600",
            "--timeout-seconds",
            "120",
        ]
        completed = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "vision_harness failed")
        payload = json.loads(completed.stdout)
        if not isinstance(payload, list) or not payload:
            raise RuntimeError("vision_harness returned empty payload")
        entry = payload[0]
        evaluation = entry.get("evaluation") or {}
        result = entry.get("result") or {}
        rows.append(
            {
                "scenario_id": str((evaluation.get("scenario_id") or "")),
                "verdict": str(evaluation.get("verdict") or ""),
                "normalized_score": float(evaluation.get("normalized_score") or 0.0),
                "noise_count": len(result.get("likely_issues") or []) + len(result.get("recommended_checks") or []),
            }
        )
    return rows


@pytest.mark.slow
def test_real_view_variant_models_remain_strong_and_clean():
    """The current local MLX baselines should stay clean, and 4B should remain the stronger default."""

    try:
        results_2b = _run_model("mlx-community/Qwen3-VL-2B-Instruct-4bit")
        results_4b = _run_model("mlx-community/Qwen3-VL-4B-Instruct-4bit")
    except Exception as exc:  # pragma: no cover - runtime guard
        pytest.skip(f"real MLX comparison unavailable in this environment: {exc}")

    assert all(str(row["verdict"]) == "strong" for row in results_4b)
    assert all(str(row["verdict"]) in {"strong", "usable"} for row in results_2b)

    total_noise_2b = sum(int(row["noise_count"]) for row in results_2b)
    total_noise_4b = sum(int(row["noise_count"]) for row in results_4b)
    total_score_2b = sum(float(row["normalized_score"] or 0.0) for row in results_2b)
    total_score_4b = sum(float(row["normalized_score"] or 0.0) for row in results_4b)

    assert total_noise_2b <= 4
    assert total_noise_4b == 0
    assert total_score_4b >= total_score_2b
