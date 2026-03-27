# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Surface profile selection for FastMCP factory composition."""

from __future__ import annotations

from dataclasses import replace

from server.adapters.mcp.providers import (
    build_core_tools_provider,
    build_internal_tools_provider,
    build_prompt_assets_provider,
    build_router_tools_provider,
    build_workflow_tools_provider,
)
from server.adapters.mcp.settings import SurfaceProfileSettings
from server.adapters.mcp.version_policy import (
    SURFACE_ALLOWED_CONTRACT_LINES,
    get_default_contract_line,
    resolve_contract_line,
)

SURFACE_PROFILES: dict[str, SurfaceProfileSettings] = {
    "legacy-manual": SurfaceProfileSettings(
        name="legacy-manual",
        server_name="blender-ai-mcp",
        provider_builders=(
            build_core_tools_provider,
            build_prompt_assets_provider,
        ),
        list_page_size=250,
        tasks_enabled=False,
        instructions=(
            "Manual legacy MCP surface. Broad low-level access for maintainer/manual work. "
            "Router and workflow catalog tools are intentionally not exposed here. "
            "Goal-first is not required on this surface. "
            "Use direct scene, modeling, mesh, material, UV, collection, import/export, and inspection tools. "
            "This is not the preferred production LLM path; if you want goal-first workflow/macro guidance, use llm-guided."
        ),
        delivery_mode="compatibility",
        default_contract_line=get_default_contract_line("legacy-manual"),
        allowed_contract_lines=SURFACE_ALLOWED_CONTRACT_LINES["legacy-manual"],
    ),
    "legacy-flat": SurfaceProfileSettings(
        name="legacy-flat",
        server_name="blender-ai-mcp",
        provider_builders=(
            build_core_tools_provider,
            build_router_tools_provider,
            build_workflow_tools_provider,
            build_prompt_assets_provider,
        ),
        list_page_size=250,
        tasks_enabled=False,
        instructions=(
            "Legacy compatibility/control surface. Broad public catalog including router and workflow tools. "
            "This surface is not the preferred long-term production LLM path. "
            "If you use router/workflow capabilities here, start from router_set_goal first; otherwise treat this as a compatibility or maintainer-oriented surface."
        ),
        delivery_mode="compatibility",
        default_contract_line=get_default_contract_line("legacy-flat"),
        allowed_contract_lines=SURFACE_ALLOWED_CONTRACT_LINES["legacy-flat"],
    ),
    "llm-guided": SurfaceProfileSettings(
        name="llm-guided",
        server_name="blender-ai-mcp",
        provider_builders=(
            build_core_tools_provider,
            build_router_tools_provider,
            build_workflow_tools_provider,
            build_prompt_assets_provider,
        ),
        list_page_size=50,
        tasks_enabled=True,
        instructions=(
            "Guided MCP surface. Start from router_set_goal first; this is the required production session bootstrap. "
            "Current entry tools are router_set_goal, router_get_status, browse_workflows, "
            "reference_images, search_tools, call_tool, list_prompts, and get_prompt. "
            "Prefer workflow/macro paths over raw low-level atomics. "
            "When a bounded intent matches, prefer macro_cutout_recess for recess/opening work, "
            "macro_relative_layout for part placement/alignment, and macro_finish_form for finishing stacks "
            "before assembling manual atomic chains. "
            "Use reference_images to attach/list/remove/clear goal-scoped reference images for later vision comparison. "
            "Other capability families can unlock progressively by session phase. "
            "Use visible direct tools directly when they are already available on the current shaped surface. "
            "Use search_tools/call_tool only when you actually need discovery or need to reach a non-entry tool that is not already visible. "
            "If you want a manual non-router workflow, load the prompt 'manual_tools_no_router'. "
            "Verify meaningful changes with inspection and, when appropriate, before/after capture plus deterministic measure/assert tooling. "
            "This surface is task-capable: adopted heavy tools can run as background tasks with progress, "
            "poll, cancel, and foreground fallback semantics."
        ),
        delivery_mode="structured_first",
        search_enabled=True,
        default_contract_line=get_default_contract_line("llm-guided"),
        allowed_contract_lines=SURFACE_ALLOWED_CONTRACT_LINES["llm-guided"],
    ),
    "internal-debug": SurfaceProfileSettings(
        name="internal-debug",
        server_name="blender-ai-mcp-debug",
        provider_builders=(
            build_core_tools_provider,
            build_router_tools_provider,
            build_workflow_tools_provider,
            build_prompt_assets_provider,
            build_internal_tools_provider,
        ),
        list_page_size=100,
        tasks_enabled=True,
        instructions=(
            "Internal debug surface. Broad maintainer-oriented access with structured-first delivery. "
            "This surface may expose internal/hidden layers and is not representative of the normal production public catalog. "
            "Goal-first is optional here. "
            "This surface is task-capable: adopted heavy tools can run as background tasks with progress, "
            "poll, cancel, and foreground fallback semantics."
        ),
        delivery_mode="structured_first",
        default_contract_line=get_default_contract_line("internal-debug"),
        allowed_contract_lines=SURFACE_ALLOWED_CONTRACT_LINES["internal-debug"],
    ),
    "code-mode-pilot": SurfaceProfileSettings(
        name="code-mode-pilot",
        server_name="blender-ai-mcp-code",
        provider_builders=(
            build_core_tools_provider,
            build_router_tools_provider,
            build_workflow_tools_provider,
            build_prompt_assets_provider,
            build_internal_tools_provider,
        ),
        list_page_size=50,
        tasks_enabled=True,
        instructions=(
            "Experimental Code Mode pilot. "
            "Use only the visible read-only MCP capabilities, prompts, and resources. "
            "Do not attempt geometry-destructive or write-heavy flows on this surface. "
            "This is not the normal production write path. Goal-first is optional here. "
            "This surface is task-capable, but keep background task usage aligned with the visible read-only pilot tools."
        ),
        delivery_mode="structured_first",
        code_mode_enabled=True,
        code_mode_allowed_tools=(
            "check_scene",
            "inspect_scene",
            "mesh_inspect",
            "scene_snapshot_state",
            "scene_compare_snapshot",
            "scene_get_hierarchy",
            "scene_get_bounding_box",
            "scene_get_origin_info",
            "router_get_status",
            "router_find_similar_workflows",
            "router_get_inherited_proportions",
            "list_prompts",
            "get_prompt",
        ),
        code_mode_benchmark_baselines=(
            "legacy-flat",
            "llm-guided",
            "code-mode-pilot",
        ),
        default_contract_line=get_default_contract_line("code-mode-pilot"),
        allowed_contract_lines=SURFACE_ALLOWED_CONTRACT_LINES["code-mode-pilot"],
    ),
}


def get_surface_profile(name: str) -> SurfaceProfileSettings:
    """Return the configured surface profile or raise a clear error."""

    try:
        return SURFACE_PROFILES[name]
    except KeyError as exc:
        known = ", ".join(sorted(SURFACE_PROFILES))
        raise ValueError(f"Unknown MCP surface profile '{name}'. Expected one of: {known}") from exc


def resolve_surface_contract_profile(
    name: str,
    *,
    contract_line: str | None = None,
) -> SurfaceProfileSettings:
    """Return a surface profile with a validated active contract line."""

    surface = get_surface_profile(name)
    selected_contract_line = resolve_contract_line(name, contract_line)
    return replace(surface, default_contract_line=selected_contract_line)
