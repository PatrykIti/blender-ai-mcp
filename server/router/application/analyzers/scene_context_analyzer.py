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
            # If specific object requested and matches cache, return cache
            if object_name is None or object_name == cached.active_object:
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
            response = self._rpc_client.send_request("scene.context", {"action": "mode"})
            if isinstance(response, dict):
                return response.get("mode", "OBJECT")
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
            response = self._rpc_client.send_request("scene.context", {"action": "selection"})
            if isinstance(response, dict):
                selection = response.get("selection", {})
                if isinstance(selection, dict):
                    return bool(selection.get("has_selection", False))
            return False
        except Exception:
            return False

    def _build_context(self, object_name: Optional[str] = None) -> SceneContext:
        """Build scene context from RPC calls.

        Args:
            object_name: Specific object to focus on.

        Returns:
            SceneContext with current scene state.
        """
        if self._rpc_client is None:
            return SceneContext.empty()

        try:
            # Get full context via scene_context tool
            response = self._rpc_client.send_request("scene.context", {"action": "full"})

            if not isinstance(response, dict):
                return SceneContext.empty()

            return self._parse_context_response(response, object_name)

        except Exception:
            return SceneContext.empty()

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
