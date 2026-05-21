"""Subprocess E2E coverage for the fixture-only reference-understanding harness path."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[3]


def _write_fake_mlx_vlm_package(root: Path) -> None:
    package_dir = root / "mlx_vlm"
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").write_text(
        """
class _GenerationResult:
    def __init__(self, text):
        self.text = text


def load(model_source):
    return "model", "processor"


def generate(model, processor, *args, **kwargs):
    return _GenerationResult(
        '{"subject":{"label":"low poly squirrel","category":"creature","confidence":0.8,"uncertainty_notes":[]},'
        '"style":{"style_label":"low_poly_faceted","confidence":0.8,"notes":[]},'
        '"views":[{"view_id":"front","detected":true,"confidence":0.9,"reference_ids":["fixture_ref_1"],"key_features":["faceted head"]}],'
        '"required_parts":[{"part_label":"body core","target_label":"body_core","construction_hint":"Start with a simple faceted primary mass.","priority":"high","source_reference_ids":["fixture_ref_1"]}],'
        '"mass_recipe":[],"attachment_plan":[],"contact_expectations":[],"shape_profile_hints":[],"silhouette_landmarks":[],"part_order":[],"must_seat_before_next_stage":[],'
        '"non_goals":[],"construction_strategy":{"construction_path":"low_poly_facet","primary_family":"modeling_mesh","allowed_families":["macro","modeling_mesh","inspect_only"],"stage_sequence":["primary_masses"],"finish_policy":"preserve_facets"},'
        '"router_handoff_hints":{"preferred_family":"modeling_mesh","allowed_guided_families":["reference_context","primary_masses"],"sculpt_policy":"hidden"},'
        '"gate_proposals":[],"visual_evidence_refs":[],"verification_requirements":[]}'
    )
""",
        encoding="utf-8",
    )
    (package_dir / "prompt_utils.py").write_text(
        """
def apply_chat_template(processor, config, prompt_payload, num_images=0):
    return f"PROMPT::{num_images}"
""",
        encoding="utf-8",
    )
    (package_dir / "utils.py").write_text(
        """
def load_config(model_source):
    return {"model_source": model_source}
""",
        encoding="utf-8",
    )


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
    assert row["result"]["goal"] == "create a low-poly squirrel matching front and side references"
    assert row["result"]["target_object"] is None
    assert row["result"]["image_count"] == 1
    assert row["result"]["image_roles"] == ["reference"]
    assert row["result"]["metadata"]["mode"] == "reference_understanding"
    assert row["result"]["metadata"]["reference_ids"] == ["fixture_ref_1"]


@pytest.mark.e2e
def test_vision_harness_fixture_only_reference_understanding_bundle_subprocess(tmp_path: Path):
    bundle_path = tmp_path / "bundle.json"
    before_path = tmp_path / "before.jpg"
    after_path = tmp_path / "after.jpg"
    reference_path = tmp_path / "reference.png"
    before_path.write_bytes(b"before")
    after_path.write_bytes(b"after")
    Image.new("RGBA", (8, 8), (0, 0, 0, 255)).save(reference_path)
    bundle_path.write_text(
        json.dumps(
            {
                "bundle_id": "bundle_1",
                "target_object": "Housing",
                "preset_names": ["context_wide"],
                "captures_before": [
                    {
                        "label": "before_1",
                        "image_path": str(before_path),
                        "media_type": "image/jpeg",
                    }
                ],
                "captures_after": [
                    {
                        "label": "after_1",
                        "image_path": str(after_path),
                        "media_type": "image/jpeg",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    references_path = tmp_path / "references.json"
    references_path.write_text(
        json.dumps(
            {
                "references": [
                    {
                        "reference_id": "ref_1",
                        "goal": "rounded housing",
                        "label": "front_reference",
                        "media_type": "image/png",
                        "source_kind": "local_path",
                        "original_path": str(reference_path),
                        "stored_path": str(reference_path),
                        "host_visible_path": str(reference_path),
                        "added_at": "2026-03-26T00:00:00Z",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/vision_harness.py",
            "--backend",
            "mlx_local",
            "--goal",
            "rounded housing",
            "--bundle-json",
            str(bundle_path),
            "--references-json",
            str(references_path),
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
    assert row["fixture_only_mode"] == "reference-understanding"
    assert row["result"]["goal"] == "rounded housing"
    assert row["result"]["image_count"] == 1
    assert row["result"]["image_roles"] == ["reference"]
    assert row["result"]["metadata"]["reference_ids"] == ["ref_1"]


@pytest.mark.e2e
def test_vision_harness_live_reference_understanding_subprocess_with_fake_mlx_backend(tmp_path: Path):
    reference_path = tmp_path / "front_ref.png"
    Image.new("RGBA", (8, 8), (0, 0, 0, 255)).save(reference_path)
    fake_modules = tmp_path / "fake_modules"
    _write_fake_mlx_vlm_package(fake_modules)
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{fake_modules}:{REPO_ROOT}"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/vision_harness.py",
            "--backend",
            "mlx_local",
            "--goal",
            "create a low-poly squirrel matching front and side references",
            "--mode",
            "reference-understanding",
            "--reference",
            str(reference_path),
            "--mlx-model",
            "mlx-community/Qwen3-VL-4B-Instruct-4bit",
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    payload = json.loads(completed.stdout)
    assert isinstance(payload, list) and payload
    row = payload[0]
    assert row["backend"] == "mlx_local"
    assert row["status"] == "success"
    assert row["result"]["status"] == "available"
    assert row["result"]["reference_ids"] == ["fixture_ref_1"]
    assert row["result"]["construction_strategy"]["primary_family"] == "modeling_mesh"
    assert row["diagnostics"]["payload_shape"] == "contract"


@pytest.mark.e2e
def test_vision_harness_live_reference_understanding_bundle_subprocess_with_fake_mlx_backend(tmp_path: Path):
    bundle_path = tmp_path / "bundle.json"
    before_path = tmp_path / "before.jpg"
    after_path = tmp_path / "after.jpg"
    reference_path = tmp_path / "reference.png"
    before_path.write_bytes(b"before")
    after_path.write_bytes(b"after")
    Image.new("RGBA", (8, 8), (0, 0, 0, 255)).save(reference_path)
    bundle_path.write_text(
        json.dumps(
            {
                "bundle_id": "bundle_1",
                "target_object": "Housing",
                "preset_names": ["context_wide"],
                "captures_before": [
                    {
                        "label": "before_1",
                        "image_path": str(before_path),
                        "media_type": "image/jpeg",
                    }
                ],
                "captures_after": [
                    {
                        "label": "after_1",
                        "image_path": str(after_path),
                        "media_type": "image/jpeg",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    references_path = tmp_path / "references.json"
    references_path.write_text(
        json.dumps(
            {
                "references": [
                    {
                        "reference_id": "ref_1",
                        "goal": "rounded housing",
                        "label": "front_reference",
                        "media_type": "image/png",
                        "source_kind": "local_path",
                        "original_path": str(reference_path),
                        "stored_path": str(reference_path),
                        "host_visible_path": str(reference_path),
                        "added_at": "2026-03-26T00:00:00Z",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    fake_modules = tmp_path / "fake_modules"
    _write_fake_mlx_vlm_package(fake_modules)
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{fake_modules}:{REPO_ROOT}"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/vision_harness.py",
            "--backend",
            "mlx_local",
            "--goal",
            "rounded housing",
            "--mode",
            "reference-understanding",
            "--bundle-json",
            str(bundle_path),
            "--references-json",
            str(references_path),
            "--mlx-model",
            "mlx-community/Qwen3-VL-4B-Instruct-4bit",
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    payload = json.loads(completed.stdout)
    assert isinstance(payload, list) and payload
    row = payload[0]
    assert row["backend"] == "mlx_local"
    assert row["status"] == "success"
    assert row["result"]["status"] == "available"
    assert row["result"]["reference_ids"] == ["ref_1"]
    assert row["result"]["construction_strategy"]["primary_family"] == "modeling_mesh"
    assert row["diagnostics"]["payload_shape"] == "contract"


@pytest.mark.e2e
def test_vision_harness_live_reference_understanding_bundle_inline_reference_subprocess_with_fake_mlx_backend(
    tmp_path: Path,
):
    bundle_path = tmp_path / "bundle.json"
    before_path = tmp_path / "before.jpg"
    after_path = tmp_path / "after.jpg"
    reference_path = tmp_path / "reference.png"
    before_path.write_bytes(b"before")
    after_path.write_bytes(b"after")
    Image.new("RGBA", (8, 8), (0, 0, 0, 255)).save(reference_path)
    bundle_path.write_text(
        json.dumps(
            {
                "bundle_id": "bundle_1",
                "target_object": "Housing",
                "preset_names": ["context_wide"],
                "captures_before": [
                    {
                        "label": "before_1",
                        "image_path": str(before_path),
                        "media_type": "image/jpeg",
                    }
                ],
                "captures_after": [
                    {
                        "label": "after_1",
                        "image_path": str(after_path),
                        "media_type": "image/jpeg",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    fake_modules = tmp_path / "fake_modules"
    _write_fake_mlx_vlm_package(fake_modules)
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{fake_modules}:{REPO_ROOT}"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/vision_harness.py",
            "--backend",
            "mlx_local",
            "--goal",
            "rounded housing",
            "--mode",
            "reference-understanding",
            "--bundle-json",
            str(bundle_path),
            "--reference",
            str(reference_path),
            "--mlx-model",
            "mlx-community/Qwen3-VL-4B-Instruct-4bit",
        ],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    payload = json.loads(completed.stdout)
    assert isinstance(payload, list) and payload
    row = payload[0]
    assert row["backend"] == "mlx_local"
    assert row["status"] == "success"
    assert row["result"]["status"] == "available"
    assert row["result"]["reference_ids"] == ["cli_ref_1"]
    assert row["result"]["construction_strategy"]["primary_family"] == "modeling_mesh"
    assert row["diagnostics"]["payload_shape"] == "contract"


@pytest.mark.e2e
def test_vision_harness_fixture_only_reference_understanding_bundle_inline_reference_subprocess(tmp_path: Path):
    bundle_path = tmp_path / "bundle.json"
    before_path = tmp_path / "before.jpg"
    after_path = tmp_path / "after.jpg"
    reference_path = tmp_path / "reference.png"
    before_path.write_bytes(b"before")
    after_path.write_bytes(b"after")
    Image.new("RGBA", (8, 8), (0, 0, 0, 255)).save(reference_path)
    bundle_path.write_text(
        json.dumps(
            {
                "bundle_id": "bundle_1",
                "target_object": "Housing",
                "preset_names": ["context_wide"],
                "captures_before": [
                    {
                        "label": "before_1",
                        "image_path": str(before_path),
                        "media_type": "image/jpeg",
                    }
                ],
                "captures_after": [
                    {
                        "label": "after_1",
                        "image_path": str(after_path),
                        "media_type": "image/jpeg",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/vision_harness.py",
            "--backend",
            "mlx_local",
            "--goal",
            "rounded housing",
            "--bundle-json",
            str(bundle_path),
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
    assert row["fixture_only_mode"] == "reference-understanding"
    assert row["result"]["goal"] == "rounded housing"
    assert row["result"]["image_count"] == 1
    assert row["result"]["image_roles"] == ["reference"]
    assert row["result"]["metadata"]["reference_ids"] == ["cli_ref_1"]
