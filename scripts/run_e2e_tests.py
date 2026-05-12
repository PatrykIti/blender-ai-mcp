#!/usr/bin/env python3
"""
E2E Test Runner for blender-ai-mcp.

This script automates the full E2E testing workflow:
1. Build the addon ZIP
2. Launch Blender and check addon status
3. Uninstall old addon if present (requires restart)
4. Install new addon
5. Run E2E tests
6. Save logs on failure
7. Cleanup Blender process

Usage:
    python scripts/run_e2e_tests.py
    python scripts/run_e2e_tests.py --blender-path /path/to/blender
    python scripts/run_e2e_tests.py --skip-build
"""

import argparse
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ADDON_OUTPUT = PROJECT_ROOT / "outputs" / "blender_ai_mcp.zip"
E2E_TESTS_DIR = PROJECT_ROOT / "tests" / "e2e"
BUILD_SCRIPT = PROJECT_ROOT / "scripts" / "build_addon.py"
ADDON_NAME = "blender_ai_mcp"

# Blender paths (platform-specific)
BLENDER_PATHS = {
    "darwin": "/Applications/Blender.app/Contents/MacOS/Blender",
    "linux": "/usr/bin/blender",
    "win32": r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
}

# RPC Config
RPC_HOST = os.environ.get("BLENDER_RPC_HOST", "127.0.0.1")
RPC_PORT = int(os.environ.get("BLENDER_RPC_PORT", "8765"))
RPC_TIMEOUT = 30  # seconds to wait for Blender RPC server


def log(msg: str, level: str = "INFO"):
    """Print timestamped log message."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERR": "❌", "RUN": "🚀"}.get(level, "•")
    print(f"[{timestamp}] {prefix} {msg}")


def create_blender_runtime_log_path() -> Path:
    """Return one timestamped Blender runtime log path for this runner session."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return E2E_TESTS_DIR / f"blender_runtime_{timestamp}.log"


def tail_log_file(path: Path, max_lines: int = 80) -> str:
    """Return the tail of a text log file, best-effort."""
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    return "\n".join(lines[-max_lines:])


def find_blender_path(custom_path: Optional[str] = None) -> str:
    """Find Blender executable path."""
    if custom_path and Path(custom_path).exists():
        return custom_path

    platform_path = BLENDER_PATHS.get(sys.platform)
    if platform_path and Path(platform_path).exists():
        return platform_path

    # Try to find in PATH
    try:
        result = subprocess.run(["which", "blender"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass

    raise FileNotFoundError(f"Blender not found. Please specify path with --blender-path. Checked: {platform_path}")


def build_addon() -> bool:
    """Build the addon ZIP file."""
    log("Building addon...", "RUN")
    try:
        result = subprocess.run(
            [sys.executable, str(BUILD_SCRIPT)], capture_output=True, text=True, cwd=str(PROJECT_ROOT)
        )
        if result.returncode != 0:
            log(f"Build failed: {result.stderr}", "ERR")
            return False

        if not ADDON_OUTPUT.exists():
            log(f"Build output not found: {ADDON_OUTPUT}", "ERR")
            return False

        log(f"Addon built: {ADDON_OUTPUT} ({ADDON_OUTPUT.stat().st_size / 1024:.1f} KB)", "OK")
        return True
    except Exception as e:
        log(f"Build error: {e}", "ERR")
        return False


def wait_for_rpc_server(timeout: int = RPC_TIMEOUT) -> bool:
    """Wait for Blender RPC server to become available."""
    log(f"Waiting for RPC server on {RPC_HOST}:{RPC_PORT}...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((RPC_HOST, RPC_PORT))
            sock.close()
            if result == 0:
                log("RPC server is ready!", "OK")
                return True
        except Exception:
            pass
        time.sleep(1)

    log(f"RPC server not available after {timeout}s", "ERR")
    return False


def _port_is_listening(host: str, port: int) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def select_rpc_port_for_run() -> int:
    """Return the preferred RPC port, or a temporary free port when it is already occupied."""

    if not _port_is_listening(RPC_HOST, RPC_PORT):
        return RPC_PORT

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((RPC_HOST, 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        selected_port = int(sock.getsockname()[1])

    log(
        f"Preferred RPC port {RPC_PORT} is already in use; falling back to free port {selected_port}.",
        "WARN",
    )
    return selected_port


def detect_blender_version_series(blender_path: str) -> str:
    """Return the Blender major.minor version for one executable path."""

    result = subprocess.run([blender_path, "--version"], capture_output=True, text=True, timeout=30)
    version_output = f"{result.stdout}\n{result.stderr}"
    match = re.search(r"Blender\s+(\d+\.\d+)", version_output)
    if match is None:
        raise RuntimeError(f"Could not determine Blender version from: {version_output.strip()}")
    return match.group(1)


def resolve_blender_addons_dir(blender_path: str) -> Path:
    """Resolve the per-version Blender addons directory without launching background Python."""

    version_series = detect_blender_version_series(blender_path)
    if sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support" / "Blender" / version_series
    elif sys.platform == "linux":
        root = Path.home() / ".config" / "blender" / version_series
    elif sys.platform == "win32":
        appdata = os.getenv("APPDATA")
        if not appdata:
            raise RuntimeError("APPDATA is not set, cannot resolve Blender addons directory on Windows.")
        root = Path(appdata) / "Blender Foundation" / "Blender" / version_series
    else:
        raise RuntimeError(f"Unsupported platform for Blender addons directory resolution: {sys.platform}")
    return root / "scripts" / "addons"


def check_addon_installed(blender_path: str) -> bool:
    """Check if blender_ai_mcp addon is installed."""
    log("Checking if addon is installed...")
    addon_dir = resolve_blender_addons_dir(blender_path) / ADDON_NAME
    is_installed = addon_dir.is_dir() and (addon_dir / "__init__.py").exists()
    log(f"Addon installed: {is_installed}", "OK" if is_installed else "INFO")
    return is_installed


def uninstall_addon(blender_path: str) -> bool:
    """Uninstall the blender_ai_mcp addon."""
    log("Uninstalling old addon...", "RUN")
    try:
        addon_dir = resolve_blender_addons_dir(blender_path) / ADDON_NAME
        if addon_dir.exists():
            shutil.rmtree(addon_dir)
            log(f"Removed addon directory: {addon_dir}", "INFO")
        log("Addon uninstalled successfully", "OK")
        return True
    except Exception as e:
        log(f"Uninstall failed: {e}", "ERR")
        return False


def install_addon(blender_path: str) -> bool:
    """Install the blender_ai_mcp addon files into the user addons directory."""
    log(f"Installing addon from {ADDON_OUTPUT}...", "RUN")
    try:
        addons_dir = resolve_blender_addons_dir(blender_path)
        addons_dir.mkdir(parents=True, exist_ok=True)
        addon_dir = addons_dir / ADDON_NAME
        if addon_dir.exists():
            shutil.rmtree(addon_dir)

        with zipfile.ZipFile(ADDON_OUTPUT, "r") as zip_ref:
            zip_ref.extractall(addons_dir)

        success = addon_dir.is_dir() and (addon_dir / "__init__.py").exists()
        if success:
            log("Addon files installed successfully", "OK")
        else:
            log(f"Install failed: extracted addon directory missing at {addon_dir}", "ERR")
        return success
    except Exception as e:
        log(f"Install failed: {e}", "ERR")
        return False


def run_blender_with_rpc(blender_path: str) -> Tuple[subprocess.Popen, bool, Path]:
    """Start Blender with RPC server running.

    Note: The addon's RPC server uses bpy.app.timers which requires
    Blender's main event loop to be running. Pure --background mode
    doesn't process timers, so we need to run Blender normally.
    """
    log("Starting Blender with RPC server...", "RUN")
    log("NOTE: Blender window will open - this is required for RPC server", "INFO")
    runtime_log_path = create_blender_runtime_log_path()
    runtime_log_path.parent.mkdir(parents=True, exist_ok=True)
    runtime_log_path.write_text(
        f"Blender runtime log started at {datetime.now().isoformat()}\n"
        f"Executable: {blender_path}\n"
        "============================================================\n",
        encoding="utf-8",
    )
    log(f"Blender runtime log: {runtime_log_path}", "INFO")
    bootstrap_script_path = runtime_log_path.with_suffix(".bootstrap.py")
    bootstrap_script_path.write_text(
        "\n".join(
            (
                "import addon_utils",
                "",
                f"addon_name = {ADDON_NAME!r}",
                "print(f'[E2E bootstrap] enabling {addon_name}')",
                "enabled, loaded = addon_utils.check(addon_name)",
                "print(f'[E2E bootstrap] before enable: enabled={enabled} loaded={loaded}')",
                "if not enabled:",
                "    addon_utils.enable(addon_name, default_set=False, persistent=False)",
                "enabled, loaded = addon_utils.check(addon_name)",
                "print(f'[E2E bootstrap] after enable: enabled={enabled} loaded={loaded}')",
            )
        )
        + "\n",
        encoding="utf-8",
    )

    # Start Blender normally - the addon will auto-start its RPC server
    # The addon is enabled for this session via a one-shot bootstrap script to
    # avoid depending on background preference writes during install helpers.
    blender_env = {
        **os.environ,
        "BLENDER_RPC_HOST": RPC_HOST,
        "BLENDER_RPC_PORT": str(RPC_PORT),
    }
    with runtime_log_path.open("ab") as runtime_log_handle:
        process = subprocess.Popen(
            [blender_path, "--python", str(bootstrap_script_path)],
            stdout=runtime_log_handle,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid if sys.platform != "win32" else None,
            env=blender_env,
        )

    # Wait for RPC server
    rpc_ready = wait_for_rpc_server()
    try:
        bootstrap_script_path.unlink(missing_ok=True)
    except Exception:
        pass
    if not rpc_ready and process.poll() is not None:
        log(f"Blender exited before RPC became ready. See runtime log: {runtime_log_path}", "ERR")
        tail = tail_log_file(runtime_log_path, max_lines=40)
        if tail:
            print(tail)

    return process, rpc_ready, runtime_log_path


def kill_blender_process(process: subprocess.Popen):
    """Terminate Blender process and all children."""
    log("Terminating Blender process...", "RUN")
    try:
        if sys.platform != "win32":
            # Kill the process group
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        else:
            process.terminate()

        # Wait for graceful shutdown
        process.wait(timeout=10)
        log("Blender terminated gracefully", "OK")
    except subprocess.TimeoutExpired:
        log("Force killing Blender...", "WARN")
        if sys.platform != "win32":
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        else:
            process.kill()
    except Exception as e:
        log(f"Error killing Blender: {e}", "WARN")


def run_e2e_tests(verbose: bool = True) -> Tuple[bool, str]:
    """Run E2E tests with pytest via poetry.

    Args:
        verbose: If True, stream output to console in real-time
    """
    log("Running E2E tests...", "RUN")
    print("-" * 60)

    if verbose:
        # Run with real-time output to console
        process = subprocess.Popen(
            ["poetry", "run", "pytest", str(E2E_TESTS_DIR), "-v", "--tb=short"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(PROJECT_ROOT),
            env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT)},
        )

        # Capture output while streaming to console
        assert process.stdout is not None
        output_lines = []
        for line in process.stdout:
            print(line, end="")  # Print to console
            output_lines.append(line)

        process.wait()
        success = process.returncode == 0
        output = "".join(output_lines)
    else:
        # Capture output silently
        result = subprocess.run(
            ["poetry", "run", "pytest", str(E2E_TESTS_DIR), "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT)},
        )
        output = f"{result.stdout}\n{result.stderr}"
        success = result.returncode == 0

    print("-" * 60)

    if success:
        log("E2E tests passed!", "OK")
    else:
        log("E2E tests failed!", "ERR")

    return success, output


def save_test_log(output: str, success: bool, blender_log_path: Path | None = None):
    """Save test output to log file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    status = "PASSED" if success else "FAILED"
    log_file = E2E_TESTS_DIR / f"e2e_test_{status}_{timestamp}.log"
    blender_log_tail = tail_log_file(blender_log_path, max_lines=80) if blender_log_path is not None else ""
    blender_log_section = ""
    if blender_log_path is not None:
        blender_log_section = (
            "\n"
            "Blender runtime log path:\n"
            f"{blender_log_path}\n"
            "\n"
            "Blender runtime log tail:\n"
            "--------------------------------------------------------------------------------\n"
            f"{blender_log_tail}\n"
            "--------------------------------------------------------------------------------\n"
        )

    log_content = f"""
================================================================================
E2E Test Run - {datetime.now().isoformat()}
Status: {status}
================================================================================
{blender_log_section}

{output}
"""

    log_file.write_text(log_content)
    log(f"Test log saved: {log_file}", "OK")
    return log_file


def main():
    parser = argparse.ArgumentParser(description="Run E2E tests for blender-ai-mcp")
    parser.add_argument("--blender-path", help="Path to Blender executable")
    parser.add_argument("--skip-build", action="store_true", help="Skip addon build step")
    parser.add_argument("--keep-blender", action="store_true", help="Don't kill Blender after tests")
    parser.add_argument("--quiet", "-q", action="store_true", help="Don't stream test output to console")
    args = parser.parse_args()

    blender_process = None
    blender_log_path: Path | None = None
    test_success = False

    try:
        # Find Blender
        blender_path = find_blender_path(args.blender_path)
        log(f"Using Blender: {blender_path}", "OK")

        selected_rpc_port = select_rpc_port_for_run()
        os.environ["BLENDER_RPC_HOST"] = RPC_HOST
        os.environ["BLENDER_RPC_PORT"] = str(selected_rpc_port)
        globals()["RPC_PORT"] = selected_rpc_port

        # Step 1: Build addon
        if not args.skip_build:
            if not build_addon():
                log("Addon build failed, aborting", "ERR")
                return 1
        else:
            log("Skipping addon build (--skip-build)", "INFO")
            if not ADDON_OUTPUT.exists():
                log(f"Addon not found at {ADDON_OUTPUT}. Run without --skip-build", "ERR")
                return 1

        # Step 2: Check if addon is installed
        addon_was_installed = check_addon_installed(blender_path)

        # Step 3: Uninstall if present
        if addon_was_installed:
            if not uninstall_addon(blender_path):
                log("Failed to uninstall old addon", "ERR")
                return 1
            log("Blender restart required after uninstall", "INFO")

        # Step 4: Install new addon
        if not install_addon(blender_path):
            log("Failed to install addon", "ERR")
            return 1

        # Step 5: Start Blender with RPC server
        blender_process, rpc_ready, blender_log_path = run_blender_with_rpc(blender_path)

        if not rpc_ready:
            log("RPC server not available, cannot run E2E tests", "ERR")
            save_test_log(
                "RPC server not available, cannot run E2E tests.",
                False,
                blender_log_path=blender_log_path,
            )
            return 1

        # Step 6: Run E2E tests
        test_success, test_output = run_e2e_tests(verbose=not args.quiet)

        # Step 7: Always save log (both success and failure)
        save_test_log(test_output, test_success, blender_log_path=blender_log_path)

        return 0 if test_success else 1

    except FileNotFoundError as e:
        log(str(e), "ERR")
        return 1
    except KeyboardInterrupt:
        log("Interrupted by user", "WARN")
        return 130
    except Exception as e:
        log(f"Unexpected error: {e}", "ERR")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        # Step 8: Cleanup - kill Blender
        if blender_process and not args.keep_blender:
            kill_blender_process(blender_process)


if __name__ == "__main__":
    sys.exit(main())
