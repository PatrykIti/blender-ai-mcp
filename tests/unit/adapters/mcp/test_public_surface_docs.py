"""Docs/tests coverage for the current llm-guided public surface baseline."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_readme_documents_llm_guided_public_aliases():
    """User-facing README should describe the current llm-guided public line."""

    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for expected in (
        "LLM-Guided Public Surface",
        "check_scene",
        "inspect_scene",
        "configure_scene",
        "browse_workflows",
        "reference_images",
        "scene_scope_graph",
        "scene_relation_graph",
        "scene_view_diagnostics",
        "guided_reference_readiness",
        "MCP_TRANSPORT_MODE",
        "streamable",
        "macro_cutout_recess",
        "macro_relative_layout",
        "macro_finish_form",
        "Vision Layer Docs",
        "target_object",
        "config",
        "search_query",
        "keep_lights_and_cameras",
        "raw schema noise",
        "collection_manage(action=..., collection_name=...)",
        "modeling_create_primitive(...)",
        "stop free-form modeling and switch to",
        "strong deterministic truth findings still",
        "use the same inspect/measure/assert handoff",
        "Guided Handoff Contract",
        "guided_handoff",
        "Server-Driven Guided Flow State",
        "guided_flow_state",
        "domain_profile",
        "current_step",
        "active_target_scope",
        "spatial_scope_fingerprint",
        "spatial_state_version",
        "spatial_state_stale",
        "last_spatial_check_version",
        "spatial_refresh_required",
        "required_checks",
        "allowed_families",
        "allowed_roles",
        "missing_roles",
        "guided_register_part",
        "required prompt bundle",
        "preferred prompt bundle",
        "refresh_spatial_context",
        'scene_view_diagnostics(target_object="Camera"',
        "Contact Truth Semantics",
        "mesh-surface contact/gap semantics",
        "bbox fallback semantics",
        "prompt-library assets",
        "generic search-first stabilizer",
        "staged refs stay separate from the already-active goal",
        "ready session still carries explicit pending refs for another goal",
        "build-phase cleanup is still allowed when recovery is needed",
    ):
        assert expected in text


def test_mcp_docs_describe_aliases_and_hidden_arguments():
    """MCP server docs should explain public aliases and current hidden args."""

    text = (REPO_ROOT / "_docs" / "_MCP_SERVER" / "README.md").read_text(encoding="utf-8")

    for expected in (
        "LLM-Guided Public Surface Baseline",
        "check_scene",
        "inspect_scene",
        "configure_scene",
        "browse_workflows",
        "reference_images",
        "reference_compare_checkpoint",
        "reference_compare_current_view",
        "reference_compare_stage_checkpoint",
        "reference_iterate_stage_checkpoint",
        "scene_scope_graph",
        "scene_relation_graph",
        "scene_view_diagnostics",
        "guided_reference_readiness",
        "session_id",
        "transport",
        "MCP_TRANSPORT_MODE",
        "streamable",
        "Vision Layer Docs",
        "Guided Handoff Contract",
        "guided_handoff",
        "bbox-touching but still visibly gapped",
        "keep_lights_and_cameras",
        "keep_lights` / `keep_cameras`",
        "directly visible guided tools",
        "direct `reference_images(...)` attach catches batch-like",
        "direct `collection_manage(...)` keeps `collection_name` canonical",
        "direct `modeling_create_primitive(...)` rejects `scale`, `segments`",
        "raw FastMCP schema noise",
        "stop-and-check branch",
        "pause free-form modeling and switch to inspect/measure/assert immediately",
        "staged compare degrades but deterministic truth findings remain strong",
        "Canonical operator guidance for this surface now lives in `_docs/_PROMPTS/`",
        "generic search-first stabilizer",
        "bounded recovery hatch",
        "Server-Driven Guided Flow State",
        "active_target_scope",
        "spatial_scope_fingerprint",
        "spatial_state_version",
        "spatial_state_stale",
        "last_spatial_check_version",
        "spatial_refresh_required",
        "required_prompts",
        "preferred_prompts",
        "allowed_roles",
        "missing_roles",
        "guided_register_part",
        "scene_scope_graph(...) now binds the active guided target scope",
        "Camera",
        "refresh_spatial_context",
        "hidden/blocked-by-flow",
        "scene_hide_object",
        "scene_show_all_objects",
        "scene_isolate_object",
        "USER_PERSPECTIVE",
        "named cameras follow render visibility",
        "combined visible set",
        "copying active records into pending storage",
        "ready sessions that",
        "update pending state as well",
        "Current hidden/expert-only arguments on `llm-guided` include:",
        "`inspect_scene`",
        "`mesh_inspect`",
        "`browse_workflows`",
    ):
        assert expected in text


def test_mcp_client_config_examples_document_guided_creature_contract():
    text = (REPO_ROOT / "_docs" / "_MCP_SERVER" / "MCP_CLIENT_CONFIG_EXAMPLES.md").read_text(encoding="utf-8")

    for expected in (
        "Guided creature contract reminders for this profile:",
        "call_tool(name=..., arguments=...)",
        "scene_clean_scene(keep_lights_and_cameras=...)",
        'reference_images(action="attach", source_path=...)',
        "collection_manage(action=..., collection_name=...)",
        'loop_disposition="inspect_validate"',
        "stop free-form modeling and switch to inspect/measure/assert",
    ):
        assert expected in text


def test_vision_docs_exist_and_describe_runtime_scope():
    text = (REPO_ROOT / "_docs" / "_VISION" / "README.md").read_text(encoding="utf-8")

    for expected in (
        "Vision Layer Docs",
        "pluggable vision backend strategy",
        "deterministic capture-bundle inputs",
        "goal-scoped reference image context",
        "guided_reference_readiness",
        "request-bound attachment of `vision_assistant`",
        "Multi-View Capture Plan",
        "HYBRID_LOOP_REAL_CREATURE_EVAL.md",
        "CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md",
        "bbox-touching but mesh surfaces still separated",
        "`correction_candidates`",
        "`refinement_route`",
        "`refinement_handoff`",
        "`scene_scope_graph(...)`",
        "`scene_relation_graph(...)`",
        "`scene_view_diagnostics(...)`",
        "separate from the",
        "already-active goal refs",
        "leaving broken pending file paths behind",
    ):
        assert expected in text


def test_hybrid_loop_eval_pack_doc_exists():
    text = (REPO_ROOT / "_docs" / "_VISION" / "HYBRID_LOOP_REAL_CREATURE_EVAL.md").read_text(encoding="utf-8")

    for expected in (
        "Hybrid Loop Real Creature Eval",
        "tests/e2e/vision/test_reference_stage_truth_handoff.py",
        "tests/e2e/vision/test_reference_guided_creature_comparison.py",
        "`loop_disposition`",
        "`correction_candidates`",
        "`truth_followup`",
        "`correction_focus`",
    ):
        assert expected in text


def test_cross_domain_refinement_eval_doc_exists():
    text = (REPO_ROOT / "_docs" / "_VISION" / "CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md").read_text(encoding="utf-8")

    for expected in (
        "Cross-Domain Refinement Routing Eval",
        "`refinement_route`",
        "`refinement_handoff`",
        "Hard-Surface / Electronics",
        "Building / Architecture",
        "Garment / Soft Accessory",
        "Organ / Anatomy",
        "Low-Poly Creature / Assembled Model",
    ):
        assert expected in text


def test_reference_guided_creature_test_prompt_doc_exists():
    text = (REPO_ROOT / "_docs" / "_VISION" / "REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md").read_text(encoding="utf-8")

    for expected in (
        "Reference-Guided Creature Test Prompt",
        "outside `_docs/_PROMPTS/`",
        "blender-ai-mcp-guided-docker-openrouter",
        "`reference_iterate_stage_checkpoint(...)`",
        "`scene_get_viewport(...)`",
        "`guided_reference_readiness`",
        "`correction_candidates`",
        "`truth_followup`",
        "`USER_PERSPECTIVE`",
    ):
        assert expected in text


def test_multi_view_capture_plan_docs_exist():
    text = (REPO_ROOT / "_docs" / "_VISION" / "MULTI_VIEW_CAPTURE_PLAN.md").read_text(encoding="utf-8")

    for expected in (
        "Multi-View Capture Plan",
        'The long-term target is not "create permanent camera objects everywhere in the',
        "`scene_get_viewport`",
        "`scene_camera_focus`",
        "`scene_camera_orbit`",
        "`target_front`",
        "`target_side`",
        "`target_top`",
    ):
        assert expected in text


def test_tools_summary_describes_llm_guided_alias_layer():
    """Available tools summary should include the alias layer, not only canonical names."""

    text = (REPO_ROOT / "_docs" / "AVAILABLE_TOOLS_SUMMARY.md").read_text(encoding="utf-8")

    for expected in (
        "LLM-Guided Public Aliases",
        "check_scene",
        "inspect_scene",
        "configure_scene",
        "browse_workflows",
        "scene_scope_graph",
        "scene_relation_graph",
        "scene_view_diagnostics",
    ):
        assert expected in text


def test_prompt_templates_use_llm_guided_aliases_for_public_surface_examples():
    """Prompt docs should prefer current llm-guided aliases for user-facing examples."""

    prompt_readme = (REPO_ROOT / "_docs" / "_PROMPTS" / "README.md").read_text(encoding="utf-8")
    workflow_prompt = (REPO_ROOT / "_docs" / "_PROMPTS" / "WORKFLOW_ROUTER_FIRST.md").read_text(encoding="utf-8")
    manual_prompt = (REPO_ROOT / "_docs" / "_PROMPTS" / "MANUAL_TOOLS_NO_ROUTER.md").read_text(encoding="utf-8")
    creature_prompt = (REPO_ROOT / "_docs" / "_PROMPTS" / "REFERENCE_GUIDED_CREATURE_BUILD.md").read_text(
        encoding="utf-8"
    )

    assert "check_scene" in prompt_readme
    assert "inspect_scene" in prompt_readme
    assert "configure_scene" in prompt_readme
    assert "browse_workflows" in prompt_readme
    assert "reference_images" in prompt_readme
    assert "reference_compare_checkpoint" in prompt_readme
    assert "reference_compare_current_view" in prompt_readme
    assert "reference_compare_stage_checkpoint" in prompt_readme
    assert "reference_iterate_stage_checkpoint" in prompt_readme
    assert "scene_scope_graph(...)" in prompt_readme
    assert "scene_relation_graph(...)" in prompt_readme
    assert "scene_view_diagnostics(...)" in prompt_readme
    assert "search_tools" in prompt_readme
    assert "call_tool" in prompt_readme
    assert "call it directly instead of routing through `search_tools(...)` / `call_tool(...)`" in prompt_readme
    assert "practical `llm-guided` operating model" in prompt_readme
    assert "vision-assisted build:" in prompt_readme
    assert "## `llm-guided` Flow Summary" in prompt_readme
    assert "GUIDED_SESSION_START.md" in prompt_readme
    assert "REFERENCE_GUIDED_CREATURE_BUILD.md" in prompt_readme
    assert "guided_session_start" in prompt_readme
    assert "canonical prompt library" in prompt_readme
    assert "generic search-first stabilizer" in prompt_readme
    assert "server-driven guided flow" in prompt_readme
    assert "guided_flow_state" in prompt_readme
    assert "active_target_scope" in prompt_readme
    assert "spatial_scope_fingerprint" in prompt_readme
    assert "spatial_state_version" in prompt_readme
    assert "last_spatial_check_version" in prompt_readme
    assert "spatial_refresh_required" in prompt_readme
    assert "required prompt bundle" in prompt_readme
    assert "preferred prompt bundle" in prompt_readme
    assert "refresh_spatial_context" in prompt_readme
    assert "guided_register_part(object_name=..., role=...)" in prompt_readme
    assert "guided_role=..." in prompt_readme
    assert "allowed_families" in prompt_readme
    assert "allowed_roles" in prompt_readme
    assert "missing_roles" in prompt_readme
    assert "If a tool is not already directly visible" in prompt_readme
    assert '`continuation_mode="guided_manual_build"`' in prompt_readme
    assert "`guided_handoff`" in prompt_readme
    assert "`guided_handoff.direct_tools`" in prompt_readme
    assert "manual_tools_no_router" in prompt_readme
    assert 'call_tool(name="scene_get_viewport", arguments={...})' in prompt_readme
    assert 'call_tool(name="scene_clean_scene", arguments={"keep_lights_and_cameras": true})' in prompt_readme
    assert "split `keep_lights` / `keep_cameras` form is legacy compatibility only" in prompt_readme
    assert "canonical `call_tool(...)` wrapper is `name=...` plus `arguments=...`" in prompt_readme
    assert "The same guided contract hardening now applies on directly visible tools as" in prompt_readme
    assert "actionable guidance instead of" in prompt_readme
    assert "raw schema noise on the guided surface" in prompt_readme
    assert "one `source_path` per attach call" in prompt_readme
    assert "collection_manage(action=..., collection_name=...)" in prompt_readme
    assert "modeling_transform_object(scale=...)" in prompt_readme
    assert "do **not** force `router_set_goal(...)`" in prompt_readme
    assert "`call_tool(...)` is not a bypass for hidden or phase-locked tools" in prompt_readme
    assert "`Unknown tool`" in prompt_readme
    assert "current phase/surface is wrong" in prompt_readme
    assert "build-phase cleanup is still allowed when recovery is needed" in prompt_readme
    assert "manual_tools_no_router` is a different operating mode" in prompt_readme
    assert "correction_focus" in prompt_readme
    assert "correction_candidates" in prompt_readme
    assert "truth_followup" in prompt_readme
    assert "guided_reference_readiness" in prompt_readme
    assert "stop free-form modeling and switch to inspect/measure/assert" in prompt_readme
    assert "staged compare degrades but strong deterministic truth findings still remain" in prompt_readme
    assert "ready session still lists explicit pending refs for another goal" in prompt_readme
    assert "refinement_route" in prompt_readme
    assert "refinement_handoff" in prompt_readme

    assert 'browse_workflows(action="search", search_query="<user prompt>")' in workflow_prompt
    assert 'browse_workflows(action="get", name="<workflow_name>")' in workflow_prompt
    assert "workflow_catalog import" not in workflow_prompt
    assert "router_clear_goal()" not in workflow_prompt
    assert "REQUEST TRIAGE (FIRST STEP)" in workflow_prompt
    assert "For A) build/workflow goal:" in workflow_prompt
    assert "If vision should support the task" in workflow_prompt
    assert "For B) utility/capture/scene-prep:" in workflow_prompt
    assert '`continuation_mode == "guided_manual_build"`' in workflow_prompt
    assert "`guided_handoff.direct_tools`" in workflow_prompt
    assert "`guided_flow_state`" in workflow_prompt
    assert "`allowed_families`" in workflow_prompt
    assert "`allowed_roles`" in workflow_prompt
    assert "`missing_roles`" in workflow_prompt
    assert "`guided_register_part(object_name=..., role=...)`" in workflow_prompt
    assert "`guided_role=...`" in workflow_prompt
    assert "`workflow_import_recommended=false`" in workflow_prompt
    assert "Do not guess hidden internal tool names and feed them into `call_tool(...)`." in workflow_prompt
    assert "If a needed tool is not already directly visible, run `search_tools(...)`" in workflow_prompt
    assert "allowed recovery hatch there" in workflow_prompt
    assert "If `call_tool(...)` reports `Unknown tool`, do not keep guessing names" in workflow_prompt
    assert (
        "If a needed tool is already directly visible on the current surface/phase, call it directly."
        in workflow_prompt
    )
    assert 'search_tools(query="viewport screenshot save file")' in workflow_prompt
    assert 'call_tool(name="scene_get_viewport", arguments={...})' in workflow_prompt
    assert 'call_tool(name="scene_clean_scene", arguments={"keep_lights_and_cameras": true})' in workflow_prompt
    assert "macro_cutout_recess" in prompt_readme
    assert "macro_relative_layout" in prompt_readme
    assert "macro_finish_form" in prompt_readme
    assert 'search_tools(query="align panel housing gap contact placement")' in workflow_prompt
    assert (
        'call_tool(name="macro_relative_layout", arguments={"moving_object":"Panel","reference_object":"Housing","x_mode":"center","y_mode":"center","contact_axis":"Z","contact_side":"positive","gap":0.002})'
        in workflow_prompt
    )
    assert 'search_tools(query="cutout recess opening boolean front face")' in workflow_prompt
    assert (
        'call_tool(name="macro_cutout_recess", arguments={"target_object":"Housing","width":0.12,"height":0.06,"depth":0.01,"face":"front","mode":"recess"})'
        in workflow_prompt
    )
    assert 'search_tools(query="finish housing bevel subdivision shell")' in workflow_prompt
    assert (
        'call_tool(name="macro_finish_form", arguments={"target_object":"Housing","preset":"rounded_housing"})'
        in workflow_prompt
    )
    assert (
        'call_tool(name="scene_measure_dimensions", arguments={"object_name":"Housing","world_space":true})'
        in workflow_prompt
    )
    assert 'inspect_scene(action="object", target_object=...)' in workflow_prompt

    assert 'check_scene(query="mode")' in manual_prompt
    assert 'check_scene(query="selection")' in manual_prompt
    assert 'inspect_scene(action="object", target_object=...)' in manual_prompt
    assert "`scene_camera_focus(object_name=...)`" in manual_prompt
    assert (
        "`scene_camera_orbit(angle_horizontal=..., angle_vertical=..., target_object=... or target_point=...)`"
        in manual_prompt
    )
    assert '`scene_get_viewport(shading=..., focus_target=..., output_mode="IMAGE")`' in manual_prompt
    assert (
        '`scene_get_viewport(camera_name="USER_PERSPECTIVE")` follows the live viewport; named cameras follow render visibility'
        in manual_prompt
    )
    assert "scene_show_all_objects(include_render=true)" in manual_prompt

    assert "`reference_iterate_stage_checkpoint(...)`" in creature_prompt
    assert "generic search-first operating baseline" in creature_prompt
    assert "`guided_flow_state`" in creature_prompt
    assert "required prompt bundle" in creature_prompt
    assert "`guided_register_part(object_name=..., role=...)`" in creature_prompt
    assert "`guided_role=...`" in creature_prompt
    assert "`allowed_roles`" in creature_prompt
    assert "`missing_roles`" in creature_prompt
    assert "body + head primary masses" in creature_prompt
    assert "do not jump early to ears or legs" in creature_prompt
    assert "if a tool is not already directly visible, use `search_tools(...)` before" in creature_prompt
    assert "allowed build-phase recovery hatch" in creature_prompt
    assert "`guided_reference_readiness`" in creature_prompt
    assert "`loop_disposition`" in creature_prompt
    assert "`correction_candidates`" in creature_prompt
    assert "`truth_followup`" in creature_prompt
    assert "`truth_followup.focus_pairs`" in creature_prompt
    assert "`truth_followup.macro_candidates`" in creature_prompt
    assert "the same guided contract hardening now applies on directly visible tools too" in creature_prompt
    assert "actionable guidance instead of raw" in creature_prompt
    assert 'reference_images(action="attach", source_path=..., ...)' in creature_prompt
    assert 'collection_manage(action="create", collection_name=...)' in creature_prompt
    assert "modeling_transform_object(scale=...)" in creature_prompt


def test_reference_guided_creature_prompt_stays_english():
    """The public creature prompt guide should not drift back into Polish prose."""

    creature_prompt = (REPO_ROOT / "_docs" / "_PROMPTS" / "REFERENCE_GUIDED_CREATURE_BUILD.md").read_text(
        encoding="utf-8"
    )

    assert re.search(r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]", creature_prompt) is None
    for unexpected in ("Zasady:", "Na końcu", "wyczyść", "dołącz", "wiewiór"):
        assert unexpected not in creature_prompt
