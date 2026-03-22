# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Task-mode infrastructure for FastMCP background execution."""

from server.adapters.mcp.tasks.candidacy import (
    TASK_CANDIDACY_MATRIX,
    get_task_candidacy,
    get_tool_task_config,
)
from server.adapters.mcp.tasks.job_registry import (
    BackgroundJobRecord,
    BackgroundJobRegistry,
    get_background_job_registry,
    reset_background_job_registry_for_tests,
)
from server.adapters.mcp.tasks.result_store import (
    BackgroundResultRecord,
    BackgroundResultStore,
    get_background_result_store,
    reset_background_result_store_for_tests,
)
from server.adapters.mcp.tasks.runtime_policy import (
    TaskRuntimeReport,
    get_task_runtime_report,
    validate_task_runtime_or_raise,
)

__all__ = [
    "BackgroundJobRecord",
    "BackgroundJobRegistry",
    "BackgroundResultRecord",
    "BackgroundResultStore",
    "TASK_CANDIDACY_MATRIX",
    "get_background_job_registry",
    "get_background_result_store",
    "get_task_candidacy",
    "get_task_runtime_report",
    "get_tool_task_config",
    "reset_background_job_registry_for_tests",
    "reset_background_result_store_for_tests",
    "TaskRuntimeReport",
    "validate_task_runtime_or_raise",
]
