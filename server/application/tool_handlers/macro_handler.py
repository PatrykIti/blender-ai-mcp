from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, cast, overload
from uuid import uuid4

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract
from server.adapters.mcp.contracts.vision import VisionCaptureImageContract
from server.adapters.mcp.vision.capture_runtime import (
    CapturePresetProfile,
    CaptureStage,
    build_capture_bundle,
    capture_stage_images,
)
from server.adapters.mcp.vision.reporting import attach_vision_artifacts
from server.domain.tools.macro import IMacroTool
from server.domain.tools.modeling import IModelingTool
from server.domain.tools.scene import ISceneTool
from server.infrastructure.config import get_config

AxisName = Literal["X", "Y", "Z"]
ContactSideName = Literal["positive", "negative"]
SymmetryAnchorName = Literal["auto", "left", "right"]
ScaleTargetName = Literal["primary", "reference"]


class MacroToolHandler(IMacroTool):
    """Server-side bounded macro orchestrator built on top of existing atomic/grouped tools."""

    _FACE_SPECS: dict[str, tuple[int, int, int]] = {
        "front": (1, 0, 2),
        "back": (1, 0, 2),
        "left": (0, 1, 2),
        "right": (0, 1, 2),
        "bottom": (2, 0, 1),
        "top": (2, 0, 1),
    }
    _AXIS_INDEX: dict[str, int] = {"X": 0, "Y": 1, "Z": 2}
    _FINISH_PRESETS: dict[str, dict[str, float | int | None]] = {
        "rounded_housing": {"bevel_width": 0.03, "bevel_segments": 3, "subsurf_levels": 2, "thickness": None},
        "panel_finish": {"bevel_width": 0.01, "bevel_segments": 2, "subsurf_levels": None, "thickness": None},
        "shell_thicken": {"bevel_width": None, "bevel_segments": None, "subsurf_levels": None, "thickness": 0.03},
        "smooth_subdivision": {"bevel_width": None, "bevel_segments": None, "subsurf_levels": 2, "thickness": None},
    }

    def __init__(self, scene_tool: ISceneTool, modeling_tool: IModelingTool):
        self._scene = scene_tool
        self._modeling = modeling_tool

    def cutout_recess(
        self,
        target_object: str,
        width: float,
        height: float,
        depth: float,
        face: str = "front",
        offset: Optional[List[float]] = None,
        mode: str = "recess",
        bevel_width: Optional[float] = None,
        bevel_segments: int = 2,
        cleanup: str = "delete",
        cutter_name: Optional[str] = None,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        face_name = self._normalize_face(face)
        mode_name = self._normalize_mode(mode)
        cleanup_mode = self._normalize_cleanup(cleanup)
        offset_vector = self._normalize_offset(offset)

        width_value = self._require_positive(width, "width")
        height_value = self._require_positive(height, "height")
        depth_value = self._require_positive(depth, "depth")
        bevel_segments_value = self._require_segments(bevel_segments)
        bevel_width_value = self._require_optional_positive(bevel_width, "bevel_width")
        bundle_id = self._make_capture_bundle_id("macro_cutout_recess", target_object)
        captures_before = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="before",
            target_object=target_object,
            capture_profile=capture_profile,
        )

        bbox = self._scene.get_bounding_box(target_object, world_space=True)
        cutter_dimensions = self._compute_cutter_dimensions(
            bbox=bbox,
            face=face_name,
            width=width_value,
            height=height_value,
            depth=depth_value,
            mode=mode_name,
        )
        cutter_location = self._compute_cutter_location(
            bbox=bbox,
            face=face_name,
            depth=depth_value,
            mode=mode_name,
            offset=offset_vector,
        )
        cutter_scale = [dimension / 2.0 for dimension in cutter_dimensions]
        resolved_cutter_name = self._allocate_cutter_name(cutter_name or f"{target_object}_macro_cutout_helper")

        actions_taken: list[Dict[str, Any]] = []

        self._modeling.create_primitive(
            primitive_type="Cube",
            size=2.0,
            location=cutter_location,
            rotation=[0.0, 0.0, 0.0],
            name=resolved_cutter_name,
        )
        actions_taken.append(
            {
                "status": "applied",
                "action": "create_cutter",
                "tool_name": "modeling_create_primitive",
                "summary": f"Created cutter '{resolved_cutter_name}'",
                "details": {
                    "primitive_type": "Cube",
                    "location": cutter_location,
                },
            }
        )

        self._modeling.transform_object(name=resolved_cutter_name, scale=cutter_scale)
        actions_taken.append(
            {
                "status": "applied",
                "action": "fit_cutter",
                "tool_name": "modeling_transform_object",
                "summary": "Scaled cutter to requested recess dimensions",
                "details": {"scale": cutter_scale, "dimensions": cutter_dimensions},
            }
        )

        if bevel_width_value is not None:
            before_cutter_modifiers = self._modifier_names(resolved_cutter_name)
            self._modeling.add_modifier(
                resolved_cutter_name,
                "BEVEL",
                properties={
                    "width": bevel_width_value,
                    "segments": bevel_segments_value,
                    "limit_method": "NONE",
                },
            )
            bevel_modifier_name = self._resolve_new_modifier_name(
                target_object=resolved_cutter_name,
                before_names=before_cutter_modifiers,
                modifier_type="BEVEL",
            )
            self._modeling.apply_modifier(resolved_cutter_name, bevel_modifier_name)
            actions_taken.append(
                {
                    "status": "applied",
                    "action": "round_cutter",
                    "tool_name": "modeling_apply_modifier",
                    "summary": f"Applied bevel '{bevel_modifier_name}' on cutter",
                    "details": {
                        "modifier_type": "BEVEL",
                        "width": bevel_width_value,
                        "segments": bevel_segments_value,
                    },
                }
            )

        before_target_modifiers = self._modifier_names(target_object)
        self._modeling.add_modifier(
            target_object,
            "BOOLEAN",
            properties={
                "operation": "DIFFERENCE",
                "solver": "EXACT",
                "object": resolved_cutter_name,
            },
        )
        boolean_modifier_name = self._resolve_new_modifier_name(
            target_object=target_object,
            before_names=before_target_modifiers,
            modifier_type="BOOLEAN",
        )
        self._modeling.apply_modifier(target_object, boolean_modifier_name)
        actions_taken.append(
            {
                "status": "applied",
                "action": "apply_boolean_difference",
                "tool_name": "modeling_apply_modifier",
                "summary": f"Applied boolean '{boolean_modifier_name}' on '{target_object}'",
                "details": {
                    "modifier_type": "BOOLEAN",
                    "cutter_name": resolved_cutter_name,
                    "operation": "DIFFERENCE",
                },
            }
        )

        helper_objects = [resolved_cutter_name]
        if cleanup_mode == "delete":
            self._scene.delete_object(resolved_cutter_name)
            helper_objects = []
            actions_taken.append(
                {
                    "status": "applied",
                    "action": "cleanup_cutter",
                    "tool_name": "scene_delete_object",
                    "summary": f"Deleted cutter '{resolved_cutter_name}'",
                }
            )
        elif cleanup_mode == "hide":
            self._scene.hide_object(resolved_cutter_name, hide=True, hide_render=True)
            actions_taken.append(
                {
                    "status": "applied",
                    "action": "cleanup_cutter",
                    "tool_name": "scene_hide_object",
                    "summary": f"Hid cutter '{resolved_cutter_name}' from viewport and render",
                }
            )

        report = {
            "status": "success",
            "macro_name": "macro_cutout_recess",
            "intent": f"{mode_name} cutout on the {face_name} face of '{target_object}'",
            "actions_taken": actions_taken,
            "objects_created": helper_objects or None,
            "objects_modified": [target_object],
            "verification_recommended": [
                {
                    "tool_name": "inspect_scene",
                    "reason": "Verify the target object after the boolean cutout operation.",
                    "priority": "normal",
                    "arguments_hint": {"action": "object", "target_object": target_object},
                },
                {
                    "tool_name": "scene_get_bounding_box",
                    "reason": "Confirm the target bounding box still matches the intended outer dimensions.",
                    "priority": "normal",
                    "arguments_hint": {"object_name": target_object, "world_space": True},
                },
                {
                    "tool_name": "scene_get_viewport",
                    "reason": "Do a quick visual check of the cutout footprint and face placement.",
                    "priority": "normal",
                    "arguments_hint": {"focus_target": target_object, "shading": "SOLID"},
                },
            ],
            "requires_followup": True,
        }
        captures_after = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="after",
            target_object=target_object,
            capture_profile=capture_profile,
        )
        return self._finalize_report(
            report,
            bundle_id=bundle_id,
            target_object=target_object,
            captures_before=captures_before,
            captures_after=captures_after,
        )

    def relative_layout(
        self,
        moving_object: str,
        reference_object: str,
        x_mode: str = "center",
        y_mode: str = "center",
        z_mode: str = "none",
        contact_axis: Optional[str] = None,
        contact_side: str = "positive",
        gap: float = 0.0,
        offset: Optional[List[float]] = None,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        if moving_object == reference_object:
            raise ValueError("moving_object and reference_object must be different")

        modes = {
            "X": self._normalize_layout_mode(x_mode, field_name="x_mode"),
            "Y": self._normalize_layout_mode(y_mode, field_name="y_mode"),
            "Z": self._normalize_layout_mode(z_mode, field_name="z_mode"),
        }
        resolved_contact_axis = self._normalize_contact_axis(contact_axis)
        resolved_contact_side = self._normalize_contact_side(contact_side)
        gap_value = self._require_non_negative(gap, "gap")
        offset_vector = self._normalize_offset(offset)

        if resolved_contact_axis is None and all(mode == "none" for mode in modes.values()):
            raise ValueError("macro_relative_layout needs at least one alignment mode or contact_axis")
        intent_parts = [f"x={modes['X']}", f"y={modes['Y']}", f"z={modes['Z']}"]
        if resolved_contact_axis is not None:
            intent_parts.append(f"contact {resolved_contact_side} on {resolved_contact_axis}")
            intent_parts.append(f"gap={gap_value:g}")
        return self._execute_relative_layout_macro(
            macro_name="macro_relative_layout",
            moving_object=moving_object,
            reference_object=reference_object,
            modes=modes,
            resolved_contact_axis=resolved_contact_axis,
            resolved_contact_side=resolved_contact_side,
            gap_value=gap_value,
            offset_vector=offset_vector,
            capture_profile=capture_profile,
            intent=f"Layout '{moving_object}' relative to '{reference_object}' ({', '.join(intent_parts)})",
            placement_action="apply_relative_layout",
            placement_summary=f"Moved '{moving_object}' relative to '{reference_object}'",
        )

    def attach_part_to_surface(
        self,
        part_object: str,
        surface_object: str,
        surface_axis: str,
        surface_side: str = "positive",
        align_mode: str = "center",
        gap: float = 0.0,
        offset: Optional[List[float]] = None,
        max_mesh_nudge: float = 0.15,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        if part_object == surface_object:
            raise ValueError("part_object and surface_object must be different")

        resolved_surface_axis = self._normalize_contact_axis(surface_axis)
        resolved_surface_side = self._normalize_contact_side(surface_side)
        resolved_align_mode = self._normalize_layout_mode(align_mode, field_name="align_mode")
        gap_value = self._require_non_negative(gap, "gap")
        max_mesh_nudge_value = self._require_non_negative(max_mesh_nudge, "max_mesh_nudge")
        offset_vector = self._normalize_offset(offset)

        modes = {
            axis_name: ("none" if axis_name == resolved_surface_axis else resolved_align_mode)
            for axis_name in self._AXIS_INDEX
        }
        tangential_axes = [axis_name for axis_name in self._AXIS_INDEX if axis_name != resolved_surface_axis]
        base_report = self._execute_relative_layout_macro(
            macro_name="macro_attach_part_to_surface",
            moving_object=part_object,
            reference_object=surface_object,
            modes=modes,
            resolved_contact_axis=resolved_surface_axis,
            resolved_contact_side=resolved_surface_side,
            gap_value=gap_value,
            offset_vector=offset_vector,
            capture_profile=capture_profile,
            intent=(
                f"Attach '{part_object}' to the {resolved_surface_side} {resolved_surface_axis} surface of "
                f"'{surface_object}' with {resolved_align_mode} tangential alignment on {', '.join(tangential_axes)}"
            ),
            placement_action="attach_part_to_surface",
            placement_summary=f"Seated '{part_object}' onto '{surface_object}'",
        )
        after_truth = self._pair_truth_summary(part_object, surface_object)
        attachment_verdict = self._pair_attachment_verdict(after_truth)
        actions_taken = list(base_report.get("actions_taken") or [])
        actions_taken.append(
            {
                "status": "applied",
                "action": "inspect_pair_truth_after",
                "tool_name": "scene_measure_gap",
                "summary": f"Read pair truth after seating '{part_object}' onto '{surface_object}'",
                "details": after_truth,
            }
        )
        mesh_nudge_delta = self._mesh_surface_gap_nudge_delta(after_truth)
        if (
            gap_value == 0.0
            and attachment_verdict == "floating_gap"
            and mesh_nudge_delta is not None
            and max_mesh_nudge_value > 0.0
        ):
            nudge_distance = round(math.sqrt(sum(value * value for value in mesh_nudge_delta)), 6)
            if nudge_distance <= max_mesh_nudge_value:
                current_bbox = self._scene.get_bounding_box(part_object, world_space=True)
                current_center = [float(value) for value in current_bbox["center"]]
                target_center = [round(current_center[index] + mesh_nudge_delta[index], 6) for index in range(3)]
                self._modeling.transform_object(name=part_object, location=target_center)
                actions_taken.append(
                    {
                        "status": "applied",
                        "action": "mesh_surface_gap_nudge",
                        "tool_name": "modeling_transform_object",
                        "summary": (
                            "Applied a bounded mesh-surface nudge using nearest surface points after bbox seating."
                        ),
                        "details": {
                            "translation_delta": mesh_nudge_delta,
                            "nudge_distance": nudge_distance,
                            "max_mesh_nudge": max_mesh_nudge_value,
                            "target_center": target_center,
                        },
                    }
                )
                after_truth = self._pair_truth_summary(part_object, surface_object)
                attachment_verdict = self._pair_attachment_verdict(after_truth)
                actions_taken.append(
                    {
                        "status": "applied",
                        "action": "inspect_pair_truth_after_mesh_nudge",
                        "tool_name": "scene_measure_gap",
                        "summary": f"Read pair truth after mesh-surface nudge for '{part_object}' and '{surface_object}'",
                        "details": after_truth,
                    }
                )
            else:
                actions_taken.append(
                    {
                        "status": "skipped",
                        "action": "mesh_surface_gap_nudge",
                        "tool_name": "modeling_transform_object",
                        "summary": "Skipped mesh-surface nudge because it exceeded the bounded repair limit.",
                        "details": {
                            "translation_delta": mesh_nudge_delta,
                            "nudge_distance": nudge_distance,
                            "max_mesh_nudge": max_mesh_nudge_value,
                        },
                    }
                )
        capture_bundle = base_report.get("capture_bundle") if isinstance(base_report, dict) else None
        if isinstance(capture_bundle, dict):
            captures_before = [
                VisionCaptureImageContract.model_validate(item)
                for item in list(capture_bundle.get("captures_before") or [])
            ]
            refreshed_captures_after = self._maybe_capture_stage(
                bundle_id=str(
                    capture_bundle.get("bundle_id")
                    or self._make_capture_bundle_id("macro_attach_part_to_surface", part_object)
                ),
                stage="after",
                target_object=part_object,
                capture_profile=capture_profile,
            )
            if captures_before and refreshed_captures_after:
                refreshed_bundle = build_capture_bundle(
                    bundle_id=str(
                        capture_bundle.get("bundle_id")
                        or self._make_capture_bundle_id("macro_attach_part_to_surface", part_object)
                    ),
                    target_object=part_object,
                    captures_before=captures_before,
                    captures_after=refreshed_captures_after,
                    truth_summary=self._build_truth_summary(part_object),
                )
                base_report["capture_bundle"] = refreshed_bundle.model_dump(mode="json", exclude_none=True)
        actions_taken.append(
            {
                "status": "applied",
                "action": "evaluate_attachment_outcome",
                "tool_name": "scene_assert_contact",
                "summary": f"Attachment verdict after bounded seating: {attachment_verdict}",
                "details": {"attachment_verdict": attachment_verdict},
            }
        )
        base_report["actions_taken"] = actions_taken
        if gap_value == 0.0 and attachment_verdict != "seated_contact":
            base_report["status"] = "partial"
            base_report["error"] = (
                "The bounded seating move completed, but the pair is still not seated/attached correctly."
            )
        return base_report

    def _mesh_surface_gap_nudge_delta(self, truth_summary: Dict[str, Any]) -> list[float] | None:
        gap_payload = truth_summary.get("gap") if isinstance(truth_summary, dict) else None
        contact_assertion = truth_summary.get("contact_assertion") if isinstance(truth_summary, dict) else None
        if not isinstance(gap_payload, dict):
            return None
        if str(gap_payload.get("measurement_basis") or "") != "mesh_surface":
            return None
        if str(gap_payload.get("relation") or "").lower() != "separated":
            return None
        if isinstance(contact_assertion, dict):
            actual_value = contact_assertion.get("actual")
            actual = actual_value if isinstance(actual_value, dict) else {}
            if str(actual.get("relation") or "").lower() != "separated":
                return None
        nearest_points = gap_payload.get("nearest_points")
        if not isinstance(nearest_points, dict):
            return None
        from_point = nearest_points.get("from_object")
        to_point = nearest_points.get("to_object")
        if (
            not isinstance(from_point, list)
            or not isinstance(to_point, list)
            or len(from_point) != 3
            or len(to_point) != 3
        ):
            return None
        try:
            return [round(float(to_point[index]) - float(from_point[index]), 6) for index in range(3)]
        except (TypeError, ValueError):
            return None

    def align_part_with_contact(
        self,
        part_object: str,
        reference_object: str,
        target_relation: str = "contact",
        gap: float = 0.0,
        align_mode: str = "none",
        normal_axis: Optional[str] = None,
        preserve_side: bool = True,
        max_nudge: float = 0.5,
        offset: Optional[List[float]] = None,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        if part_object == reference_object:
            raise ValueError("part_object and reference_object must be different")

        relation_name = self._normalize_target_relation(target_relation)
        gap_value = self._require_non_negative(gap, "gap")
        if relation_name == "contact" and gap_value != 0.0:
            raise ValueError("gap must be 0 when target_relation='contact'")
        align_mode_name = self._normalize_layout_mode(align_mode, field_name="align_mode")
        offset_vector = self._normalize_offset(offset)
        max_nudge_value = self._require_positive(max_nudge, "max_nudge")

        reference_bbox = self._scene.get_bounding_box(reference_object, world_space=True)
        moving_bbox = self._scene.get_bounding_box(part_object, world_space=True)
        before_truth = self._pair_truth_summary(part_object, reference_object)
        before_overlap = before_truth.get("overlap") if isinstance(before_truth, dict) else None
        if (
            relation_name == "contact"
            and normal_axis is None
            and isinstance(before_overlap, dict)
            and bool(before_overlap.get("overlaps"))
        ):
            return self._blocked_repair_report(
                macro_name="macro_align_part_with_contact",
                intent=f"Repair '{part_object}' relative to '{reference_object}'",
                message=(
                    "The pair already overlaps/intersects. Inferring a contact axis here would push only "
                    f"'{part_object}' to one side of '{reference_object}' and can detach dependent parts. "
                    "Use an explicit normal_axis if you intentionally want a side contact repair, or use "
                    "macro_attach_part_to_surface / semantic seam validation for organic embedded seating."
                ),
                before_truth=before_truth,
            )

        resolved_normal_axis = self._normalize_contact_axis(normal_axis) if normal_axis is not None else None
        if resolved_normal_axis is None:
            resolved_normal_axis = self._infer_repair_axis(
                moving_bbox=moving_bbox,
                reference_bbox=reference_bbox,
                truth_summary=before_truth,
                gap_value=gap_value,
            )
        if resolved_normal_axis is None:
            return self._blocked_repair_report(
                macro_name="macro_align_part_with_contact",
                intent=f"Repair '{part_object}' relative to '{reference_object}'",
                message="Could not infer a stable repair axis from the current pair state.",
                before_truth=before_truth,
            )

        resolved_side = self._infer_side_from_centers(moving_bbox, reference_bbox, resolved_normal_axis)
        if resolved_side is None:
            if preserve_side:
                return self._blocked_repair_report(
                    macro_name="macro_align_part_with_contact",
                    intent=f"Repair '{part_object}' relative to '{reference_object}'",
                    message="Could not infer the current side to preserve; pass normal_axis only after the pair has a clear side relation.",
                    before_truth=before_truth,
                )
            resolved_side = self._choose_min_nudge_side(
                moving_bbox=moving_bbox,
                reference_bbox=reference_bbox,
                axis_name=resolved_normal_axis,
                gap_value=gap_value,
            )

        modes = {
            axis_name: ("none" if axis_name == resolved_normal_axis else align_mode_name)
            for axis_name in self._AXIS_INDEX
        }
        target_location, moving_center, _reference_center, _moving_half, _center_axes = self._compute_target_location(
            moving_bbox=moving_bbox,
            reference_bbox=reference_bbox,
            modes=modes,
            resolved_contact_axis=resolved_normal_axis,
            resolved_contact_side=resolved_side,
            gap_value=gap_value,
            offset_vector=offset_vector,
        )
        translation_delta = [round(target - current, 6) for target, current in zip(target_location, moving_center)]
        nudge_distance = round(
            math.sqrt(sum((target - current) ** 2 for target, current in zip(target_location, moving_center))), 6
        )

        if nudge_distance > max_nudge_value:
            return self._blocked_repair_report(
                macro_name="macro_align_part_with_contact",
                intent=f"Repair '{part_object}' relative to '{reference_object}'",
                message=(
                    f"Required repair nudge {nudge_distance:g} exceeds max_nudge {max_nudge_value:g}; "
                    "use a broader placement macro or raise the bound explicitly."
                ),
                before_truth=before_truth,
                repair_plan={
                    "target_relation": relation_name,
                    "normal_axis": resolved_normal_axis,
                    "preserved_side": resolved_side,
                    "align_mode": align_mode_name,
                    "translation_delta": translation_delta,
                    "nudge_distance": nudge_distance,
                    "max_nudge": max_nudge_value,
                },
            )

        base_report = self._execute_relative_layout_macro(
            macro_name="macro_align_part_with_contact",
            moving_object=part_object,
            reference_object=reference_object,
            modes=modes,
            resolved_contact_axis=resolved_normal_axis,
            resolved_contact_side=resolved_side,
            gap_value=gap_value,
            offset_vector=offset_vector,
            capture_profile=capture_profile,
            intent=(
                f"Repair '{part_object}' against '{reference_object}' toward {relation_name} "
                f"using inferred {resolved_side} {resolved_normal_axis} side"
            ),
            placement_action="align_part_with_contact",
            placement_summary=f"Nudged '{part_object}' toward a bounded {relation_name} repair against '{reference_object}'",
        )
        after_truth = self._pair_truth_summary(part_object, reference_object)
        actions_taken = list(base_report.get("actions_taken") or [])
        actions_taken.insert(
            0,
            {
                "status": "applied",
                "action": "inspect_pair_truth_before",
                "tool_name": "scene_measure_gap",
                "summary": f"Read pair truth before repairing '{part_object}' relative to '{reference_object}'",
                "details": before_truth,
            },
        )
        actions_taken.insert(
            1,
            {
                "status": "applied",
                "action": "infer_repair_plan",
                "tool_name": None,
                "summary": "Inferred bounded repair direction from the current pair state",
                "details": {
                    "target_relation": relation_name,
                    "normal_axis": resolved_normal_axis,
                    "preserved_side": resolved_side,
                    "align_mode": align_mode_name,
                    "translation_delta": translation_delta,
                    "nudge_distance": nudge_distance,
                    "max_nudge": max_nudge_value,
                    "preserve_side": preserve_side,
                },
            },
        )
        actions_taken.append(
            {
                "status": "applied",
                "action": "inspect_pair_truth_after",
                "tool_name": "scene_measure_gap",
                "summary": f"Read pair truth after repairing '{part_object}' relative to '{reference_object}'",
                "details": after_truth,
            }
        )
        attachment_verdict = self._pair_attachment_verdict(after_truth)
        actions_taken.append(
            {
                "status": "applied",
                "action": "evaluate_attachment_outcome",
                "tool_name": "scene_assert_contact",
                "summary": f"Attachment verdict after bounded repair: {attachment_verdict}",
                "details": {"attachment_verdict": attachment_verdict},
            }
        )
        verification_recommended = list(base_report.get("verification_recommended") or [])
        verification_recommended.append(
            {
                "tool_name": "scene_measure_overlap",
                "reason": "Confirm that the bounded repair did not introduce a new overlap issue.",
                "priority": "normal",
                "arguments_hint": {"from_object": part_object, "to_object": reference_object},
            }
        )
        base_report["actions_taken"] = actions_taken
        base_report["verification_recommended"] = verification_recommended
        if relation_name == "contact" and attachment_verdict != "seated_contact":
            base_report["status"] = "partial"
            base_report["error"] = "The bounded repair completed, but the pair is still not seated/attached correctly."
        return base_report

    def place_symmetry_pair(
        self,
        left_object: str,
        right_object: str,
        axis: str = "X",
        mirror_coordinate: float = 0.0,
        anchor_object: str = "auto",
        tolerance: float = 0.0001,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        if left_object == right_object:
            raise ValueError("left_object and right_object must be different")

        axis_name = self._normalize_contact_axis(axis)
        anchor_mode = self._normalize_symmetry_anchor(anchor_object)
        tolerance_value = self._require_non_negative(tolerance, "tolerance")
        bundle_id = self._make_capture_bundle_id("macro_place_symmetry_pair", left_object)
        captures_before = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="before",
            target_object=left_object,
            capture_profile=capture_profile,
        )

        left_bbox = self._scene.get_bounding_box(left_object, world_space=True)
        right_bbox = self._scene.get_bounding_box(right_object, world_space=True)
        before_symmetry = self._scene.assert_symmetry(
            left_object,
            right_object,
            axis=axis_name,
            mirror_coordinate=mirror_coordinate,
            tolerance=tolerance_value,
        )

        anchor_name, follower_name, anchor_bbox = self._resolve_symmetry_anchor(
            left_object=left_object,
            right_object=right_object,
            left_bbox=left_bbox,
            right_bbox=right_bbox,
            axis_name=axis_name,
            mirror_coordinate=mirror_coordinate,
            anchor_mode=anchor_mode,
        )
        follower_bbox = right_bbox if follower_name == right_object else left_bbox
        target_center = self._mirrored_center(
            anchor_center=[float(value) for value in anchor_bbox["center"]],
            axis_name=axis_name,
            mirror_coordinate=float(mirror_coordinate),
        )
        current_center = [float(value) for value in follower_bbox["center"]]
        translation_delta = [round(target - current, 6) for target, current in zip(target_center, current_center)]

        actions_taken: list[Dict[str, Any]] = [
            {
                "status": "applied",
                "action": "inspect_symmetry_before",
                "tool_name": "scene_assert_symmetry",
                "summary": f"Read symmetry state for '{left_object}' and '{right_object}' before placement repair",
                "details": before_symmetry,
            },
            {
                "status": "applied",
                "action": "select_symmetry_anchor",
                "tool_name": None,
                "summary": f"Using '{anchor_name}' as the symmetry anchor",
                "details": {
                    "anchor_mode": anchor_mode,
                    "anchor_object": anchor_name,
                    "follower_object": follower_name,
                    "axis": axis_name,
                    "mirror_coordinate": float(mirror_coordinate),
                },
            },
        ]

        self._modeling.transform_object(name=follower_name, location=target_center)
        actions_taken.append(
            {
                "status": "applied",
                "action": "place_symmetry_pair",
                "tool_name": "modeling_transform_object",
                "summary": f"Moved '{follower_name}' to the mirrored position of '{anchor_name}'",
                "details": {
                    "axis": axis_name,
                    "mirror_coordinate": float(mirror_coordinate),
                    "target_center": target_center,
                    "translation_delta": translation_delta,
                },
            }
        )

        after_symmetry = self._scene.assert_symmetry(
            left_object,
            right_object,
            axis=axis_name,
            mirror_coordinate=mirror_coordinate,
            tolerance=tolerance_value,
        )
        actions_taken.append(
            {
                "status": "applied",
                "action": "inspect_symmetry_after",
                "tool_name": "scene_assert_symmetry",
                "summary": f"Read symmetry state for '{left_object}' and '{right_object}' after placement repair",
                "details": after_symmetry,
            }
        )

        report = {
            "status": "success",
            "macro_name": "macro_place_symmetry_pair",
            "intent": (
                f"Place/correct mirrored pair '{left_object}' and '{right_object}' across "
                f"{axis_name}={float(mirror_coordinate):g} using '{anchor_name}' as anchor"
            ),
            "actions_taken": actions_taken,
            "objects_created": None,
            "objects_modified": [follower_name],
            "verification_recommended": [
                {
                    "tool_name": "scene_assert_symmetry",
                    "reason": "Confirm the pair is mirrored around the requested axis and mirror coordinate.",
                    "priority": "high",
                    "arguments_hint": {
                        "left_object": left_object,
                        "right_object": right_object,
                        "axis": axis_name,
                        "mirror_coordinate": float(mirror_coordinate),
                        "tolerance": tolerance_value,
                    },
                },
                {
                    "tool_name": "inspect_scene",
                    "reason": "Verify the mirrored pair visually after the bounded symmetry placement.",
                    "priority": "normal",
                    "arguments_hint": {"action": "object", "target_object": follower_name},
                },
                {
                    "tool_name": "scene_get_viewport",
                    "reason": "Do a quick visual check of the mirrored pair before continuing the build.",
                    "priority": "normal",
                    "arguments_hint": {"focus_target": follower_name, "shading": "SOLID"},
                },
            ],
            "requires_followup": True,
        }
        captures_after = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="after",
            target_object=follower_name,
            capture_profile=capture_profile,
        )
        return self._finalize_report(
            report,
            bundle_id=bundle_id,
            target_object=follower_name,
            captures_before=captures_before,
            captures_after=captures_after,
        )

    def place_supported_pair(
        self,
        left_object: str,
        right_object: str,
        support_object: str,
        axis: str = "X",
        mirror_coordinate: float = 0.0,
        support_axis: str = "Z",
        support_side: str = "positive",
        anchor_object: str = "auto",
        gap: float = 0.0,
        tolerance: float = 0.0001,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        if left_object == right_object:
            raise ValueError("left_object and right_object must be different")
        if support_object in {left_object, right_object}:
            raise ValueError("support_object must be different from left_object and right_object")

        axis_name = self._normalize_contact_axis(axis)
        support_axis_name = self._normalize_contact_axis(support_axis)
        if axis_name == support_axis_name:
            raise ValueError("axis and support_axis must be different for a supported pair")

        support_side_name = self._normalize_contact_side(support_side)
        anchor_mode = self._normalize_symmetry_anchor(anchor_object)
        gap_value = self._require_non_negative(gap, "gap")
        tolerance_value = self._require_non_negative(tolerance, "tolerance")
        bundle_id = self._make_capture_bundle_id("macro_place_supported_pair", left_object)
        captures_before = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="before",
            target_object=left_object,
            capture_profile=capture_profile,
        )

        left_bbox = self._scene.get_bounding_box(left_object, world_space=True)
        right_bbox = self._scene.get_bounding_box(right_object, world_space=True)
        support_bbox = self._scene.get_bounding_box(support_object, world_space=True)
        before_symmetry = self._scene.assert_symmetry(
            left_object,
            right_object,
            axis=axis_name,
            mirror_coordinate=mirror_coordinate,
            tolerance=tolerance_value,
        )
        before_support = {
            left_object: self._support_truth_summary(left_object, support_object),
            right_object: self._support_truth_summary(right_object, support_object),
        }

        anchor_name, follower_name, anchor_bbox = self._resolve_symmetry_anchor(
            left_object=left_object,
            right_object=right_object,
            left_bbox=left_bbox,
            right_bbox=right_bbox,
            axis_name=axis_name,
            mirror_coordinate=mirror_coordinate,
            anchor_mode=anchor_mode,
        )
        follower_bbox = right_bbox if follower_name == right_object else left_bbox
        anchor_support_coordinate = self._support_target_coordinate(
            moving_bbox=anchor_bbox,
            reference_bbox=support_bbox,
            axis_name=support_axis_name,
            side_name=support_side_name,
            gap_value=gap_value,
        )
        follower_support_coordinate = self._support_target_coordinate(
            moving_bbox=follower_bbox,
            reference_bbox=support_bbox,
            axis_name=support_axis_name,
            side_name=support_side_name,
            gap_value=gap_value,
        )
        support_coordinate_delta = round(abs(anchor_support_coordinate - follower_support_coordinate), 6)

        intent = (
            f"Place/correct supported pair '{left_object}' and '{right_object}' on '{support_object}' "
            f"around {axis_name}={float(mirror_coordinate):g}"
        )

        if support_coordinate_delta > tolerance_value:
            return {
                "status": "blocked",
                "macro_name": "macro_place_supported_pair",
                "intent": intent,
                "actions_taken": [
                    {
                        "status": "applied",
                        "action": "inspect_symmetry_before",
                        "tool_name": "scene_assert_symmetry",
                        "summary": f"Read symmetry state for '{left_object}' and '{right_object}' before support placement",
                        "details": before_symmetry,
                    },
                    {
                        "status": "applied",
                        "action": "inspect_support_contacts_before",
                        "tool_name": "scene_assert_contact",
                        "summary": f"Read support contact state for '{left_object}' and '{right_object}' against '{support_object}'",
                        "details": {
                            "support_object": support_object,
                            "support_axis": support_axis_name,
                            "support_side": support_side_name,
                            "support_checks": before_support,
                        },
                    },
                    {
                        "status": "skipped",
                        "action": "plan_supported_pair_blocked",
                        "tool_name": None,
                        "summary": "Mirror placement and support contact would require materially different support coordinates.",
                        "details": {
                            "anchor_object": anchor_name,
                            "follower_object": follower_name,
                            "support_axis": support_axis_name,
                            "anchor_support_coordinate": anchor_support_coordinate,
                            "follower_support_coordinate": follower_support_coordinate,
                            "support_coordinate_delta": support_coordinate_delta,
                            "tolerance": tolerance_value,
                        },
                    },
                ],
                "objects_created": None,
                "objects_modified": None,
                "verification_recommended": [
                    {
                        "tool_name": "scene_assert_symmetry",
                        "reason": "Re-check the pair symmetry before trying a broader rebuild step.",
                        "priority": "high",
                        "arguments_hint": {
                            "left_object": left_object,
                            "right_object": right_object,
                            "axis": axis_name,
                            "mirror_coordinate": float(mirror_coordinate),
                            "tolerance": tolerance_value,
                        },
                    },
                    {
                        "tool_name": "scene_assert_contact",
                        "reason": "Verify one object's current support contact before relaxing the bound.",
                        "priority": "high",
                        "arguments_hint": {
                            "from_object": anchor_name,
                            "to_object": support_object,
                            "max_gap": 0.001,
                            "allow_overlap": False,
                        },
                    },
                ],
                "requires_followup": True,
                "error": (
                    f"Support placement would require different {support_axis_name} coordinates "
                    f"({anchor_support_coordinate:g} vs {follower_support_coordinate:g}), which exceeds tolerance "
                    f"{tolerance_value:g} and would break the bounded mirrored pair."
                ),
            }

        anchor_target_center = [float(value) for value in anchor_bbox["center"]]
        anchor_target_center[self._AXIS_INDEX[support_axis_name]] = anchor_support_coordinate
        follower_target_center = self._mirrored_center(
            anchor_center=anchor_target_center,
            axis_name=axis_name,
            mirror_coordinate=float(mirror_coordinate),
        )
        follower_target_center[self._AXIS_INDEX[support_axis_name]] = follower_support_coordinate

        anchor_translation_delta = [
            round(target - current, 6)
            for target, current in zip(anchor_target_center, [float(value) for value in anchor_bbox["center"]])
        ]
        follower_translation_delta = [
            round(target - current, 6)
            for target, current in zip(follower_target_center, [float(value) for value in follower_bbox["center"]])
        ]

        actions_taken: list[Dict[str, Any]] = [
            {
                "status": "applied",
                "action": "inspect_symmetry_before",
                "tool_name": "scene_assert_symmetry",
                "summary": f"Read symmetry state for '{left_object}' and '{right_object}' before support placement",
                "details": before_symmetry,
            },
            {
                "status": "applied",
                "action": "inspect_support_contacts_before",
                "tool_name": "scene_assert_contact",
                "summary": f"Read support contact state for '{left_object}' and '{right_object}' against '{support_object}'",
                "details": {
                    "support_object": support_object,
                    "support_axis": support_axis_name,
                    "support_side": support_side_name,
                    "support_checks": before_support,
                },
            },
            {
                "status": "applied",
                "action": "plan_supported_pair",
                "tool_name": None,
                "summary": f"Planned a bounded mirrored pair placement against '{support_object}'",
                "details": {
                    "axis": axis_name,
                    "mirror_coordinate": float(mirror_coordinate),
                    "support_axis": support_axis_name,
                    "support_side": support_side_name,
                    "anchor_object": anchor_name,
                    "follower_object": follower_name,
                    "gap": gap_value,
                    "anchor_target_center": anchor_target_center,
                    "follower_target_center": follower_target_center,
                    "support_coordinate_delta": support_coordinate_delta,
                },
            },
        ]

        self._modeling.transform_object(name=anchor_name, location=anchor_target_center)
        actions_taken.append(
            {
                "status": "applied",
                "action": "place_supported_pair_anchor",
                "tool_name": "modeling_transform_object",
                "summary": f"Moved '{anchor_name}' onto the requested support surface",
                "details": {
                    "support_object": support_object,
                    "support_axis": support_axis_name,
                    "support_side": support_side_name,
                    "target_center": anchor_target_center,
                    "translation_delta": anchor_translation_delta,
                },
            }
        )

        self._modeling.transform_object(name=follower_name, location=follower_target_center)
        actions_taken.append(
            {
                "status": "applied",
                "action": "place_supported_pair_follower",
                "tool_name": "modeling_transform_object",
                "summary": f"Moved '{follower_name}' into mirrored support placement relative to '{anchor_name}'",
                "details": {
                    "axis": axis_name,
                    "mirror_coordinate": float(mirror_coordinate),
                    "support_object": support_object,
                    "support_axis": support_axis_name,
                    "support_side": support_side_name,
                    "target_center": follower_target_center,
                    "translation_delta": follower_translation_delta,
                },
            }
        )

        after_symmetry = self._scene.assert_symmetry(
            left_object,
            right_object,
            axis=axis_name,
            mirror_coordinate=mirror_coordinate,
            tolerance=tolerance_value,
        )
        after_support = {
            left_object: self._support_truth_summary(left_object, support_object),
            right_object: self._support_truth_summary(right_object, support_object),
        }
        actions_taken.append(
            {
                "status": "applied",
                "action": "inspect_symmetry_after",
                "tool_name": "scene_assert_symmetry",
                "summary": f"Read symmetry state for '{left_object}' and '{right_object}' after support placement",
                "details": after_symmetry,
            }
        )
        actions_taken.append(
            {
                "status": "applied",
                "action": "inspect_support_contacts_after",
                "tool_name": "scene_assert_contact",
                "summary": f"Read support contact state for '{left_object}' and '{right_object}' against '{support_object}' after placement",
                "details": {"support_object": support_object, "support_checks": after_support},
            }
        )

        report = {
            "status": "success",
            "macro_name": "macro_place_supported_pair",
            "intent": intent,
            "actions_taken": actions_taken,
            "objects_created": None,
            "objects_modified": [anchor_name, follower_name],
            "verification_recommended": [
                {
                    "tool_name": "scene_assert_symmetry",
                    "reason": "Confirm the pair still satisfies the requested mirrored placement after support alignment.",
                    "priority": "high",
                    "arguments_hint": {
                        "left_object": left_object,
                        "right_object": right_object,
                        "axis": axis_name,
                        "mirror_coordinate": float(mirror_coordinate),
                        "tolerance": tolerance_value,
                    },
                },
                {
                    "tool_name": "scene_assert_contact",
                    "reason": "Confirm the left object is actually supported instead of visually floating.",
                    "priority": "high",
                    "arguments_hint": {
                        "from_object": left_object,
                        "to_object": support_object,
                        "max_gap": 0.001,
                        "allow_overlap": False,
                    },
                },
                {
                    "tool_name": "scene_assert_contact",
                    "reason": "Confirm the right object is actually supported instead of visually floating.",
                    "priority": "high",
                    "arguments_hint": {
                        "from_object": right_object,
                        "to_object": support_object,
                        "max_gap": 0.001,
                        "allow_overlap": False,
                    },
                },
                {
                    "tool_name": "scene_get_viewport",
                    "reason": "Do a quick visual check of the supported pair before continuing the build.",
                    "priority": "normal",
                    "arguments_hint": {"focus_target": follower_name, "shading": "SOLID"},
                },
            ],
            "requires_followup": True,
        }
        captures_after = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="after",
            target_object=follower_name,
            capture_profile=capture_profile,
        )
        return self._finalize_report(
            report,
            bundle_id=bundle_id,
            target_object=follower_name,
            captures_before=captures_before,
            captures_after=captures_after,
        )

    def cleanup_part_intersections(
        self,
        part_object: str,
        reference_object: str,
        gap: float = 0.0,
        normal_axis: Optional[str] = None,
        preserve_side: bool = True,
        max_push: float = 0.5,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        if part_object == reference_object:
            raise ValueError("part_object and reference_object must be different")

        gap_value = self._require_non_negative(gap, "gap")
        max_push_value = self._require_positive(max_push, "max_push")
        reference_bbox = self._scene.get_bounding_box(reference_object, world_space=True)
        moving_bbox = self._scene.get_bounding_box(part_object, world_space=True)
        before_truth = self._pair_truth_summary(part_object, reference_object)
        before_overlap = before_truth.get("overlap") if isinstance(before_truth, dict) else None
        before_gap = before_truth.get("gap") if isinstance(before_truth, dict) else None
        overlap_relation = str((before_overlap or {}).get("relation") or "").lower()

        if overlap_relation != "overlap" or not bool((before_overlap or {}).get("overlaps")):
            noop_report = {
                "status": "success",
                "macro_name": "macro_cleanup_part_intersections",
                "intent": f"Clean intersection between '{part_object}' and '{reference_object}'",
                "actions_taken": [
                    {
                        "status": "applied",
                        "action": "inspect_overlap_before",
                        "tool_name": "scene_measure_overlap",
                        "summary": "Current pair is already non-overlapping; no bounded cleanup push was needed.",
                        "details": {
                            "overlap": before_overlap,
                            "gap": before_gap,
                        },
                    }
                ],
                "objects_created": None,
                "objects_modified": None,
                "verification_recommended": [
                    {
                        "tool_name": "scene_measure_overlap",
                        "reason": "Reconfirm overlap state if later edits reintroduce intersection risk.",
                        "priority": "normal",
                        "arguments_hint": {"from_object": part_object, "to_object": reference_object},
                    }
                ],
                "requires_followup": False,
            }
            return noop_report

        axis_candidates = (
            [self._normalize_contact_axis(normal_axis)]
            if normal_axis is not None
            else self._ordered_overlap_axes(before_overlap)
        )
        resolved_normal_axis = next(
            (
                axis_name
                for axis_name in axis_candidates
                if axis_name is not None
                and (
                    not preserve_side
                    or self._infer_side_from_centers(moving_bbox, reference_bbox, axis_name) is not None
                )
            ),
            None,
        )
        if resolved_normal_axis is None and axis_candidates:
            resolved_normal_axis = axis_candidates[0]
        if resolved_normal_axis is None:
            return {
                "status": "blocked",
                "macro_name": "macro_cleanup_part_intersections",
                "intent": f"Clean intersection between '{part_object}' and '{reference_object}'",
                "actions_taken": [
                    {
                        "status": "applied",
                        "action": "inspect_overlap_before",
                        "tool_name": "scene_measure_overlap",
                        "summary": "Read overlap truth before bounded cleanup planning.",
                        "details": before_truth,
                    }
                ],
                "objects_created": None,
                "objects_modified": None,
                "verification_recommended": [
                    {
                        "tool_name": "scene_measure_overlap",
                        "reason": "Re-check the overlap state before attempting a broader cleanup step.",
                        "priority": "high",
                        "arguments_hint": {"from_object": part_object, "to_object": reference_object},
                    }
                ],
                "requires_followup": True,
                "error": "Could not infer a stable cleanup axis from the current overlap state.",
            }

        resolved_side = self._infer_side_from_centers(moving_bbox, reference_bbox, resolved_normal_axis)
        if resolved_side is None:
            if preserve_side:
                return {
                    "status": "blocked",
                    "macro_name": "macro_cleanup_part_intersections",
                    "intent": f"Clean intersection between '{part_object}' and '{reference_object}'",
                    "actions_taken": [
                        {
                            "status": "applied",
                            "action": "inspect_overlap_before",
                            "tool_name": "scene_measure_overlap",
                            "summary": "Read overlap truth before bounded cleanup planning.",
                            "details": before_truth,
                        }
                    ],
                    "objects_created": None,
                    "objects_modified": None,
                    "verification_recommended": [
                        {
                            "tool_name": "scene_measure_overlap",
                            "reason": "Re-check the overlap state before attempting a broader cleanup step.",
                            "priority": "high",
                            "arguments_hint": {"from_object": part_object, "to_object": reference_object},
                        }
                    ],
                    "requires_followup": True,
                    "error": (
                        "Could not infer the current side to preserve for overlap cleanup; "
                        "pass normal_axis only after the pair has a clear side relation or disable preserve_side."
                    ),
                }
            resolved_side = self._choose_min_nudge_side(
                moving_bbox=moving_bbox,
                reference_bbox=reference_bbox,
                axis_name=resolved_normal_axis,
                gap_value=gap_value,
            )

        target_location, moving_center, _reference_center, _moving_half, _center_axes = self._compute_target_location(
            moving_bbox=moving_bbox,
            reference_bbox=reference_bbox,
            modes={axis_name: "none" for axis_name in self._AXIS_INDEX},
            resolved_contact_axis=resolved_normal_axis,
            resolved_contact_side=resolved_side,
            gap_value=gap_value,
            offset_vector=[0.0, 0.0, 0.0],
        )
        translation_delta = [round(target - current, 6) for target, current in zip(target_location, moving_center)]
        push_distance = round(
            math.sqrt(sum((target - current) ** 2 for target, current in zip(target_location, moving_center))),
            6,
        )

        if push_distance > max_push_value:
            return {
                "status": "blocked",
                "macro_name": "macro_cleanup_part_intersections",
                "intent": f"Clean intersection between '{part_object}' and '{reference_object}'",
                "actions_taken": [
                    {
                        "status": "applied",
                        "action": "inspect_overlap_before",
                        "tool_name": "scene_measure_overlap",
                        "summary": "Read overlap truth before bounded cleanup planning.",
                        "details": before_truth,
                    },
                    {
                        "status": "skipped",
                        "action": "cleanup_plan_blocked",
                        "tool_name": None,
                        "summary": (
                            f"Required cleanup push {push_distance:g} exceeds max_push {max_push_value:g}; "
                            "use a broader rebuild step or raise the bound explicitly."
                        ),
                        "details": {
                            "normal_axis": resolved_normal_axis,
                            "preserved_side": resolved_side,
                            "translation_delta": translation_delta,
                            "push_distance": push_distance,
                            "max_push": max_push_value,
                            "gap": gap_value,
                        },
                    },
                ],
                "objects_created": None,
                "objects_modified": None,
                "verification_recommended": [
                    {
                        "tool_name": "scene_measure_overlap",
                        "reason": "Re-check the overlap state before attempting a broader cleanup step.",
                        "priority": "high",
                        "arguments_hint": {"from_object": part_object, "to_object": reference_object},
                    }
                ],
                "requires_followup": True,
                "error": (
                    f"Required cleanup push {push_distance:g} exceeds max_push {max_push_value:g}; "
                    "use a broader rebuild step or raise the bound explicitly."
                ),
            }

        bundle_id = self._make_capture_bundle_id("macro_cleanup_part_intersections", part_object)
        captures_before = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="before",
            target_object=part_object,
            capture_profile=capture_profile,
        )

        actions_taken: list[Dict[str, Any]] = [
            {
                "status": "applied",
                "action": "inspect_overlap_before",
                "tool_name": "scene_measure_overlap",
                "summary": f"Read overlap truth for '{part_object}' relative to '{reference_object}' before cleanup.",
                "details": before_truth,
            },
            {
                "status": "applied",
                "action": "plan_intersection_cleanup",
                "tool_name": None,
                "summary": "Planned a bounded push to clear the current overlap.",
                "details": {
                    "normal_axis": resolved_normal_axis,
                    "preserved_side": resolved_side,
                    "translation_delta": translation_delta,
                    "push_distance": push_distance,
                    "max_push": max_push_value,
                    "gap": gap_value,
                    "preserve_side": preserve_side,
                },
            },
        ]

        self._modeling.transform_object(name=part_object, location=target_location)
        actions_taken.append(
            {
                "status": "applied",
                "action": "cleanup_part_intersections",
                "tool_name": "modeling_transform_object",
                "summary": f"Moved '{part_object}' to clear the overlap against '{reference_object}'",
                "details": {
                    "target_location": target_location,
                    "translation_delta": translation_delta,
                    "normal_axis": resolved_normal_axis,
                    "preserved_side": resolved_side,
                    "gap": gap_value,
                },
            }
        )

        after_truth = self._pair_truth_summary(part_object, reference_object)
        actions_taken.append(
            {
                "status": "applied",
                "action": "inspect_overlap_after",
                "tool_name": "scene_measure_overlap",
                "summary": f"Read overlap truth for '{part_object}' relative to '{reference_object}' after cleanup.",
                "details": after_truth,
            }
        )
        attachment_verdict = self._pair_attachment_verdict(after_truth)
        actions_taken.append(
            {
                "status": "applied",
                "action": "evaluate_attachment_outcome",
                "tool_name": "scene_assert_contact",
                "summary": f"Attachment verdict after bounded cleanup: {attachment_verdict}",
                "details": {"attachment_verdict": attachment_verdict},
            }
        )

        cleanup_report: Dict[str, Any] = {
            "status": "success",
            "macro_name": "macro_cleanup_part_intersections",
            "intent": f"Clean intersection between '{part_object}' and '{reference_object}'",
            "actions_taken": actions_taken,
            "objects_created": None,
            "objects_modified": [part_object],
            "verification_recommended": [
                {
                    "tool_name": "scene_measure_overlap",
                    "reason": "Confirm the overlap volume is gone after the bounded cleanup push.",
                    "priority": "high",
                    "arguments_hint": {"from_object": part_object, "to_object": reference_object},
                },
                (
                    {
                        "tool_name": "scene_assert_contact",
                        "reason": "Confirm the pair now resolves to contact without overlap.",
                        "priority": "high",
                        "arguments_hint": {
                            "from_object": part_object,
                            "to_object": reference_object,
                            "max_gap": 0.001,
                            "allow_overlap": False,
                        },
                    }
                    if gap_value == 0.0
                    else {
                        "tool_name": "scene_measure_gap",
                        "reason": "Confirm the requested post-cleanup clearance after the bounded push.",
                        "priority": "high",
                        "arguments_hint": {"from_object": part_object, "to_object": reference_object},
                    }
                ),
                {
                    "tool_name": "scene_get_viewport",
                    "reason": "Do a quick visual check of the cleaned pair before continuing the build.",
                    "priority": "normal",
                    "arguments_hint": {"focus_target": part_object, "shading": "SOLID"},
                },
            ],
            "requires_followup": True,
        }
        if gap_value == 0.0 and attachment_verdict != "seated_contact":
            cleanup_report["status"] = "partial"
            cleanup_report["error"] = (
                "The bounded cleanup removed or reduced overlap, but the pair is still not seated/attached correctly."
            )
        captures_after = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="after",
            target_object=part_object,
            capture_profile=capture_profile,
        )
        return self._finalize_report(
            cleanup_report,
            bundle_id=bundle_id,
            target_object=part_object,
            captures_before=captures_before,
            captures_after=captures_after,
        )

    def adjust_relative_proportion(
        self,
        primary_object: str,
        reference_object: str,
        expected_ratio: float,
        primary_axis: str = "X",
        reference_axis: str = "X",
        scale_target: str = "primary",
        tolerance: float = 0.01,
        uniform_scale: bool = True,
        max_scale_delta: float = 0.5,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        if primary_object == reference_object:
            raise ValueError("primary_object and reference_object must be different")

        expected_ratio_value = self._require_positive(expected_ratio, "expected_ratio")
        primary_axis_name = self._normalize_contact_axis(primary_axis)
        reference_axis_name = self._normalize_contact_axis(reference_axis)
        scale_target_name = self._normalize_scale_target(scale_target)
        tolerance_value = self._require_non_negative(tolerance, "tolerance")
        max_scale_delta_value = self._require_positive(max_scale_delta, "max_scale_delta")
        bundle_id = self._make_capture_bundle_id("macro_adjust_relative_proportion", primary_object)
        captures_before = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="before",
            target_object=primary_object,
            capture_profile=capture_profile,
        )

        before_proportion = self._scene.assert_proportion(
            primary_object,
            axis_a=primary_axis_name,
            expected_ratio=expected_ratio_value,
            reference_object=reference_object,
            reference_axis=reference_axis_name,
            tolerance=tolerance_value,
            world_space=True,
        )
        current_ratio = float(before_proportion["actual"]["ratio"])
        if current_ratio <= 0.0:
            return self._blocked_repair_report(
                macro_name="macro_adjust_relative_proportion",
                intent=f"Repair relative proportion for '{primary_object}' relative to '{reference_object}'",
                message="Current cross-object ratio is zero or invalid; cannot compute a bounded scale repair.",
                before_truth={"proportion": before_proportion},
            )

        if abs(current_ratio - expected_ratio_value) <= tolerance_value:
            noop_report = {
                "status": "success",
                "macro_name": "macro_adjust_relative_proportion",
                "intent": (
                    f"Repair relative proportion for '{primary_object}' relative to '{reference_object}' "
                    f"toward ratio {expected_ratio_value:g}"
                ),
                "actions_taken": [
                    {
                        "status": "applied",
                        "action": "inspect_proportion_before",
                        "tool_name": "scene_assert_proportion",
                        "summary": "Current proportion is already within tolerance; no scale repair was needed.",
                        "details": before_proportion,
                    }
                ],
                "objects_created": None,
                "objects_modified": None,
                "verification_recommended": [
                    {
                        "tool_name": "scene_assert_proportion",
                        "reason": "Reconfirm the ratio if later edits change the relationship.",
                        "priority": "normal",
                        "arguments_hint": {
                            "object_name": primary_object,
                            "axis_a": primary_axis_name,
                            "expected_ratio": expected_ratio_value,
                            "reference_object": reference_object,
                            "reference_axis": reference_axis_name,
                            "tolerance": tolerance_value,
                            "world_space": True,
                        },
                    }
                ],
                "requires_followup": False,
            }
            return noop_report

        current_scale = self._object_scale(primary_object if scale_target_name == "primary" else reference_object)
        scale_factor = (
            expected_ratio_value / current_ratio
            if scale_target_name == "primary"
            else current_ratio / expected_ratio_value
        )
        scale_delta = abs(scale_factor - 1.0)
        if scale_delta > max_scale_delta_value:
            return self._blocked_repair_report(
                macro_name="macro_adjust_relative_proportion",
                intent=f"Repair relative proportion for '{primary_object}' relative to '{reference_object}'",
                message=(
                    f"Required scale delta {scale_delta:g} exceeds max_scale_delta {max_scale_delta_value:g}; "
                    "choose a broader rebuild step or raise the bound explicitly."
                ),
                before_truth={"proportion": before_proportion},
                repair_plan={
                    "scale_target": scale_target_name,
                    "current_ratio": current_ratio,
                    "expected_ratio": expected_ratio_value,
                    "scale_factor": scale_factor,
                    "max_scale_delta": max_scale_delta_value,
                },
            )

        scale_object = primary_object if scale_target_name == "primary" else reference_object
        new_scale = (
            [round(component * scale_factor, 6) for component in current_scale]
            if uniform_scale
            else self._scaled_axis_only(
                current_scale=current_scale,
                axis_name=primary_axis_name if scale_target_name == "primary" else reference_axis_name,
                scale_factor=scale_factor,
            )
        )
        self._modeling.transform_object(name=scale_object, scale=new_scale)
        after_proportion = self._scene.assert_proportion(
            primary_object,
            axis_a=primary_axis_name,
            expected_ratio=expected_ratio_value,
            reference_object=reference_object,
            reference_axis=reference_axis_name,
            tolerance=tolerance_value,
            world_space=True,
        )

        repair_report: Dict[str, Any] = {
            "status": "success",
            "macro_name": "macro_adjust_relative_proportion",
            "intent": (
                f"Repair relative proportion for '{primary_object}' relative to '{reference_object}' "
                f"toward ratio {expected_ratio_value:g}"
            ),
            "actions_taken": [
                {
                    "status": "applied",
                    "action": "inspect_proportion_before",
                    "tool_name": "scene_assert_proportion",
                    "summary": "Read the current ratio before the scale repair.",
                    "details": before_proportion,
                },
                {
                    "status": "applied",
                    "action": "adjust_relative_proportion",
                    "tool_name": "modeling_transform_object",
                    "summary": f"Scaled '{scale_object}' to repair the target cross-object ratio.",
                    "details": {
                        "scale_target": scale_target_name,
                        "current_ratio": current_ratio,
                        "expected_ratio": expected_ratio_value,
                        "scale_factor": round(scale_factor, 6),
                        "uniform_scale": uniform_scale,
                        "new_scale": new_scale,
                    },
                },
                {
                    "status": "applied",
                    "action": "inspect_proportion_after",
                    "tool_name": "scene_assert_proportion",
                    "summary": "Read the ratio after the scale repair.",
                    "details": after_proportion,
                },
            ],
            "objects_created": None,
            "objects_modified": [scale_object],
            "verification_recommended": [
                {
                    "tool_name": "scene_assert_proportion",
                    "reason": "Confirm the repaired relative ratio against the requested target.",
                    "priority": "high",
                    "arguments_hint": {
                        "object_name": primary_object,
                        "axis_a": primary_axis_name,
                        "expected_ratio": expected_ratio_value,
                        "reference_object": reference_object,
                        "reference_axis": reference_axis_name,
                        "tolerance": tolerance_value,
                        "world_space": True,
                    },
                },
                {
                    "tool_name": "scene_measure_dimensions",
                    "reason": "Inspect the updated object dimensions after the bounded scale repair.",
                    "priority": "normal",
                    "arguments_hint": {"object_name": scale_object, "world_space": True},
                },
                {
                    "tool_name": "scene_get_viewport",
                    "reason": "Do a quick visual check of the repaired relative proportion before continuing the build.",
                    "priority": "normal",
                    "arguments_hint": {"focus_target": primary_object, "shading": "SOLID"},
                },
            ],
            "requires_followup": True,
        }
        captures_after = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="after",
            target_object=primary_object,
            capture_profile=capture_profile,
        )
        return self._finalize_report(
            repair_report,
            bundle_id=bundle_id,
            target_object=primary_object,
            captures_before=captures_before,
            captures_after=captures_after,
        )

    def adjust_segment_chain_arc(
        self,
        segment_objects: List[str],
        rotation_axis: str = "Y",
        total_angle: float = 30.0,
        direction: str = "positive",
        segment_spacing: Optional[float] = None,
        apply_rotation: bool = True,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_segments = [str(name).strip() for name in segment_objects if str(name).strip()]
        if len(normalized_segments) < 2:
            raise ValueError("segment_objects must contain at least 2 object names")

        rotation_axis_name = self._normalize_contact_axis(rotation_axis)
        direction_name = self._normalize_contact_side(direction)
        total_angle_value = self._require_non_negative(total_angle, "total_angle")
        spacing_override = (
            None if segment_spacing is None else self._require_non_negative(segment_spacing, "segment_spacing")
        )
        bundle_id = self._make_capture_bundle_id("macro_adjust_segment_chain_arc", normalized_segments[0])
        captures_before = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="before",
            target_object=normalized_segments[0],
            capture_profile=capture_profile,
        )

        bbox_map = {name: self._scene.get_bounding_box(name, world_space=True) for name in normalized_segments}
        inspect_map = {name: self._scene.inspect_object(name) for name in normalized_segments}
        centers = {name: [float(value) for value in bbox_map[name]["center"]] for name in normalized_segments}
        rotations = {
            name: [float(value) for value in inspect_map[name].get("rotation") or [0.0, 0.0, 0.0]]
            for name in normalized_segments
        }
        base_name = normalized_segments[0]
        base_center = centers[base_name]
        direction_vector = self._initial_arc_direction(
            start_center=base_center,
            next_center=centers[normalized_segments[1]],
            rotation_axis=rotation_axis_name,
        )
        spacing_values = self._tail_spacing_values(
            segment_names=normalized_segments,
            centers=centers,
            fallback_spacing=spacing_override,
        )

        actions_taken: list[Dict[str, Any]] = [
            {
                "status": "applied",
                "action": "inspect_segment_chain",
                "tool_name": "scene_get_bounding_box",
                "summary": f"Read the current segment-chain state for {len(normalized_segments)} segment(s)",
                "details": {
                    "segment_objects": normalized_segments,
                    "rotation_axis": rotation_axis_name,
                    "direction": direction_name,
                    "total_angle": total_angle_value,
                    "segment_spacing": spacing_values,
                },
            }
        ]

        previous_center = list(base_center)
        total_angle_radians = math.radians(total_angle_value)
        sign = 1.0 if direction_name == "positive" else -1.0
        modified_objects: list[str] = []
        angle_steps: list[Dict[str, Any]] = []

        for index, object_name in enumerate(normalized_segments[1:], start=1):
            spacing = spacing_values[index - 1]
            cumulative_angle = sign * total_angle_radians * (index / (len(normalized_segments) - 1))
            rotated_direction = self._rotate_vector_about_axis(
                direction_vector,
                rotation_axis=rotation_axis_name,
                angle_radians=cumulative_angle,
            )
            target_center = [round(previous_center[idx] + rotated_direction[idx] * spacing, 6) for idx in range(3)]
            updated_rotation = None
            if apply_rotation:
                updated_rotation = list(rotations[object_name])
                updated_rotation[self._AXIS_INDEX[rotation_axis_name]] = round(
                    updated_rotation[self._AXIS_INDEX[rotation_axis_name]] + cumulative_angle,
                    6,
                )

            self._modeling.transform_object(name=object_name, location=target_center, rotation=updated_rotation)
            modified_objects.append(object_name)
            angle_steps.append(
                {
                    "object_name": object_name,
                    "cumulative_angle_degrees": round(math.degrees(cumulative_angle), 6),
                    "target_center": target_center,
                    "rotation_applied": updated_rotation,
                }
            )
            previous_center = target_center

        actions_taken.append(
            {
                "status": "applied",
                "action": "adjust_segment_chain_arc",
                "tool_name": "modeling_transform_object",
                "summary": f"Repositioned {len(modified_objects)} segment(s) along a bounded planar arc",
                "details": {"steps": angle_steps},
            }
        )

        report = {
            "status": "success",
            "macro_name": "macro_adjust_segment_chain_arc",
            "intent": (
                f"Adjust segment chain arc for {len(normalized_segments)} segment(s) around {rotation_axis_name} "
                f"with total_angle={total_angle_value:g} and direction={direction_name}"
            ),
            "actions_taken": actions_taken,
            "objects_created": None,
            "objects_modified": modified_objects,
            "verification_recommended": [
                {
                    "tool_name": "inspect_scene",
                    "reason": "Verify the updated segment-chain object states after the bounded arc adjustment.",
                    "priority": "normal",
                    "arguments_hint": {"action": "object", "target_object": normalized_segments[-1]},
                },
                {
                    "tool_name": "scene_get_viewport",
                    "reason": "Do a quick visual check of the adjusted segment chain before continuing the build.",
                    "priority": "normal",
                    "arguments_hint": {"focus_target": normalized_segments[-1], "shading": "SOLID"},
                },
            ],
            "requires_followup": True,
        }
        captures_after = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="after",
            target_object=normalized_segments[-1],
            capture_profile=capture_profile,
        )
        return self._finalize_report(
            report,
            bundle_id=bundle_id,
            target_object=normalized_segments[-1],
            captures_before=captures_before,
            captures_after=captures_after,
        )

    def _execute_relative_layout_macro(
        self,
        *,
        macro_name: str,
        moving_object: str,
        reference_object: str,
        modes: dict[str, str],
        resolved_contact_axis: Optional[str],
        resolved_contact_side: str,
        gap_value: float,
        offset_vector: list[float],
        capture_profile: Optional[str],
        intent: str,
        placement_action: str,
        placement_summary: str,
    ) -> Dict[str, Any]:
        bundle_id = self._make_capture_bundle_id(macro_name, moving_object)
        captures_before = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="before",
            target_object=moving_object,
            capture_profile=capture_profile,
        )

        reference_bbox = self._scene.get_bounding_box(reference_object, world_space=True)
        moving_bbox = self._scene.get_bounding_box(moving_object, world_space=True)
        target_location, moving_center, reference_center, _moving_half, center_axes = self._compute_target_location(
            moving_bbox=moving_bbox,
            reference_bbox=reference_bbox,
            modes=modes,
            resolved_contact_axis=resolved_contact_axis,
            resolved_contact_side=resolved_contact_side,
            gap_value=gap_value,
            offset_vector=offset_vector,
        )
        translation_delta = [round(target - current, 6) for target, current in zip(target_location, moving_center)]

        actions_taken: list[Dict[str, Any]] = [
            {
                "status": "applied",
                "action": "inspect_reference_bounds",
                "tool_name": "scene_get_bounding_box",
                "summary": f"Read world-space bounds for '{reference_object}'",
                "details": {
                    "object_name": reference_object,
                    "center": reference_center,
                    "dimensions": reference_bbox["dimensions"],
                },
            },
            {
                "status": "applied",
                "action": "inspect_moving_bounds",
                "tool_name": "scene_get_bounding_box",
                "summary": f"Read world-space bounds for '{moving_object}'",
                "details": {
                    "object_name": moving_object,
                    "center": moving_center,
                    "dimensions": moving_bbox["dimensions"],
                },
            },
        ]

        self._modeling.transform_object(name=moving_object, location=target_location)
        actions_taken.append(
            {
                "status": "applied",
                "action": placement_action,
                "tool_name": "modeling_transform_object",
                "summary": placement_summary,
                "details": {
                    "target_location": target_location,
                    "translation_delta": translation_delta,
                    "alignment_modes": {axis.lower(): mode for axis, mode in modes.items()},
                    "contact_axis": resolved_contact_axis,
                    "contact_side": resolved_contact_side if resolved_contact_axis is not None else None,
                    "gap": gap_value,
                    "offset": offset_vector,
                },
            }
        )

        verification_recommended: list[Dict[str, Any]] = [
            {
                "tool_name": "inspect_scene",
                "reason": "Verify the moved part after the bounded layout transform.",
                "priority": "normal",
                "arguments_hint": {"action": "object", "target_object": moving_object},
            },
            {
                "tool_name": "scene_get_bounding_box",
                "reason": "Confirm the moved object's final world-space bounds and footprint.",
                "priority": "normal",
                "arguments_hint": {"object_name": moving_object, "world_space": True},
            },
        ]

        if center_axes:
            verification_recommended.append(
                {
                    "tool_name": "scene_measure_alignment",
                    "reason": "Confirm center alignment on the requested axes.",
                    "priority": "normal",
                    "arguments_hint": {
                        "from_object": moving_object,
                        "to_object": reference_object,
                        "axes": center_axes,
                        "reference": "CENTER",
                    },
                }
            )

        if resolved_contact_axis is not None:
            verification_recommended.append(
                {
                    "tool_name": "scene_measure_gap",
                    "reason": "Confirm the expected gap/contact relation after the layout move.",
                    "priority": "high",
                    "arguments_hint": {
                        "from_object": moving_object,
                        "to_object": reference_object,
                    },
                }
            )
            if gap_value == 0.0:
                verification_recommended.append(
                    {
                        "tool_name": "scene_assert_contact",
                        "reason": "Assert that the layout contact is real instead of visually assumed.",
                        "priority": "high",
                        "arguments_hint": {
                            "from_object": moving_object,
                            "to_object": reference_object,
                            "max_gap": 0.001,
                            "allow_overlap": False,
                        },
                    }
                )

        verification_recommended.append(
            {
                "tool_name": "scene_get_viewport",
                "reason": "Do a quick visual check of the relative placement before continuing the build.",
                "priority": "normal",
                "arguments_hint": {"focus_target": moving_object, "shading": "SOLID"},
            }
        )

        report = {
            "status": "success",
            "macro_name": macro_name,
            "intent": intent,
            "actions_taken": actions_taken,
            "objects_created": None,
            "objects_modified": [moving_object],
            "verification_recommended": verification_recommended,
            "requires_followup": True,
        }
        captures_after = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="after",
            target_object=moving_object,
            capture_profile=capture_profile,
        )
        return self._finalize_report(
            report,
            bundle_id=bundle_id,
            target_object=moving_object,
            captures_before=captures_before,
            captures_after=captures_after,
        )

    def _compute_target_location(
        self,
        *,
        moving_bbox: Dict[str, Any],
        reference_bbox: Dict[str, Any],
        modes: dict[str, str],
        resolved_contact_axis: Optional[str],
        resolved_contact_side: str,
        gap_value: float,
        offset_vector: list[float],
    ) -> tuple[list[float], list[float], list[float], list[float], list[str]]:
        moving_center = [float(value) for value in moving_bbox["center"]]
        reference_center = [float(value) for value in reference_bbox["center"]]
        moving_half = [float(value) / 2.0 for value in moving_bbox["dimensions"]]

        target_location = list(moving_center)
        center_axes: list[str] = []

        for axis_name, mode in modes.items():
            if mode == "none":
                continue
            axis_index = self._AXIS_INDEX[axis_name]
            if mode == "center":
                target_location[axis_index] = reference_center[axis_index]
                center_axes.append(axis_name)
            elif mode == "min":
                target_location[axis_index] = float(reference_bbox["min"][axis_index]) + moving_half[axis_index]
            else:
                target_location[axis_index] = float(reference_bbox["max"][axis_index]) - moving_half[axis_index]

        if resolved_contact_axis is not None:
            axis_index = self._AXIS_INDEX[resolved_contact_axis]
            if resolved_contact_side == "positive":
                target_location[axis_index] = (
                    float(reference_bbox["max"][axis_index]) + gap_value + moving_half[axis_index]
                )
            else:
                target_location[axis_index] = (
                    float(reference_bbox["min"][axis_index]) - gap_value - moving_half[axis_index]
                )

        target_location = [target + delta for target, delta in zip(target_location, offset_vector)]
        return target_location, moving_center, reference_center, moving_half, center_axes

    def finish_form(
        self,
        target_object: str,
        preset: str = "rounded_housing",
        bevel_width: Optional[float] = None,
        bevel_segments: Optional[int] = None,
        subsurf_levels: Optional[int] = None,
        thickness: Optional[float] = None,
        solidify_offset: float = 0.0,
        capture_profile: Optional[str] = None,
    ) -> Dict[str, Any]:
        preset_name = self._normalize_finish_preset(preset)
        solidify_offset_value = float(solidify_offset)

        resolved = self._resolve_finish_preset_parameters(
            preset_name=preset_name,
            bevel_width=bevel_width,
            bevel_segments=bevel_segments,
            subsurf_levels=subsurf_levels,
            thickness=thickness,
            solidify_offset=solidify_offset_value,
        )
        bundle_id = self._make_capture_bundle_id("macro_finish_form", target_object)
        captures_before = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="before",
            target_object=target_object,
            capture_profile=capture_profile,
        )

        actions_taken: list[Dict[str, Any]] = []
        added_stack: list[Dict[str, Any]] = []

        if resolved["bevel_width"] is not None:
            bevel_width_value = float(resolved["bevel_width"])
            bevel_segments_value = cast(int, resolved["bevel_segments"])
            before_names = self._modifier_names(target_object)
            self._modeling.add_modifier(
                target_object,
                "BEVEL",
                properties={
                    "width": bevel_width_value,
                    "segments": bevel_segments_value,
                    "limit_method": "ANGLE",
                },
            )
            bevel_modifier_name = self._resolve_new_modifier_name(
                target_object=target_object,
                before_names=before_names,
                modifier_type="BEVEL",
            )
            actions_taken.append(
                {
                    "status": "applied",
                    "action": "add_bevel_finish",
                    "tool_name": "modeling_add_modifier",
                    "summary": f"Added bevel modifier '{bevel_modifier_name}'",
                    "details": {
                        "modifier_name": bevel_modifier_name,
                        "modifier_type": "BEVEL",
                        "width": bevel_width_value,
                        "segments": bevel_segments_value,
                        "limit_method": "ANGLE",
                    },
                }
            )
            added_stack.append({"name": bevel_modifier_name, "type": "BEVEL"})

        if resolved["thickness"] is not None:
            thickness_value = float(resolved["thickness"])
            before_names = self._modifier_names(target_object)
            self._modeling.add_modifier(
                target_object,
                "SOLIDIFY",
                properties={
                    "thickness": thickness_value,
                    "offset": solidify_offset_value,
                },
            )
            solidify_modifier_name = self._resolve_new_modifier_name(
                target_object=target_object,
                before_names=before_names,
                modifier_type="SOLIDIFY",
            )
            actions_taken.append(
                {
                    "status": "applied",
                    "action": "add_shell_thickness",
                    "tool_name": "modeling_add_modifier",
                    "summary": f"Added solidify modifier '{solidify_modifier_name}'",
                    "details": {
                        "modifier_name": solidify_modifier_name,
                        "modifier_type": "SOLIDIFY",
                        "thickness": thickness_value,
                        "offset": solidify_offset_value,
                    },
                }
            )
            added_stack.append({"name": solidify_modifier_name, "type": "SOLIDIFY"})

        if resolved["subsurf_levels"] is not None:
            subsurf_levels_value = int(resolved["subsurf_levels"])
            before_names = self._modifier_names(target_object)
            self._modeling.add_modifier(
                target_object,
                "SUBSURF",
                properties={
                    "levels": subsurf_levels_value,
                    "render_levels": subsurf_levels_value,
                },
            )
            subsurf_modifier_name = self._resolve_new_modifier_name(
                target_object=target_object,
                before_names=before_names,
                modifier_type="SUBSURF",
            )
            actions_taken.append(
                {
                    "status": "applied",
                    "action": "add_subdivision_finish",
                    "tool_name": "modeling_add_modifier",
                    "summary": f"Added subdivision modifier '{subsurf_modifier_name}'",
                    "details": {
                        "modifier_name": subsurf_modifier_name,
                        "modifier_type": "SUBSURF",
                        "levels": subsurf_levels_value,
                        "render_levels": subsurf_levels_value,
                    },
                }
            )
            added_stack.append({"name": subsurf_modifier_name, "type": "SUBSURF"})

        actions_taken.append(
            {
                "status": "applied",
                "action": "compose_finish_stack",
                "tool_name": None,
                "summary": f"Prepared preset '{preset_name}' on '{target_object}'",
                "details": {
                    "preset": preset_name,
                    "modifier_stack": added_stack,
                },
            }
        )

        verification_recommended: list[Dict[str, Any]] = [
            {
                "tool_name": "inspect_scene",
                "reason": "Verify the modifier stack after applying the finishing preset.",
                "priority": "normal",
                "arguments_hint": {"action": "modifiers", "target_object": target_object},
            },
            {
                "tool_name": "scene_get_viewport",
                "reason": "Do a quick visual check of the silhouette and edge finish.",
                "priority": "normal",
                "arguments_hint": {"focus_target": target_object, "shading": "SOLID"},
            },
        ]

        if resolved["thickness"] is not None:
            verification_recommended.append(
                {
                    "tool_name": "scene_measure_dimensions",
                    "reason": "Confirm the outer dimensions after shell thickening.",
                    "priority": "normal",
                    "arguments_hint": {"object_name": target_object, "world_space": True},
                }
            )

        report = {
            "status": "success",
            "macro_name": "macro_finish_form",
            "intent": f"Apply '{preset_name}' finishing preset to '{target_object}'",
            "actions_taken": actions_taken,
            "objects_created": None,
            "objects_modified": [target_object],
            "verification_recommended": verification_recommended,
            "requires_followup": True,
        }
        captures_after = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="after",
            target_object=target_object,
            capture_profile=capture_profile,
        )
        return self._finalize_report(
            report,
            bundle_id=bundle_id,
            target_object=target_object,
            captures_before=captures_before,
            captures_after=captures_after,
        )

    def _make_capture_bundle_id(self, macro_name: str, target_object: str) -> str:
        return f"{macro_name}_{target_object}_{uuid4().hex[:8]}"

    def _maybe_capture_stage(
        self,
        *,
        bundle_id: str,
        stage: str,
        target_object: str,
        capture_profile: str | None,
    ):
        if not get_config().VISION_ENABLED:
            return None
        if not hasattr(self._scene, "get_viewport"):
            return None
        try:
            captures = capture_stage_images(
                self._scene,
                bundle_id=bundle_id,
                stage=cast(CaptureStage, stage),
                target_object=target_object,
                preset_profile=cast(CapturePresetProfile, capture_profile or "compact"),
            )
        except Exception:
            return None
        return captures or None

    def _build_truth_summary(self, target_object: str) -> Dict[str, Any] | None:
        summary: dict[str, Any] = {}
        try:
            summary["dimensions"] = self._scene.measure_dimensions(target_object, world_space=True)
        except Exception:
            pass
        try:
            summary["bounding_box"] = self._scene.get_bounding_box(target_object, world_space=True)
        except Exception:
            pass
        return summary or None

    def _finalize_report(
        self,
        report_data: Dict[str, Any],
        *,
        bundle_id: str,
        target_object: str,
        captures_before,
        captures_after,
    ) -> Dict[str, Any]:
        report = MacroExecutionReportContract.model_validate(report_data)
        if not captures_before or not captures_after:
            return report.model_dump(exclude_none=True)

        capture_bundle = build_capture_bundle(
            bundle_id=bundle_id,
            target_object=target_object,
            captures_before=captures_before,
            captures_after=captures_after,
            truth_summary=self._build_truth_summary(target_object),
        )
        enriched = attach_vision_artifacts(report, capture_bundle=capture_bundle)
        return enriched.model_dump(exclude_none=True)

    def _normalize_face(self, face: str) -> str:
        value = str(face).lower()
        if value not in self._FACE_SPECS:
            raise ValueError("face must be one of front, back, left, right, top, bottom")
        return value

    def _normalize_finish_preset(self, preset: str) -> str:
        normalized = str(preset).lower()
        if normalized not in self._FINISH_PRESETS:
            raise ValueError("preset must be one of rounded_housing, panel_finish, shell_thicken, smooth_subdivision")
        return normalized

    def _normalize_layout_mode(self, value: str, field_name: str) -> str:
        normalized = str(value).lower()
        if normalized not in {"none", "center", "min", "max"}:
            raise ValueError(f"{field_name} must be one of none, center, min, max")
        return normalized

    @overload
    def _normalize_contact_axis(self, axis: None) -> None: ...

    @overload
    def _normalize_contact_axis(self, axis: str) -> AxisName: ...

    def _normalize_contact_axis(self, axis: Optional[str]) -> Optional[AxisName]:
        if axis is None:
            return None
        normalized = str(axis).upper()
        if normalized not in self._AXIS_INDEX:
            raise ValueError("contact_axis must be one of X, Y, Z")
        return cast(AxisName, normalized)

    def _normalize_contact_side(self, side: str) -> ContactSideName:
        normalized = str(side).lower()
        if normalized not in {"positive", "negative"}:
            raise ValueError("contact_side must be one of positive or negative")
        return cast(ContactSideName, normalized)

    def _normalize_target_relation(self, relation: str) -> str:
        normalized = str(relation).lower()
        if normalized not in {"contact", "gap"}:
            raise ValueError("target_relation must be one of contact or gap")
        return normalized

    def _normalize_symmetry_anchor(self, anchor_object: str) -> SymmetryAnchorName:
        normalized = str(anchor_object).lower()
        if normalized not in {"auto", "left", "right"}:
            raise ValueError("anchor_object must be one of auto, left, or right")
        return cast(SymmetryAnchorName, normalized)

    def _initial_arc_direction(
        self,
        *,
        start_center: list[float],
        next_center: list[float],
        rotation_axis: str,
    ) -> list[float]:
        vector = [next_center[idx] - start_center[idx] for idx in range(3)]
        axis_index = self._AXIS_INDEX[rotation_axis]
        vector[axis_index] = 0.0
        length = math.sqrt(sum(component * component for component in vector))
        if length <= 1e-9:
            defaults = {
                "X": [0.0, 1.0, 0.0],
                "Y": [1.0, 0.0, 0.0],
                "Z": [1.0, 0.0, 0.0],
            }
            return defaults[rotation_axis]
        return [component / length for component in vector]

    def _tail_spacing_values(
        self,
        *,
        segment_names: list[str],
        centers: dict[str, list[float]],
        fallback_spacing: float | None,
    ) -> list[float]:
        if fallback_spacing is not None:
            return [fallback_spacing for _ in segment_names[1:]]

        values: list[float] = []
        for current_name, next_name in zip(segment_names, segment_names[1:]):
            current_center = centers[current_name]
            next_center = centers[next_name]
            distance = math.sqrt(sum((next_center[idx] - current_center[idx]) ** 2 for idx in range(3)))
            values.append(round(distance, 6))
        return values

    def _rotate_vector_about_axis(
        self,
        vector: list[float],
        *,
        rotation_axis: str,
        angle_radians: float,
    ) -> list[float]:
        x, y, z = vector
        cosine = math.cos(angle_radians)
        sine = math.sin(angle_radians)
        if rotation_axis == "X":
            return [x, y * cosine - z * sine, y * sine + z * cosine]
        if rotation_axis == "Y":
            return [x * cosine + z * sine, y, -x * sine + z * cosine]
        return [x * cosine - y * sine, x * sine + y * cosine, z]

    def _normalize_scale_target(self, scale_target: str) -> ScaleTargetName:
        normalized = str(scale_target).lower()
        if normalized not in {"primary", "reference"}:
            raise ValueError("scale_target must be one of primary or reference")
        return cast(ScaleTargetName, normalized)

    def _pair_truth_summary(self, part_object: str, reference_object: str) -> Dict[str, Any]:
        gap = self._scene.measure_gap(part_object, reference_object)
        contact_assertion = self._scene.assert_contact(
            part_object, reference_object, max_gap=0.001, allow_overlap=False
        )
        summary: Dict[str, Any] = {
            "gap": gap,
            "alignment": self._scene.measure_alignment(part_object, reference_object, ["X", "Y", "Z"], "CENTER"),
            "overlap": self._scene.measure_overlap(part_object, reference_object),
            "contact_assertion": contact_assertion,
        }
        contact_semantics = self._contact_semantics_note(gap=gap, contact_assertion=contact_assertion)
        if contact_semantics is not None:
            summary["contact_semantics"] = contact_semantics
        return summary

    def _pair_attachment_verdict(self, truth_summary: Dict[str, Any]) -> str:
        overlap = truth_summary.get("overlap") if isinstance(truth_summary, dict) else None
        if isinstance(overlap, dict) and bool(overlap.get("overlaps")):
            return "intersecting"

        contact_assertion = truth_summary.get("contact_assertion") if isinstance(truth_summary, dict) else None
        if isinstance(contact_assertion, dict) and contact_assertion.get("passed") is True:
            return "seated_contact"
        if isinstance(contact_assertion, dict):
            actual_value = contact_assertion.get("actual")
            actual = actual_value if isinstance(actual_value, dict) else {}
            actual_relation = str(actual.get("relation") or "").lower()
            if actual_relation == "separated":
                return "floating_gap"
            if actual_relation == "overlapping":
                return "intersecting"

        gap = truth_summary.get("gap") if isinstance(truth_summary, dict) else None
        if isinstance(gap, dict) and str(gap.get("relation") or "").lower() == "separated":
            return "floating_gap"

        return "needs_followup"

    def _support_truth_summary(self, part_object: str, support_object: str) -> Dict[str, Any]:
        gap = self._scene.measure_gap(part_object, support_object)
        contact_assertion = self._scene.assert_contact(part_object, support_object, max_gap=0.001, allow_overlap=False)
        summary: Dict[str, Any] = {
            "gap": gap,
            "contact_assertion": contact_assertion,
        }
        contact_semantics = self._contact_semantics_note(gap=gap, contact_assertion=contact_assertion)
        if contact_semantics is not None:
            summary["contact_semantics"] = contact_semantics
        return summary

    def _contact_semantics_note(
        self,
        *,
        gap: Dict[str, Any] | None,
        contact_assertion: Dict[str, Any] | None,
    ) -> str | None:
        if not isinstance(contact_assertion, dict):
            return None

        details_value = contact_assertion.get("details")
        details: Dict[str, Any] = details_value if isinstance(details_value, dict) else {}
        actual_value = contact_assertion.get("actual")
        actual: Dict[str, Any] = actual_value if isinstance(actual_value, dict) else {}
        measurement_basis = str(details.get("measurement_basis") or (gap or {}).get("measurement_basis") or "")
        bbox_relation = str(details.get("bbox_relation") or (gap or {}).get("bbox_relation") or "")
        measured_relation = str(actual.get("relation") or (gap or {}).get("relation") or "")

        if (
            measurement_basis == "mesh_surface"
            and bbox_relation in {"contact", "touching"}
            and measured_relation == "separated"
        ):
            return "Bounding boxes touch, but the measured mesh surfaces still have a real gap."
        return None

    def _infer_side_from_centers(
        self,
        moving_bbox: Dict[str, Any],
        reference_bbox: Dict[str, Any],
        axis_name: str,
        *,
        epsilon: float = 1e-6,
    ) -> Optional[ContactSideName]:
        axis_index = self._AXIS_INDEX[axis_name]
        moving_center = float(moving_bbox["center"][axis_index])
        reference_center = float(reference_bbox["center"][axis_index])
        delta = moving_center - reference_center
        if delta > epsilon:
            return "positive"
        if delta < -epsilon:
            return "negative"
        return None

    def _resolve_symmetry_anchor(
        self,
        *,
        left_object: str,
        right_object: str,
        left_bbox: Dict[str, Any],
        right_bbox: Dict[str, Any],
        axis_name: str,
        mirror_coordinate: float,
        anchor_mode: str,
    ) -> tuple[str, str, Dict[str, Any]]:
        if anchor_mode == "left":
            return left_object, right_object, left_bbox
        if anchor_mode == "right":
            return right_object, left_object, right_bbox

        axis_index = self._AXIS_INDEX[axis_name]
        left_delta = abs(float(left_bbox["center"][axis_index]) - mirror_coordinate)
        right_delta = abs(float(right_bbox["center"][axis_index]) - mirror_coordinate)
        if left_delta >= right_delta:
            return left_object, right_object, left_bbox
        return right_object, left_object, right_bbox

    def _mirrored_center(
        self,
        *,
        anchor_center: list[float],
        axis_name: str,
        mirror_coordinate: float,
    ) -> list[float]:
        mirrored = list(anchor_center)
        axis_index = self._AXIS_INDEX[axis_name]
        mirrored[axis_index] = round((2.0 * mirror_coordinate) - anchor_center[axis_index], 6)
        return mirrored

    def _support_target_coordinate(
        self,
        *,
        moving_bbox: Dict[str, Any],
        reference_bbox: Dict[str, Any],
        axis_name: str,
        side_name: str,
        gap_value: float,
    ) -> float:
        target_location, *_ = self._compute_target_location(
            moving_bbox=moving_bbox,
            reference_bbox=reference_bbox,
            modes={axis: "none" for axis in self._AXIS_INDEX},
            resolved_contact_axis=axis_name,
            resolved_contact_side=side_name,
            gap_value=gap_value,
            offset_vector=[0.0, 0.0, 0.0],
        )
        return float(target_location[self._AXIS_INDEX[axis_name]])

    def _ordered_overlap_axes(self, overlap_summary: Dict[str, Any] | None) -> list[AxisName]:
        overlap_dimensions = overlap_summary.get("overlap_dimensions") if isinstance(overlap_summary, dict) else None
        if not isinstance(overlap_dimensions, list) or len(overlap_dimensions) != 3:
            return []

        ordered = sorted(
            (
                (cast(AxisName, axis_name), abs(float(overlap_dimensions[axis_index] or 0.0)))
                for axis_name, axis_index in self._AXIS_INDEX.items()
                if abs(float(overlap_dimensions[axis_index] or 0.0)) > 1e-6
            ),
            key=lambda item: item[1],
        )
        return [axis_name for axis_name, _ in ordered]

    def _choose_min_nudge_side(
        self,
        *,
        moving_bbox: Dict[str, Any],
        reference_bbox: Dict[str, Any],
        axis_name: str,
        gap_value: float,
    ) -> ContactSideName:
        axis_index = self._AXIS_INDEX[axis_name]
        moving_center = float(moving_bbox["center"][axis_index])
        moving_half = float(moving_bbox["dimensions"][axis_index]) / 2.0
        positive_target = float(reference_bbox["max"][axis_index]) + gap_value + moving_half
        negative_target = float(reference_bbox["min"][axis_index]) - gap_value - moving_half
        return (
            "positive" if abs(positive_target - moving_center) <= abs(negative_target - moving_center) else "negative"
        )

    def _infer_repair_axis(
        self,
        *,
        moving_bbox: Dict[str, Any],
        reference_bbox: Dict[str, Any],
        truth_summary: Dict[str, Any],
        gap_value: float,
    ) -> Optional[AxisName]:
        gap_payload = truth_summary.get("gap") if isinstance(truth_summary, dict) else None
        axis_gap = gap_payload.get("axis_gap") if isinstance(gap_payload, dict) else None
        if isinstance(axis_gap, dict):
            ordered = sorted(
                ((axis_name, abs(float(axis_gap.get(axis_name.lower()) or 0.0))) for axis_name in self._AXIS_INDEX),
                key=lambda item: item[1],
                reverse=True,
            )
            if ordered and ordered[0][1] > 1e-6:
                return cast(AxisName, ordered[0][0])

        best_axis: Optional[AxisName] = None
        best_delta: float | None = None
        for axis_name, axis_index in self._AXIS_INDEX.items():
            inferred_side = self._infer_side_from_centers(moving_bbox, reference_bbox, axis_name)
            if inferred_side is None:
                continue
            moving_center = float(moving_bbox["center"][axis_index])
            moving_half = float(moving_bbox["dimensions"][axis_index]) / 2.0
            if inferred_side == "positive":
                target = float(reference_bbox["max"][axis_index]) + gap_value + moving_half
            else:
                target = float(reference_bbox["min"][axis_index]) - gap_value - moving_half
            delta = abs(target - moving_center)
            if best_delta is None or delta < best_delta:
                best_axis = cast(AxisName, axis_name)
                best_delta = delta
        return best_axis

    def _blocked_repair_report(
        self,
        *,
        macro_name: str,
        intent: str,
        message: str,
        before_truth: Dict[str, Any],
        repair_plan: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        actions_taken: list[Dict[str, Any]] = [
            {
                "status": "applied",
                "action": "inspect_pair_truth_before",
                "tool_name": "scene_measure_gap",
                "summary": "Read pair truth before bounded repair planning",
                "details": before_truth,
            }
        ]
        if repair_plan is not None:
            actions_taken.append(
                {
                    "status": "skipped",
                    "action": "repair_plan_blocked",
                    "tool_name": None,
                    "summary": message,
                    "details": repair_plan,
                }
            )
        return {
            "status": "blocked",
            "macro_name": macro_name,
            "intent": intent,
            "actions_taken": actions_taken,
            "objects_created": None,
            "objects_modified": None,
            "verification_recommended": [
                {
                    "tool_name": "scene_measure_gap",
                    "reason": "Re-check the pair state before attempting a broader placement or a larger repair bound.",
                    "priority": "high",
                    "arguments_hint": None,
                }
            ],
            "requires_followup": True,
            "error": message,
        }

    def _object_scale(self, object_name: str) -> list[float]:
        object_snapshot = self._scene.inspect_object(object_name)
        scale = list(object_snapshot.get("scale") or [1.0, 1.0, 1.0])
        if len(scale) != 3:
            raise ValueError(f"Object '{object_name}' did not return a valid scale vector")
        return [float(value) for value in scale]

    def _scaled_axis_only(
        self,
        *,
        current_scale: list[float],
        axis_name: str,
        scale_factor: float,
    ) -> list[float]:
        updated = list(current_scale)
        updated[self._AXIS_INDEX[axis_name]] = round(updated[self._AXIS_INDEX[axis_name]] * scale_factor, 6)
        return [round(value, 6) for value in updated]

    def _resolve_finish_preset_parameters(
        self,
        *,
        preset_name: str,
        bevel_width: Optional[float],
        bevel_segments: Optional[int],
        subsurf_levels: Optional[int],
        thickness: Optional[float],
        solidify_offset: float,
    ) -> Dict[str, float | int | None]:
        if preset_name == "rounded_housing":
            if thickness is not None:
                raise ValueError("thickness override is only valid for preset 'shell_thicken'")
            if solidify_offset != 0.0:
                raise ValueError("solidify_offset is only valid for preset 'shell_thicken'")
        elif preset_name == "panel_finish":
            if thickness is not None:
                raise ValueError("thickness override is only valid for preset 'shell_thicken'")
            if subsurf_levels is not None:
                raise ValueError("subsurf_levels override is not valid for preset 'panel_finish'")
            if solidify_offset != 0.0:
                raise ValueError("solidify_offset is only valid for preset 'shell_thicken'")
        elif preset_name == "shell_thicken":
            if bevel_width is not None or bevel_segments is not None:
                raise ValueError("bevel overrides are not valid for preset 'shell_thicken'")
            if subsurf_levels is not None:
                raise ValueError("subsurf_levels override is not valid for preset 'shell_thicken'")
        elif preset_name == "smooth_subdivision":
            if bevel_width is not None or bevel_segments is not None:
                raise ValueError("bevel overrides are not valid for preset 'smooth_subdivision'")
            if thickness is not None:
                raise ValueError("thickness override is only valid for preset 'shell_thicken'")
            if solidify_offset != 0.0:
                raise ValueError("solidify_offset is only valid for preset 'shell_thicken'")

        defaults = self._FINISH_PRESETS[preset_name]

        resolved_bevel_width = defaults["bevel_width"]
        resolved_bevel_segments = defaults["bevel_segments"]
        resolved_subsurf_levels = defaults["subsurf_levels"]
        resolved_thickness = defaults["thickness"]

        if bevel_width is not None:
            resolved_bevel_width = self._require_positive(bevel_width, "bevel_width")
        if bevel_segments is not None:
            resolved_bevel_segments = self._require_int_at_least(bevel_segments, "bevel_segments", 1)
        if subsurf_levels is not None:
            resolved_subsurf_levels = self._require_int_at_least(subsurf_levels, "subsurf_levels", 1)
        if thickness is not None:
            resolved_thickness = self._require_positive(thickness, "thickness")

        return {
            "bevel_width": resolved_bevel_width,
            "bevel_segments": resolved_bevel_segments,
            "subsurf_levels": resolved_subsurf_levels,
            "thickness": resolved_thickness,
        }

    def _normalize_mode(self, mode: str) -> str:
        value = str(mode).lower()
        if value not in {"recess", "cut_through"}:
            raise ValueError("mode must be either 'recess' or 'cut_through'")
        return value

    def _normalize_cleanup(self, cleanup: str) -> str:
        value = str(cleanup).lower()
        if value not in {"delete", "hide", "keep"}:
            raise ValueError("cleanup must be one of delete, hide, keep")
        return value

    def _normalize_offset(self, offset: Optional[List[float]]) -> List[float]:
        if offset is None:
            return [0.0, 0.0, 0.0]
        if len(offset) != 3:
            raise ValueError("offset must contain exactly 3 values")
        return [float(value) for value in offset]

    def _require_positive(self, value: float, field_name: str) -> float:
        numeric = float(value)
        if numeric <= 0:
            raise ValueError(f"{field_name} must be > 0")
        return numeric

    def _require_optional_positive(self, value: Optional[float], field_name: str) -> Optional[float]:
        if value is None:
            return None
        return self._require_positive(value, field_name)

    def _require_non_negative(self, value: float, field_name: str) -> float:
        numeric = float(value)
        if numeric < 0:
            raise ValueError(f"{field_name} must be >= 0")
        return numeric

    def _require_int_at_least(self, value: int, field_name: str, minimum: int) -> int:
        integer = int(value)
        if integer < minimum:
            raise ValueError(f"{field_name} must be >= {minimum}")
        return integer

    def _require_segments(self, value: int) -> int:
        integer = int(value)
        if integer < 1:
            raise ValueError("bevel_segments must be >= 1")
        return integer

    def _compute_cutter_dimensions(
        self,
        *,
        bbox: Dict[str, Any],
        face: str,
        width: float,
        height: float,
        depth: float,
        mode: str,
    ) -> List[float]:
        normal_axis, plane_axis_a, plane_axis_b = self._FACE_SPECS[face]
        dimensions = [0.0, 0.0, 0.0]
        dimensions[plane_axis_a] = width
        dimensions[plane_axis_b] = height

        target_depth = float(bbox["dimensions"][normal_axis])
        if mode == "recess":
            if depth >= target_depth:
                raise ValueError("recess depth must be smaller than the target thickness on the chosen face axis")
            dimensions[normal_axis] = depth
        else:
            dimensions[normal_axis] = target_depth + 0.002

        return dimensions

    def _compute_cutter_location(
        self,
        *,
        bbox: Dict[str, Any],
        face: str,
        depth: float,
        mode: str,
        offset: List[float],
    ) -> List[float]:
        normal_axis, _, _ = self._FACE_SPECS[face]
        center = [float(value) for value in bbox["center"]]

        if mode == "recess":
            min_corner = [float(value) for value in bbox["min"]]
            max_corner = [float(value) for value in bbox["max"]]
            if face in {"front", "left", "bottom"}:
                center[normal_axis] = min_corner[normal_axis] + depth / 2.0
            else:
                center[normal_axis] = max_corner[normal_axis] - depth / 2.0

        return [center[index] + offset[index] for index in range(3)]

    def _allocate_cutter_name(self, base_name: str) -> str:
        existing = {item["name"] for item in self._scene.list_objects()}
        if base_name not in existing:
            return base_name

        suffix = 1
        while f"{base_name}_{suffix}" in existing:
            suffix += 1
        return f"{base_name}_{suffix}"

    def _modifier_names(self, object_name: str) -> List[Dict[str, Any]]:
        return list(self._modeling.get_modifiers(object_name))

    def _resolve_new_modifier_name(
        self,
        *,
        target_object: str,
        before_names: List[Dict[str, Any]],
        modifier_type: str,
    ) -> str:
        before = {item.get("name") for item in before_names}
        after = self._modifier_names(target_object)
        new_names = [item.get("name") for item in after if item.get("name") not in before]
        if new_names:
            return str(new_names[-1])

        same_type = [item.get("name") for item in after if str(item.get("type", "")).upper() == modifier_type.upper()]
        if same_type:
            return str(same_type[-1])

        raise RuntimeError(f"Could not resolve newly added {modifier_type} modifier on '{target_object}'")
