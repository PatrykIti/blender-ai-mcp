"""Tests for tagged providers and deterministic visibility policy."""

from __future__ import annotations

from dataclasses import dataclass

from server.adapters.mcp.areas.router import register_router_tools
from server.adapters.mcp.areas.scene import register_scene_tools
from server.adapters.mcp.platform.capability_manifest import get_capability_manifest
from server.adapters.mcp.session_phase import SessionPhase
from server.adapters.mcp.surfaces import get_surface_profile
from server.adapters.mcp.transforms import materialize_transforms
from server.adapters.mcp.transforms.visibility_policy import (
    GUIDED_BUILD_ESCAPE_HATCH_TOOLS,
    GUIDED_ENTRY_TOOLS,
    GUIDED_INSPECT_ESCAPE_HATCH_TOOLS,
    build_visibility_rules,
)
from server.adapters.mcp.visibility.tags import ENTRY_GUIDED, get_capability_tags, phase_tag


@dataclass
class RegisteredTool:
    """Minimal stand-in for a registered tool object."""

    name: str
    fn_name: str
    tags: set[str]


class FakeRegistrarTarget:
    """A FastMCP-compatible target exposing the .tool(...) registration shape."""

    def __init__(self) -> None:
        self.registered: dict[str, RegisteredTool] = {}

    def tool(self, name_or_fn=None, **kwargs):
        explicit_name = kwargs.get("name")
        explicit_tags = set(kwargs.get("tags", set()))

        def register(fn):
            tool_name = explicit_name or (name_or_fn if isinstance(name_or_fn, str) else fn.__name__)
            tool = RegisteredTool(name=tool_name, fn_name=fn.__name__, tags=set(explicit_tags))
            self.registered[tool_name] = tool
            return tool

        if callable(name_or_fn):
            return register(name_or_fn)

        return register


def test_capability_manifest_carries_canonical_visibility_tags():
    """Capability manifest should be the canonical visibility registry."""

    manifest = {entry.capability_id: entry for entry in get_capability_manifest()}

    assert ENTRY_GUIDED in manifest["router"].tags
    assert ENTRY_GUIDED in manifest["workflow_catalog"].tags
    assert phase_tag(SessionPhase.BUILD) in manifest["modeling"].tags
    assert phase_tag(SessionPhase.INSPECT_VALIDATE) in manifest["mesh"].tags


def test_registrars_apply_manifest_tags_to_registered_tools():
    """Provider registration should materialize tags from the shared capability model."""

    router_target = FakeRegistrarTarget()
    scene_target = FakeRegistrarTarget()

    register_router_tools(router_target)
    register_scene_tools(scene_target)

    assert router_target.registered["router_set_goal"].tags == set(get_capability_tags("router"))
    assert scene_target.registered["scene_context"].tags == set(get_capability_tags("scene"))


def test_visibility_rules_are_profile_and_phase_deterministic():
    """Visibility policy should produce deterministic rules for profile/phase pairs."""

    assert build_visibility_rules("legacy-manual", SessionPhase.BOOTSTRAP) == []
    assert build_visibility_rules("legacy-flat", SessionPhase.BOOTSTRAP) == []

    bootstrap_rules = build_visibility_rules("llm-guided", SessionPhase.BOOTSTRAP)
    build_rules = build_visibility_rules("llm-guided", SessionPhase.BUILD)
    inspect_rules = build_visibility_rules("llm-guided", SessionPhase.INSPECT_VALIDATE)

    assert bootstrap_rules[0]["enabled"] is False
    assert bootstrap_rules[0]["match_all"] is True
    assert bootstrap_rules[1]["names"] == set(GUIDED_ENTRY_TOOLS)
    assert bootstrap_rules[2]["names"] == {"list_prompts", "get_prompt"}
    assert bootstrap_rules[3]["components"] == {"prompt"}
    assert build_rules[-1]["names"] == set(GUIDED_BUILD_ESCAPE_HATCH_TOOLS)
    assert inspect_rules[-1]["names"] == set(GUIDED_INSPECT_ESCAPE_HATCH_TOOLS)

    code_mode_rules = build_visibility_rules(get_surface_profile("code-mode-pilot"), SessionPhase.BOOTSTRAP)
    assert code_mode_rules[0]["enabled"] is False
    assert code_mode_rules[0]["match_all"] is True
    assert "scene_snapshot_state" in code_mode_rules[1]["names"]
    assert "mesh_extrude_region" not in code_mode_rules[1]["names"]


def test_llm_guided_surface_materializes_visibility_transforms():
    """llm-guided should carry concrete visibility transforms while legacy-flat stays unfiltered."""

    guided_transforms = materialize_transforms(get_surface_profile("llm-guided"))
    manual_transforms = materialize_transforms(get_surface_profile("legacy-manual"))
    legacy_transforms = materialize_transforms(get_surface_profile("legacy-flat"))

    assert len(guided_transforms) == 7
    assert len(manual_transforms) == 1
    assert len(legacy_transforms) == 1
