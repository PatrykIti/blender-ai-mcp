from typing import Any, Dict, List, Optional

from server.application.tool_handlers._rpc_utils import (
    require_dict_result,
    require_list_of_dicts_result,
    require_str_result,
)
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.scene import ISceneTool


class SceneToolHandler(ISceneTool):
    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def list_objects(self) -> List[Dict[str, Any]]:
        return require_list_of_dicts_result(self.rpc.send_request("scene.list_objects"))

    def delete_object(self, name: str) -> str:
        response = self.rpc.send_request("scene.delete_object", {"name": name})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return f"Successfully deleted object: {name}"

    def clean_scene(self, keep_lights_and_cameras: bool) -> str:
        response = self.rpc.send_request("scene.clean_scene", {"keep_lights_and_cameras": keep_lights_and_cameras})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return f"Scene cleaned. (Kept lights/cameras: {keep_lights_and_cameras})"

    def duplicate_object(self, name: str, translation: Optional[List[float]] = None) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request("scene.duplicate_object", {"name": name, "translation": translation})
        )

    def set_active_object(self, name: str) -> str:
        response = self.rpc.send_request("scene.set_active_object", {"name": name})
        if response.status == "error":
            raise RuntimeError(f"Blender Error: {response.error}")
        return f"Successfully set active object to: {name}"

    def get_viewport(
        self,
        width: int = 1024,
        height: int = 768,
        shading: str = "SOLID",
        camera_name: Optional[str] = None,
        focus_target: Optional[str] = None,
    ) -> str:
        # Note: Large base64 strings might be heavy.
        args = {
            "width": width,
            "height": height,
            "shading": shading,
            "camera_name": camera_name,
            "focus_target": focus_target,
        }
        return require_str_result(self.rpc.send_request("scene.get_viewport", args))

    def create_light(
        self, type: str, energy: float, color: List[float], location: List[float], name: Optional[str] = None
    ) -> str:
        args = {"type": type, "energy": energy, "color": color, "location": location, "name": name}
        return require_str_result(self.rpc.send_request("scene.create_light", args))

    def create_camera(
        self,
        location: List[float],
        rotation: List[float],
        lens: float = 50.0,
        clip_start: Optional[float] = None,
        clip_end: Optional[float] = None,
        name: Optional[str] = None,
    ) -> str:
        args = {
            "location": location,
            "rotation": rotation,
            "lens": lens,
            "clip_start": clip_start,
            "clip_end": clip_end,
            "name": name,
        }
        return require_str_result(self.rpc.send_request("scene.create_camera", args))

    def create_empty(self, type: str, size: float, location: List[float], name: Optional[str] = None) -> str:
        args = {"type": type, "size": size, "location": location, "name": name}
        return require_str_result(self.rpc.send_request("scene.create_empty", args))

    def set_mode(self, mode: str) -> str:
        return require_str_result(self.rpc.send_request("scene.set_mode", {"mode": mode}))

    def get_mode(self) -> Dict[str, Any]:
        return require_dict_result(self.rpc.send_request("scene.get_mode"))

    def list_selection(self) -> Dict[str, Any]:
        return require_dict_result(self.rpc.send_request("scene.list_selection"))

    def inspect_object(self, name: str) -> Dict[str, Any]:
        return require_dict_result(self.rpc.send_request("scene.inspect_object", {"name": name}))

    def snapshot_state(self, include_mesh_stats: bool = False, include_materials: bool = False) -> Dict[str, Any]:
        args = {"include_mesh_stats": include_mesh_stats, "include_materials": include_materials}
        return require_dict_result(self.rpc.send_request("scene.snapshot_state", args))

    def inspect_material_slots(
        self, material_filter: Optional[str] = None, include_empty_slots: bool = True
    ) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request(
                "scene.inspect_material_slots",
                {"material_filter": material_filter, "include_empty_slots": include_empty_slots},
            )
        )

    def inspect_mesh_topology(self, object_name: str, detailed: bool = False) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request("scene.inspect_mesh_topology", {"object_name": object_name, "detailed": detailed})
        )

    def inspect_modifiers(self, object_name: Optional[str] = None, include_disabled: bool = True) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request(
                "scene.inspect_modifiers", {"object_name": object_name, "include_disabled": include_disabled}
            )
        )

    def inspect_render_settings(self) -> Dict[str, Any]:
        return require_dict_result(self.rpc.send_request("scene.inspect_render_settings"))

    def inspect_color_management(self) -> Dict[str, Any]:
        return require_dict_result(self.rpc.send_request("scene.inspect_color_management"))

    def inspect_world(self) -> Dict[str, Any]:
        return require_dict_result(self.rpc.send_request("scene.inspect_world"))

    def configure_render_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        return require_dict_result(self.rpc.send_request("scene.configure_render_settings", {"settings": settings}))

    def configure_color_management(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        return require_dict_result(self.rpc.send_request("scene.configure_color_management", {"settings": settings}))

    def configure_world(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        return require_dict_result(self.rpc.send_request("scene.configure_world", {"settings": settings}))

    def get_constraints(self, object_name: str, include_bones: bool = False) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request("scene.get_constraints", {"object_name": object_name, "include_bones": include_bones})
        )

    # TASK-043: Scene Utility Tools
    def rename_object(self, old_name: str, new_name: str) -> str:
        return require_str_result(
            self.rpc.send_request("scene.rename_object", {"old_name": old_name, "new_name": new_name})
        )

    def hide_object(self, object_name: str, hide: bool = True, hide_render: bool = False) -> str:
        return require_str_result(
            self.rpc.send_request(
                "scene.hide_object", {"object_name": object_name, "hide": hide, "hide_render": hide_render}
            )
        )

    def show_all_objects(self, include_render: bool = False) -> str:
        return require_str_result(self.rpc.send_request("scene.show_all_objects", {"include_render": include_render}))

    def isolate_object(self, object_names: List[str]) -> str:
        return require_str_result(self.rpc.send_request("scene.isolate_object", {"object_names": object_names}))

    def camera_orbit(
        self,
        angle_horizontal: float = 0.0,
        angle_vertical: float = 0.0,
        target_object: Optional[str] = None,
        target_point: Optional[List[float]] = None,
    ) -> str:
        return require_str_result(
            self.rpc.send_request(
                "scene.camera_orbit",
                {
                    "angle_horizontal": angle_horizontal,
                    "angle_vertical": angle_vertical,
                    "target_object": target_object,
                    "target_point": target_point,
                },
            )
        )

    def camera_focus(self, object_name: str, zoom_factor: float = 1.0) -> str:
        return require_str_result(
            self.rpc.send_request("scene.camera_focus", {"object_name": object_name, "zoom_factor": zoom_factor})
        )

    def get_view_state(self) -> Dict[str, Any]:
        return require_dict_result(self.rpc.send_request("scene.get_view_state"))

    def restore_view_state(self, view_state: Dict[str, Any]) -> str:
        return require_str_result(self.rpc.send_request("scene.restore_view_state", {"view_state": view_state}))

    # TASK-045: Object Inspection Tools
    def get_custom_properties(self, object_name: str) -> Dict[str, Any]:
        return require_dict_result(self.rpc.send_request("scene.get_custom_properties", {"object_name": object_name}))

    def set_custom_property(
        self, object_name: str, property_name: str, property_value: Any, delete: bool = False
    ) -> str:
        return require_str_result(
            self.rpc.send_request(
                "scene.set_custom_property",
                {
                    "object_name": object_name,
                    "property_name": property_name,
                    "property_value": property_value,
                    "delete": delete,
                },
            )
        )

    def get_hierarchy(self, object_name: Optional[str] = None, include_transforms: bool = False) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request(
                "scene.get_hierarchy", {"object_name": object_name, "include_transforms": include_transforms}
            )
        )

    def get_bounding_box(self, object_name: str, world_space: bool = True) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request("scene.get_bounding_box", {"object_name": object_name, "world_space": world_space})
        )

    def get_origin_info(self, object_name: str) -> Dict[str, Any]:
        return require_dict_result(self.rpc.send_request("scene.get_origin_info", {"object_name": object_name}))

    def measure_distance(self, from_object: str, to_object: str, reference: str = "ORIGIN") -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request(
                "scene.measure_distance",
                {"from_object": from_object, "to_object": to_object, "reference": reference},
            )
        )

    def measure_dimensions(self, object_name: str, world_space: bool = True) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request(
                "scene.measure_dimensions",
                {"object_name": object_name, "world_space": world_space},
            )
        )

    def measure_gap(self, from_object: str, to_object: str, tolerance: float = 0.0001) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request(
                "scene.measure_gap",
                {"from_object": from_object, "to_object": to_object, "tolerance": tolerance},
            )
        )

    def measure_alignment(
        self,
        from_object: str,
        to_object: str,
        axes: Optional[List[str]] = None,
        reference: str = "CENTER",
        tolerance: float = 0.0001,
    ) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request(
                "scene.measure_alignment",
                {
                    "from_object": from_object,
                    "to_object": to_object,
                    "axes": axes,
                    "reference": reference,
                    "tolerance": tolerance,
                },
            )
        )

    def measure_overlap(self, from_object: str, to_object: str, tolerance: float = 0.0001) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request(
                "scene.measure_overlap",
                {"from_object": from_object, "to_object": to_object, "tolerance": tolerance},
            )
        )

    def assert_contact(
        self,
        from_object: str,
        to_object: str,
        max_gap: float = 0.0001,
        allow_overlap: bool = False,
    ) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request(
                "scene.assert_contact",
                {
                    "from_object": from_object,
                    "to_object": to_object,
                    "max_gap": max_gap,
                    "allow_overlap": allow_overlap,
                },
            )
        )

    def assert_dimensions(
        self,
        object_name: str,
        expected_dimensions: List[float],
        tolerance: float = 0.0001,
        world_space: bool = True,
    ) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request(
                "scene.assert_dimensions",
                {
                    "object_name": object_name,
                    "expected_dimensions": expected_dimensions,
                    "tolerance": tolerance,
                    "world_space": world_space,
                },
            )
        )

    def assert_containment(
        self,
        inner_object: str,
        outer_object: str,
        min_clearance: float = 0.0,
        tolerance: float = 0.0001,
    ) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request(
                "scene.assert_containment",
                {
                    "inner_object": inner_object,
                    "outer_object": outer_object,
                    "min_clearance": min_clearance,
                    "tolerance": tolerance,
                },
            )
        )

    def assert_symmetry(
        self,
        left_object: str,
        right_object: str,
        axis: str = "X",
        mirror_coordinate: float = 0.0,
        tolerance: float = 0.0001,
    ) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request(
                "scene.assert_symmetry",
                {
                    "left_object": left_object,
                    "right_object": right_object,
                    "axis": axis,
                    "mirror_coordinate": mirror_coordinate,
                    "tolerance": tolerance,
                },
            )
        )

    def assert_proportion(
        self,
        object_name: str,
        axis_a: str,
        expected_ratio: float,
        axis_b: Optional[str] = None,
        reference_object: Optional[str] = None,
        reference_axis: Optional[str] = None,
        tolerance: float = 0.01,
        world_space: bool = True,
    ) -> Dict[str, Any]:
        return require_dict_result(
            self.rpc.send_request(
                "scene.assert_proportion",
                {
                    "object_name": object_name,
                    "axis_a": axis_a,
                    "expected_ratio": expected_ratio,
                    "axis_b": axis_b,
                    "reference_object": reference_object,
                    "reference_axis": reference_axis,
                    "tolerance": tolerance,
                    "world_space": world_space,
                },
            )
        )
