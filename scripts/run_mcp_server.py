#!/usr/bin/env python3
"""Interactive macOS-first launcher for blender-ai-mcp."""

from __future__ import annotations

import getpass
import os
import platform
import shutil
import subprocess
import sys
import webbrowser
from dataclasses import dataclass
from pathlib import Path

DOCKER_MAC_INSTALL_DOC_URL = "https://docs.docker.com/desktop/setup/install/mac-install/"
APPLE_MACOS_UPDATE_URL = "x-apple.systempreferences:com.apple.Software-Update-Settings.extension"
POETRY_INSTALLER_COMMAND = "curl -sSL https://install.python-poetry.org | python3 -"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_DOCKER_DMG = Path.home() / "Downloads" / "Docker.dmg"


@dataclass
class PythonRuntimeState:
    version: tuple[int, int, int]
    version_text: str
    machine: str
    is_macos: bool
    macos_version: str | None


@dataclass
class ToolState:
    installed: bool
    version: str | None


@dataclass
class DockerDesktopState:
    app_exists: bool
    cli_exists: bool
    daemon_ready: bool
    version: str | None
    dmg_path: Path


@dataclass
class LauncherPlan:
    enable_classifier: bool
    auto_start_classifier: bool
    classifier_endpoint: str | None
    classifier_model: str | None
    openrouter_model: str
    openrouter_api_key: str
    install_mlx: bool
    install_vision: bool


def _print_header(title: str) -> None:
    print(f"\n== {title} ==")


def _run_command(
    command: list[str],
    *,
    env: dict[str, str] | None = None,
    capture: bool = True,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        env=env,
        text=True,
        capture_output=capture,
        check=check,
    )


def _ask_yes_no(prompt: str, *, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    raw = input(f"{prompt} {suffix} ").strip().lower()
    if not raw:
        return default
    if raw in {"y", "yes"}:
        return True
    if raw in {"n", "no"}:
        return False
    print("Please answer yes or no.")
    return _ask_yes_no(prompt, default=default)


def _ask_text(prompt: str, *, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    raw = input(f"{prompt}{suffix}: ").strip()
    if raw:
        return raw
    if default is not None:
        return default
    return _ask_text(prompt, default=default)


def _ask_secret(prompt: str) -> str:
    value = getpass.getpass(f"{prompt}: ").strip()
    if value:
        return value
    print("This value cannot be empty.")
    return _ask_secret(prompt)


def _open_path_or_url(target: str) -> None:
    webbrowser.open(target)


def detect_python_runtime() -> PythonRuntimeState:
    macos_version = None
    if platform.system() == "Darwin":
        try:
            result = _run_command(["sw_vers", "-productVersion"], check=False)
            macos_version = result.stdout.strip() or None
        except Exception:
            macos_version = None
    return PythonRuntimeState(
        version=sys.version_info[:3],
        version_text=platform.python_version(),
        machine=platform.machine(),
        is_macos=platform.system() == "Darwin",
        macos_version=macos_version,
    )


def detect_poetry() -> ToolState:
    poetry_bin = shutil.which("poetry")
    if poetry_bin is None:
        return ToolState(installed=False, version=None)
    result = _run_command([poetry_bin, "--version"], check=False)
    version = (result.stdout or result.stderr).strip() or None
    return ToolState(installed=True, version=version)


def detect_docker_desktop() -> DockerDesktopState:
    docker_app = Path("/Applications/Docker.app")
    docker_bin = shutil.which("docker")
    version = None
    daemon_ready = False
    if docker_bin:
        version_result = _run_command([docker_bin, "--version"], check=False)
        version = (version_result.stdout or version_result.stderr).strip() or None
        daemon_result = _run_command([docker_bin, "info"], check=False)
        daemon_ready = daemon_result.returncode == 0
    return DockerDesktopState(
        app_exists=docker_app.exists(),
        cli_exists=docker_bin is not None,
        daemon_ready=daemon_ready,
        version=version,
        dmg_path=DEFAULT_DOCKER_DMG,
    )


def _ensure_macos(runtime: PythonRuntimeState) -> None:
    if runtime.is_macos:
        return
    raise SystemExit(
        "run_mcp_server.sh currently supports only macOS in v1. "
        "Linux and Windows are planned follow-ons under TASK-165."
    )


def _ensure_python_baseline(runtime: PythonRuntimeState) -> None:
    print(f"Python version: {runtime.version_text}")
    print(f"Machine: {runtime.machine}")
    if runtime.macos_version:
        print(f"macOS version: {runtime.macos_version}")
    if runtime.version < (3, 11, 0):
        raise SystemExit("This repo requires Python 3.11+.")


def _maybe_install_poetry(poetry: ToolState) -> None:
    _print_header("Poetry")
    if poetry.installed:
        print(f"Poetry detected: {poetry.version}")
        if _ask_yes_no("Do you want to keep the current Poetry version?", default=True):
            return
    else:
        print("Poetry is not installed.")

    if not _ask_yes_no("Do you want to run the official Poetry installer now?", default=False):
        raise SystemExit("Poetry is required to continue with the guided launcher.")

    subprocess.run(["bash", "-lc", POETRY_INSTALLER_COMMAND], cwd=str(REPO_ROOT), check=True)
    raise SystemExit(
        "Poetry installer completed. Restart your shell so the `poetry` command is on PATH, then rerun `./scripts/run_mcp_server.sh`."
    )


def _install_docker_from_dmg(dmg_path: Path) -> None:
    subprocess.run(["sudo", "hdiutil", "attach", str(dmg_path)], check=True)
    try:
        subprocess.run(
            ["sudo", "/Volumes/Docker/Docker.app/Contents/MacOS/install", "--accept-license"],
            check=True,
        )
    finally:
        subprocess.run(["sudo", "hdiutil", "detach", "/Volumes/Docker"], check=False)


def _ensure_docker_desktop() -> None:
    _print_header("Docker Desktop")
    state = detect_docker_desktop()
    if state.app_exists:
        print("Docker Desktop app detected: /Applications/Docker.app")
    else:
        print("Docker Desktop app is not installed.")

    if state.version:
        print(f"Docker CLI version: {state.version}")
        if _ask_yes_no("Do you want to keep the current Docker Desktop version?", default=True):
            if state.daemon_ready:
                print("Docker daemon is already reachable.")
                return
        else:
            print("Opening the official Docker Desktop for Mac install page.")
            _open_path_or_url(DOCKER_MAC_INSTALL_DOC_URL)
    elif not state.app_exists:
        if _ask_yes_no("Do you want to open the official Docker Desktop for Mac install page?", default=True):
            _open_path_or_url(DOCKER_MAC_INSTALL_DOC_URL)

    if state.dmg_path.exists() and _ask_yes_no(
        f"Found Docker installer at {state.dmg_path}. Install it now using the official CLI path?",
        default=False,
    ):
        _install_docker_from_dmg(state.dmg_path)

    if not state.app_exists or not state.daemon_ready:
        if _ask_yes_no("Do you want to open Docker Desktop now?", default=True):
            subprocess.run(["open", "-a", "Docker"], check=False)
            input("Wait for Docker Desktop to finish starting, then press Enter to continue...")

    refreshed = detect_docker_desktop()
    if not refreshed.daemon_ready:
        raise SystemExit(
            "Docker daemon is not reachable yet. Finish installing/starting Docker Desktop, then rerun the launcher."
        )


def _poetry_import_available(module_name: str) -> bool:
    result = _run_command(["poetry", "run", "python", "-c", f"import {module_name}"], check=False)
    return result.returncode == 0


def _maybe_install_poetry_groups(*groups: str) -> None:
    unique_groups = [group for group in groups if group]
    if not unique_groups:
        return
    _print_header("Repo Dependencies")
    group_text = ", ".join(unique_groups)
    print(f"Need Poetry dependency groups: {group_text}")
    if not _ask_yes_no(f"Install Poetry groups now ({group_text})?", default=True):
        return
    subprocess.run(["poetry", "install", "--with", ",".join(unique_groups)], cwd=str(REPO_ROOT), check=True)


def _ensure_optional_runtime_groups() -> tuple[bool, bool]:
    _print_header("Optional Runtime Groups")
    install_mlx = _ask_yes_no("Do you want to install MLX support for local model execution?", default=False)
    install_vision = _ask_yes_no(
        "Do you want to install optional vision dependencies for the local classifier sidecar?",
        default=True,
    )

    needed_groups: list[str] = []
    if install_mlx and not _poetry_import_available("mlx_vlm"):
        needed_groups.append("mlx")
    if install_vision and not _poetry_import_available("transformers"):
        needed_groups.append("vision")
    if needed_groups:
        _maybe_install_poetry_groups(*needed_groups)
    return install_mlx, install_vision


def _collect_launch_plan() -> LauncherPlan:
    _print_header("Runtime Profile")
    print("This macOS-first launcher currently supports the Docker-guided OpenRouter profile.")

    enable_classifier = _ask_yes_no("Do you want to enable the optional reference classifier?", default=True)
    auto_start_classifier = False
    classifier_endpoint = None
    classifier_model = None

    if enable_classifier:
        auto_start_classifier = _ask_yes_no(
            "Do you want the launcher to auto-start the local classifier sidecar?",
            default=True,
        )
        if auto_start_classifier:
            classifier_model = _ask_text(
                "Classifier model override",
                default=os.getenv("VISION_REFERENCE_CLASSIFIER_MODEL") or "google/siglip2-base-patch16-224",
            )
        else:
            classifier_endpoint = _ask_text(
                "Remote classifier endpoint",
                default=os.getenv("VISION_REFERENCE_CLASSIFIER_ENDPOINT") or "http://127.0.0.1:9200/classify",
            )
            classifier_model = _ask_text(
                "Classifier model label for bookkeeping",
                default=os.getenv("VISION_REFERENCE_CLASSIFIER_MODEL") or "google/siglip2-base-patch16-224",
            )

    openrouter_model = _ask_text(
        "OpenRouter model",
        default=os.getenv("VISION_OPENROUTER_MODEL") or "openai/gpt-5.4-mini",
    )
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY") or _ask_secret("Paste OPENROUTER_API_KEY for this launch")

    install_mlx, install_vision = _ensure_optional_runtime_groups()
    return LauncherPlan(
        enable_classifier=enable_classifier,
        auto_start_classifier=auto_start_classifier,
        classifier_endpoint=classifier_endpoint,
        classifier_model=classifier_model,
        openrouter_model=openrouter_model,
        openrouter_api_key=openrouter_api_key,
        install_mlx=install_mlx,
        install_vision=install_vision,
    )


def _run_streamable_openrouter(plan: LauncherPlan) -> int:
    env = os.environ.copy()
    env["OPENROUTER_API_KEY"] = plan.openrouter_api_key
    env["VISION_OPENROUTER_MODEL"] = plan.openrouter_model
    env["VISION_REFERENCE_CLASSIFIER_ENABLED"] = "true" if plan.enable_classifier else "false"
    if plan.enable_classifier:
        env["VISION_REFERENCE_CLASSIFIER_PROVIDER"] = "generic_sidecar"
        if plan.classifier_model:
            env["VISION_REFERENCE_CLASSIFIER_MODEL"] = plan.classifier_model
        env["REFERENCE_CLASSIFIER_AUTO_START"] = "true" if plan.auto_start_classifier else "false"
        if plan.classifier_endpoint:
            env["VISION_REFERENCE_CLASSIFIER_ENDPOINT"] = plan.classifier_endpoint
    else:
        env["REFERENCE_CLASSIFIER_AUTO_START"] = "false"

    print("\nFinal launch plan:")
    print(f"- OpenRouter model: {plan.openrouter_model}")
    print(f"- Reference classifier enabled: {plan.enable_classifier}")
    if plan.enable_classifier:
        if plan.auto_start_classifier:
            print("- Classifier sidecar: auto-start local")
            print(f"- Classifier model: {plan.classifier_model}")
        else:
            print(f"- Classifier endpoint: {plan.classifier_endpoint}")
            print(f"- Classifier model: {plan.classifier_model}")
    print(f"- Optional MLX dependencies requested: {plan.install_mlx}")
    print(f"- Optional vision dependencies requested: {plan.install_vision}")

    if not _ask_yes_no("Launch the MCP server now?", default=True):
        print("Launch cancelled by user.")
        return 0

    return subprocess.run(
        ["bash", str(SCRIPT_DIR / "run_streamable_openrouter.sh")],
        cwd=str(REPO_ROOT),
        env=env,
        check=False,
    ).returncode


def main(argv: list[str] | None = None) -> int:
    _print_header("blender-ai-mcp macOS-first launcher")
    print("This wizard checks prerequisites, explains each step, and can start the Docker-guided MCP profile.")
    runtime = detect_python_runtime()
    _ensure_macos(runtime)
    _ensure_python_baseline(runtime)
    _maybe_install_poetry(detect_poetry())
    _ensure_docker_desktop()
    plan = _collect_launch_plan()
    return _run_streamable_openrouter(plan)


if __name__ == "__main__":
    raise SystemExit(main())
