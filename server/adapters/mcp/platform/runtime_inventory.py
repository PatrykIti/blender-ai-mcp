# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Runtime inventory for the FastMCP 3.x migration baseline.

This module is the canonical audit seam introduced by TASK-083-01.
It captures the current MCP runtime layout, the remaining post-migration
coupling points, and the explicit Python / FastMCP baseline for the
migration series.

The inventory is intentionally static and source-controlled. It is not meant
to infer architecture from imports at runtime; it is meant to document the
current runtime truth so later provider/factory work can shrink these gaps
deliberately instead of rediscovering them ad hoc.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Iterable, Literal

SUPPORTED_PYTHON_BASELINE: Final[str] = ">=3.11,<4.0"
FASTMCP_BASELINE: Final[str] = ">=3.1.1,<3.2.0"
FASTMCP_DEPENDENCY_DECLARATION: Final[str] = "fastmcp[tasks]"
PYDOCKET_BASELINE: Final[str] = ">=0.18.2,<0.19.0"
PYDOCKET_DEPENDENCY_DECLARATION: Final[str] = "pydocket"
FASTMCP_FEATURE_GATE_BASELINE: Final[str] = ">=3.1.1,<3.2.0"

SURFACE_PROFILES: Final[tuple[str, ...]] = (
    "legacy-flat",
    "llm-guided",
    "internal-debug",
    "code-mode-pilot",
)

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[4]
AREAS_DIR: Final[Path] = REPO_ROOT / "server" / "adapters" / "mcp" / "areas"
AREAS_INIT_PATH: Final[Path] = AREAS_DIR / "__init__.py"
ROUTER_METADATA_DIR: Final[Path] = REPO_ROOT / "server" / "router" / "infrastructure" / "tools_metadata"
METADATA_LOADER_PATH: Final[Path] = REPO_ROOT / "server" / "router" / "infrastructure" / "metadata_loader.py"

ContextImportStyle = Literal["fastmcp", "mcp.server.fastmcp", "none"]


@dataclass(frozen=True)
class SurfaceModule:
    """Canonical audit record for one MCP area module."""

    area: str
    import_path: str
    public: bool
    router_callable: bool
    bootstrapped_by_side_effect: bool
    uses_global_mcp_singleton: bool
    context_import_style: ContextImportStyle
    uses_ctx_info_bridge: bool
    router_metadata_directory: bool
    metadata_loader_covered: bool
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class RuntimeCoupling:
    """Known FastMCP 2.x-style coupling to remove in later TASK-083 waves."""

    file_path: str
    coupling: str
    current_assumption: str
    follow_up_tasks: tuple[str, ...]


MCP_SURFACE_MODULES: Final[tuple[SurfaceModule, ...]] = (
    SurfaceModule(
        area="armature",
        import_path="server.adapters.mcp.areas.armature",
        public=True,
        router_callable=True,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=False,
        router_metadata_directory=True,
        metadata_loader_covered=True,
        notes=(),
    ),
    SurfaceModule(
        area="baking",
        import_path="server.adapters.mcp.areas.baking",
        public=True,
        router_callable=True,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=False,
        router_metadata_directory=True,
        metadata_loader_covered=True,
    ),
    SurfaceModule(
        area="collection",
        import_path="server.adapters.mcp.areas.collection",
        public=True,
        router_callable=True,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=True,
        router_metadata_directory=True,
        metadata_loader_covered=True,
    ),
    SurfaceModule(
        area="curve",
        import_path="server.adapters.mcp.areas.curve",
        public=True,
        router_callable=True,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=False,
        router_metadata_directory=True,
        metadata_loader_covered=True,
    ),
    SurfaceModule(
        area="extraction",
        import_path="server.adapters.mcp.areas.extraction",
        public=True,
        router_callable=True,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=True,
        router_metadata_directory=True,
        metadata_loader_covered=True,
        notes=(),
    ),
    SurfaceModule(
        area="lattice",
        import_path="server.adapters.mcp.areas.lattice",
        public=True,
        router_callable=True,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=False,
        router_metadata_directory=True,
        metadata_loader_covered=True,
    ),
    SurfaceModule(
        area="material",
        import_path="server.adapters.mcp.areas.material",
        public=True,
        router_callable=True,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=True,
        router_metadata_directory=True,
        metadata_loader_covered=True,
    ),
    SurfaceModule(
        area="mesh",
        import_path="server.adapters.mcp.areas.mesh",
        public=True,
        router_callable=True,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=True,
        router_metadata_directory=True,
        metadata_loader_covered=True,
    ),
    SurfaceModule(
        area="modeling",
        import_path="server.adapters.mcp.areas.modeling",
        public=True,
        router_callable=True,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=False,
        router_metadata_directory=True,
        metadata_loader_covered=True,
    ),
    SurfaceModule(
        area="reference",
        import_path="server.adapters.mcp.areas.reference",
        public=True,
        router_callable=False,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=True,
        router_metadata_directory=True,
        metadata_loader_covered=True,
        notes=("Goal-scoped reference image surface for TASK-121.",),
    ),
    SurfaceModule(
        area="router",
        import_path="server.adapters.mcp.areas.router",
        public=True,
        router_callable=False,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=True,
        router_metadata_directory=False,
        metadata_loader_covered=True,
        notes=("Router tool exposure is public but intentionally outside MetadataLoader.AREAS.",),
    ),
    SurfaceModule(
        area="scene",
        import_path="server.adapters.mcp.areas.scene",
        public=True,
        router_callable=True,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=True,
        router_metadata_directory=True,
        metadata_loader_covered=True,
    ),
    SurfaceModule(
        area="sculpt",
        import_path="server.adapters.mcp.areas.sculpt",
        public=True,
        router_callable=True,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=False,
        router_metadata_directory=True,
        metadata_loader_covered=True,
    ),
    SurfaceModule(
        area="system",
        import_path="server.adapters.mcp.areas.system",
        public=True,
        router_callable=True,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=True,
        router_metadata_directory=True,
        metadata_loader_covered=True,
    ),
    SurfaceModule(
        area="text",
        import_path="server.adapters.mcp.areas.text",
        public=True,
        router_callable=True,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=False,
        router_metadata_directory=True,
        metadata_loader_covered=True,
        notes=(),
    ),
    SurfaceModule(
        area="uv",
        import_path="server.adapters.mcp.areas.uv",
        public=True,
        router_callable=True,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=True,
        router_metadata_directory=True,
        metadata_loader_covered=True,
    ),
    SurfaceModule(
        area="workflow_catalog",
        import_path="server.adapters.mcp.areas.workflow_catalog",
        public=True,
        router_callable=False,
        bootstrapped_by_side_effect=False,
        uses_global_mcp_singleton=False,
        context_import_style="fastmcp",
        uses_ctx_info_bridge=True,
        router_metadata_directory=False,
        metadata_loader_covered=False,
        notes=("Workflow catalog is public but intentionally outside MetadataLoader.AREAS.",),
    ),
)

MCP_RUNTIME_COUPLINGS: Final[tuple[RuntimeCoupling, ...]] = (
    RuntimeCoupling(
        file_path="pyproject.toml",
        coupling="dependency_and_runtime_baseline",
        current_assumption=(
            "The project metadata defines the FastMCP and Python baseline used by the "
            "current bootstrap and by downstream 3.x-gated tasks."
        ),
        follow_up_tasks=("TASK-083-01",),
    ),
    RuntimeCoupling(
        file_path="server/adapters/mcp/router_helper.py",
        coupling="direct_router_wrapper",
        current_assumption=(
            "Router-aware execution still lives in adapter-side helper code instead of "
            "a platform-owned transform/runtime execution layer."
        ),
        follow_up_tasks=("TASK-095", "TASK-096", "TASK-097"),
    ),
    RuntimeCoupling(
        file_path="server/router/adapters/mcp_integration.py",
        coupling="router_execution_contract_alignment",
        current_assumption=(
            "Router middleware still needs fuller alignment with structured execution "
            "contracts and composed public surfaces."
        ),
        follow_up_tasks=("TASK-089",),
    ),
)


def build_runtime_inventory() -> tuple[SurfaceModule, ...]:
    """Return the canonical MCP surface inventory for the current repo state."""

    return MCP_SURFACE_MODULES


def build_runtime_couplings() -> tuple[RuntimeCoupling, ...]:
    """Return the canonical list of known FastMCP migration coupling points."""

    return MCP_RUNTIME_COUPLINGS


def get_filesystem_area_modules(base_dir: Path = AREAS_DIR) -> tuple[str, ...]:
    """Return all MCP area modules currently present on disk."""

    return tuple(
        sorted(
            path.stem for path in base_dir.glob("*.py") if path.name != "__init__.py" and not path.stem.startswith("_")
        )
    )


def get_bootstrap_side_effect_modules(init_path: Path = AREAS_INIT_PATH) -> tuple[str, ...]:
    """Return the area modules imported for side-effect registration."""

    module = ast.parse(init_path.read_text(encoding="utf-8"))
    imported_modules: list[str] = []

    for node in module.body:
        if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module is None:
            imported_modules.extend(alias.name for alias in node.names)

    return tuple(sorted(imported_modules))


def get_router_metadata_directories(base_dir: Path = ROUTER_METADATA_DIR) -> tuple[str, ...]:
    """Return router metadata family directories present on disk."""

    directories = []
    for path in base_dir.iterdir():
        if not path.is_dir():
            continue
        directories.append(path.name)
    return tuple(sorted(directories))


def get_metadata_loader_gap_areas(
    modules: Iterable[SurfaceModule] = MCP_SURFACE_MODULES,
) -> tuple[str, ...]:
    """Return runtime areas with router metadata on disk but no MetadataLoader coverage."""

    return tuple(
        sorted(
            module.area for module in modules if module.router_metadata_directory and not module.metadata_loader_covered
        )
    )


def get_metadata_loader_areas() -> tuple[str, ...]:
    """Return the area families currently loaded by MetadataLoader."""

    module = ast.parse(METADATA_LOADER_PATH.read_text(encoding="utf-8"))

    for node in module.body:
        if not isinstance(node, ast.ClassDef) or node.name != "MetadataLoader":
            continue

        for statement in node.body:
            if not isinstance(statement, ast.Assign):
                continue

            if not any(isinstance(target, ast.Name) and target.id == "AREAS" for target in statement.targets):
                continue

            return tuple(sorted(ast.literal_eval(statement.value)))

    raise RuntimeError("Could not locate MetadataLoader.AREAS in metadata_loader.py")
