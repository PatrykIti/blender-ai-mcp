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
import subprocess
import sys
import time
import socket
import os
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ADDON_OUTPUT = PROJECT_ROOT / "outputs" / "blender_ai_mcp.zip"
E2E_TESTS_DIR = PROJECT_ROOT / "tests" / "e2e"
BUILD_SCRIPT = PROJECT_ROOT / "scripts" / "build_addon.py"

# Blender paths (platform-specific)
BLENDER_PATHS = {
    "darwin": "/Applications/Blender.app/Contents/MacOS/Blender",
    "linux": "/usr/bin/blender",
    "win32": r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
}

# RPC Config
RPC_HOST = "127.0.0.1"
RPC_PORT = 8765
RPC_TIMEOUT = 30  # seconds to wait for Blender RPC server


def log(msg: str, level: str = "INFO"):
    """Print timestamped log message."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERR": "❌", "RUN": "🚀"}.get(level, "•")
    print(f"[{timestamp}] {prefix} {msg}")


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

    raise FileNotFoundError(
        f"Blender not found. Please specify path with --blender-path. "
        f"Checked: {platform_path}"
    )


def build_addon() -> bool:
    """Build the addon ZIP file."""
    log("Building addon...", "RUN")
    try:
        result = subprocess.run(
            [sys.executable, str(BUILD_SCRIPT)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
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


def check_addon_installed(blender_path: str) -> bool:
    """Check if blender_ai_mcp addon is installed."""
    log("Checking if addon is installed...")

    check_script = '''
import bpy
import sys
import addon_utils
import os

addon_name = "blender_ai_mcp"

# Check if addon module exists in available addons
is_installed = False
addon_path = None

for mod in addon_utils.modules():
    if mod.__name__ == addon_name:
        is_installed = True
        addon_path = os.path.dirname(mod.__file__)
        break

# Also check preferences
is_enabled = addon_name in bpy.context.preferences.addons

print(f"Addon module found: {is_installed}")
print(f"Addon enabled in prefs: {is_enabled}")
if addon_path:
    print(f"Addon path: {addon_path}")

if is_installed or is_enabled:
    print("ADDON_STATUS: INSTALLED")
    sys.exit(0)
else:
    print("ADDON_STATUS: NOT_INSTALLED")
    sys.exit(1)
'''

    result = subprocess.run(
        [blender_path, "--background", "--python-expr", check_script],
        capture_output=True,
        text=True,
        timeout=30
    )

    is_installed = "ADDON_STATUS: INSTALLED" in result.stdout
    log(f"Addon installed: {is_installed}", "OK" if is_installed else "INFO")
    return is_installed


def uninstall_addon(blender_path: str) -> bool:
    """Uninstall the blender_ai_mcp addon."""
    log("Uninstalling old addon...", "RUN")

    # Use addon_utils instead of bpy.ops to avoid UI context issues in --background mode
    uninstall_script = '''
import bpy
import sys
import shutil
import os
import addon_utils

addon_name = "blender_ai_mcp"

try:
    # Disable addon using addon_utils (no UI context needed)
    addon_utils.disable(addon_name, default_set=True)
    print(f"Disabled {addon_name}")

    # Find and remove addon directory
    addon_path = None
    for mod in addon_utils.modules():
        if mod.__name__ == addon_name:
            addon_path = os.path.dirname(mod.__file__)
            break

    if addon_path and os.path.exists(addon_path):
        shutil.rmtree(addon_path)
        print(f"Removed addon directory: {addon_path}")
    else:
        # Try standard location
        scripts_path = bpy.utils.user_resource('SCRIPTS')
        addon_dir = os.path.join(scripts_path, "addons", addon_name)
        if os.path.exists(addon_dir):
            shutil.rmtree(addon_dir)
            print(f"Removed addon directory: {addon_dir}")

    # Save preferences
    bpy.ops.wm.save_userpref()
    print("Preferences saved")

    print("UNINSTALL_STATUS: SUCCESS")
    sys.exit(0)
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"UNINSTALL_STATUS: FAILED - {e}")
    sys.exit(1)
'''

    result = subprocess.run(
        [blender_path, "--background", "--python-expr", uninstall_script],
        capture_output=True,
        text=True,
        timeout=60
    )

    success = "UNINSTALL_STATUS: SUCCESS" in result.stdout
    if success:
        log("Addon uninstalled successfully", "OK")
    else:
        log(f"Uninstall failed: {result.stdout}\n{result.stderr}", "ERR")

    return success


def install_addon(blender_path: str) -> bool:
    """Install and enable the blender_ai_mcp addon."""
    log(f"Installing addon from {ADDON_OUTPUT}...", "RUN")

    addon_path = str(ADDON_OUTPUT).replace("\\", "/")

    # Use addon_utils for enabling to avoid UI context issues
    install_script = f'''
import bpy
import sys
import addon_utils
import zipfile
import os

addon_zip = "{addon_path}"
addon_name = "blender_ai_mcp"

try:
    # Get addons directory
    scripts_path = bpy.utils.user_resource('SCRIPTS')
    addons_dir = os.path.join(scripts_path, "addons")
    os.makedirs(addons_dir, exist_ok=True)

    # Extract addon from ZIP
    with zipfile.ZipFile(addon_zip, 'r') as zip_ref:
        zip_ref.extractall(addons_dir)
    print(f"Extracted addon to {{addons_dir}}")

    # Refresh addon list
    addon_utils.modules_refresh()

    # Enable the addon using addon_utils (works in background mode)
    addon_utils.enable(addon_name, default_set=True, persistent=True)
    print(f"Enabled {{addon_name}}")

    # Save preferences
    bpy.ops.wm.save_userpref()
    print("Preferences saved")

    # Verify installation
    enabled_addons = [mod.__name__ for mod in addon_utils.modules()
                      if addon_utils.check(mod.__name__)[0]]

    if addon_name in enabled_addons or addon_name in bpy.context.preferences.addons:
        print("INSTALL_STATUS: SUCCESS")
        sys.exit(0)
    else:
        print(f"INSTALL_STATUS: FAILED - Addon not enabled. Available: {{enabled_addons}}")
        sys.exit(1)

except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"INSTALL_STATUS: FAILED - {{e}}")
    sys.exit(1)
'''

    result = subprocess.run(
        [blender_path, "--background", "--python-expr", install_script],
        capture_output=True,
        text=True,
        timeout=120
    )

    success = "INSTALL_STATUS: SUCCESS" in result.stdout
    if success:
        log("Addon installed and enabled successfully", "OK")
    else:
        log(f"Install failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}", "ERR")

    return success


def run_blender_with_rpc(blender_path: str) -> Tuple[subprocess.Popen, bool]:
    """Start Blender with RPC server running.

    Note: The addon's RPC server uses bpy.app.timers which requires
    Blender's main event loop to be running. Pure --background mode
    doesn't process timers, so we need to run Blender normally.
    """
    log("Starting Blender with RPC server...", "RUN")
    log("NOTE: Blender window will open - this is required for RPC server", "INFO")

    # Start Blender normally - the addon will auto-start its RPC server
    # We just open a new file to have a clean scene for testing
    process = subprocess.Popen(
        [blender_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid if sys.platform != "win32" else None
    )

    # Wait for RPC server
    rpc_ready = wait_for_rpc_server()

    return process, rpc_ready


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
            env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT)}
        )

        # Capture output while streaming to console
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
            env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT)}
        )
        output = f"{result.stdout}\n{result.stderr}"
        success = result.returncode == 0

    print("-" * 60)

    if success:
        log("E2E tests passed!", "OK")
    else:
        log("E2E tests failed!", "ERR")

    return success, output


def save_test_log(output: str, success: bool):
    """Save test output to log file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    status = "PASSED" if success else "FAILED"
    log_file = E2E_TESTS_DIR / f"e2e_test_{status}_{timestamp}.log"

    log_content = f"""
================================================================================
E2E Test Run - {datetime.now().isoformat()}
Status: {status}
================================================================================

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
    test_success = False

    try:
        # Find Blender
        blender_path = find_blender_path(args.blender_path)
        log(f"Using Blender: {blender_path}", "OK")

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
        blender_process, rpc_ready = run_blender_with_rpc(blender_path)

        if not rpc_ready:
            log("RPC server not available, cannot run E2E tests", "ERR")
            return 1

        # Step 6: Run E2E tests
        test_success, test_output = run_e2e_tests(verbose=not args.quiet)

        # Step 7: Always save log (both success and failure)
        save_test_log(test_output, test_success)

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
