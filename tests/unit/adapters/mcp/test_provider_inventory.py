"""Tests for the first provider inventory slice."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from server.adapters.mcp.areas.mesh import register_mesh_tools
from server.adapters.mcp.areas.router import register_router_tools
from server.adapters.mcp.areas.scene import register_scene_tools
from server.adapters.mcp.areas.modeling import register_modeling_tools
from server.adapters.mcp.areas.workflow_catalog import register_workflow_tools
from server.adapters.mcp.providers import core_tools
from server.adapters.mcp.providers import internal_tools, router_tools, workflow_tools


EXPECTED_MODELING_TOOLS = {
    "modeling_create_primitive",
    "modeling_transform_object",
    "modeling_add_modifier",
    "modeling_apply_modifier",
    "modeling_convert_to_mesh",
    "modeling_join_objects",
    "modeling_separate_object",
    "modeling_list_modifiers",
    "modeling_set_origin",
    "metaball_create",
    "metaball_add_element",
    "metaball_to_mesh",
    "skin_create_skeleton",
    "skin_set_radius",
}

EXPECTED_SCENE_TOOLS = {
    "scene_list_objects",
    "scene_delete_object",
    "scene_clean_scene",
    "scene_duplicate_object",
    "scene_set_active_object",
    "scene_context",
    "scene_inspect",
    "scene_get_viewport",
    "scene_snapshot_state",
    "scene_compare_snapshot",
    "scene_create",
    "scene_set_mode",
    "scene_rename_object",
    "scene_hide_object",
    "scene_show_all_objects",
    "scene_isolate_object",
    "scene_camera_orbit",
    "scene_camera_focus",
    "scene_get_custom_properties",
    "scene_set_custom_property",
    "scene_get_hierarchy",
    "scene_get_bounding_box",
    "scene_get_origin_info",
}

EXPECTED_MESH_TOOLS = {
    "mesh_select",
    "mesh_select_targeted",
    "mesh_delete_selected",
    "mesh_extrude_region",
    "mesh_fill_holes",
    "mesh_bevel",
    "mesh_loop_cut",
    "mesh_inset",
    "mesh_boolean",
    "mesh_merge_by_distance",
    "mesh_subdivide",
    "mesh_smooth",
    "mesh_flatten",
    "mesh_list_groups",
    "mesh_inspect",
    "mesh_randomize",
    "mesh_shrink_fatten",
    "mesh_create_vertex_group",
    "mesh_assign_to_group",
    "mesh_remove_from_group",
    "mesh_bisect",
    "mesh_edge_slide",
    "mesh_vert_slide",
    "mesh_triangulate",
    "mesh_remesh_voxel",
    "mesh_transform_selected",
    "mesh_bridge_edge_loops",
    "mesh_duplicate_selected",
    "mesh_spin",
    "mesh_screw",
    "mesh_add_vertex",
    "mesh_add_edge_face",
    "mesh_edge_crease",
    "mesh_bevel_weight",
    "mesh_mark_sharp",
    "mesh_dissolve",
    "mesh_tris_to_quads",
    "mesh_normals_make_consistent",
    "mesh_decimate",
    "mesh_knife_project",
    "mesh_rip",
    "mesh_split",
    "mesh_edge_split",
    "mesh_set_proportional_edit",
    "mesh_symmetrize",
    "mesh_grid_fill",
    "mesh_poke_faces",
    "mesh_beautify_fill",
    "mesh_mirror",
}

EXPECTED_ROUTER_TOOLS = {
    "router_set_goal",
    "router_get_status",
    "router_clear_goal",
    "router_find_similar_workflows",
    "router_get_inherited_proportions",
    "router_feedback",
}

EXPECTED_WORKFLOW_TOOLS = {"workflow_catalog"}


@dataclass
class RegisteredTool:
    """Minimal stand-in for a registered tool object."""

    name: str
    fn_name: str


class FakeRegistrarTarget:
    """A FastMCP-compatible target exposing the .tool(...) registration shape."""

    def __init__(self) -> None:
        self.registered: dict[str, RegisteredTool] = {}

    def tool(self, name_or_fn=None, **kwargs):
        explicit_name = kwargs.get("name")

        def register(fn):
            tool_name = explicit_name or (name_or_fn if isinstance(name_or_fn, str) else fn.__name__)
            tool = RegisteredTool(name=tool_name, fn_name=fn.__name__)
            self.registered[tool_name] = tool
            return tool

        if callable(name_or_fn):
            return register(name_or_fn)

        return register


def test_register_modeling_tools_registers_expected_public_surface():
    """Modeling registrar should expose the expected public tool names."""

    target = FakeRegistrarTarget()

    registered = register_modeling_tools(target)

    assert set(registered) == EXPECTED_MODELING_TOOLS
    assert set(target.registered) == EXPECTED_MODELING_TOOLS


def test_register_scene_tools_registers_expected_public_surface():
    """Scene registrar should expose the expected public tool names."""

    target = FakeRegistrarTarget()

    registered = register_scene_tools(target)

    assert set(registered) == EXPECTED_SCENE_TOOLS
    assert set(target.registered) == EXPECTED_SCENE_TOOLS


def test_register_mesh_tools_registers_expected_public_surface():
    """Mesh registrar should expose the expected public tool names."""

    target = FakeRegistrarTarget()

    registered = register_mesh_tools(target)

    assert set(registered) == EXPECTED_MESH_TOOLS
    assert set(target.registered) == EXPECTED_MESH_TOOLS


def test_register_router_tools_registers_expected_public_surface():
    """Router registrar should expose the expected public tool names."""

    target = FakeRegistrarTarget()

    registered = register_router_tools(target)

    assert set(registered) == EXPECTED_ROUTER_TOOLS
    assert set(target.registered) == EXPECTED_ROUTER_TOOLS


def test_register_workflow_tools_registers_expected_public_surface():
    """Workflow registrar should expose the expected public tool names."""

    target = FakeRegistrarTarget()

    registered = register_workflow_tools(target)

    assert set(registered) == EXPECTED_WORKFLOW_TOOLS
    assert set(target.registered) == EXPECTED_WORKFLOW_TOOLS


def test_register_core_tools_delegates_to_modeling_slice():
    """The first core provider slice should contain scene, mesh, and modeling families."""

    target = FakeRegistrarTarget()

    registered = core_tools.register_core_tools(target)

    expected = EXPECTED_SCENE_TOOLS | EXPECTED_MESH_TOOLS | EXPECTED_MODELING_TOOLS

    assert set(registered) == expected
    assert set(target.registered) == expected


def test_build_core_tools_provider_uses_local_provider_when_available(monkeypatch):
    """Provider builder should register the same modeling surface on a LocalProvider-like target."""

    class FakeLocalProvider(FakeRegistrarTarget):
        pass

    monkeypatch.setattr(core_tools, "LocalProvider", FakeLocalProvider)

    provider = core_tools.build_core_tools_provider()

    expected = EXPECTED_SCENE_TOOLS | EXPECTED_MESH_TOOLS | EXPECTED_MODELING_TOOLS

    assert isinstance(provider, FakeLocalProvider)
    assert set(provider.registered) == expected


def test_build_router_tools_provider_uses_local_provider_when_available(monkeypatch):
    """Router provider builder should register the expected router tool surface."""

    class FakeLocalProvider(FakeRegistrarTarget):
        pass

    monkeypatch.setattr(router_tools, "LocalProvider", FakeLocalProvider)

    provider = router_tools.build_router_tools_provider()

    assert isinstance(provider, FakeLocalProvider)
    assert set(provider.registered) == EXPECTED_ROUTER_TOOLS


def test_build_workflow_tools_provider_uses_local_provider_when_available(monkeypatch):
    """Workflow provider builder should register the expected workflow tool surface."""

    class FakeLocalProvider(FakeRegistrarTarget):
        pass

    monkeypatch.setattr(workflow_tools, "LocalProvider", FakeLocalProvider)

    provider = workflow_tools.build_workflow_tools_provider()

    assert isinstance(provider, FakeLocalProvider)
    assert set(provider.registered) == EXPECTED_WORKFLOW_TOOLS


def test_build_internal_tools_provider_starts_empty(monkeypatch):
    """Internal provider scaffold should be buildable before helper tools are populated."""

    class FakeLocalProvider(FakeRegistrarTarget):
        pass

    monkeypatch.setattr(internal_tools, "LocalProvider", FakeLocalProvider)

    provider = internal_tools.build_internal_tools_provider()

    assert isinstance(provider, FakeLocalProvider)
    assert provider.registered == {}


def test_build_core_tools_provider_requires_local_provider():
    """Provider builder should fail clearly when FastMCP 3.x LocalProvider is unavailable."""

    original = core_tools.LocalProvider
    core_tools.LocalProvider = None
    try:
        with pytest.raises(RuntimeError, match="LocalProvider requires FastMCP >=3.0"):
            core_tools.build_core_tools_provider()
    finally:
        core_tools.LocalProvider = original
