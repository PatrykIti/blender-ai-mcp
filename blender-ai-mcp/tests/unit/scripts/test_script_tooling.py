from __future__ import annotations

import importlib.util
import json
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
        "VISION_EXTERNAL_PROVIDER=openrouter",
        'VISION_EXTERNAL_CONTRACT_PROFILE="${VISION_EXTERNAL_CONTRACT_PROFILE}"',
        'VISION_OPENROUTER_MODEL="${VISION_OPENROUTER_MODEL}"',
        'VISION_OPENROUTER_REQUIRE_PARAMETERS="${VISION_OPENROUTER_REQUIRE_PARAMETERS}"',
        'VISION_OPENROUTER_ENABLE_RESPONSE_HEALING="${VISION_OPENROUTER_ENABLE_RESPONSE_HEALING}"',
        'VISION_OPENROUTER_PREFER_JSON_OBJECT_FOR_QWEN="${VISION_OPENROUTER_PREFER_JSON_OBJECT_FOR_QWEN}"',
    ):
        assert expected in script


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


def test_check_install_uninstall_helpers_use_subprocess(monkeypatch):
    module = _load_script("run_e2e_tests")

    monkeypatch.setattr(
        module.subprocess,
        "run",
        MagicMock(
            side_effect=[
                types.SimpleNamespace(stdout="ADDON_STATUS: INSTALLED", stderr=""),
                types.SimpleNamespace(stdout="UNINSTALL_STATUS: SUCCESS", stderr=""),
                types.SimpleNamespace(stdout="INSTALL_STATUS: SUCCESS", stderr=""),
            ]
        ),
    )

    assert module.check_addon_installed("/Applications/Blender") is True
    assert module.uninstall_addon("/Applications/Blender") is True
    assert module.install_addon("/Applications/Blender") is True


def test_run_blender_with_rpc_and_kill_process(monkeypatch):
    module = _load_script("run_e2e_tests")

    process = MagicMock()
    process.pid = 123
    process.wait.return_value = 0

    monkeypatch.setattr(module.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(module, "wait_for_rpc_server", lambda timeout=module.RPC_TIMEOUT: True)
    monkeypatch.setattr(module.os, "getpgid", lambda pid: pid)
    kill_calls = []
    monkeypatch.setattr(module.os, "killpg", lambda pgid, sig: kill_calls.append((pgid, sig)))

    started_process, ready, runtime_log_path = module.run_blender_with_rpc("/Applications/Blender")
    assert started_process is process
    assert ready is True
    assert runtime_log_path.name.startswith("blender_runtime_")
    assert runtime_log_path.exists()

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
    assert '"mode": "reference_understanding"' in output
