"""Tests for the FastMCP 3.x runtime inventory baseline."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from server.adapters.mcp.platform.runtime_inventory import (
    AREAS_DIR,
    AREAS_INIT_PATH,
    FASTMCP_BASELINE,
    MCP_RUNTIME_COUPLINGS,
    MCP_SURFACE_MODULES,
    REPO_ROOT,
    ROUTER_METADATA_DIR,
    SUPPORTED_PYTHON_BASELINE,
    get_bootstrap_side_effect_modules,
    get_filesystem_area_modules,
    get_metadata_loader_areas,
    get_metadata_loader_gap_areas,
    get_router_metadata_directories,
)


def test_runtime_inventory_lists_every_area_module_on_disk():
    """The runtime inventory should enumerate every MCP area module present in the repo."""

    inventory_areas = {module.area for module in MCP_SURFACE_MODULES}

    assert inventory_areas == set(get_filesystem_area_modules())


def test_runtime_inventory_matches_side_effect_bootstrap_modules():
    """Inventory side-effect flags should match the empty post-migration bootstrap list."""

    bootstrapped_modules = set(get_bootstrap_side_effect_modules())
    inventory_bootstrapped = {
        module.area for module in MCP_SURFACE_MODULES if module.bootstrapped_by_side_effect
    }

    assert inventory_bootstrapped == bootstrapped_modules
    assert bootstrapped_modules == set()


def test_runtime_inventory_tracks_singleton_and_context_import_coupling():
    """Inventory should stay aligned with the source-level singleton/context coupling."""

    for module in MCP_SURFACE_MODULES:
        source_path = AREAS_DIR / f"{module.area}.py"
        source = source_path.read_text(encoding="utf-8")

        assert (
            "from server.adapters.mcp.instance import mcp" in source
        ) is module.uses_global_mcp_singleton

        if module.context_import_style == "fastmcp":
            assert "from fastmcp import Context" in source
            assert "from mcp.server.fastmcp import Context" not in source
        elif module.context_import_style == "mcp.server.fastmcp":
            assert "from mcp.server.fastmcp import Context" in source
            assert "from fastmcp import Context" not in source
        else:
            assert "Context" not in source

        assert ("ctx_info(" in source) is module.uses_ctx_info_bridge


def test_runtime_inventory_tracks_router_metadata_coverage_gaps():
    """Inventory should capture router-metadata families missing from MetadataLoader.AREAS."""

    metadata_directories = set(get_router_metadata_directories())
    metadata_loader_areas = set(get_metadata_loader_areas())

    assert metadata_directories >= {
        module.area for module in MCP_SURFACE_MODULES if module.router_metadata_directory
    }
    assert set(get_metadata_loader_gap_areas()) == (metadata_directories - metadata_loader_areas)
    assert set(get_metadata_loader_gap_areas()) == {"armature", "extraction", "text"}


def test_runtime_inventory_baseline_matches_pyproject():
    """The runtime inventory baseline should agree with project metadata."""

    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    dependencies = project["dependencies"]

    assert project["requires-python"] == SUPPORTED_PYTHON_BASELINE
    assert f"fastmcp ({FASTMCP_BASELINE})" in dependencies


def test_runtime_inventory_documents_required_coupling_points():
    """Only the remaining post-TASK-083 coupling points should stay explicit."""

    coupling_files = {coupling.file_path for coupling in MCP_RUNTIME_COUPLINGS}

    assert {
        "pyproject.toml",
        "server/adapters/mcp/router_helper.py",
        "server/router/adapters/mcp_integration.py",
    } <= coupling_files


def test_area_init_no_longer_uses_side_effect_relative_imports():
    """The area package should expose registrars without side-effect bootstrap imports."""

    init_source = AREAS_INIT_PATH.read_text(encoding="utf-8")
    import_lines = re.findall(r"^from \. import (\w+)$", init_source, flags=re.MULTILINE)

    assert sorted(import_lines) == list(get_bootstrap_side_effect_modules()) == []
    assert (ROUTER_METADATA_DIR / "text").is_dir()
