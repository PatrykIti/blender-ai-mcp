"""Subprocess E2E coverage for the fixture-only reference-understanding harness path."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.e2e
def test_vision_harness_fixture_only_reference_understanding_subprocess(tmp_path: Path):
    reference_path = tmp_path / "front_ref.png"
    Image.new("RGBA", (8, 8), (0, 0, 0, 255)).save(reference_path)

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/vision_harness.py",
            "--backend",
            "mlx_local",
            "--goal",
            "create a low-poly squirrel matching front and side references",
            "--reference",
            str(reference_path),
            "--fixture-only",
            "reference-understanding",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    payload = json.loads(completed.stdout)
    assert isinstance(payload, list) and payload
    row = payload[0]
    assert row["status"] == "fixture_only"
    assert row["fixture_only_mode"] == "reference-understanding"
    assert row["result"]["metadata"]["mode"] == "reference_understanding"
