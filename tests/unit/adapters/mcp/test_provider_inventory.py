"""Tests for the first provider inventory slice."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest
from server.adapters.mcp.areas.armature import ARMATURE_PUBLIC_TOOL_NAMES, register_armature_tools
from server.adapters.mcp.areas.baking import BAKING_PUBLIC_TOOL_NAMES, register_baking_tools
from server.adapters.mcp.areas.collection import COLLECTION_PUBLIC_TOOL_NAMES, register_collection_tools
from server.adapters.mcp.areas.curve import CURVE_PUBLIC_TOOL_NAMES, register_curve_tools
from server.adapters.mcp.areas.extraction import EXTRACTION_PUBLIC_TOOL_NAMES, register_extraction_tools
from server.adapters.mcp.areas.lattice import LATTICE_PUBLIC_TOOL_NAMES, register_lattice_tools
from server.adapters.mcp.areas.material import MATERIAL_PUBLIC_TOOL_NAMES, register_material_tools
from server.adapters.mcp.areas.mesh import register_mesh_tools
from server.adapters.mcp.areas.modeling import register_modeling_tools
from server.adapters.mcp.areas.router import register_router_tools
from server.adapters.mcp.areas.scene import register_scene_tools
from server.adapters.mcp.areas.sculpt import SCULPT_PUBLIC_TOOL_NAMES, register_sculpt_tools
from server.adapters.mcp.areas.system import SYSTEM_PUBLIC_TOOL_NAMES, register_system_tools
from server.adapters.mcp.areas.text import TEXT_PUBLIC_TOOL_NAMES, register_text_tools
from server.adapters.mcp.areas.uv import UV_PUBLIC_TOOL_NAMES, register_uv_tools
from server.adapters.mcp.areas.workflow_catalog import register_workflow_tools
from server.adapters.mcp.providers import core_tools, internal_tools, router_tools, workflow_tools

EXPECTED_MODELING_TOOLS = {
    "macro_cutout_recess",
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
    "scene_configure",
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
    "scene_measure_distance",
    "scene_measure_dimensions",
    "scene_measure_gap",
    "scene_measure_alignment",
    "scene_measure_overlap",
    "scene_assert_contact",
    "scene_assert_dimensions",
    "scene_assert_containment",
    "scene_assert_symmetry",
    "scene_assert_proportion",
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

ADDITIONAL_AREA_REGISTRARS = [
    ("material", register_material_tools, set(MATERIAL_PUBLIC_TOOL_NAMES)),
    ("uv", register_uv_tools, set(UV_PUBLIC_TOOL_NAMES)),
    ("collection", register_collection_tools, set(COLLECTION_PUBLIC_TOOL_NAMES)),
    ("curve", register_curve_tools, set(CURVE_PUBLIC_TOOL_NAMES)),
    ("lattice", register_lattice_tools, set(LATTICE_PUBLIC_TOOL_NAMES)),
    ("sculpt", register_sculpt_tools, set(SCULPT_PUBLIC_TOOL_NAMES)),
    ("baking", register_baking_tools, set(BAKING_PUBLIC_TOOL_NAMES)),
    ("text", register_text_tools, set(TEXT_PUBLIC_TOOL_NAMES)),
    ("armature", register_armature_tools, set(ARMATURE_PUBLIC_TOOL_NAMES)),
    ("system", register_system_tools, set(SYSTEM_PUBLIC_TOOL_NAMES)),
    ("extraction", register_extraction_tools, set(EXTRACTION_PUBLIC_TOOL_NAMES)),
]


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


@pytest.mark.parametrize(
    ("area_name", "registrar", "expected_tools"),
    ADDITIONAL_AREA_REGISTRARS,
)
def test_additional_area_registrars_register_expected_public_surface(
    area_name,
    registrar,
    expected_tools,
):
    """Remaining area registrars should expose the expected public tool names."""

    target = FakeRegistrarTarget()

    registered = registrar(target)

    assert set(registered) == expected_tools, area_name
    assert set(target.registered) == expected_tools, area_name


def test_register_core_tools_delegates_to_modeling_slice():
    """The core provider slice should contain the full reusable public core tool surface."""

    target = FakeRegistrarTarget()

    registered = core_tools.register_core_tools(target)

    expected = (
        EXPECTED_SCENE_TOOLS
        | EXPECTED_MESH_TOOLS
        | EXPECTED_MODELING_TOOLS
        | set(MATERIAL_PUBLIC_TOOL_NAMES)
        | set(UV_PUBLIC_TOOL_NAMES)
        | set(COLLECTION_PUBLIC_TOOL_NAMES)
        | set(CURVE_PUBLIC_TOOL_NAMES)
        | set(LATTICE_PUBLIC_TOOL_NAMES)
        | set(SCULPT_PUBLIC_TOOL_NAMES)
        | set(BAKING_PUBLIC_TOOL_NAMES)
        | set(TEXT_PUBLIC_TOOL_NAMES)
        | set(ARMATURE_PUBLIC_TOOL_NAMES)
        | set(SYSTEM_PUBLIC_TOOL_NAMES)
        | set(EXTRACTION_PUBLIC_TOOL_NAMES)
    )

    assert set(registered) == expected
    assert set(target.registered) == expected


def test_build_core_tools_provider_uses_local_provider_when_available(monkeypatch):
    """Provider builder should register the same modeling surface on a LocalProvider-like target."""

    class FakeLocalProvider(FakeRegistrarTarget):
        pass

    monkeypatch.setattr(core_tools, "LocalProvider", FakeLocalProvider)

    provider = core_tools.build_core_tools_provider()

    expected = (
        EXPECTED_SCENE_TOOLS
        | EXPECTED_MESH_TOOLS
        | EXPECTED_MODELING_TOOLS
        | set(MATERIAL_PUBLIC_TOOL_NAMES)
        | set(UV_PUBLIC_TOOL_NAMES)
        | set(COLLECTION_PUBLIC_TOOL_NAMES)
        | set(CURVE_PUBLIC_TOOL_NAMES)
        | set(LATTICE_PUBLIC_TOOL_NAMES)
        | set(SCULPT_PUBLIC_TOOL_NAMES)
        | set(BAKING_PUBLIC_TOOL_NAMES)
        | set(TEXT_PUBLIC_TOOL_NAMES)
        | set(ARMATURE_PUBLIC_TOOL_NAMES)
        | set(SYSTEM_PUBLIC_TOOL_NAMES)
        | set(EXTRACTION_PUBLIC_TOOL_NAMES)
    )

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


def test_area_modules_no_longer_depend_on_instance_singleton():
    """Provider-based registrars should not require `server.adapters.mcp.instance.mcp`."""

    areas_dir = Path("server/adapters/mcp/areas")

    for path in sorted(areas_dir.glob("*.py")):
        if path.name == "__init__.py" or path.stem.startswith("_"):
            continue
        source = path.read_text(encoding="utf-8")
        assert "from server.adapters.mcp.instance import mcp" not in source, path.name
        assert "@mcp.tool()" not in source, path.name
