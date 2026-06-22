from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tomllib
import types
import urllib.error
import zipfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_script(script_name: str):
    script_path = REPO_ROOT / "scripts" / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(f"tests_{script_name}", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_streamable_openrouter_shell_script_contains_required_runtime_env():
    script = (REPO_ROOT / "scripts" / "run_streamable_openrouter.sh").read_text(encoding="utf-8")

    for expected in (
        "OPENROUTER_API_KEY must be set",
        "MCP_TRANSPORT_MODE=streamable",
        "MCP_HTTP_PORT",
        "MCP_STREAMABLE_HTTP_PATH",
        "BLENDER_RPC_HOST",
        "BLENDER_AI_DEBUG",
        "VISION_EXTERNAL_PROVIDER=openrouter",
        'VISION_EXTERNAL_CONTRACT_PROFILE="${VISION_EXTERNAL_CONTRACT_PROFILE}"',
        'VISION_OPENROUTER_MODEL="${VISION_OPENROUTER_MODEL}"',
        'VISION_OPENROUTER_REQUIRE_PARAMETERS="${VISION_OPENROUTER_REQUIRE_PARAMETERS}"',
        'VISION_OPENROUTER_ENABLE_RESPONSE_HEALING="${VISION_OPENROUTER_ENABLE_RESPONSE_HEALING}"',
        'VISION_OPENROUTER_PREFER_JSON_OBJECT_FOR_QWEN="${VISION_OPENROUTER_PREFER_JSON_OBJECT_FOR_QWEN}"',
        "REFERENCE_CLASSIFIER_AUTO_START",
        "REFERENCE_CLASSIFIER_DOCKER_HOST",
        "REFERENCE_CLASSIFIER_LOG_PATH",
        "run_reference_classifier_sidecar.sh",
        "SEGMENTATION_SIDECAR_AUTO_START",
        "SEGMENTATION_SIDECAR_DOCKER_HOST",
        "SEGMENTATION_SIDECAR_LOG_PATH",
        "run_segmentation_sidecar.sh",
        "LOCALIZATION_SIDECAR_AUTO_START",
        "LOCALIZATION_SIDECAR_DOCKER_HOST",
        "LOCALIZATION_SIDECAR_LOG_PATH",
        "run_localization_sidecar.sh",
        "Appending reference classifier sidecar logs to:",
        "Appending segmentation sidecar logs to:",
        "Appending localization sidecar logs to:",
        'VISION_MAX_INPUT_CHARS="${VISION_MAX_INPUT_CHARS}"',
        'VISION_SEGMENTATION_ENABLED="${VISION_SEGMENTATION_ENABLED}"',
        'VISION_SEGMENTATION_ENDPOINT="${VISION_SEGMENTATION_ENDPOINT}"',
        'VISION_SEGMENTATION_MAX_PARTS="${VISION_SEGMENTATION_MAX_PARTS}"',
        'VISION_LOCALIZATION_ENABLED="${VISION_LOCALIZATION_ENABLED}"',
        'VISION_LOCALIZATION_ENDPOINT="${VISION_LOCALIZATION_ENDPOINT}"',
        'VISION_LOCALIZATION_MAX_CANDIDATES="${VISION_LOCALIZATION_MAX_CANDIDATES}"',
        "/health",
        "host-gateway",
        "Set REFERENCE_CLASSIFIER_AUTO_START=false if you want to use a remote classifier endpoint.",
        "Set SEGMENTATION_SIDECAR_AUTO_START=false if you want to use a remote segmentation endpoint.",
        "Set LOCALIZATION_SIDECAR_AUTO_START=false if you want to use a remote localization endpoint.",
    ):
        assert expected in script


def test_reference_classifier_sidecar_shell_script_contains_operator_defaults():
    script = (REPO_ROOT / "scripts" / "run_reference_classifier_sidecar.sh").read_text(encoding="utf-8")

    for expected in (
        "REFERENCE_CLASSIFIER_HOST",
        "REFERENCE_CLASSIFIER_PORT",
        "REFERENCE_CLASSIFIER_MODEL",
        "VISION_REFERENCE_CLASSIFIER_MODEL",
        "foreground sidecar-only helper",
        "does not start the FastMCP server",
        "poetry install --with vision",
        "Docker MCP endpoint",
        "Local MCP endpoint",
        "scripts/reference_classifier_sidecar.py",
    ):
        assert expected in script


def test_segmentation_sidecar_shell_script_contains_operator_defaults():
    script = (REPO_ROOT / "scripts" / "run_segmentation_sidecar.sh").read_text(encoding="utf-8")

    for expected in (
        "SEGMENTATION_SIDECAR_HOST",
        "SEGMENTATION_SIDECAR_PORT",
        "SEGMENTATION_SIDECAR_MODEL",
        "VISION_SEGMENTATION_MODEL",
        "foreground sidecar-only helper",
        "does not start the FastMCP server",
        "poetry install --with vision",
        "Docker MCP endpoint",
        "Local MCP endpoint",
        "First launch downloads the configured model weights automatically.",
        "scripts/segmentation_sidecar.py",
    ):
        assert expected in script


def test_localization_sidecar_shell_script_contains_operator_defaults():
    script = (REPO_ROOT / "scripts" / "run_localization_sidecar.sh").read_text(encoding="utf-8")

    for expected in (
        "LOCALIZATION_SIDECAR_HOST",
        "LOCALIZATION_SIDECAR_PORT",
        "LOCALIZATION_SIDECAR_MODEL",
        "VISION_LOCALIZATION_MODEL",
        "foreground sidecar-only helper",
        "does not start the FastMCP server",
        "poetry install --with vision",
        "Docker MCP endpoint",
        "Local MCP endpoint",
        "First launch downloads the configured model weights automatically.",
        "scripts/localization_sidecar.py",
    ):
        assert expected in script


def test_localization_sidecar_script_can_run_help_via_file_path():
    completed = subprocess.run(
        [sys.executable, "scripts/localization_sidecar.py", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert "Run a local compare-time localization sidecar" in completed.stdout


def test_segmentation_sidecar_script_can_run_help_via_file_path():
    completed = subprocess.run(
        [sys.executable, "scripts/segmentation_sidecar.py", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    assert "Run a local compare-time segmentation sidecar" in completed.stdout


def test_run_mcp_server_shell_script_invokes_python_launcher():
    script = (REPO_ROOT / "scripts" / "run_mcp_server.sh").read_text(encoding="utf-8")

    assert 'poetry run python scripts/run_mcp_server.py "$@"' in script


def test_run_mcp_server_docs_explain_macos_first_flow():
    doc = (REPO_ROOT / "scripts" / "RUN_MCP_SERVER.md").read_text(encoding="utf-8")

    for expected in (
        "macOS-first",
        "scripts/run_mcp_server.sh",
        "scripts/run_streamable_openrouter.sh",
        "scripts/run_reference_classifier_sidecar.sh",
        "scripts/run_segmentation_sidecar.sh",
        "scripts/run_localization_sidecar.sh",
        "does not launch the FastMCP server",
        "First Run",
        "Docker On macOS",
        "Optional Dependency Groups",
    ):
        assert expected in doc


def test_run_mcp_server_launch_env_wires_classifier_plan(monkeypatch):
    module = _load_script("run_mcp_server")

    captured: dict[str, object] = {}

    def _fake_run(command, cwd=None, env=None, check=False, **kwargs):
        captured["command"] = command
        captured["cwd"] = cwd
        captured["env"] = env
        return types.SimpleNamespace(returncode=0)

    monkeypatch.setattr(module.subprocess, "run", _fake_run)
    monkeypatch.setattr(module, "_ask_yes_no", lambda *args, **kwargs: True)

    plan = module.LauncherPlan(
        enable_classifier=True,
        auto_start_classifier=True,
        classifier_endpoint=None,
        classifier_model="google/siglip2-base-patch16-224",
        openrouter_model="openai/gpt-5.4-mini",
        openrouter_api_key="secret",
        debug_selector="tools,transport",
        install_mlx=False,
        install_vision=True,
    )

    result = module._run_streamable_openrouter(plan)

    assert result == 0
    assert captured["command"] == ["bash", str(module.SCRIPT_DIR / "run_streamable_openrouter.sh")]
    env = captured["env"]
    assert isinstance(env, dict)
    assert env["OPENROUTER_API_KEY"] == "secret"
    assert env["VISION_OPENROUTER_MODEL"] == "openai/gpt-5.4-mini"
    assert env["VISION_REFERENCE_CLASSIFIER_ENABLED"] == "true"
    assert env["REFERENCE_CLASSIFIER_AUTO_START"] == "true"
    assert env["VISION_REFERENCE_CLASSIFIER_MODEL"] == "google/siglip2-base-patch16-224"
    assert env["BLENDER_AI_DEBUG"] == "tools,transport"


def test_reference_classifier_sidecar_parser_and_service_contract(tmp_path, monkeypatch):
    module = _load_script("reference_classifier_sidecar")
    image_path = tmp_path / "reference.png"

    try:
        from PIL import Image
    except ModuleNotFoundError:
        pytest.skip("Pillow is required for script-side image contract tests")

    Image.new("RGB", (16, 16), (255, 255, 255)).save(image_path)

    args = module.build_parser().parse_args(
        [
            "--host",
            "127.0.0.1",
            "--port",
            "9200",
            "--model",
            "google/siglip2-base-patch16-224",
            "--device",
            "cpu",
            "--top-k",
            "3",
        ]
    )

    assert args.host == "127.0.0.1"
    assert args.port == 9200
    assert args.model == "google/siglip2-base-patch16-224"
    assert args.device == "cpu"
    assert args.top_k == 3

    def _fake_pipeline(image, candidate_labels):
        assert candidate_labels
        return [
            {"label": "a low-poly faceted animal reference", "score": 0.93},
            {"label": "a generic creature blockout reference", "score": 0.62},
            {"label": "a hard-surface product or prop reference", "score": 0.11},
        ]

    monkeypatch.setattr(module, "_build_classifier_pipeline", lambda **kwargs: _fake_pipeline)

    service = module.ReferenceClassifierService(
        model_name="google/siglip2-base-patch16-224",
        device_name="cpu",
        top_k=2,
    )
    assert service._pipeline is None
    service.warmup()
    assert service._pipeline is _fake_pipeline
    response = service.classify_payload(
        {
            "goal": "classify the attached squirrel reference",
            "references": [
                {
                    "reference_id": "ref_1",
                    "image_path": str(image_path),
                }
            ],
        }
    )

    assert response["classification_scores"] == [
        {"label": "low_poly_faceted", "score": 0.93},
        {"label": "creature_blockout", "score": 0.62},
    ]
    assert response["model_name"] == "google/siglip2-base-patch16-224"
    assert response["device_name"] == "cpu"


def test_localization_sidecar_parser_and_service_contract(tmp_path, monkeypatch):
    module = _load_script("localization_sidecar")
    image_path = tmp_path / "capture.png"

    try:
        from PIL import Image
    except ModuleNotFoundError:
        pytest.skip("Pillow is required for script-side image contract tests")

    Image.new("RGB", (32, 24), (255, 255, 255)).save(image_path)

    args = module.build_parser().parse_args(
        [
            "--host",
            "127.0.0.1",
            "--port",
            "9300",
            "--model",
            "grounding-sidecar-v1",
            "--device",
            "cpu",
            "--max-candidates",
            "4",
            "--threshold",
            "0.2",
        ]
    )

    assert args.host == "127.0.0.1"
    assert args.port == 9300
    assert args.model == "grounding-sidecar-v1"
    assert args.device == "cpu"
    assert args.max_candidates == 4
    assert args.threshold == 0.2

    def _fake_detector(image, candidate_labels, threshold):
        assert candidate_labels == ["tail mass", "ear pair"]
        assert threshold == 0.2
        return [
            {
                "label": "tail mass",
                "score": 0.91,
                "box": {"xmin": 3, "ymin": 4, "xmax": 18, "ymax": 20},
            }
        ]

    monkeypatch.setattr(module, "_build_localization_pipeline", lambda **kwargs: _fake_detector)

    service = module.LocalizationService(
        requested_model_name="grounding-sidecar-v1",
        device_name="cpu",
        max_candidates=4,
        threshold=0.2,
    )
    service.warmup()
    response = service.localize_payload(
        {
            "captures": [{"label": "after_1", "target_view": "front", "image_path": str(image_path)}],
            "query_labels": ["tail_mass", "ear_pair"],
        }
    )

    assert response["resolved_model_name"] == module.DEFAULT_LOCALIZATION_MODEL
    assert response["device_name"] == "cpu"
    assert len(response["candidates"]) == 1
    assert response["candidates"][0]["query_label"] == "tail_mass"
    assert response["candidates"][0]["capture_label"] == "after_1"
    assert response["candidates"][0]["target_view"] == "front"


def test_segmentation_sidecar_parser_and_service_contract(tmp_path, monkeypatch):
    module = _load_script("segmentation_sidecar")
    image_path = tmp_path / "capture.png"

    try:
        from PIL import Image
    except ModuleNotFoundError:
        pytest.skip("Pillow is required for script-side image contract tests")

    Image.new("RGB", (24, 24), (255, 255, 255)).save(image_path)

    args = module.build_parser().parse_args(
        [
            "--host",
            "127.0.0.1",
            "--port",
            "9100",
            "--model",
            "sam-sidecar-v1",
            "--device",
            "cpu",
            "--max-parts",
            "3",
        ]
    )

    assert args.host == "127.0.0.1"
    assert args.port == 9100
    assert args.model == "sam-sidecar-v1"
    assert args.device == "cpu"
    assert args.max_parts == 3

    monkeypatch.setattr(module, "_build_segmentation_runtime", lambda **kwargs: object())

    def _fake_predict(runtime, *, image, prompts):
        assert len(prompts) == 1
        return [
            module.SegmentationPrediction(
                mask=module.np.pad(module.np.ones((8, 8), dtype=bool), ((4, 12), (5, 11))),
                confidence=0.87,
            )
        ]

    monkeypatch.setattr(module, "_predict_segmentation", _fake_predict)

    service = module.SegmentationService(
        requested_model_name="sam-sidecar-v1",
        device_name="cpu",
        max_parts=3,
    )
    service.warmup()
    response = service.segment_payload(
        {
            "packet": {
                "packet_label": "tail packet",
                "scope_label": "tail_mass",
                "target_objects": ["Squirrel_Tail"],
            },
            "captures": [{"label": "after_1", "target_view": "front", "image_path": str(image_path)}],
            "seed_boxes": [
                {
                    "query_label": "tail_mass",
                    "capture_label": "after_1",
                    "box_xyxy": [5, 4, 13, 12],
                }
            ],
        }
    )

    assert response["resolved_model_name"] == module.DEFAULT_SEGMENTATION_MODEL
    assert response["device_name"] == "cpu"
    assert len(response["parts"]) == 1
    assert response["parts"][0]["part_label"] == "tail_mass"
    assert response["parts"][0]["confidence"] == 0.87
    assert response["parts"][0]["mask_path"].endswith(".png")
    assert response["parts"][0]["crop_path"].endswith(".png")


def test_update_openrouter_model_profiles_generates_vision_candidates(tmp_path):
    module = _load_script("update_openrouter_model_profiles")
    output_path = tmp_path / "openrouter_candidates.py"
    catalog_path = tmp_path / "models.json"
    catalog_path.write_text(
        json.dumps(
            {
                "data": [
                    {
                        "id": "google/gemma-4-31b-it",
                        "context_length": 262144,
                        "architecture": {
                            "input_modalities": ["image", "text"],
                            "output_modalities": ["text"],
                        },
                        "top_provider": {"max_completion_tokens": 131072},
                        "supported_parameters": ["max_tokens", "response_format"],
                    },
                    {
                        "id": "openai/gpt-5.4-nano",
                        "context_length": 400000,
                        "architecture": {
                            "input_modalities": ["file", "image", "text"],
                            "output_modalities": ["text"],
                        },
                        "top_provider": {"max_completion_tokens": 128000},
                        "supported_parameters": ["max_tokens", "response_format", "structured_outputs"],
                    },
                    {
                        "id": "z-ai/glm-5.1",
                        "context_length": 202752,
                        "architecture": {
                            "input_modalities": ["text"],
                            "output_modalities": ["text"],
                        },
                        "top_provider": {"max_completion_tokens": 65535},
                        "supported_parameters": ["max_tokens"],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    result = module.main(
        [
            "--catalog-json",
            str(catalog_path),
            "--output",
            str(output_path),
            "--top-n",
            "1",
            "--reviewed-on",
            "2026-04-12",
        ]
    )

    output = output_path.read_text(encoding="utf-8")
    assert result == 0
    assert "google/gemma-4-31b-it" in output
    assert "openai/gpt-5.4-nano" in output
    assert "z-ai/glm-5.1" not in output
    assert "context_length=400000" in output
    assert "last_reviewed='2026-04-12'" in output


def test_docker_runtime_install_path_keeps_pillow_in_main_dependencies():
    dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    main_dependencies = pyproject["project"]["dependencies"]

    assert "RUN poetry install --no-interaction --no-ansi --no-root --only main" in dockerfile
    assert any(dependency.startswith("pillow ") for dependency in main_dependencies)


def test_build_addon_creates_zip_and_skips_ignored_files(tmp_path, monkeypatch, capsys):
    module = _load_script("build_addon")
    project_root = tmp_path / "project"
    addon_dir = project_root / "blender_addon"
    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir(parents=True)
    (addon_dir / "__pycache__").mkdir(parents=True)
    (addon_dir / "__init__.py").write_text("print('addon')\n")
    (addon_dir / "keep.txt").write_text("keep\n")
    (addon_dir / "skip.pyc").write_bytes(b"pyc")
    (addon_dir / "__pycache__" / "cached.pyc").write_bytes(b"pyc")
    monkeypatch.setattr(module, "__file__", str(scripts_dir / "build_addon.py"))

    stale_zip = project_root / "outputs" / "blender_ai_mcp.zip"
    stale_zip.parent.mkdir(parents=True)
    stale_zip.write_bytes(b"stale")

    module.build_addon()

    out = capsys.readouterr().out
    assert "Removed old build" in out
    assert stale_zip.exists()

    with zipfile.ZipFile(stale_zip) as archive:
        names = set(archive.namelist())

    assert "blender_ai_mcp/__init__.py" in names
    assert "blender_ai_mcp/keep.txt" in names
    assert all("__pycache__" not in name for name in names)
    assert all(not name.endswith(".pyc") for name in names)


def test_run_e2e_build_addon_reports_success_and_failure(tmp_path, monkeypatch):
    module = _load_script("run_e2e_tests")
    addon_output = tmp_path / "outputs" / "blender_ai_mcp.zip"
    addon_output.parent.mkdir(parents=True)
    monkeypatch.setattr(module, "ADDON_OUTPUT", addon_output)
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(module, "BUILD_SCRIPT", tmp_path / "scripts" / "build_addon.py")

    success_result = types.SimpleNamespace(returncode=0, stderr="")
    failure_result = types.SimpleNamespace(returncode=1, stderr="boom")
    mock_run = MagicMock(side_effect=[success_result, failure_result])
    monkeypatch.setattr(module.subprocess, "run", mock_run)

    addon_output.write_bytes(b"zip")
    assert module.build_addon() is True
    assert module.build_addon() is False


def test_wait_for_rpc_server_retries_until_ready(monkeypatch):
    module = _load_script("run_e2e_tests")

    class FakeSocket:
        def __init__(self, results):
            self._results = results

        def settimeout(self, _timeout):
            return None

        def connect_ex(self, _addr):
            return self._results.pop(0)

        def close(self):
            return None

    attempts = [1, 1, 0]
    monkeypatch.setattr(module.socket, "socket", lambda *args, **kwargs: FakeSocket(attempts))
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)

    assert module.wait_for_rpc_server(timeout=3) is True


def test_select_rpc_port_for_run_uses_fallback_when_default_is_busy(monkeypatch):
    module = _load_script("run_e2e_tests")

    monkeypatch.setattr(module, "_port_is_listening", lambda host, port: True)

    class FakeSocket:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def bind(self, address):
            self._address = address

        def setsockopt(self, *_args):
            return None

        def getsockname(self):
            return ("127.0.0.1", 9123)

    monkeypatch.setattr(module.socket, "socket", lambda *args, **kwargs: FakeSocket())

    assert module.select_rpc_port_for_run() == 9123


def test_find_blender_path_uses_custom_and_path_lookup(tmp_path, monkeypatch):
    module = _load_script("run_e2e_tests")

    custom = tmp_path / "Blender"
    custom.write_text("")
    assert module.find_blender_path(str(custom)) == str(custom)

    monkeypatch.setattr(module.sys, "platform", "linux")
    monkeypatch.setitem(module.BLENDER_PATHS, "linux", "/missing/blender")
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *args, **kwargs: types.SimpleNamespace(returncode=0, stdout="/usr/local/bin/blender\n"),
    )
    assert module.find_blender_path() == "/usr/local/bin/blender"


def test_check_install_uninstall_helpers_use_subprocess(tmp_path, monkeypatch):
    module = _load_script("run_e2e_tests")
    addons_dir = tmp_path / "_tmp_addons"
    addon_dir = addons_dir / module.ADDON_NAME
    addons_dir.mkdir(parents=True)
    addon_dir.mkdir()
    (addon_dir / "__init__.py").write_text("# test addon\n", encoding="utf-8")

    monkeypatch.setattr(module, "resolve_blender_addons_dir", lambda _path: addons_dir)

    assert module.check_addon_installed("/Applications/Blender") is True
    assert module.uninstall_addon("/Applications/Blender") is True
    assert addon_dir.exists() is False

    module.ADDON_OUTPUT = REPO_ROOT / "outputs" / "blender_ai_mcp.zip"
    assert module.install_addon("/Applications/Blender") is True
    assert (addons_dir / module.ADDON_NAME / "__init__.py").exists() is True


def test_run_blender_with_rpc_and_kill_process(monkeypatch):
    module = _load_script("run_e2e_tests")

    process = MagicMock()
    process.pid = 123
    process.wait.return_value = 0

    popen = MagicMock(return_value=process)
    monkeypatch.setattr(module.subprocess, "Popen", popen)
    monkeypatch.setattr(module, "wait_for_rpc_server", lambda timeout=module.RPC_TIMEOUT: True)
    monkeypatch.setattr(module.os, "getpgid", lambda pid: pid)
    kill_calls = []
    monkeypatch.setattr(module.os, "killpg", lambda pgid, sig: kill_calls.append((pgid, sig)))

    started_process, ready, runtime_log_path = module.run_blender_with_rpc("/Applications/Blender")
    assert started_process is process
    assert ready is True
    assert runtime_log_path.name.startswith("blender_runtime_")
    assert runtime_log_path.exists()
    bootstrap_script_path = runtime_log_path.with_suffix(".bootstrap.py")
    command = popen.call_args.args[0]
    assert command == ["/Applications/Blender", "--python", str(bootstrap_script_path)]
    assert popen.call_args.kwargs["env"]["BLENDER_RPC_PORT"] == str(module.RPC_PORT)
    assert bootstrap_script_path.exists() is False

    module.kill_blender_process(process)
    assert kill_calls


def test_save_test_log_and_main_happy_path(tmp_path, monkeypatch):
    module = _load_script("run_e2e_tests")

    addon_output = tmp_path / "outputs" / "blender_ai_mcp.zip"
    addon_output.parent.mkdir(parents=True)
    addon_output.write_bytes(b"zip")
    e2e_dir = tmp_path / "tests" / "e2e"
    e2e_dir.mkdir(parents=True)

    monkeypatch.setattr(module, "ADDON_OUTPUT", addon_output)
    monkeypatch.setattr(module, "E2E_TESTS_DIR", e2e_dir)
    monkeypatch.setattr(module, "find_blender_path", lambda _path=None: "/Applications/Blender")
    monkeypatch.setattr(module, "select_rpc_port_for_run", lambda: 9911)
    monkeypatch.setattr(module, "check_addon_installed", lambda _path: False)
    monkeypatch.setattr(module, "install_addon", lambda _path: True)
    runtime_log = e2e_dir / "blender_runtime_test.log"
    runtime_log.write_text("runtime ok\n", encoding="utf-8")
    monkeypatch.setattr(module, "run_blender_with_rpc", lambda _path: (MagicMock(), True, runtime_log))
    monkeypatch.setattr(module, "run_e2e_tests", lambda verbose=True: (True, "OK"))
    monkeypatch.setattr(module, "kill_blender_process", lambda process: None)
    monkeypatch.setattr(module.sys, "argv", ["run_e2e_tests.py", "--skip-build", "--quiet"])

    result = module.main()
    assert result == 0
    assert module.RPC_PORT == 9911
    assert os.environ["BLENDER_RPC_PORT"] == "9911"

    logs = sorted(e2e_dir.glob("e2e_test_PASSED_*.log"))
    assert logs
    assert "Status: PASSED" in logs[0].read_text()
    assert str(runtime_log) in logs[0].read_text()


def test_run_e2e_tests_verbose_streams_output(monkeypatch):
    module = _load_script("run_e2e_tests")

    class FakeProcess:
        def __init__(self):
            self.stdout = iter(["line 1\n", "line 2\n"])
            self.returncode = 0

        def wait(self):
            return 0

    monkeypatch.setattr(module.subprocess, "Popen", lambda *args, **kwargs: FakeProcess())

    success, output = module.run_e2e_tests(verbose=True)

    assert success is True
    assert "line 1" in output
    assert "line 2" in output


def test_save_test_log_includes_blender_runtime_tail(tmp_path, monkeypatch):
    module = _load_script("run_e2e_tests")
    monkeypatch.setattr(module, "E2E_TESTS_DIR", tmp_path)

    runtime_log = tmp_path / "blender_runtime_123.log"
    runtime_log.write_text("line a\nline b\nline c\n", encoding="utf-8")

    saved = module.save_test_log("pytest output", False, blender_log_path=runtime_log)

    content = saved.read_text(encoding="utf-8")
    assert str(runtime_log) in content
    assert "line a" in content
    assert "pytest output" in content


def test_translate_docs_helpers_cover_local_parsing_paths(tmp_path):
    module = _load_script("translate_docs")

    env_file = tmp_path / ".env"
    env_file.write_text(
        "# comment\nOPENAI_API_KEY='secret'\nOPENAI_MODEL=\"gpt-test\"\nINVALID_LINE\n\n",
        encoding="utf-8",
    )

    assert module.default_endpoint("responses").endswith("/responses")
    assert module.default_endpoint("chat").endswith("/chat/completions")
    with pytest.raises(ValueError):
        module.default_endpoint("unknown")

    assert module.looks_non_english("To jest stół i ławka.") is True
    assert module.looks_non_english("This is a clean English sentence.") is False
    assert module.load_env_file(env_file) == {
        "OPENAI_API_KEY": "secret",
        "OPENAI_MODEL": "gpt-test",
    }
    assert module.unwrap_full_document_code_fence("```md\nHello\n```\n") == "Hello\n"
    assert module._extract_openai_error_code('{"error": {"code": "rate_limit"}}') == "rate_limit"
    assert module._extract_openai_error_code("not-json") is None
    assert (
        module._parse_responses_text(
            {
                "output": [
                    {
                        "content": [
                            {"text": "Hello "},
                            {"text": "World"},
                        ]
                    }
                ]
            }
        )
        == "Hello World"
    )


def test_translate_docs_openai_translate_handles_success_and_retry(monkeypatch):
    module = _load_script("translate_docs")
    cfg = module.OpenAIConfig(api_key="secret", model="gpt-test", api="responses", endpoint="https://example.test")

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"output":[{"content":[{"text":"Translated"}]}]}'

    attempts = {"count": 0}

    def fake_urlopen(req, timeout):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise urllib.error.URLError("temporary")
        return FakeResponse()

    monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)

    assert module.openai_translate(cfg, "tekst") == "Translated\n"
    assert attempts["count"] == 2


def test_translate_docs_main_dry_run_and_output_root(tmp_path, monkeypatch, capsys):
    module = _load_script("translate_docs")

    root = tmp_path / "_docs"
    root.mkdir()
    (root / "pl.md").write_text("To jest stół.\n", encoding="utf-8")
    (root / "en.md").write_text("This is already English.\n", encoding="utf-8")
    output_root = tmp_path / "_docs_en"

    dry_run_result = module.main(["--root", str(root), "--dry-run"])
    assert dry_run_result == 0
    dry_run_output = capsys.readouterr().out
    assert "pl.md" in dry_run_output

    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    monkeypatch.setattr(module, "openai_translate", lambda cfg, source_text: "Translated doc\n")

    result = module.main(["--root", str(root), "--output-root", str(output_root)])
    assert result == 0
    assert (output_root / "pl.md").read_text(encoding="utf-8") == "Translated doc\n"
    assert (output_root / "en.md").read_text(encoding="utf-8") == "This is already English.\n"


def test_vision_harness_requires_inputs_and_can_build_bundle_request(tmp_path, monkeypatch, capsys):
    module = _load_script("vision_harness")

    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(
        '{"bundle_id":"bundle_1","target_object":"Housing","preset_names":["context_wide"],"captures_before":[{"label":"before_1","image_path":"/tmp/before.jpg","media_type":"image/jpeg"}],"captures_after":[{"label":"after_1","image_path":"/tmp/after.jpg","media_type":"image/jpeg"}]}',
        encoding="utf-8",
    )
    refs_path = tmp_path / "references.json"
    refs_path.write_text(
        '{"references":[{"reference_id":"ref_1","goal":"rounded housing","label":"front_reference","media_type":"image/png","source_kind":"local_path","original_path":"/tmp/ref.png","stored_path":"/tmp/ref_stored.png","added_at":"2026-03-26T00:00:00Z"}]}',
        encoding="utf-8",
    )

    async def _fake_run(args):
        request = module._build_request_from_args(args)
        return [
            {
                "backend": "mlx_local",
                "status": "success",
                "result": {"goal": request.goal, "image_count": len(request.images)},
            }
        ]

    monkeypatch.setattr(module, "_run", _fake_run)

    result = module.main(
        [
            "--backend",
            "mlx_local",
            "--goal",
            "rounded housing",
            "--bundle-json",
            str(bundle_path),
            "--references-json",
            str(refs_path),
        ]
    )

    assert result == 0
    output = capsys.readouterr().out
    assert '"backend": "mlx_local"' in output
    assert '"image_count": 3' in output


def test_vision_harness_rejects_missing_inputs():
    module = _load_script("vision_harness")

    with pytest.raises(SystemExit):
        module.main(["--goal", "rounded housing"])


def test_vision_harness_can_build_openrouter_backend_config():
    module = _load_script("vision_harness")

    args = module.build_parser().parse_args(
        [
            "--backend",
            "openai_compatible_external",
            "--goal",
            "rounded housing",
            "--before",
            "/tmp/before.png",
            "--external-provider",
            "openrouter",
            "--external-contract-profile",
            "google_family_compare",
            "--openrouter-model",
            "google/gemma-3-27b-it:free",
            "--openrouter-api-key-env",
            "OPENROUTER_API_KEY",
            "--openrouter-site-url",
            "https://example.com",
            "--openrouter-site-name",
            "blender-ai-mcp-dev",
        ]
    )

    config = module._config_for_backend(args, "openai_compatible_external")

    assert config.VISION_EXTERNAL_PROVIDER == "openrouter"
    assert config.VISION_EXTERNAL_CONTRACT_PROFILE == "google_family_compare"
    assert config.VISION_OPENROUTER_MODEL == "google/gemma-3-27b-it:free"
    assert config.VISION_OPENROUTER_API_KEY_ENV == "OPENROUTER_API_KEY"
    assert config.VISION_OPENROUTER_SITE_URL == "https://example.com"
    assert config.VISION_OPENROUTER_SITE_NAME == "blender-ai-mcp-dev"


def test_vision_harness_can_build_gemini_backend_config():
    module = _load_script("vision_harness")

    args = module.build_parser().parse_args(
        [
            "--backend",
            "openai_compatible_external",
            "--goal",
            "rounded housing",
            "--before",
            "/tmp/before.png",
            "--external-provider",
            "google_ai_studio",
            "--external-contract-profile",
            "generic_full",
            "--gemini-model",
            "gemini-2.5-flash",
            "--gemini-api-key-env",
            "GEMINI_API_KEY",
        ]
    )

    config = module._config_for_backend(args, "openai_compatible_external")

    assert config.VISION_EXTERNAL_PROVIDER == "google_ai_studio"
    assert config.VISION_EXTERNAL_CONTRACT_PROFILE == "generic_full"
    assert config.VISION_GEMINI_MODEL == "gemini-2.5-flash"
    assert config.VISION_GEMINI_API_KEY_ENV == "GEMINI_API_KEY"


def test_vision_harness_fixture_only_reference_understanding_keeps_backend_path_opt_in(capsys):
    module = _load_script("vision_harness")

    result = module.main(
        [
            "--backend",
            "mlx_local",
            "--goal",
            "low poly squirrel",
            "--reference",
            "/tmp/ref.png",
            "--fixture-only",
            "reference-understanding",
        ]
    )

    assert result == 0
    output = capsys.readouterr().out
    assert '"status": "fixture_only"' in output
    assert '"fixture_only_mode": "reference-understanding"' in output
    assert '"goal": "low poly squirrel"' in output
    assert '"image_count": 1' in output
    assert '"image_roles": [' in output
    assert '"mode": "reference_understanding"' in output


def test_vision_harness_reliability_scorecard_is_default_off(capsys):
    module = _load_script("vision_harness")

    result = module.main(
        [
            "--backend",
            "mlx_local",
            "--goal",
            "low poly squirrel",
            "--reference",
            "/tmp/ref.png",
            "--fixture-only",
            "reference-understanding",
        ]
    )

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    assert "reliability_scorecard" not in payload[0]


def test_vision_harness_reliability_scorecard_is_opt_in(capsys):
    module = _load_script("vision_harness")

    result = module.main(
        [
            "--backend",
            "mlx_local",
            "--goal",
            "low poly squirrel",
            "--reference",
            "/tmp/ref.png",
            "--fixture-only",
            "reference-understanding",
            "--emit-reliability-scorecard",
        ]
    )

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    scorecard = payload[0]["reliability_scorecard"]
    assert scorecard["advisory_only"] is True
    assert [axis["axis"] for axis in scorecard["axes"]] == [
        "object_identity",
        "mark_correspondence",
        "spatial_direction",
        "depth_ordering",
        "contact_support",
        "shape_profile",
    ]
    assert {axis["status"] for axis in scorecard["axes"]} == {"skipped"}


def test_vision_harness_fixture_only_reference_understanding_bundle_uses_reference_images_only(
    tmp_path,
    monkeypatch,
    capsys,
):
    module = _load_script("vision_harness")
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(
        json.dumps(
            {
                "bundle_id": "bundle_1",
                "target_object": "Housing",
                "preset_names": ["context_wide"],
                "captures_before": [
                    {
                        "label": "before_1",
                        "image_path": str(tmp_path / "before.jpg"),
                        "media_type": "image/jpeg",
                    }
                ],
                "captures_after": [
                    {
                        "label": "after_1",
                        "image_path": str(tmp_path / "after.jpg"),
                        "media_type": "image/jpeg",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    refs_path = tmp_path / "references.json"
    refs_path.write_text(
        json.dumps(
            {
                "references": [
                    {
                        "reference_id": "ref_1",
                        "goal": "rounded housing",
                        "label": "front_reference",
                        "media_type": "image/png",
                        "source_kind": "local_path",
                        "original_path": str(tmp_path / "ref.png"),
                        "stored_path": str(tmp_path / "ref.png"),
                        "host_visible_path": str(tmp_path / "ref.png"),
                        "added_at": "2026-03-26T00:00:00Z",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = module.main(
        [
            "--backend",
            "mlx_local",
            "--goal",
            "rounded housing",
            "--bundle-json",
            str(bundle_path),
            "--references-json",
            str(refs_path),
            "--fixture-only",
            "reference-understanding",
        ]
    )

    assert result == 0
    output = capsys.readouterr().out
    assert '"fixture_only_mode": "reference-understanding"' in output
    assert '"image_count": 1' in output
    assert '"image_roles": [' in output
    assert '"reference"' in output
    assert '"before"' not in output
    assert '"after"' not in output


def test_vision_harness_live_reference_understanding_mode_uses_reference_images_only(tmp_path, monkeypatch, capsys):
    module = _load_script("vision_harness")

    async def _fake_run(args):
        request = module._build_request_from_args(args)
        return [
            {
                "backend": "mlx_local",
                "status": "success",
                "result": {
                    "goal": request.goal,
                    "image_count": len(request.images),
                    "image_roles": [image.role for image in request.images],
                    "metadata": request.metadata,
                },
            }
        ]

    monkeypatch.setattr(module, "_run", _fake_run)

    reference_path = tmp_path / "reference.png"
    reference_path.write_bytes(b"ref")

    result = module.main(
        [
            "--backend",
            "mlx_local",
            "--goal",
            "low poly squirrel",
            "--mode",
            "reference-understanding",
            "--reference",
            str(reference_path),
        ]
    )

    assert result == 0
    output = capsys.readouterr().out
    assert '"image_count": 1' in output
    assert '"image_roles": [' in output
    assert '"mode": "reference_understanding"' in output


@pytest.mark.parametrize(
    ("argv", "expected_backend"),
    [
        (
            [
                "--backend",
                "mlx_local",
                "--goal",
                "low poly squirrel",
                "--mode",
                "reference-understanding",
            ],
            "mlx_local",
        ),
        (
            [
                "--backend",
                "openai_compatible_external",
                "--goal",
                "low poly squirrel",
                "--mode",
                "reference-understanding",
                "--external-provider",
                "openrouter",
                "--external-contract-profile",
                "generic_full",
                "--openrouter-model",
                "qwen/qwen3-vl-32b-instruct",
                "--openrouter-api-key-env",
                "OPENROUTER_API_KEY",
            ],
            "openai_compatible_external",
        ),
    ],
)
def test_vision_harness_live_reference_understanding_executes_backend_path(
    tmp_path,
    monkeypatch,
    capsys,
    argv,
    expected_backend,
):
    module = _load_script("vision_harness")
    reference_path = tmp_path / "reference.png"
    reference_path.write_bytes(b"ref")
    captured: dict[str, object] = {}

    class FakeBackend:
        def __init__(self) -> None:
            self.last_output_diagnostics = {"provider_path": "backend-executed"}

        async def analyze(self, request):
            captured["metadata"] = dict(request.metadata)
            captured["roles"] = [image.role for image in request.images]
            return {"status": "available", "understanding_id": "understanding_live_harness"}

    monkeypatch.setattr(module, "create_vision_backend", lambda runtime: FakeBackend())

    result = module.main([*argv, "--reference", str(reference_path)])

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["backend"] == expected_backend
    assert payload[0]["status"] == "success"
    assert payload[0]["diagnostics"] == {"provider_path": "backend-executed"}
    assert captured["metadata"] == {
        "mode": "reference_understanding",
        "reference_ids": ["fixture_ref_1"],
        "source": "vision_harness",
    }
    assert captured["roles"] == ["reference"]


def test_vision_harness_live_reference_understanding_executes_bundle_backend_path(
    tmp_path,
    monkeypatch,
    capsys,
):
    module = _load_script("vision_harness")
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(
        json.dumps(
            {
                "bundle_id": "bundle_1",
                "target_object": "Housing",
                "preset_names": ["context_wide"],
                "captures_before": [
                    {
                        "label": "before_1",
                        "image_path": str(tmp_path / "before.jpg"),
                        "media_type": "image/jpeg",
                    }
                ],
                "captures_after": [
                    {
                        "label": "after_1",
                        "image_path": str(tmp_path / "after.jpg"),
                        "media_type": "image/jpeg",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    refs_path = tmp_path / "references.json"
    refs_path.write_text(
        json.dumps(
            {
                "references": [
                    {
                        "reference_id": "ref_1",
                        "goal": "rounded housing",
                        "label": "front_reference",
                        "media_type": "image/png",
                        "source_kind": "local_path",
                        "original_path": str(tmp_path / "ref.png"),
                        "stored_path": str(tmp_path / "ref.png"),
                        "host_visible_path": str(tmp_path / "ref.png"),
                        "added_at": "2026-03-26T00:00:00Z",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    class FakeBackend:
        def __init__(self) -> None:
            self.last_output_diagnostics = {"provider_path": "bundle-backend-executed"}

        async def analyze(self, request):
            captured["metadata"] = dict(request.metadata)
            captured["roles"] = [image.role for image in request.images]
            return {"status": "available", "understanding_id": "understanding_bundle_harness"}

    monkeypatch.setattr(module, "create_vision_backend", lambda runtime: FakeBackend())

    result = module.main(
        [
            "--backend",
            "mlx_local",
            "--goal",
            "rounded housing",
            "--mode",
            "reference-understanding",
            "--bundle-json",
            str(bundle_path),
            "--references-json",
            str(refs_path),
        ]
    )

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["status"] == "success"
    assert payload[0]["diagnostics"] == {"provider_path": "bundle-backend-executed"}
    assert captured["metadata"] == {
        "mode": "reference_understanding",
        "reference_ids": ["ref_1"],
        "source": "vision_harness",
    }
    assert captured["roles"] == ["reference"]


def test_vision_harness_reference_understanding_mode_rejects_missing_reference_inputs():
    module = _load_script("vision_harness")

    with pytest.raises(SystemExit):
        module.main(
            [
                "--backend",
                "mlx_local",
                "--goal",
                "low poly squirrel",
                "--mode",
                "reference-understanding",
            ]
        )


def test_vision_harness_reference_understanding_mode_rejects_bundle_without_reference_inputs():
    module = _load_script("vision_harness")

    with pytest.raises(SystemExit):
        module.main(
            [
                "--backend",
                "mlx_local",
                "--goal",
                "low poly squirrel",
                "--mode",
                "reference-understanding",
                "--bundle-json",
                "/tmp/bundle.json",
            ]
        )


def test_vision_harness_fixture_only_localized_support_keeps_owner_path_opt_in(capsys):
    module = _load_script("vision_harness")

    result = module.main(
        [
            "--backend",
            "mlx_local",
            "--goal",
            "low poly squirrel",
            "--mode",
            "localized-support",
            "--target-object",
            "Squirrel_Body",
            "--target-view",
            "front",
            "--localized-support-reason",
            "part_missing_ambiguity",
            "--localized-support-query-label",
            "tail_mass",
            "--after",
            "/tmp/after.png",
            "--reference",
            "/tmp/ref.png",
            "--fixture-only",
            "localized-support",
        ]
    )

    assert result == 0
    output = capsys.readouterr().out
    assert '"status": "fixture_only"' in output
    assert '"fixture_only_mode": "localized-support"' in output
    assert '"localized_support_reason": "part_missing_ambiguity"' in output
    assert '"query_labels": [' in output
    assert '"tail_mass"' in output


def test_vision_harness_fixture_only_localized_support_accepts_references_json_without_inline_reference(
    tmp_path, capsys
):
    module = _load_script("vision_harness")
    references_path = tmp_path / "references.json"
    after_path = tmp_path / "after.png"
    after_path.write_bytes(b"after")
    references_path.write_text(
        json.dumps(
            {
                "references": [
                    {
                        "reference_id": "ref_1",
                        "goal": "low poly squirrel",
                        "label": "front_reference",
                        "target_object": "Squirrel_Body",
                        "target_view": "front",
                        "media_type": "image/png",
                        "source_kind": "local_path",
                        "original_path": str((tmp_path / "front_ref.png").resolve()),
                        "stored_path": str((tmp_path / "front_ref.png").resolve()),
                        "host_visible_path": str((tmp_path / "front_ref.png").resolve()),
                        "added_at": "2026-05-23T00:00:00Z",
                    }
                ]
            }
        )
    )

    result = module.main(
        [
            "--backend",
            "mlx_local",
            "--goal",
            "low poly squirrel",
            "--mode",
            "localized-support",
            "--target-object",
            "Squirrel_Body",
            "--target-view",
            "front",
            "--localized-support-query-label",
            "tail_mass",
            "--after",
            str(after_path),
            "--references-json",
            str(references_path),
            "--fixture-only",
            "localized-support",
        ]
    )

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    row = payload[0]
    assert row["status"] == "fixture_only"
    assert row["result"]["reference_count"] == 1
    assert row["result"]["query_labels"] == ["tail_mass"]


def test_vision_harness_localized_support_mode_rejects_missing_query_label():
    module = _load_script("vision_harness")

    with pytest.raises(SystemExit):
        module.main(
            [
                "--backend",
                "mlx_local",
                "--goal",
                "low poly squirrel",
                "--mode",
                "localized-support",
                "--after",
                "/tmp/after.png",
                "--reference",
                "/tmp/ref.png",
            ]
        )


def test_vision_harness_live_localized_support_reports_disabled_by_default(tmp_path, monkeypatch, capsys):
    module = _load_script("vision_harness")
    reference_path = tmp_path / "reference.png"
    after_path = tmp_path / "after.png"
    reference_path.write_bytes(b"ref")
    after_path.write_bytes(b"after")

    result = module.main(
        [
            "--backend",
            "mlx_local",
            "--goal",
            "low poly squirrel",
            "--mode",
            "localized-support",
            "--target-object",
            "Squirrel_Body",
            "--target-view",
            "front",
            "--localized-support-query-label",
            "tail_mass",
            "--after",
            str(after_path),
            "--reference",
            str(reference_path),
        ]
    )

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    row = payload[0]
    assert row["status"] == "success"
    assert row["localized_optional_mode"] == "packet_support"
    assert row["result"]["part_segmentation"]["status"] == "disabled"


def test_vision_harness_live_localized_support_does_not_require_primary_backend_config(tmp_path, monkeypatch, capsys):
    module = _load_script("vision_harness")
    reference_path = tmp_path / "reference.png"
    after_path = tmp_path / "after.png"
    reference_path.write_bytes(b"ref")
    after_path.write_bytes(b"after")

    result = module.main(
        [
            "--backend",
            "openai_compatible_external",
            "--goal",
            "low poly squirrel",
            "--mode",
            "localized-support",
            "--target-object",
            "Squirrel_Body",
            "--target-view",
            "front",
            "--localized-support-query-label",
            "tail_mass",
            "--after",
            str(after_path),
            "--reference",
            str(reference_path),
        ]
    )

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    row = payload[0]
    assert row["status"] == "success"
    assert row["result"]["part_segmentation"]["status"] == "disabled"


def test_vision_harness_live_localized_support_threads_localization_candidates_into_segmentation(
    tmp_path, monkeypatch, capsys
):
    module = _load_script("vision_harness")
    reference_path = tmp_path / "reference.png"
    after_path = tmp_path / "after.png"
    reference_path.write_bytes(b"ref")
    after_path.write_bytes(b"after")
    monkeypatch.setenv("VISION_LOCALIZATION_ENABLED", "true")
    monkeypatch.setenv("VISION_LOCALIZATION_ENDPOINT", "http://localhost:9300/localize")
    monkeypatch.setenv("VISION_SEGMENTATION_ENABLED", "true")
    monkeypatch.setenv("VISION_SEGMENTATION_ENDPOINT", "http://localhost:9100/segment")

    captured: dict[str, object] = {}

    async def _fake_localization(*, config, goal, packet, reference_records, captures):
        return (
            [
                module.compare_packets_area.VisionLocalizationCandidate(
                    packet_id=packet.packet_id,
                    query_label="tail_mass",
                    reference_id=reference_records[0].reference_id,
                    capture_label=captures[0].label,
                    target_view=packet.target_view,
                    confidence=0.88,
                    box_xyxy=(101.0, 44.0, 218.0, 162.0),
                    crop_path="/tmp/localization_tail_crop.png",
                )
            ],
            module.ReferencePartSegmentationContract(
                status="available",
                provider_name="generic_sidecar",
                advisory_only=True,
                parts=[
                    {
                        "part_label": "tail_mass",
                        "crop_path": "/tmp/localization_tail_crop.png",
                        "confidence": 0.88,
                        "landmarks": [{"landmark_id": "box_center", "x": 159.5, "y": 103.0}],
                    }
                ],
            ),
        )

    async def _fake_segmentation(
        *,
        config,
        goal,
        packet_id,
        packet_label,
        target_view,
        scope_label,
        target_objects,
        reference_records,
        captures,
        localization_candidates,
    ):
        captured["seed_query_labels"] = [item.query_label for item in localization_candidates]
        return module.ReferencePartSegmentationContract(
            status="available",
            provider_name="generic_sidecar",
            advisory_only=True,
            parts=[
                {
                    "part_label": "tail_profile",
                    "crop_path": "/tmp/tail_profile_crop.png",
                    "confidence": 0.91,
                    "landmarks": [],
                }
            ],
        )

    monkeypatch.setattr(module.compare_packets_area, "collect_compare_time_localization_support", _fake_localization)
    monkeypatch.setattr(module.compare_packets_area, "collect_compare_time_segmentation_support", _fake_segmentation)

    result = module.main(
        [
            "--backend",
            "mlx_local",
            "--goal",
            "low poly squirrel",
            "--mode",
            "localized-support",
            "--target-object",
            "Squirrel_Body",
            "--target-view",
            "front",
            "--localized-support-reason",
            "part_missing_ambiguity",
            "--localized-support-query-label",
            "tail_mass",
            "--after",
            str(after_path),
            "--reference",
            str(reference_path),
        ]
    )

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    row = payload[0]
    assert row["result"]["localization_candidate_count"] == 1
    assert row["result"]["part_segmentation"]["status"] == "available"
    assert captured["seed_query_labels"] == ["tail_mass"]


@pytest.mark.parametrize(
    ("notes", "expected_fragment"),
    [
        (["Optional compare-time localization unavailable: timeout"], "timeout"),
        (["Optional compare-time localization returned no bounded candidates for compare support."], "no bounded"),
    ],
)
def test_vision_harness_live_localized_support_surfaces_unavailable_and_empty_results(
    tmp_path, monkeypatch, capsys, notes, expected_fragment
):
    module = _load_script("vision_harness")
    reference_path = tmp_path / "reference.png"
    after_path = tmp_path / "after.png"
    reference_path.write_bytes(b"ref")
    after_path.write_bytes(b"after")
    monkeypatch.setenv("VISION_LOCALIZATION_ENABLED", "true")
    monkeypatch.setenv("VISION_LOCALIZATION_ENDPOINT", "http://localhost:9300/localize")

    async def _fake_localization(*, config, goal, packet, reference_records, captures):
        return (
            [],
            module.ReferencePartSegmentationContract(
                status="unavailable",
                provider_name="generic_sidecar",
                advisory_only=True,
                parts=[],
                notes=notes,
            ),
        )

    monkeypatch.setattr(module.compare_packets_area, "collect_compare_time_localization_support", _fake_localization)

    result = module.main(
        [
            "--backend",
            "mlx_local",
            "--goal",
            "low poly squirrel",
            "--mode",
            "localized-support",
            "--target-object",
            "Squirrel_Body",
            "--target-view",
            "front",
            "--localized-support-query-label",
            "tail_mass",
            "--after",
            str(after_path),
            "--reference",
            str(reference_path),
        ]
    )

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    row = payload[0]
    assert row["result"]["part_segmentation"]["status"] == "unavailable"
    assert expected_fragment in " ".join(row["result"]["part_segmentation"]["notes"])
