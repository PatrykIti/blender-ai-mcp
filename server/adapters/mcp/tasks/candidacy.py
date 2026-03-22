# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Execution-mode candidacy matrix for heavy MCP operations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Literal

from fastmcp.tools.tool import TaskConfig


ExecutionMode = Literal["foreground_only", "task_optional", "task_required"]


@dataclass(frozen=True)
class TaskCandidacy:
    """Product-facing execution-mode classification for a heavy operation."""

    operation_key: str
    execution_mode: ExecutionMode
    backend_kind: Literal["addon_job", "server_local", "planned"]
    adopted: bool
    rationale: str


TASK_CANDIDACY_MATRIX: tuple[TaskCandidacy, ...] = (
    TaskCandidacy(
        operation_key="scene_get_viewport",
        execution_mode="task_optional",
        backend_kind="addon_job",
        adopted=True,
        rationale="Viewport capture is read-heavy and can block the client while image bytes are produced.",
    ),
    TaskCandidacy(
        operation_key="extraction_render_angles",
        execution_mode="task_optional",
        backend_kind="addon_job",
        adopted=True,
        rationale="Multi-angle rendering is the clearest first extraction candidate for observable progress and cancellation.",
    ),
    TaskCandidacy(
        operation_key="workflow_catalog.import_finalize",
        execution_mode="task_optional",
        backend_kind="server_local",
        adopted=True,
        rationale="Chunked workflow import finalization can reload registries and embeddings, so task mode keeps the client responsive.",
    ),
    TaskCandidacy(
        operation_key="import.obj",
        execution_mode="task_optional",
        backend_kind="addon_job",
        adopted=True,
        rationale="OBJ import can block while Blender parses geometry and rebuilds imported object state, so it should join the shared background path.",
    ),
    TaskCandidacy(
        operation_key="import.fbx",
        execution_mode="task_optional",
        backend_kind="addon_job",
        adopted=True,
        rationale="FBX import may include geometry, materials, armatures, and image lookups, making it a strong background-task candidate.",
    ),
    TaskCandidacy(
        operation_key="import.glb",
        execution_mode="task_optional",
        backend_kind="addon_job",
        adopted=True,
        rationale="GLB/GLTF import can take long enough on asset-heavy scenes that progress and cancellation should be observable.",
    ),
    TaskCandidacy(
        operation_key="import.image_as_plane",
        execution_mode="task_optional",
        backend_kind="addon_job",
        adopted=True,
        rationale="Image-as-plane import performs file loading plus geometry/material creation and should participate in the same observable background model as other import paths.",
    ),
    TaskCandidacy(
        operation_key="export.glb",
        execution_mode="task_optional",
        backend_kind="addon_job",
        adopted=True,
        rationale="GLB/GLTF export is a natural background-task candidate because file generation can materially block the client interaction loop.",
    ),
    TaskCandidacy(
        operation_key="export.fbx",
        execution_mode="task_optional",
        backend_kind="addon_job",
        adopted=True,
        rationale="FBX export often includes heavier scene serialization and should share the same observable job model as other long-running file operations.",
    ),
    TaskCandidacy(
        operation_key="export.obj",
        execution_mode="task_optional",
        backend_kind="addon_job",
        adopted=True,
        rationale="OBJ export already performs extra filesystem and scene validation and benefits from background execution and cancellation semantics.",
    ),
)


_TOOL_TASK_CONFIGS = {
    "scene_get_viewport": TaskConfig(mode="optional", poll_interval=timedelta(seconds=1)),
    "extraction_render_angles": TaskConfig(mode="optional", poll_interval=timedelta(seconds=1)),
    "workflow_catalog": TaskConfig(mode="optional", poll_interval=timedelta(seconds=1)),
    "export_glb": TaskConfig(mode="optional", poll_interval=timedelta(seconds=1)),
    "export_fbx": TaskConfig(mode="optional", poll_interval=timedelta(seconds=1)),
    "export_obj": TaskConfig(mode="optional", poll_interval=timedelta(seconds=1)),
    "import_obj": TaskConfig(mode="optional", poll_interval=timedelta(seconds=1)),
    "import_fbx": TaskConfig(mode="optional", poll_interval=timedelta(seconds=1)),
    "import_glb": TaskConfig(mode="optional", poll_interval=timedelta(seconds=1)),
    "import_image_as_plane": TaskConfig(mode="optional", poll_interval=timedelta(seconds=1)),
}


def get_task_candidacy(operation_key: str) -> TaskCandidacy | None:
    """Return the candidacy entry for an operation key."""

    for entry in TASK_CANDIDACY_MATRIX:
        if entry.operation_key == operation_key:
            return entry
    return None


def get_tool_task_config(tool_name: str) -> TaskConfig | None:
    """Return the explicit TaskConfig for adopted MCP endpoints."""

    return _TOOL_TASK_CONFIGS.get(tool_name)
