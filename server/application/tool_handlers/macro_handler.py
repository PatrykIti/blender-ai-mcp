from __future__ import annotations

from uuid import uuid4
from typing import Any, Dict, List, Optional

from server.adapters.mcp.contracts.macro import MacroExecutionReportContract
from server.adapters.mcp.vision.capture_runtime import build_capture_bundle, capture_stage_images
from server.adapters.mcp.vision.reporting import attach_vision_artifacts
from server.domain.tools.macro import IMacroTool
from server.domain.tools.modeling import IModelingTool
from server.domain.tools.scene import ISceneTool
from server.infrastructure.config import get_config


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
        bundle_id = self._make_capture_bundle_id("macro_relative_layout", moving_object)
        captures_before = self._maybe_capture_stage(
            bundle_id=bundle_id,
            stage="before",
            target_object=moving_object,
            capture_profile=capture_profile,
        )

        reference_bbox = self._scene.get_bounding_box(reference_object, world_space=True)
        moving_bbox = self._scene.get_bounding_box(moving_object, world_space=True)
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
                target_location[axis_index] = float(reference_bbox["max"][axis_index]) + gap_value + moving_half[axis_index]
            else:
                target_location[axis_index] = float(reference_bbox["min"][axis_index]) - gap_value - moving_half[axis_index]

        target_location = [target + delta for target, delta in zip(target_location, offset_vector)]
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
                "action": "apply_relative_layout",
                "tool_name": "modeling_transform_object",
                "summary": f"Moved '{moving_object}' relative to '{reference_object}'",
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

        intent_parts = [f"x={modes['X']}", f"y={modes['Y']}", f"z={modes['Z']}"]
        if resolved_contact_axis is not None:
            intent_parts.append(f"contact {resolved_contact_side} on {resolved_contact_axis}")
            intent_parts.append(f"gap={gap_value:g}")

        report = {
            "status": "success",
            "macro_name": "macro_relative_layout",
            "intent": f"Layout '{moving_object}' relative to '{reference_object}' ({', '.join(intent_parts)})",
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
            bevel_segments_value = int(resolved["bevel_segments"])
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
                stage=stage,
                target_object=target_object,
                preset_profile=(capture_profile or "compact"),
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
            raise ValueError(
                "preset must be one of rounded_housing, panel_finish, shell_thicken, smooth_subdivision"
            )
        return normalized

    def _normalize_layout_mode(self, value: str, field_name: str) -> str:
        normalized = str(value).lower()
        if normalized not in {"none", "center", "min", "max"}:
            raise ValueError(f"{field_name} must be one of none, center, min, max")
        return normalized

    def _normalize_contact_axis(self, axis: Optional[str]) -> Optional[str]:
        if axis is None:
            return None
        normalized = str(axis).upper()
        if normalized not in self._AXIS_INDEX:
            raise ValueError("contact_axis must be one of X, Y, Z")
        return normalized

    def _normalize_contact_side(self, side: str) -> str:
        normalized = str(side).lower()
        if normalized not in {"positive", "negative"}:
            raise ValueError("contact_side must be one of positive or negative")
        return normalized

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
