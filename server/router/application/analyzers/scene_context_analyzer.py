"""
Scene Context Analyzer Implementation.

Analyzes Blender scene state via RPC for router decision making.
"""

from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any, List

from server.router.domain.interfaces.i_scene_analyzer import ISceneAnalyzer
from server.router.domain.entities.scene_context import (
    SceneContext,
    ObjectInfo,
    TopologyInfo,
    ProportionInfo,
)
from server.router.application.analyzers.proportion_calculator import calculate_proportions


class SceneContextAnalyzer(ISceneAnalyzer):
    """Implementation of scene analysis.

    Analyzes current Blender scene state for router decision making.
    Uses RPC to query Blender and caches results to avoid repeated calls.

    Attributes:
        rpc_client: RPC client for Blender communication.
        cache_ttl: Cache time-to-live in seconds.
    """

    def __init__(
        self,
        rpc_client: Optional[Any] = None,
        cache_ttl: float = 1.0,
    ):
        """Initialize analyzer.

        Args:
            rpc_client: RPC client for Blender communication.
            cache_ttl: Cache time-to-live in seconds.
        """
        self._rpc_client = rpc_client
        self._cache_ttl = cache_ttl
        self._cached_context: Optional[SceneContext] = None
        self._cache_timestamp: Optional[datetime] = None

    def set_rpc_client(self, rpc_client: Any) -> None:
        """Set the RPC client.

        Args:
            rpc_client: RPC client for Blender communication.
        """
        self._rpc_client = rpc_client

    def analyze(self, object_name: Optional[str] = None) -> SceneContext:
        """Analyze current scene context.

        Args:
            object_name: Specific object to focus on (uses active if None).

        Returns:
            SceneContext with current scene state.
        """
        # Check cache first
        cached = self.get_cached()
        if cached is not None:
            # If specific object requested and matches cache, return cache (but refresh hot state)
            if object_name is None or object_name == cached.active_object:
                if self._rpc_client is None:
                    return cached

                mode_data = self._get_mode_data_rpc()
                raw_mode = mode_data.get("mode", cached.mode)
                mode = self._normalize_mode(raw_mode)
                active_object = mode_data.get("active_object") or cached.active_object

                # If active object changed within TTL, rebuild instead of returning stale cache.
                if object_name is None and cached.active_object and active_object and active_object != cached.active_object:
                    cached = None
                else:
                    selected_objects = mode_data.get("selected_object_names", cached.selected_objects)

                    if object_name:
                        active_object = object_name

                    cached.mode = mode
                    cached.active_object = active_object
                    cached.selected_objects = selected_objects

                    # Selection is hot data in EDIT mode and should not be cached.
                    if mode == "EDIT":
                        selection_data = self._get_selection_rpc()
                        selected_verts = selection_data.get("edit_mode_vertex_count")
                        selected_edges = selection_data.get("edit_mode_edge_count")
                        selected_faces = selection_data.get("edit_mode_face_count")

                        if selected_verts is not None or selected_edges is not None or selected_faces is not None:
                            if cached.topology is None:
                                cached.topology = TopologyInfo(
                                    vertices=0,
                                    edges=0,
                                    faces=0,
                                    triangles=0,
                                    selected_verts=int(selected_verts or 0),
                                    selected_edges=int(selected_edges or 0),
                                    selected_faces=int(selected_faces or 0),
                                )
                            else:
                                cached.topology.selected_verts = int(selected_verts or 0)
                                cached.topology.selected_edges = int(selected_edges or 0)
                                cached.topology.selected_faces = int(selected_faces or 0)
                    else:
                        cached.topology = None

                    return cached

        # Build context from RPC calls
        context = self._build_context(object_name)

        # Update cache
        self._cached_context = context
        self._cache_timestamp = datetime.now()

        return context

    def get_cached(self) -> Optional[SceneContext]:
        """Get cached scene context if still valid.

        Returns:
            Cached SceneContext or None if cache expired/invalid.
        """
        if self._cached_context is None or self._cache_timestamp is None:
            return None

        # Check if cache is still valid
        elapsed = datetime.now() - self._cache_timestamp
        if elapsed > timedelta(seconds=self._cache_ttl):
            return None

        return self._cached_context

    def invalidate_cache(self) -> None:
        """Invalidate the scene context cache."""
        self._cached_context = None
        self._cache_timestamp = None

    def get_mode(self) -> str:
        """Get current Blender mode.

        Returns:
            Mode string (OBJECT, EDIT, SCULPT, etc.).
        """
        if self._rpc_client is None:
            return "OBJECT"

        try:
            # Use scene.get_mode RPC method (addon method)
            response = self._rpc_client.send_request("scene.get_mode", {})
            # RpcResponse has .status and .result
            if response.status == "ok" and isinstance(response.result, dict):
                return self._normalize_mode(response.result.get("mode", "OBJECT"))
            return "OBJECT"
        except Exception:
            return "OBJECT"

    def has_selection(self) -> bool:
        """Check if anything is selected.

        Returns:
            True if there's a selection in current context.
        """
        context = self.get_cached()
        if context:
            return context.has_selection

        if self._rpc_client is None:
            return False

        try:
            # Use scene.list_selection RPC method (addon method)
            response = self._rpc_client.send_request("scene.list_selection", {})
            # RpcResponse has .status and .result
            if response.status == "ok" and isinstance(response.result, dict):
                result = response.result
                # Addon uses "selected_object_names" not "selected_objects"
                selected_objects = result.get("selected_object_names", [])
                # Edit mode selection counts
                selected_verts = result.get("edit_mode_vertex_count") or 0
                selected_edges = result.get("edit_mode_edge_count") or 0
                selected_faces = result.get("edit_mode_face_count") or 0
                return bool(selected_objects) or selected_verts > 0 or selected_edges > 0 or selected_faces > 0
            return False
        except Exception:
            return False

    def _build_context(self, object_name: Optional[str] = None) -> SceneContext:
        """Build scene context from RPC calls.

        Uses individual addon RPC methods to gather scene state:
        - scene.get_mode (returns: mode, active_object, selected_object_names)
        - scene.list_objects (returns: [{name, type, location}])
        - scene.list_selection (returns: mode, selected_object_names)
        - scene.inspect_object (for dimensions, materials, modifiers)
        - scene.inspect_mesh_topology (for topology info)

        Args:
            object_name: Specific object to focus on.

        Returns:
            SceneContext with current scene state.
        """
        if self._rpc_client is None:
            return SceneContext.empty()

        try:
            # Get mode and active object from get_mode (includes active_object)
            mode_data = self._get_mode_data_rpc()
            raw_mode = mode_data.get("mode", "OBJECT")
            mode = self._normalize_mode(raw_mode)
            active_object = mode_data.get("active_object")
            # Note: addon uses "selected_object_names" not "selected_objects"
            selected_objects = mode_data.get("selected_object_names", [])

            # Get objects list (basic info only - no dimensions)
            objects_data = self._get_objects_rpc()

            # If specific object requested, use it
            if object_name:
                active_object = object_name

            # Build objects list - need to get dimensions from inspect_object
            objects = []
            for obj_data in objects_data:
                if isinstance(obj_data, dict):
                    obj_name = obj_data.get("name", "")
                    obj_type = obj_data.get("type", "MESH")
                    obj_location = obj_data.get("location", [0.0, 0.0, 0.0])

                    # Get dimensions from inspect_object (only for active object to avoid many RPC calls)
                    dimensions = [1.0, 1.0, 1.0]
                    if obj_name == active_object:
                        inspect_data = self._get_inspect_rpc(obj_name)
                        if inspect_data:
                            dimensions = inspect_data.get("dimensions", [1.0, 1.0, 1.0])

                    objects.append(ObjectInfo(
                        name=obj_name,
                        type=obj_type,
                        location=obj_location,
                        dimensions=dimensions,
                        selected=obj_name in selected_objects,
                        active=obj_name == active_object,
                    ))

            # Get topology for active mesh object in EDIT mode
            topology = None
            if active_object and mode == "EDIT":
                selection_data = self._get_selection_rpc()
                topology = self._get_topology_rpc(active_object, selection_data)

            # Calculate proportions for active object
            proportions = None
            for obj in objects:
                if obj.active and obj.dimensions:
                    proportions = calculate_proportions(obj.dimensions)
                    break

            # Get materials and modifiers for active object (already fetched above)
            materials = []
            modifiers = []
            if active_object:
                inspect_data = self._get_inspect_rpc(active_object)
                if inspect_data:
                    # Addon uses "material_slots" not "materials"
                    material_slots = inspect_data.get("material_slots", [])
                    materials = [slot.get("material_name", "") for slot in material_slots if isinstance(slot, dict)]
                    # Addon uses list of modifier dicts
                    mod_list = inspect_data.get("modifiers", [])
                    modifiers = [mod.get("name", "") for mod in mod_list if isinstance(mod, dict)]

            return SceneContext(
                mode=mode,
                active_object=active_object,
                selected_objects=selected_objects,
                objects=objects,
                topology=topology,
                proportions=proportions,
                materials=materials if isinstance(materials, list) else [],
                modifiers=modifiers if isinstance(modifiers, list) else [],
                timestamp=datetime.now(),
            )

        except Exception as e:
            import logging
            logging.error(f"SceneContextAnalyzer._build_context failed: {e}", exc_info=True)
            return SceneContext.empty()

    @staticmethod
    def _normalize_mode(mode: Any) -> str:
        """Normalize Blender mode strings (e.g. EDIT_MESH -> EDIT)."""
        if not isinstance(mode, str) or not mode:
            return "OBJECT"

        if mode.startswith("EDIT"):
            return "EDIT"

        return mode

    def _get_mode_rpc(self) -> str:
        """Get mode string via RPC."""
        data = self._get_mode_data_rpc()
        return self._normalize_mode(data.get("mode", "OBJECT"))

    def _get_mode_data_rpc(self) -> Dict[str, Any]:
        """Get full mode data via RPC (includes active_object, selected_object_names)."""
        try:
            response = self._rpc_client.send_request("scene.get_mode", {})
            # RpcResponse has .status and .result
            if response.status == "ok" and isinstance(response.result, dict):
                return response.result
            import logging
            logging.warning(f"_get_mode_data_rpc: status={response.status}, result type={type(response.result)}")
            return {"mode": "OBJECT"}
        except Exception as e:
            import logging
            logging.error(f"_get_mode_data_rpc failed: {e}")
            return {"mode": "OBJECT"}

    def _get_objects_rpc(self) -> List[Dict[str, Any]]:
        """Get objects list via RPC."""
        try:
            response = self._rpc_client.send_request("scene.list_objects", {})
            # RpcResponse has .status and .result
            if response.status == "ok":
                if isinstance(response.result, list):
                    return response.result
                elif isinstance(response.result, dict):
                    return response.result.get("objects", [])
            return []
        except Exception:
            return []

    def _get_selection_rpc(self) -> Dict[str, Any]:
        """Get selection info via RPC."""
        try:
            response = self._rpc_client.send_request("scene.list_selection", {})
            # RpcResponse has .status and .result
            if response.status == "ok" and isinstance(response.result, dict):
                return response.result
            return {}
        except Exception:
            return {}

    def _get_topology_rpc(
        self,
        object_name: str,
        selection_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[TopologyInfo]:
        """Get mesh topology via RPC."""
        try:
            response = self._rpc_client.send_request(
                "scene.inspect_mesh_topology",
                {"object_name": object_name}
            )
            # RpcResponse has .status and .result
            if response.status == "ok" and isinstance(response.result, dict):
                result = response.result

                vertices = result.get("vertices", result.get("vertex_count", 0))
                edges = result.get("edges", result.get("edge_count", 0))
                faces = result.get("faces", result.get("face_count", 0))
                triangles = result.get("triangles", result.get("triangle_count", 0))

                selected_verts = result.get("selected_verts", 0)
                selected_edges = result.get("selected_edges", 0)
                selected_faces = result.get("selected_faces", 0)

                if selection_data:
                    selected_verts = selection_data.get("edit_mode_vertex_count", selected_verts) or 0
                    selected_edges = selection_data.get("edit_mode_edge_count", selected_edges) or 0
                    selected_faces = selection_data.get("edit_mode_face_count", selected_faces) or 0

                return TopologyInfo(
                    vertices=int(vertices or 0),
                    edges=int(edges or 0),
                    faces=int(faces or 0),
                    triangles=int(triangles or 0),
                    selected_verts=int(selected_verts or 0),
                    selected_edges=int(selected_edges or 0),
                    selected_faces=int(selected_faces or 0),
                )
            return None
        except Exception:
            return None

    def _get_inspect_rpc(self, object_name: str) -> Dict[str, Any]:
        """Get object inspection data via RPC."""
        try:
            response = self._rpc_client.send_request(
                "scene.inspect_object",
                {"object_name": object_name}
            )
            # RpcResponse has .status and .result
            if response.status == "ok" and isinstance(response.result, dict):
                return response.result
            return {}
        except Exception:
            return {}

    def _parse_context_response(
        self,
        response: Dict[str, Any],
        object_name: Optional[str] = None,
    ) -> SceneContext:
        """Parse RPC response into SceneContext.

        Args:
            response: RPC response dictionary.
            object_name: Specific object to focus on.

        Returns:
            Parsed SceneContext.
        """
        # Extract basic info
        mode = response.get("mode", "OBJECT")
        active_object = response.get("active_object")
        selected_objects = response.get("selected_objects", [])

        # If specific object requested, try to use it
        if object_name:
            active_object = object_name

        # Parse objects info
        objects = []
        objects_data = response.get("objects", [])
        for obj_data in objects_data:
            if isinstance(obj_data, dict):
                objects.append(ObjectInfo(
                    name=obj_data.get("name", ""),
                    type=obj_data.get("type", "MESH"),
                    location=obj_data.get("location", [0.0, 0.0, 0.0]),
                    dimensions=obj_data.get("dimensions", [1.0, 1.0, 1.0]),
                    selected=obj_data.get("selected", False),
                    active=obj_data.get("active", False),
                ))

        # Parse topology info
        topology = None
        topo_data = response.get("topology")
        if isinstance(topo_data, dict):
            topology = TopologyInfo(
                vertices=topo_data.get("vertices", 0),
                edges=topo_data.get("edges", 0),
                faces=topo_data.get("faces", 0),
                triangles=topo_data.get("triangles", 0),
                selected_verts=topo_data.get("selected_verts", 0),
                selected_edges=topo_data.get("selected_edges", 0),
                selected_faces=topo_data.get("selected_faces", 0),
            )

        # Calculate proportions for active object
        proportions = None
        for obj in objects:
            if obj.active and obj.dimensions:
                proportions = calculate_proportions(obj.dimensions)
                break

        # Parse materials and modifiers
        materials = response.get("materials", [])
        modifiers = response.get("modifiers", [])

        return SceneContext(
            mode=mode,
            active_object=active_object,
            selected_objects=selected_objects,
            objects=objects,
            topology=topology,
            proportions=proportions,
            materials=materials if isinstance(materials, list) else [],
            modifiers=modifiers if isinstance(modifiers, list) else [],
            timestamp=datetime.now(),
        )

    def analyze_from_data(self, data: Dict[str, Any]) -> SceneContext:
        """Build SceneContext from provided data (for testing/offline use).

        Args:
            data: Dictionary with scene data.

        Returns:
            SceneContext built from the data.
        """
        return self._parse_context_response(data)
