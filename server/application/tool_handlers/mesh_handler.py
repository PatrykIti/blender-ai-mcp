from typing import Any, Dict, List, Optional

from server.application.tool_handlers._rpc_utils import require_dict_result, require_str_result
from server.domain.interfaces.rpc import IRpcClient
from server.domain.tools.mesh import IMeshTool


class MeshToolHandler(IMeshTool):
    def __init__(self, rpc_client: IRpcClient):
        self.rpc = rpc_client

    def select_all(self, deselect: bool = False) -> str:
        return require_str_result(self.rpc.send_request("mesh.select_all", {"deselect": deselect}))

    def delete_selected(self, type: str = "VERT") -> str:
        return require_str_result(self.rpc.send_request("mesh.delete_selected", {"type": type}))

    def select_by_index(self, indices: List[int], type: str = "VERT", selection_mode: str = "SET") -> str:
        return require_str_result(
            self.rpc.send_request(
                "mesh.select_by_index", {"indices": indices, "type": type, "selection_mode": selection_mode}
            )
        )

    def extrude_region(self, move: List[float] = None) -> str:
        args = {"move": move} if move else {}
        return require_str_result(self.rpc.send_request("mesh.extrude_region", args))

    def fill_holes(self) -> str:
        return require_str_result(self.rpc.send_request("mesh.fill_holes"))

    def bevel(self, offset: float, segments: int = 1, profile: float = 0.5, affect: str = "EDGES") -> str:
        args = {"offset": offset, "segments": segments, "profile": profile, "affect": affect}
        return require_str_result(self.rpc.send_request("mesh.bevel", args))

    def loop_cut(self, number_cuts: int = 1, smoothness: float = 0.0) -> str:
        args = {"number_cuts": number_cuts, "smoothness": smoothness}
        return require_str_result(self.rpc.send_request("mesh.loop_cut", args))

    def inset(self, thickness: float, depth: float = 0.0) -> str:
        args = {"thickness": thickness, "depth": depth}
        return require_str_result(self.rpc.send_request("mesh.inset", args))

    def boolean(self, operation: str, solver: str = "FAST") -> str:
        args = {"operation": operation, "solver": solver}
        return require_str_result(self.rpc.send_request("mesh.boolean", args))

    def merge_by_distance(self, distance: float = 0.001) -> str:
        args = {"distance": distance}
        return require_str_result(self.rpc.send_request("mesh.merge_by_distance", args))

    def subdivide(self, number_cuts: int = 1, smoothness: float = 0.0) -> str:
        args = {"number_cuts": number_cuts, "smoothness": smoothness}
        return require_str_result(self.rpc.send_request("mesh.subdivide", args))

    def smooth_vertices(self, iterations: int = 1, factor: float = 0.5) -> str:
        args = {"iterations": iterations, "factor": factor}
        return require_str_result(self.rpc.send_request("mesh.smooth_vertices", args))

    def flatten_vertices(self, axis: str) -> str:
        args = {"axis": axis}
        return require_str_result(self.rpc.send_request("mesh.flatten_vertices", args))

    def list_groups(self, object_name: str, group_type: str = "VERTEX") -> dict:
        args = {"object_name": object_name, "group_type": group_type}
        return require_dict_result(self.rpc.send_request("mesh.list_groups", args))

    def select_loop(self, edge_index: int) -> str:
        args = {"edge_index": edge_index}
        return require_str_result(self.rpc.send_request("mesh.select_loop", args))

    def select_ring(self, edge_index: int) -> str:
        args = {"edge_index": edge_index}
        return require_str_result(self.rpc.send_request("mesh.select_ring", args))

    def select_linked(self) -> str:
        return require_str_result(self.rpc.send_request("mesh.select_linked"))

    def select_more(self) -> str:
        return require_str_result(self.rpc.send_request("mesh.select_more"))

    def select_less(self) -> str:
        return require_str_result(self.rpc.send_request("mesh.select_less"))

    def get_vertex_data(
        self, object_name: str, selected_only: bool = False, offset: Optional[int] = None, limit: Optional[int] = None
    ) -> dict:
        args: Dict[str, Any] = {"object_name": object_name, "selected_only": selected_only}
        if offset is not None:
            args["offset"] = offset
        if limit is not None:
            args["limit"] = limit
        return require_dict_result(self.rpc.send_request("mesh.get_vertex_data", args))

    def get_edge_data(
        self, object_name: str, selected_only: bool = False, offset: Optional[int] = None, limit: Optional[int] = None
    ) -> dict:
        args: Dict[str, Any] = {"object_name": object_name, "selected_only": selected_only}
        if offset is not None:
            args["offset"] = offset
        if limit is not None:
            args["limit"] = limit
        return require_dict_result(self.rpc.send_request("mesh.get_edge_data", args))

    def get_face_data(
        self, object_name: str, selected_only: bool = False, offset: Optional[int] = None, limit: Optional[int] = None
    ) -> dict:
        args: Dict[str, Any] = {"object_name": object_name, "selected_only": selected_only}
        if offset is not None:
            args["offset"] = offset
        if limit is not None:
            args["limit"] = limit
        return require_dict_result(self.rpc.send_request("mesh.get_face_data", args))

    def get_uv_data(
        self,
        object_name: str,
        uv_layer: Optional[str] = None,
        selected_only: bool = False,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        args: Dict[str, Any] = {"object_name": object_name, "selected_only": selected_only}
        if uv_layer is not None:
            args["uv_layer"] = uv_layer
        if offset is not None:
            args["offset"] = offset
        if limit is not None:
            args["limit"] = limit
        return require_dict_result(self.rpc.send_request("mesh.get_uv_data", args))

    def get_loop_normals(
        self, object_name: str, selected_only: bool = False, offset: Optional[int] = None, limit: Optional[int] = None
    ) -> dict:
        args: Dict[str, Any] = {"object_name": object_name, "selected_only": selected_only}
        if offset is not None:
            args["offset"] = offset
        if limit is not None:
            args["limit"] = limit
        return require_dict_result(self.rpc.send_request("mesh.get_loop_normals", args))

    def get_vertex_group_weights(
        self,
        object_name: str,
        group_name: Optional[str] = None,
        selected_only: bool = False,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        args: Dict[str, Any] = {"object_name": object_name, "selected_only": selected_only}
        if group_name is not None:
            args["group_name"] = group_name
        if offset is not None:
            args["offset"] = offset
        if limit is not None:
            args["limit"] = limit
        return require_dict_result(self.rpc.send_request("mesh.get_vertex_group_weights", args))

    def get_attributes(
        self,
        object_name: str,
        attribute_name: Optional[str] = None,
        selected_only: bool = False,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> dict:
        args: Dict[str, Any] = {"object_name": object_name, "selected_only": selected_only}
        if attribute_name is not None:
            args["attribute_name"] = attribute_name
        if offset is not None:
            args["offset"] = offset
        if limit is not None:
            args["limit"] = limit
        return require_dict_result(self.rpc.send_request("mesh.get_attributes", args))

    def get_shape_keys(
        self, object_name: str, include_deltas: bool = False, offset: Optional[int] = None, limit: Optional[int] = None
    ) -> dict:
        args: Dict[str, Any] = {"object_name": object_name, "include_deltas": include_deltas}
        if offset is not None:
            args["offset"] = offset
        if limit is not None:
            args["limit"] = limit
        return require_dict_result(self.rpc.send_request("mesh.get_shape_keys", args))

    def select_by_location(self, axis: str, min_coord: float, max_coord: float, mode: str = "VERT") -> str:
        args = {"axis": axis, "min_coord": min_coord, "max_coord": max_coord, "mode": mode}
        return require_str_result(self.rpc.send_request("mesh.select_by_location", args))

    def select_boundary(self, mode: str = "EDGE") -> str:
        args = {"mode": mode}
        return require_str_result(self.rpc.send_request("mesh.select_boundary", args))

    # TASK-016-1: Mesh Randomize Tool
    def randomize(self, amount: float = 0.1, uniform: float = 0.0, normal: float = 0.0, seed: int = 0) -> str:
        args = {"amount": amount, "uniform": uniform, "normal": normal, "seed": seed}
        return require_str_result(self.rpc.send_request("mesh.randomize", args))

    # TASK-016-2: Mesh Shrink/Fatten Tool
    def shrink_fatten(self, value: float) -> str:
        args = {"value": value}
        return require_str_result(self.rpc.send_request("mesh.shrink_fatten", args))

    # TASK-017-1: Mesh Create Vertex Group Tool
    def create_vertex_group(self, object_name: str, name: str) -> str:
        args = {"object_name": object_name, "name": name}
        return require_str_result(self.rpc.send_request("mesh.create_vertex_group", args))

    # TASK-017-2: Mesh Assign/Remove Vertex Group Tools
    def assign_to_group(self, object_name: str, group_name: str, weight: float = 1.0) -> str:
        args = {"object_name": object_name, "group_name": group_name, "weight": weight}
        return require_str_result(self.rpc.send_request("mesh.assign_to_group", args))

    def remove_from_group(self, object_name: str, group_name: str) -> str:
        args = {"object_name": object_name, "group_name": group_name}
        return require_str_result(self.rpc.send_request("mesh.remove_from_group", args))

    # TASK-018-1: Mesh Bisect Tool
    def bisect(
        self, plane_co: list, plane_no: list, clear_inner: bool = False, clear_outer: bool = False, fill: bool = False
    ) -> str:
        args = {
            "plane_co": plane_co,
            "plane_no": plane_no,
            "clear_inner": clear_inner,
            "clear_outer": clear_outer,
            "fill": fill,
        }
        return require_str_result(self.rpc.send_request("mesh.bisect", args))

    # TASK-018-2: Mesh Edge/Vertex Slide Tools
    def edge_slide(self, value: float = 0.0) -> str:
        args = {"value": value}
        return require_str_result(self.rpc.send_request("mesh.edge_slide", args))

    def vert_slide(self, value: float = 0.0) -> str:
        args = {"value": value}
        return require_str_result(self.rpc.send_request("mesh.vert_slide", args))

    # TASK-018-3: Mesh Triangulate Tool
    def triangulate(self) -> str:
        return require_str_result(self.rpc.send_request("mesh.triangulate"))

    # TASK-018-4: Mesh Remesh Voxel Tool
    def remesh_voxel(self, voxel_size: float = 0.1, adaptivity: float = 0.0) -> str:
        args = {"voxel_size": voxel_size, "adaptivity": adaptivity}
        return require_str_result(self.rpc.send_request("mesh.remesh_voxel", args))

    # TASK-019-1: Mesh Transform Selected Tool
    def transform_selected(
        self,
        translate: Optional[list] = None,
        rotate: Optional[list] = None,
        scale: Optional[list] = None,
        pivot: str = "MEDIAN_POINT",
    ) -> str:
        args: Dict[str, Any] = {"pivot": pivot}
        if translate:
            args["translate"] = translate
        if rotate:
            args["rotate"] = rotate
        if scale:
            args["scale"] = scale
        return require_str_result(self.rpc.send_request("mesh.transform_selected", args))

    # TASK-019-2: Mesh Bridge Edge Loops Tool
    def bridge_edge_loops(
        self, number_cuts: int = 0, interpolation: str = "LINEAR", smoothness: float = 0.0, twist: int = 0
    ) -> str:
        args = {"number_cuts": number_cuts, "interpolation": interpolation, "smoothness": smoothness, "twist": twist}
        return require_str_result(self.rpc.send_request("mesh.bridge_edge_loops", args))

    # TASK-019-3: Mesh Duplicate Selected Tool
    def duplicate_selected(self, translate: Optional[list] = None) -> str:
        args: Dict[str, Any] = {}
        if translate:
            args["translate"] = translate
        return require_str_result(self.rpc.send_request("mesh.duplicate_selected", args))

    # TASK-021-3: Mesh Spin Tool
    def spin(
        self, steps: int = 12, angle: float = 6.283185, axis: str = "Z", center: list = None, dupli: bool = False
    ) -> str:
        args = {"steps": steps, "angle": angle, "axis": axis, "dupli": dupli}
        if center:
            args["center"] = center
        return require_str_result(self.rpc.send_request("mesh.spin", args))

    # TASK-021-4: Mesh Screw Tool
    def screw(self, steps: int = 12, turns: int = 1, axis: str = "Z", center: list = None, offset: float = 0.0) -> str:
        args = {"steps": steps, "turns": turns, "axis": axis, "offset": offset}
        if center:
            args["center"] = center
        return require_str_result(self.rpc.send_request("mesh.screw", args))

    # TASK-021-5: Mesh Add Geometry Tools
    def add_vertex(self, position: list) -> str:
        args = {"position": position}
        return require_str_result(self.rpc.send_request("mesh.add_vertex", args))

    def add_edge_face(self) -> str:
        return require_str_result(self.rpc.send_request("mesh.add_edge_face"))

    # TASK-029-1: Mesh Edge Crease Tool
    def edge_crease(self, crease_value: float = 1.0) -> str:
        args = {"crease_value": crease_value}
        return require_str_result(self.rpc.send_request("mesh.edge_crease", args))

    # TASK-029-2: Mesh Bevel Weight Tool
    def bevel_weight(self, weight: float = 1.0) -> str:
        args = {"weight": weight}
        return require_str_result(self.rpc.send_request("mesh.bevel_weight", args))

    # TASK-029-3: Mesh Mark Sharp Tool
    def mark_sharp(self, action: str = "mark") -> str:
        args = {"action": action}
        return require_str_result(self.rpc.send_request("mesh.mark_sharp", args))

    # TASK-030-1: Mesh Dissolve Tool
    def dissolve(
        self,
        dissolve_type: str = "limited",
        angle_limit: float = 5.0,
        use_face_split: bool = False,
        use_boundary_tear: bool = False,
    ) -> str:
        args = {
            "dissolve_type": dissolve_type,
            "angle_limit": angle_limit,
            "use_face_split": use_face_split,
            "use_boundary_tear": use_boundary_tear,
        }
        return require_str_result(self.rpc.send_request("mesh.dissolve", args))

    # TASK-030-2: Mesh Tris To Quads Tool
    def tris_to_quads(self, face_threshold: float = 40.0, shape_threshold: float = 40.0) -> str:
        args = {"face_threshold": face_threshold, "shape_threshold": shape_threshold}
        return require_str_result(self.rpc.send_request("mesh.tris_to_quads", args))

    # TASK-030-3: Mesh Normals Make Consistent Tool
    def normals_make_consistent(self, inside: bool = False) -> str:
        args = {"inside": inside}
        return require_str_result(self.rpc.send_request("mesh.normals_make_consistent", args))

    # TASK-030-4: Mesh Decimate Tool
    def decimate(self, ratio: float = 0.5, use_symmetry: bool = False, symmetry_axis: str = "X") -> str:
        args = {"ratio": ratio, "use_symmetry": use_symmetry, "symmetry_axis": symmetry_axis}
        return require_str_result(self.rpc.send_request("mesh.decimate", args))

    # TASK-032-1: Mesh Knife Project Tool
    def knife_project(self, cut_through: bool = True) -> str:
        args = {"cut_through": cut_through}
        return require_str_result(self.rpc.send_request("mesh.knife_project", args))

    # TASK-032-2: Mesh Rip Tool
    def rip(self, use_fill: bool = False) -> str:
        args = {"use_fill": use_fill}
        return require_str_result(self.rpc.send_request("mesh.rip", args))

    # TASK-032-3: Mesh Split Tool
    def split(self) -> str:
        return require_str_result(self.rpc.send_request("mesh.split"))

    # TASK-032-4: Mesh Edge Split Tool
    def edge_split(self) -> str:
        return require_str_result(self.rpc.send_request("mesh.edge_split"))

    # TASK-038-5: Proportional Editing
    def set_proportional_edit(
        self,
        enabled: bool = True,
        falloff_type: str = "SMOOTH",
        size: float = 1.0,
        use_connected: bool = False,
    ) -> str:
        """Configures proportional editing settings."""
        args = {
            "enabled": enabled,
            "falloff_type": falloff_type,
            "size": size,
            "use_connected": use_connected,
        }
        return require_str_result(self.rpc.send_request("mesh.set_proportional_edit", args))

    # TASK-036-1: Mesh Symmetrize Tool
    def symmetrize(self, direction: str = "NEGATIVE_X", threshold: float = 0.0001) -> str:
        args = {"direction": direction, "threshold": threshold}
        return require_str_result(self.rpc.send_request("mesh.symmetrize", args))

    # TASK-036-2: Mesh Grid Fill Tool
    def grid_fill(self, span: int = 1, offset: int = 0, use_interp_simple: bool = False) -> str:
        args = {"span": span, "offset": offset, "use_interp_simple": use_interp_simple}
        return require_str_result(self.rpc.send_request("mesh.grid_fill", args))

    # TASK-036-3: Mesh Poke Faces Tool
    def poke_faces(
        self, offset: float = 0.0, use_relative_offset: bool = False, center_mode: str = "MEDIAN_WEIGHTED"
    ) -> str:
        args = {"offset": offset, "use_relative_offset": use_relative_offset, "center_mode": center_mode}
        return require_str_result(self.rpc.send_request("mesh.poke_faces", args))

    # TASK-036-4: Mesh Beautify Fill Tool
    def beautify_fill(self, angle_limit: float = 180.0) -> str:
        args = {"angle_limit": angle_limit}
        return require_str_result(self.rpc.send_request("mesh.beautify_fill", args))

    # TASK-036-5: Mesh Mirror Tool
    def mirror(self, axis: str = "X", use_mirror_merge: bool = True, merge_threshold: float = 0.001) -> str:
        args = {"axis": axis, "use_mirror_merge": use_mirror_merge, "merge_threshold": merge_threshold}
        return require_str_result(self.rpc.send_request("mesh.mirror", args))
