"""Integration-style tests for FastMCP structured contract delivery."""

from __future__ import annotations

import asyncio

from server.adapters.mcp.factory import build_server


class SceneHandler:
    def get_mode(self):
        return {
            "mode": "OBJECT",
            "active_object": "Cube",
            "active_object_type": "MESH",
            "selected_object_names": ["Cube"],
            "selection_count": 1,
        }

    def list_selection(self):
        return {
            "mode": "EDIT_MESH",
            "selected_object_names": ["Cube"],
            "selection_count": 1,
            "edit_mode_vertex_count": 8,
            "edit_mode_edge_count": 12,
            "edit_mode_face_count": 6,
        }

    def snapshot_state(self, include_mesh_stats=False, include_materials=False):
        return {
            "snapshot": {
                "object_count": 1,
                "mode": "OBJECT",
                "active_object": "Cube",
            },
            "hash": "abc123",
        }

    def get_custom_properties(self, object_name):
        return {
            "object_name": object_name,
            "property_count": 1,
            "properties": {"tag": "hero"},
        }

    def get_hierarchy(self, object_name=None, include_transforms=False):
        return {
            "roots": [{"name": "Cube"}],
            "total_objects": 1,
            "max_depth": 0,
        }

    def get_bounding_box(self, object_name, world_space=True):
        return {
            "object_name": object_name,
            "space": "world" if world_space else "local",
            "min": [0, 0, 0],
            "max": [1, 1, 1],
            "center": [0.5, 0.5, 0.5],
            "dimensions": [1, 1, 1],
            "volume": 1.0,
        }

    def get_origin_info(self, object_name):
        return {
            "origin_world": [0, 0, 0],
            "relative_to_bbox": {"x": 0.5, "y": 0.5, "z": 0.5},
            "suggestions": [],
        }

    def get_scope_graph(self, target_object=None, target_objects=None, collection_name=None):
        object_names = list(target_objects or ([] if target_object is None else [target_object]))
        if target_object and target_object not in object_names:
            object_names = [target_object, *object_names]
        primary_target = target_object or (object_names[-1] if object_names else None)
        return {
            "scope_kind": "object_set" if len(object_names) > 1 else ("single_object" if primary_target else "scene"),
            "primary_target": primary_target,
            "object_names": object_names,
            "object_count": len(object_names),
            "collection_name": collection_name,
            "part_groups": [],
            "object_roles": [
                {
                    "object_name": name,
                    "role": "anchor_core" if name == primary_target else "attached_appendage",
                    "is_primary": name == primary_target,
                    "signals": ["test_fixture"],
                }
                for name in object_names
            ],
        }

    def get_relation_graph(
        self,
        target_object=None,
        target_objects=None,
        collection_name=None,
        goal_hint=None,
        include_truth_payloads=False,
    ):
        scope = self.get_scope_graph(
            target_object=target_object, target_objects=target_objects, collection_name=collection_name
        )
        object_names = list(scope["object_names"])
        if len(object_names) < 2:
            return {
                "scope": scope,
                "summary": {"pairing_strategy": "none", "pair_count": 0, "evaluated_pairs": 0, "failing_pairs": 0},
                "pairs": [],
            }
        from_object, to_object = object_names[0], object_names[1]
        pair = {
            "pair_id": "pair_1",
            "from_object": from_object,
            "to_object": to_object,
            "pair_source": "primary_to_other",
            "relation_kinds": ["contact", "gap", "alignment", "attachment"],
            "relation_verdicts": ["separated", "misaligned", "floating_gap"],
            "gap_relation": "separated",
            "gap_distance": 0.5,
            "overlap_relation": "disjoint",
            "contact_passed": False,
            "alignment_status": "misaligned",
            "aligned_axes": ["Y", "Z"],
            "measurement_basis": "bounding_box",
            "attachment_semantics": {
                "relation_kind": "segment_attachment",
                "seam_kind": "head_body",
                "part_object": from_object,
                "anchor_object": to_object,
                "required_seam": False,
                "preferred_macro": "macro_align_part_with_contact",
                "attachment_verdict": "floating_gap",
            },
        }
        if include_truth_payloads:
            pair["truth_payloads"] = {
                "gap": self.measure_gap(from_object, to_object),
                "alignment": self.measure_alignment(from_object, to_object),
                "overlap": self.measure_overlap(from_object, to_object),
                "contact_assertion": self.assert_contact(from_object, to_object),
            }
        return {
            "scope": scope,
            "summary": {
                "pairing_strategy": "primary_to_others",
                "pair_count": 1,
                "evaluated_pairs": 1,
                "failing_pairs": 1,
                "attachment_pairs": 1,
                "support_pairs": 0,
                "symmetry_pairs": 0,
            },
            "pairs": [pair],
        }

    def get_view_diagnostics(
        self,
        target_object=None,
        target_objects=None,
        collection_name=None,
        camera_name=None,
        focus_target=None,
        view_name=None,
        orbit_horizontal=0.0,
        orbit_vertical=0.0,
        zoom_factor=None,
        persist_view=False,
    ):
        object_names = list(target_objects or ([] if target_object is None else [target_object]))
        if target_object and target_object not in object_names:
            object_names = [target_object, *object_names]
        return {
            "view_query": {
                "requested_view_source": "named_camera"
                if camera_name and camera_name != "USER_PERSPECTIVE"
                else "user_perspective",
                "resolved_view_source": "named_camera"
                if camera_name and camera_name != "USER_PERSPECTIVE"
                else "user_perspective",
                "requested_camera_name": camera_name if camera_name and camera_name != "USER_PERSPECTIVE" else None,
                "resolved_camera_name": camera_name if camera_name and camera_name != "USER_PERSPECTIVE" else None,
                "analysis_backend": "scene_camera"
                if camera_name and camera_name != "USER_PERSPECTIVE"
                else "mirrored_user_perspective",
                "available": True,
                "state_restored": not persist_view,
            },
            "summary": {
                "target_count": len(object_names),
                "visible_count": 1 if object_names else 0,
                "partially_visible_count": 1 if len(object_names) > 1 else 0,
                "fully_occluded_count": 0,
                "outside_frame_count": 0,
                "unavailable_count": 0,
                "centered_target_count": 1 if object_names else 0,
                "framing_issue_count": 1 if len(object_names) > 1 else 0,
            },
            "targets": [
                {
                    "object_name": name,
                    "visibility_verdict": "visible" if index == 0 else "partially_visible",
                    "projection_status": "projected",
                    "projection": {
                        "projected_center": {"x": 0.5 + (0.35 * index), "y": 0.5},
                        "projected_extent": {
                            "min_x": 0.4 + (0.3 * index),
                            "min_y": 0.3,
                            "max_x": 0.6 + (0.35 * index),
                            "max_y": 0.7,
                            "width": 0.2,
                            "height": 0.4,
                        },
                        "center_offset": {"x": 0.35 * index, "y": 0.0},
                        "frame_coverage_ratio": 1.0 if index == 0 else 0.55,
                        "frame_occupancy_ratio": 0.08,
                        "centered": index == 0,
                        "sample_count": 7,
                        "in_front_sample_count": 7,
                        "in_frame_sample_count": 7 if index == 0 else 4,
                        "visible_sample_count": 7 if index == 0 else 3,
                        "occluded_sample_count": 0 if index == 0 else 1,
                        "occlusion_test_available": True,
                    },
                }
                for index, name in enumerate(object_names)
            ],
        }

    def measure_distance(self, from_object, to_object, reference="ORIGIN"):
        return {
            "from_object": from_object,
            "to_object": to_object,
            "reference": reference,
            "distance": 2.0,
            "units": "blender_units",
        }

    def measure_dimensions(self, object_name, world_space=True):
        return {
            "object_name": object_name,
            "world_space": world_space,
            "dimensions": [1.0, 2.0, 3.0],
            "volume": 6.0,
            "units": "blender_units",
        }

    def measure_gap(self, from_object, to_object, tolerance=0.0001):
        return {
            "from_object": from_object,
            "to_object": to_object,
            "gap": 0.5,
            "relation": "separated",
            "units": "blender_units",
        }

    def measure_alignment(self, from_object, to_object, axes=None, reference="CENTER", tolerance=0.0001):
        return {
            "from_object": from_object,
            "to_object": to_object,
            "axes": axes or ["X", "Y", "Z"],
            "reference": reference,
            "is_aligned": True,
            "aligned_axes": axes or ["X", "Y", "Z"],
            "units": "blender_units",
        }

    def measure_overlap(self, from_object, to_object, tolerance=0.0001):
        return {
            "from_object": from_object,
            "to_object": to_object,
            "overlaps": False,
            "relation": "disjoint",
            "units": "blender_units",
        }

    def assert_contact(self, from_object, to_object, max_gap=0.0001, allow_overlap=False):
        return {
            "assertion": "scene_assert_contact",
            "passed": True,
            "subject": from_object,
            "target": to_object,
            "expected": {"max_gap": max_gap, "allow_overlap": allow_overlap},
            "actual": {"gap": 0.0, "relation": "contact"},
            "delta": {"gap_overage": 0.0},
            "tolerance": max_gap,
            "units": "blender_units",
        }

    def assert_dimensions(self, object_name, expected_dimensions, tolerance=0.0001, world_space=True):
        return {
            "assertion": "scene_assert_dimensions",
            "passed": True,
            "subject": object_name,
            "expected": {"dimensions": expected_dimensions},
            "actual": {"dimensions": expected_dimensions},
            "delta": {"x": 0.0, "y": 0.0, "z": 0.0},
            "tolerance": tolerance,
            "units": "blender_units",
        }

    def assert_containment(self, inner_object, outer_object, min_clearance=0.0, tolerance=0.0001):
        return {
            "assertion": "scene_assert_containment",
            "passed": True,
            "subject": inner_object,
            "target": outer_object,
            "actual": {"min_clearance": 0.2},
            "tolerance": tolerance,
            "units": "blender_units",
        }

    def assert_symmetry(self, left_object, right_object, axis="X", mirror_coordinate=0.0, tolerance=0.0001):
        return {
            "assertion": "scene_assert_symmetry",
            "passed": False,
            "subject": left_object,
            "target": right_object,
            "delta": {"mirror_axis": 0.2},
            "tolerance": tolerance,
            "units": "blender_units",
        }

    def assert_proportion(
        self,
        object_name,
        axis_a,
        expected_ratio,
        axis_b=None,
        reference_object=None,
        reference_axis=None,
        tolerance=0.01,
        world_space=True,
    ):
        return {
            "assertion": "scene_assert_proportion",
            "passed": True,
            "subject": object_name,
            "actual": {"ratio": expected_ratio},
            "tolerance": tolerance,
            "units": "ratio",
        }

    def inspect_render_settings(self):
        return {"render_engine": "BLENDER_EEVEE_NEXT", "resolution": {"x": 1920, "y": 1080, "percentage": 100}}

    def inspect_color_management(self):
        return {"display_device": "sRGB", "view_transform": "AgX", "look": "None"}

    def inspect_world(self):
        return {
            "world_name": "Studio",
            "use_nodes": True,
            "color": [0.05, 0.05, 0.05],
            "node_tree_name": "World Nodetree",
            "background": {"node_name": "Background", "color": [0.05, 0.05, 0.05, 1.0], "strength": 1.0},
            "node_graph_reference": {
                "graph_type": "world",
                "owner_name": "Studio",
                "node_tree_name": "World Nodetree",
                "background_node_name": "Background",
            },
            "node_graph_handoff": {
                "required": True,
                "target_tool_family": "node_graph",
                "reason": "world_uses_nodes",
                "world_name": "Studio",
                "node_tree_name": "World Nodetree",
                "supported_scene_configure_fields": [
                    "world_name",
                    "use_nodes",
                    "color",
                    "background.color",
                    "background.strength",
                ],
                "unsupported_scope": ["arbitrary_world_nodes", "custom_links", "full_node_topology_rebuild"],
                "background_node_name": "Background",
            },
        }

    def configure_render_settings(self, settings):
        return {"render_engine": settings.get("render_engine", "BLENDER_EEVEE_NEXT")}

    def configure_color_management(self, settings):
        return {"view_transform": settings.get("view_transform", "AgX")}

    def configure_world(self, settings):
        return {
            "world_name": settings.get("world_name", "Studio"),
            "use_nodes": settings.get("use_nodes", False),
            "node_graph_handoff": {
                "required": bool(settings.get("use_nodes", False)),
                "target_tool_family": "node_graph",
                "reason": "world_uses_nodes" if settings.get("use_nodes", False) else None,
                "world_name": settings.get("world_name", "Studio"),
                "node_tree_name": settings.get("node_tree_name"),
                "supported_scene_configure_fields": [
                    "world_name",
                    "use_nodes",
                    "color",
                    "background.color",
                    "background.strength",
                ],
                "unsupported_scope": ["arbitrary_world_nodes", "custom_links", "full_node_topology_rebuild"]
                if settings.get("use_nodes", False)
                else [],
            },
        }

    def create_light(self, type, energy, color, location, name=None):
        return name or "KeyLight"

    def create_camera(self, location, rotation, lens=50.0, clip_start=None, clip_end=None, name=None):
        return name or "Camera"

    def create_empty(self, type, size, location, name=None):
        return name or "Locator"


class MeshHandler:
    def get_shape_keys(self, object_name, include_deltas=False):
        return {"shape_key_count": 0}

    def get_loop_normals(self, object_name, selected_only=False):
        return {"custom_normals": False}

    def list_groups(self, object_name, group_type="VERTEX"):
        return {"groups": [{"name": "GroupA"}]}


class SceneInspectHandler:
    def inspect_mesh_topology(self, object_name, detailed=False):
        return {
            "vertex_count": 8,
            "edge_count": 12,
            "face_count": 6,
        }


class UVHandler:
    def list_maps(self, object_name, include_island_counts=False):
        return {"uv_map_count": 1}


class ModelingHandler:
    def get_modifiers(self, object_name):
        return [{"name": "Bevel"}]


class MacroHandler:
    def cutout_recess(self, **kwargs):
        return {
            "status": "success",
            "macro_name": "macro_cutout_recess",
            "intent": "recess cutout on BodyShell",
            "actions_taken": [
                {"status": "applied", "action": "create_cutter", "tool_name": "modeling_create_primitive"}
            ],
            "objects_modified": [kwargs.get("target_object", "BodyShell")],
            "verification_recommended": [
                {"tool_name": "inspect_scene", "reason": "Verify target state after cutout", "priority": "normal"}
            ],
            "requires_followup": True,
        }

    def finish_form(self, **kwargs):
        return {
            "status": "success",
            "macro_name": "macro_finish_form",
            "intent": "apply rounded_housing finishing preset",
            "actions_taken": [
                {"status": "applied", "action": "add_bevel_finish", "tool_name": "modeling_add_modifier"}
            ],
            "objects_modified": [kwargs.get("target_object", "BodyShell")],
            "verification_recommended": [
                {"tool_name": "inspect_scene", "reason": "Verify the finishing stack", "priority": "normal"}
            ],
            "requires_followup": True,
        }

    def relative_layout(self, **kwargs):
        return {
            "status": "success",
            "macro_name": "macro_relative_layout",
            "intent": "layout Leg relative to TableTop",
            "actions_taken": [
                {"status": "applied", "action": "apply_relative_layout", "tool_name": "modeling_transform_object"}
            ],
            "objects_modified": [kwargs.get("moving_object", "Leg")],
            "verification_recommended": [
                {"tool_name": "scene_measure_gap", "reason": "Confirm gap/contact after layout", "priority": "high"}
            ],
            "requires_followup": True,
        }

    def attach_part_to_surface(self, **kwargs):
        return {
            "status": "success",
            "macro_name": "macro_attach_part_to_surface",
            "intent": "attach Ear to Head",
            "actions_taken": [
                {"status": "applied", "action": "attach_part_to_surface", "tool_name": "modeling_transform_object"},
                {
                    "status": "applied",
                    "action": "evaluate_attachment_outcome",
                    "tool_name": "scene_assert_contact",
                    "details": {"attachment_verdict": "seated_contact"},
                },
            ],
            "objects_modified": [kwargs.get("part_object", "Ear")],
            "verification_recommended": [
                {"tool_name": "scene_measure_gap", "reason": "Confirm seating/contact after attach", "priority": "high"}
            ],
            "requires_followup": True,
        }

    def align_part_with_contact(self, **kwargs):
        return {
            "status": "success",
            "macro_name": "macro_align_part_with_contact",
            "intent": "repair Ear relative to Head",
            "actions_taken": [
                {"status": "applied", "action": "align_part_with_contact", "tool_name": "modeling_transform_object"},
                {
                    "status": "applied",
                    "action": "evaluate_attachment_outcome",
                    "tool_name": "scene_assert_contact",
                    "details": {"attachment_verdict": "seated_contact"},
                },
            ],
            "objects_modified": [kwargs.get("part_object", "Ear")],
            "verification_recommended": [
                {"tool_name": "scene_measure_gap", "reason": "Confirm repaired contact after nudge", "priority": "high"}
            ],
            "requires_followup": True,
        }

    def place_symmetry_pair(self, **kwargs):
        return {
            "status": "success",
            "macro_name": "macro_place_symmetry_pair",
            "intent": "mirror Ear_L / Ear_R",
            "actions_taken": [
                {"status": "applied", "action": "place_symmetry_pair", "tool_name": "modeling_transform_object"}
            ],
            "objects_modified": [kwargs.get("right_object", "Ear_R")],
            "verification_recommended": [
                {
                    "tool_name": "scene_assert_symmetry",
                    "reason": "Confirm mirrored placement after the move",
                    "priority": "high",
                }
            ],
            "requires_followup": True,
        }

    def place_supported_pair(self, **kwargs):
        return {
            "status": "success",
            "macro_name": "macro_place_supported_pair",
            "intent": "place Foot_L / Foot_R on Floor",
            "actions_taken": [
                {"status": "applied", "action": "place_supported_pair_anchor", "tool_name": "modeling_transform_object"}
            ],
            "objects_modified": [
                kwargs.get("left_object", "Foot_L"),
                kwargs.get("right_object", "Foot_R"),
            ],
            "verification_recommended": [
                {"tool_name": "scene_assert_contact", "reason": "Confirm shared support contact", "priority": "high"}
            ],
            "requires_followup": True,
        }

    def cleanup_part_intersections(self, **kwargs):
        return {
            "status": "success",
            "macro_name": "macro_cleanup_part_intersections",
            "intent": "clean Horn / Head overlap",
            "actions_taken": [
                {
                    "status": "applied",
                    "action": "cleanup_part_intersections",
                    "tool_name": "modeling_transform_object",
                },
                {
                    "status": "applied",
                    "action": "evaluate_attachment_outcome",
                    "tool_name": "scene_assert_contact",
                    "details": {"attachment_verdict": "seated_contact"},
                },
            ],
            "objects_modified": [kwargs.get("part_object", "Horn")],
            "verification_recommended": [
                {"tool_name": "scene_measure_overlap", "reason": "Confirm overlap is gone", "priority": "high"}
            ],
            "requires_followup": True,
        }

    def adjust_relative_proportion(self, **kwargs):
        return {
            "status": "success",
            "macro_name": "macro_adjust_relative_proportion",
            "intent": "repair Head / Body proportion",
            "actions_taken": [
                {
                    "status": "applied",
                    "action": "adjust_relative_proportion",
                    "tool_name": "modeling_transform_object",
                }
            ],
            "objects_modified": [kwargs.get("primary_object", "Head")],
            "verification_recommended": [
                {"tool_name": "scene_assert_proportion", "reason": "Confirm repaired ratio", "priority": "high"}
            ],
            "requires_followup": True,
        }

    def adjust_segment_chain_arc(self, **kwargs):
        return {
            "status": "success",
            "macro_name": "macro_adjust_segment_chain_arc",
            "intent": "adjust Segment_01/Segment_02/Segment_03 chain arc",
            "actions_taken": [
                {
                    "status": "applied",
                    "action": "adjust_segment_chain_arc",
                    "tool_name": "modeling_transform_object",
                }
            ],
            "objects_modified": list(kwargs.get("segment_objects", [])[1:]),
            "verification_recommended": [
                {"tool_name": "inspect_scene", "reason": "Verify updated chain arc", "priority": "normal"}
            ],
            "requires_followup": True,
        }


def _unwrap_structured(result):
    structured = getattr(result, "structured_content", None)
    if structured is None:
        return None
    if isinstance(structured, dict) and "result" in structured:
        return structured["result"]
    return structured


def test_contract_enabled_tools_expose_output_schema_on_listed_surface():
    """Contract-enabled tools should declare outputSchema on the MCP surface."""

    server = build_server("legacy-flat")

    async def run():
        tools = await server.list_tools()
        by_name = {tool.name: tool for tool in tools}
        return (
            by_name["macro_cutout_recess"],
            by_name["macro_finish_form"],
            by_name["macro_relative_layout"],
            by_name["macro_attach_part_to_surface"],
            by_name["macro_align_part_with_contact"],
            by_name["macro_place_symmetry_pair"],
            by_name["macro_place_supported_pair"],
            by_name["macro_cleanup_part_intersections"],
            by_name["macro_adjust_relative_proportion"],
            by_name["macro_adjust_segment_chain_arc"],
            by_name["scene_context"],
            by_name["scene_create"],
            by_name["scene_configure"],
            by_name["mesh_select"],
            by_name["mesh_select_targeted"],
            by_name["mesh_inspect"],
            by_name["router_set_goal"],
        )

    (
        macro_tool,
        finish_macro_tool,
        layout_macro_tool,
        attach_macro_tool,
        repair_macro_tool,
        symmetry_macro_tool,
        supported_pair_macro_tool,
        cleanup_macro_tool,
        proportion_macro_tool,
        tail_arc_macro_tool,
        scene_context_tool,
        scene_create_tool,
        scene_configure_tool,
        mesh_select_tool,
        mesh_select_targeted_tool,
        mesh_inspect_tool,
        router_tool,
    ) = asyncio.run(run())

    assert macro_tool.output_schema is not None
    assert finish_macro_tool.output_schema is not None
    assert layout_macro_tool.output_schema is not None
    assert attach_macro_tool.output_schema is not None
    assert repair_macro_tool.output_schema is not None
    assert symmetry_macro_tool.output_schema is not None
    assert supported_pair_macro_tool.output_schema is not None
    assert cleanup_macro_tool.output_schema is not None
    assert proportion_macro_tool.output_schema is not None
    assert tail_arc_macro_tool.output_schema is not None
    assert scene_context_tool.output_schema is not None
    assert scene_create_tool.output_schema is not None
    assert scene_configure_tool.output_schema is not None
    assert mesh_select_tool.output_schema is not None
    assert mesh_select_targeted_tool.output_schema is not None
    assert mesh_inspect_tool.output_schema is not None
    assert router_tool.output_schema is not None


def test_scene_context_and_snapshot_deliver_structured_content(monkeypatch):
    """Scene contract tools should surface machine-readable structured content."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)

    server = build_server("legacy-flat")

    async def run():
        scene_context = await server.call_tool("scene_context", {"action": "mode"})
        snapshot = await server.call_tool("scene_snapshot_state", {})
        return scene_context, snapshot

    scene_context, snapshot = asyncio.run(run())

    scene_payload = _unwrap_structured(scene_context)
    snapshot_payload = _unwrap_structured(snapshot)

    assert scene_payload["action"] == "mode"
    assert scene_payload["payload"]["active_object"] == "Cube"
    assert snapshot_payload["snapshot"]["object_count"] == 1
    assert snapshot_payload["hash"] == "abc123"


def test_scene_read_contract_tools_deliver_structured_content(monkeypatch):
    """Additional scene read tools should surface structured contracts instead of prose blobs."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)

    server = build_server("legacy-flat")

    async def run():
        props = await server.call_tool("scene_get_custom_properties", {"object_name": "Cube"})
        hierarchy = await server.call_tool("scene_get_hierarchy", {})
        bbox = await server.call_tool("scene_get_bounding_box", {"object_name": "Cube"})
        origin = await server.call_tool("scene_get_origin_info", {"object_name": "Cube"})
        return props, hierarchy, bbox, origin

    props, hierarchy, bbox, origin = asyncio.run(run())

    assert _unwrap_structured(props)["properties"]["tag"] == "hero"
    assert _unwrap_structured(hierarchy)["payload"]["total_objects"] == 1
    assert _unwrap_structured(bbox)["payload"]["volume"] == 1.0
    assert _unwrap_structured(origin)["payload"]["origin_world"] == [0, 0, 0]


def test_scene_inspect_scene_state_actions_deliver_structured_content(monkeypatch):
    """Grouped scene_inspect should also surface structured scene-level state actions."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)

    server = build_server("legacy-flat")

    async def run():
        render = await server.call_tool("scene_inspect", {"action": "render"})
        color = await server.call_tool("scene_inspect", {"action": "color_management"})
        world = await server.call_tool("scene_inspect", {"action": "world"})
        return render, color, world

    render, color, world = asyncio.run(run())

    assert _unwrap_structured(render)["payload"]["render_engine"] == "BLENDER_EEVEE_NEXT"
    assert _unwrap_structured(color)["payload"]["view_transform"] == "AgX"
    assert _unwrap_structured(world)["payload"]["world_name"] == "Studio"
    assert _unwrap_structured(world)["payload"]["node_graph_handoff"]["required"] is True
    assert _unwrap_structured(world)["payload"]["node_graph_reference"]["graph_type"] == "world"


def test_scene_configure_delivers_structured_content(monkeypatch):
    """Grouped scene_configure should also surface structured write-side payloads."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)

    server = build_server("legacy-flat")

    async def run():
        render = await server.call_tool(
            "scene_configure", {"action": "render", "settings": {"render_engine": "CYCLES"}}
        )
        color = await server.call_tool(
            "scene_configure",
            {"action": "color_management", "settings": {"view_transform": "AgX"}},
        )
        world = await server.call_tool(
            "scene_configure",
            {"action": "world", "settings": {"world_name": "Studio", "use_nodes": True}},
        )
        return render, color, world

    render, color, world = asyncio.run(run())

    assert _unwrap_structured(render)["payload"]["render_engine"] == "CYCLES"
    assert _unwrap_structured(color)["payload"]["view_transform"] == "AgX"
    assert _unwrap_structured(world)["payload"]["world_name"] == "Studio"
    assert _unwrap_structured(world)["payload"]["node_graph_handoff"]["required"] is True


def test_scene_create_and_mesh_select_deliver_structured_content(monkeypatch):
    """Grouped scene_create and mesh_select tools should also surface machine-readable payloads."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.mesh.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)
    monkeypatch.setattr("server.adapters.mcp.areas.mesh._mesh_select_all", lambda ctx, deselect=False: "All selected")
    monkeypatch.setattr(
        "server.adapters.mcp.areas.mesh._mesh_select_by_index",
        lambda ctx, indices, element_type, selection_mode: "Selected by index",
    )

    server = build_server("legacy-flat")

    async def run():
        created = await server.call_tool(
            "scene_create",
            {"action": "light", "light_type": "SUN", "energy": 5.0, "location": [0, 0, 5]},
        )
        selected = await server.call_tool("mesh_select", {"action": "all"})
        targeted = await server.call_tool(
            "mesh_select_targeted",
            {"action": "by_index", "indices": [0, 1], "element_type": "VERT", "selection_mode": "SET"},
        )
        return created, selected, targeted

    created, selected, targeted = asyncio.run(run())

    assert _unwrap_structured(created)["payload"]["object_type"] == "LIGHT"
    assert _unwrap_structured(selected)["payload"]["message"] == "All selected"
    assert _unwrap_structured(targeted)["payload"]["operation"]["indices"] == [0, 1]


def test_macro_cutout_recess_delivers_structured_content(monkeypatch):
    """Macro tools should also expose machine-readable reports on the MCP surface."""

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_macro_handler", lambda: MacroHandler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = build_server("legacy-flat")

    async def run():
        return await server.call_tool(
            "macro_cutout_recess",
            {
                "target_object": "BodyShell",
                "width": 0.8,
                "height": 1.2,
                "depth": 0.2,
            },
        )

    result = asyncio.run(run())

    payload = _unwrap_structured(result)
    assert payload["macro_name"] == "macro_cutout_recess"
    assert payload["actions_taken"][0]["action"] == "create_cutter"
    assert payload["requires_followup"] is True


def test_macro_finish_form_delivers_structured_content(monkeypatch):
    """Finishing macros should also expose machine-readable reports on the MCP surface."""

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_macro_handler", lambda: MacroHandler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = build_server("legacy-flat")

    async def run():
        return await server.call_tool(
            "macro_finish_form",
            {
                "target_object": "BodyShell",
                "preset": "rounded_housing",
            },
        )

    result = asyncio.run(run())

    payload = _unwrap_structured(result)
    assert payload["macro_name"] == "macro_finish_form"
    assert payload["actions_taken"][0]["action"] == "add_bevel_finish"
    assert payload["requires_followup"] is True


def test_macro_relative_layout_delivers_structured_content(monkeypatch):
    """Scene macro tools should expose machine-readable reports on the MCP surface."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: MacroHandler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = build_server("legacy-flat")

    async def run():
        return await server.call_tool(
            "macro_relative_layout",
            {
                "moving_object": "Leg",
                "reference_object": "TableTop",
            },
        )

    result = asyncio.run(run())

    payload = _unwrap_structured(result)
    assert payload["macro_name"] == "macro_relative_layout"
    assert payload["actions_taken"][0]["action"] == "apply_relative_layout"
    assert payload["requires_followup"] is True


def test_macro_attach_part_to_surface_delivers_structured_content(monkeypatch):
    """Surface-attach macro should expose machine-readable reports on the MCP surface."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: MacroHandler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = build_server("legacy-flat")

    async def run():
        return await server.call_tool(
            "macro_attach_part_to_surface",
            {
                "part_object": "Ear",
                "surface_object": "Head",
                "surface_axis": "X",
            },
        )

    result = asyncio.run(run())

    payload = _unwrap_structured(result)
    assert payload["macro_name"] == "macro_attach_part_to_surface"
    assert payload["actions_taken"][0]["action"] == "attach_part_to_surface"
    assert payload["actions_taken"][-1]["details"]["attachment_verdict"] == "seated_contact"
    assert payload["requires_followup"] is True


def test_macro_align_part_with_contact_delivers_structured_content(monkeypatch):
    """Repair macro should expose machine-readable reports on the MCP surface."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: MacroHandler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = build_server("legacy-flat")

    async def run():
        return await server.call_tool(
            "macro_align_part_with_contact",
            {
                "part_object": "Ear",
                "reference_object": "Head",
            },
        )

    result = asyncio.run(run())

    payload = _unwrap_structured(result)
    assert payload["macro_name"] == "macro_align_part_with_contact"
    assert payload["actions_taken"][0]["action"] == "align_part_with_contact"
    assert payload["actions_taken"][-1]["details"]["attachment_verdict"] == "seated_contact"
    assert payload["requires_followup"] is True


def test_macro_place_symmetry_pair_delivers_structured_content(monkeypatch):
    """Symmetry-pair macro should expose machine-readable reports on the MCP surface."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: MacroHandler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = build_server("legacy-flat")

    async def run():
        return await server.call_tool(
            "macro_place_symmetry_pair",
            {
                "left_object": "Ear_L",
                "right_object": "Ear_R",
            },
        )

    result = asyncio.run(run())

    payload = _unwrap_structured(result)
    assert payload["macro_name"] == "macro_place_symmetry_pair"
    assert payload["actions_taken"][0]["action"] == "place_symmetry_pair"
    assert payload["requires_followup"] is True


def test_macro_place_supported_pair_delivers_structured_content(monkeypatch):
    """Supported-pair macro should expose machine-readable reports on the MCP surface."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: MacroHandler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = build_server("legacy-flat")

    async def run():
        return await server.call_tool(
            "macro_place_supported_pair",
            {
                "left_object": "Foot_L",
                "right_object": "Foot_R",
                "support_object": "Floor",
            },
        )

    result = asyncio.run(run())

    payload = _unwrap_structured(result)
    assert payload["macro_name"] == "macro_place_supported_pair"
    assert payload["actions_taken"][0]["action"] == "place_supported_pair_anchor"
    assert payload["requires_followup"] is True


def test_macro_cleanup_part_intersections_delivers_structured_content(monkeypatch):
    """Intersection-cleanup macro should expose machine-readable reports on the MCP surface."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: MacroHandler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = build_server("legacy-flat")

    async def run():
        return await server.call_tool(
            "macro_cleanup_part_intersections",
            {
                "part_object": "Horn",
                "reference_object": "Head",
            },
        )

    result = asyncio.run(run())

    payload = _unwrap_structured(result)
    assert payload["macro_name"] == "macro_cleanup_part_intersections"
    assert payload["actions_taken"][0]["action"] == "cleanup_part_intersections"
    assert payload["actions_taken"][-1]["details"]["attachment_verdict"] == "seated_contact"
    assert payload["requires_followup"] is True


def test_macro_adjust_relative_proportion_delivers_structured_content(monkeypatch):
    """Proportion-repair macro should expose machine-readable reports on the MCP surface."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: MacroHandler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = build_server("legacy-flat")

    async def run():
        return await server.call_tool(
            "macro_adjust_relative_proportion",
            {
                "primary_object": "Head",
                "reference_object": "Body",
                "expected_ratio": 0.4,
            },
        )

    result = asyncio.run(run())

    payload = _unwrap_structured(result)
    assert payload["macro_name"] == "macro_adjust_relative_proportion"
    assert payload["actions_taken"][0]["action"] == "adjust_relative_proportion"
    assert payload["requires_followup"] is True


def test_macro_adjust_segment_chain_arc_delivers_structured_content(monkeypatch):
    """Segment-chain arc macro should expose machine-readable reports on the MCP surface."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_macro_handler", lambda: MacroHandler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = build_server("legacy-flat")

    async def run():
        return await server.call_tool(
            "macro_adjust_segment_chain_arc",
            {
                "segment_objects": ["Tail_01", "Tail_02", "Tail_03"],
            },
        )

    result = asyncio.run(run())

    payload = _unwrap_structured(result)
    assert payload["macro_name"] == "macro_adjust_segment_chain_arc"
    assert payload["actions_taken"][0]["action"] == "adjust_segment_chain_arc"
    assert payload["requires_followup"] is True


def test_scene_measure_contract_tools_deliver_structured_content(monkeypatch):
    """Truth-layer measurement tools should surface structured contracts instead of prose blobs."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)

    server = build_server("legacy-flat")

    async def run():
        distance = await server.call_tool(
            "scene_measure_distance", {"from_object": "Cube", "to_object": "Sphere", "reference": "ORIGIN"}
        )
        dimensions = await server.call_tool("scene_measure_dimensions", {"object_name": "Cube"})
        gap = await server.call_tool("scene_measure_gap", {"from_object": "Cube", "to_object": "Sphere"})
        alignment = await server.call_tool(
            "scene_measure_alignment",
            {"from_object": "Cube", "to_object": "Sphere", "axes": ["Y", "Z"]},
        )
        overlap = await server.call_tool("scene_measure_overlap", {"from_object": "Cube", "to_object": "Sphere"})
        return distance, dimensions, gap, alignment, overlap

    distance, dimensions, gap, alignment, overlap = asyncio.run(run())

    assert _unwrap_structured(distance)["payload"]["distance"] == 2.0
    assert _unwrap_structured(dimensions)["payload"]["volume"] == 6.0
    assert _unwrap_structured(gap)["payload"]["relation"] == "separated"
    assert _unwrap_structured(alignment)["payload"]["is_aligned"] is True
    assert _unwrap_structured(overlap)["payload"]["relation"] == "disjoint"


def test_scene_spatial_graph_contract_tools_deliver_structured_content(monkeypatch):
    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)

    server = build_server("legacy-flat")

    async def run():
        scope = await server.call_tool(
            "scene_scope_graph",
            {"target_object": "Squirrel_Body", "target_objects": ["Squirrel_Head", "Squirrel_Tail"]},
        )
        relations = await server.call_tool(
            "scene_relation_graph",
            {"target_objects": ["Squirrel_Head", "Squirrel_Body"], "goal_hint": "assembled creature"},
        )
        return scope, relations

    scope, relations = asyncio.run(run())
    scope_payload = _unwrap_structured(scope)
    relation_payload = _unwrap_structured(relations)

    assert scope_payload["payload"]["scope"]["primary_target"] == "Squirrel_Body"
    assert scope_payload["payload"]["scope"]["object_roles"][0]["object_name"] == "Squirrel_Body"
    assert relation_payload["payload"]["summary"]["pair_count"] == 1
    assert relation_payload["payload"]["pairs"][0]["attachment_semantics"]["attachment_verdict"] == "floating_gap"


def test_scene_view_diagnostics_contract_tool_delivers_structured_content(monkeypatch):
    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)

    server = build_server("legacy-flat")

    async def run():
        return await server.call_tool(
            "scene_view_diagnostics",
            {
                "target_object": "Squirrel_Head",
                "target_objects": ["Squirrel_Body"],
                "view_name": "TOP",
            },
        )

    result = asyncio.run(run())
    payload = _unwrap_structured(result)

    assert payload["payload"]["scope"]["primary_target"] == "Squirrel_Head"
    assert payload["payload"]["view_query"]["requested_view_source"] == "user_perspective"
    assert payload["payload"]["summary"]["target_count"] == 2
    assert payload["payload"]["targets"][0]["projection"]["projected_center"]["x"] == 0.5


def test_scene_assert_contract_tools_deliver_structured_content(monkeypatch):
    """Scene assertion tools should surface structured assertion contracts instead of prose blobs."""

    monkeypatch.setattr("server.adapters.mcp.areas.scene.get_scene_handler", lambda: SceneHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.scene.ctx_info", lambda ctx, message: None)

    server = build_server("legacy-flat")

    async def run():
        contact = await server.call_tool(
            "scene_assert_contact",
            {"from_object": "Cube", "to_object": "Sphere", "max_gap": 0.001},
        )
        dimensions = await server.call_tool(
            "scene_assert_dimensions",
            {"object_name": "Cube", "expected_dimensions": [1.0, 2.0, 3.0]},
        )
        containment = await server.call_tool(
            "scene_assert_containment",
            {"inner_object": "Cube", "outer_object": "Shell"},
        )
        symmetry = await server.call_tool(
            "scene_assert_symmetry",
            {"left_object": "Left", "right_object": "Right"},
        )
        proportion = await server.call_tool(
            "scene_assert_proportion",
            {"object_name": "Cube", "axis_a": "X", "axis_b": "Y", "expected_ratio": 0.5},
        )
        return contact, dimensions, containment, symmetry, proportion

    contact, dimensions, containment, symmetry, proportion = asyncio.run(run())

    assert _unwrap_structured(contact)["payload"]["passed"] is True
    assert _unwrap_structured(contact)["payload"]["actual"]["relation"] == "contact"
    assert _unwrap_structured(dimensions)["payload"]["assertion"] == "scene_assert_dimensions"
    assert _unwrap_structured(dimensions)["payload"]["passed"] is True
    assert _unwrap_structured(containment)["payload"]["actual"]["min_clearance"] == 0.2
    assert _unwrap_structured(symmetry)["payload"]["delta"]["mirror_axis"] == 0.2
    assert _unwrap_structured(proportion)["payload"]["actual"]["ratio"] == 0.5


def test_mesh_inspect_contract_delivers_structured_content(monkeypatch):
    """Mesh contract tools should surface machine-readable structured content."""

    monkeypatch.setattr("server.adapters.mcp.areas.mesh.get_mesh_handler", lambda: MeshHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.mesh.get_scene_handler", lambda: SceneInspectHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.mesh.get_uv_handler", lambda: UVHandler())
    monkeypatch.setattr("server.adapters.mcp.areas.mesh.get_modeling_handler", lambda: ModelingHandler())
    monkeypatch.setattr("server.adapters.mcp.router_helper.is_router_enabled", lambda: False)

    server = build_server("legacy-flat")

    async def run():
        return await server.call_tool("mesh_inspect", {"action": "summary", "object_name": "Cube"})

    result = asyncio.run(run())
    payload = _unwrap_structured(result)

    assert payload["action"] == "summary"
    assert payload["object_name"] == "Cube"
    assert payload["summary"]["vertex_count"] == 8
    assert payload["summary"]["modifiers"] == ["Bevel"]
