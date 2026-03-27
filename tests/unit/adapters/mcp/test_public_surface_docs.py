"""Docs/tests coverage for the current llm-guided public surface baseline."""

from __future__ import annotations

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
        "macro_cutout_recess",
        "macro_relative_layout",
        "macro_finish_form",
        "Vision Layer Docs",
        "target_object",
        "config",
        "search_query",
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
        "Vision Layer Docs",
        "Current hidden/expert-only arguments on `llm-guided` include:",
        "`inspect_scene`",
        "`mesh_inspect`",
        "`browse_workflows`",
    ):
        assert expected in text


def test_vision_docs_exist_and_describe_runtime_scope():
    text = (REPO_ROOT / "_docs" / "_VISION" / "README.md").read_text(encoding="utf-8")

    for expected in (
        "Vision Layer Docs",
        "pluggable vision backend strategy",
        "deterministic capture-bundle inputs",
        "goal-scoped reference image context",
        "request-bound attachment of `vision_assistant`",
        "Multi-View Capture Plan",
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
    ):
        assert expected in text


def test_prompt_templates_use_llm_guided_aliases_for_public_surface_examples():
    """Prompt docs should prefer current llm-guided aliases for user-facing examples."""

    prompt_readme = (REPO_ROOT / "_docs" / "_PROMPTS" / "README.md").read_text(encoding="utf-8")
    workflow_prompt = (REPO_ROOT / "_docs" / "_PROMPTS" / "WORKFLOW_ROUTER_FIRST.md").read_text(encoding="utf-8")
    manual_prompt = (REPO_ROOT / "_docs" / "_PROMPTS" / "MANUAL_TOOLS_NO_ROUTER.md").read_text(encoding="utf-8")

    assert "check_scene" in prompt_readme
    assert "inspect_scene" in prompt_readme
    assert "configure_scene" in prompt_readme
    assert "browse_workflows" in prompt_readme
    assert "reference_images" in prompt_readme
    assert "search_tools" in prompt_readme
    assert "call_tool" in prompt_readme
    assert "call it directly instead of routing through `search_tools(...)` / `call_tool(...)`" in prompt_readme
    assert "practical `llm-guided` operating model" in prompt_readme
    assert "vision-assisted build:" in prompt_readme
    assert "## `llm-guided` Flow Summary" in prompt_readme
    assert "manual_tools_no_router" in prompt_readme
    assert 'call_tool(name="scene_get_viewport", arguments={...})' in prompt_readme
    assert 'call_tool(name="scene_clean_scene", arguments={"keep_lights_and_cameras": true})' in prompt_readme
    assert "do **not** force `router_set_goal(...)`" in prompt_readme

    assert 'browse_workflows(action="search", search_query="<user prompt>")' in workflow_prompt
    assert 'browse_workflows(action="get", name="<workflow_name>")' in workflow_prompt
    assert "workflow_catalog import" not in workflow_prompt
    assert "router_clear_goal()" not in workflow_prompt
    assert "REQUEST TRIAGE (FIRST STEP)" in workflow_prompt
    assert "For A) build/workflow goal:" in workflow_prompt
    assert "If vision should support the task" in workflow_prompt
    assert "For B) utility/capture/scene-prep:" in workflow_prompt
    assert "If a needed tool is already directly visible on the current surface/phase, call it directly." in workflow_prompt
    assert 'search_tools(query="viewport screenshot save file")' in workflow_prompt
    assert 'call_tool(name="scene_get_viewport", arguments={...})' in workflow_prompt
    assert 'call_tool(name="scene_clean_scene", arguments={"keep_lights_and_cameras": true})' in workflow_prompt
    assert "macro_cutout_recess" in prompt_readme
    assert "macro_relative_layout" in prompt_readme
    assert "macro_finish_form" in prompt_readme
    assert 'search_tools(query="align panel housing gap contact placement")' in workflow_prompt
    assert 'call_tool(name="macro_relative_layout", arguments={"moving_object":"Panel","reference_object":"Housing","x_mode":"center","y_mode":"center","contact_axis":"Z","contact_side":"positive","gap":0.002})' in workflow_prompt
    assert 'search_tools(query="cutout recess opening boolean front face")' in workflow_prompt
    assert 'call_tool(name="macro_cutout_recess", arguments={"target_object":"Housing","width":0.12,"height":0.06,"depth":0.01,"face":"front","mode":"recess"})' in workflow_prompt
    assert 'search_tools(query="finish housing bevel subdivision shell")' in workflow_prompt
    assert 'call_tool(name="macro_finish_form", arguments={"target_object":"Housing","preset":"rounded_housing"})' in workflow_prompt
    assert 'call_tool(name="scene_measure_dimensions", arguments={"object_name":"Housing","world_space":true})' in workflow_prompt
    assert 'inspect_scene(action="object", target_object=...)' in workflow_prompt

    assert 'check_scene(query="mode")' in manual_prompt
    assert 'check_scene(query="selection")' in manual_prompt
    assert 'inspect_scene(action="object", target_object=...)' in manual_prompt
    assert "`scene_camera_focus(object_name=...)`" in manual_prompt
    assert "`scene_camera_orbit(angle_horizontal=..., angle_vertical=..., target_object=... or target_point=...)`" in manual_prompt
    assert '`scene_get_viewport(shading=..., focus_target=..., output_mode="IMAGE")`' in manual_prompt
