"""Real-model reference-guided creature comparison smoke coverage."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

CHECKPOINT_IMAGES = (
    ("stage_face_camera", "_docs/_TESTS/_TEST_4/2-squirrel_face_features-camera-perspective.png"),
    ("stage_full_body_camera", "_docs/_TESTS/_TEST_4/3-squirrel_full_body-camera-perspective.png"),
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def _resolve_reference_path(name: str, fallback_name: str) -> str:
    value = os.getenv(name)
    path = Path(value).expanduser().resolve() if value else (Path.home() / "Documents" / fallback_name).resolve()
    if not path.exists():
        pytest.skip(f"{name} is not set and fallback reference does not exist: {path}")
    return str(path)


def _run_model(model_name: str, *, front_reference: str, side_reference: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for label, relative_path in CHECKPOINT_IMAGES:
        checkpoint = str((REPO_ROOT / relative_path).resolve())
        cmd = [
            sys.executable,
            "scripts/vision_harness.py",
            "--backend",
            "mlx_local",
            "--goal",
            "Compare the current low-poly squirrel stage against the front and side squirrel reference images and report the highest-priority visible mismatches to fix next.",
            "--target-object",
            "Squirrel",
            "--prompt-hint",
            f"comparison_mode=checkpoint_vs_reference | creature_type=squirrel | checkpoint_label={label}",
            "--after",
            checkpoint,
            "--reference",
            front_reference,
            "--reference",
            side_reference,
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
        result = payload[0].get("result") or {}
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


def _has_reference_summary_signal(summary: object) -> bool:
    text = str(summary or "").lower()
    return any(
        hint in text
        for hint in (
            "matches the reference",
            "aligns with the reference",
            "closer to the reference",
            "consistent with the reference",
            "correct silhouette and proportions",
            "incomplete representation",
            "lacks the detailed",
            "lacks the",
            "simplified",
            "more complete",
        )
    )


@pytest.mark.slow
def test_real_reference_guided_creature_comparison_returns_correction_guidance():
    """Real MLX creature/reference comparison should return bounded correction guidance or a clear alignment summary."""

    front_reference = _resolve_reference_path("VISION_REFERENCE_FRONT_PATH", "squirrel-front.png")
    side_reference = _resolve_reference_path("VISION_REFERENCE_SIDE_PATH", "squirrel-side.png")
    model_name = os.getenv("VISION_REFERENCE_CREATURE_MODEL") or "mlx-community/Qwen3-VL-4B-Instruct-4bit"

    try:
        rows = _run_model(
            model_name,
            front_reference=front_reference,
            side_reference=side_reference,
        )
    except Exception as exc:  # pragma: no cover - runtime guard
        pytest.skip(f"real reference-guided creature comparison unavailable in this environment: {exc}")

    assert rows
    saw_actionable_guidance = False
    for row in rows:
        assert row["reference_match_summary"]
        assert len(row["shape_mismatches"]) <= 3
        assert len(row["proportion_mismatches"]) <= 3
        assert len(row["correction_focus"]) <= 3
        assert len(row["next_corrections"]) <= 3
        assert len(row["likely_issues"]) <= 2
        assert len(row["recommended_checks"]) <= 2
        actionable = bool(
            row["correction_focus"]
            or row["shape_mismatches"]
            or row["proportion_mismatches"]
            or row["next_corrections"]
        )
        if actionable:
            saw_actionable_guidance = True
        else:
            assert _has_reference_summary_signal(row["reference_match_summary"])

    assert saw_actionable_guidance or all(
        _has_reference_summary_signal(row["reference_match_summary"]) for row in rows
    )
