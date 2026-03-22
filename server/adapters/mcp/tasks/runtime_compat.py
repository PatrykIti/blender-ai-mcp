# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Compatibility shims for the current FastMCP+Docket task runtime."""

from __future__ import annotations


_COMPAT_APPLIED = False


def ensure_task_runtime_compatibility() -> None:
    """Patch known FastMCP/Docket symbol drift required by task-mode features.

    FastMCP 3.1.1 still imports ``current_execution`` from ``docket.dependencies``,
    while Docket 0.16 exposes ``CurrentExecution`` and the underlying contextvar
    on ``Dependency.execution``. This shim keeps the repo task runtime usable
    without vendoring FastMCP internals.
    """

    global _COMPAT_APPLIED
    if _COMPAT_APPLIED:
        return

    try:
        import docket.dependencies as docket_dependencies
    except ImportError:
        return

    dependency = getattr(docket_dependencies, "Dependency", None)
    if dependency is None:
        return

    if not hasattr(docket_dependencies, "current_execution"):
        docket_dependencies.current_execution = dependency.execution
    if not hasattr(docket_dependencies, "current_docket"):
        docket_dependencies.current_docket = dependency.docket
    if not hasattr(docket_dependencies, "current_worker"):
        docket_dependencies.current_worker = dependency.worker

    _COMPAT_APPLIED = True
