from __future__ import annotations

import importlib.util
import sys
import types
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
