# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Explicit FastMCP+Docket runtime support policy for task-capable surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version

from packaging.specifiers import SpecifierSet
from packaging.version import Version

SUPPORTED_FASTMCP_SPEC = SpecifierSet(">=3.1.1,<3.2.0")
SUPPORTED_PYDOCKET_SPEC = SpecifierSet(">=0.18.2,<0.19.0")


@dataclass(frozen=True)
class TaskRuntimeReport:
    """Resolved runtime information for the task-mode dependency pair."""

    fastmcp_version: str | None
    pydocket_version: str | None
    tasks_required: bool
    supported: bool
    reason: str | None = None

    @property
    def supported_pair_label(self) -> str:
        """Return the canonical supported-pair label used by docs and errors."""

        return f"fastmcp{SUPPORTED_FASTMCP_SPEC} + pydocket{SUPPORTED_PYDOCKET_SPEC}"

    def to_dict(self) -> dict[str, str | bool | None]:
        """Serialize the report for diagnostics and tests."""

        return {
            "fastmcp_version": self.fastmcp_version,
            "pydocket_version": self.pydocket_version,
            "tasks_required": self.tasks_required,
            "supported": self.supported,
            "reason": self.reason,
            "supported_pair": self.supported_pair_label,
        }


def _safe_version(dist_name: str) -> str | None:
    try:
        return version(dist_name)
    except PackageNotFoundError:
        return None


def get_task_runtime_report(*, tasks_required: bool) -> TaskRuntimeReport:
    """Resolve the current FastMCP+Docket runtime report for this environment."""

    fastmcp_version = _safe_version("fastmcp")
    pydocket_version = _safe_version("pydocket")

    if fastmcp_version is None:
        return TaskRuntimeReport(
            fastmcp_version=None,
            pydocket_version=pydocket_version,
            tasks_required=tasks_required,
            supported=False,
            reason="fastmcp is not installed in the active environment",
        )

    fastmcp_supported = Version(fastmcp_version) in SUPPORTED_FASTMCP_SPEC

    if not tasks_required:
        return TaskRuntimeReport(
            fastmcp_version=fastmcp_version,
            pydocket_version=pydocket_version,
            tasks_required=False,
            supported=fastmcp_supported,
            reason=None
            if fastmcp_supported
            else (f"fastmcp {fastmcp_version} is outside the supported task-runtime line {SUPPORTED_FASTMCP_SPEC}"),
        )

    if pydocket_version is None:
        return TaskRuntimeReport(
            fastmcp_version=fastmcp_version,
            pydocket_version=None,
            tasks_required=True,
            supported=False,
            reason="pydocket is not installed; task-capable surfaces require fastmcp[tasks]",
        )

    pydocket_supported = Version(pydocket_version) in SUPPORTED_PYDOCKET_SPEC
    supported = fastmcp_supported and pydocket_supported

    reason = None
    if not fastmcp_supported:
        reason = f"fastmcp {fastmcp_version} is outside supported range {SUPPORTED_FASTMCP_SPEC}"
    elif not pydocket_supported:
        reason = f"pydocket {pydocket_version} is outside supported range {SUPPORTED_PYDOCKET_SPEC}"

    return TaskRuntimeReport(
        fastmcp_version=fastmcp_version,
        pydocket_version=pydocket_version,
        tasks_required=True,
        supported=supported,
        reason=reason,
    )


def validate_task_runtime_or_raise(*, tasks_required: bool) -> TaskRuntimeReport:
    """Return the runtime report or raise a clear error for unsupported pairs."""

    report = get_task_runtime_report(tasks_required=tasks_required)
    if report.supported:
        return report

    if not tasks_required and report.fastmcp_version is not None:
        return report

    resolved_fastmcp = report.fastmcp_version or "missing"
    resolved_pydocket = report.pydocket_version or "missing"
    raise RuntimeError(
        "Unsupported task runtime for FastMCP task-capable surfaces. "
        f"Resolved pair: fastmcp={resolved_fastmcp}, pydocket={resolved_pydocket}. "
        f"Supported pair: {report.supported_pair_label}. "
        f"Reason: {report.reason}"
    )
