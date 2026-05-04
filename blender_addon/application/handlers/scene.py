from .scene_creation_utility_mixin import SceneCreationUtilityMixin
from .scene_custom_property_utility_mixin import SceneCustomPropertyUtilityMixin
from .scene_inspection_mixin import SceneInspectionMixin
from .scene_lifecycle_context_mixin import SceneLifecycleContextMixin
from .scene_measure_assert_mixin import SceneMeasureAssertMixin
from .scene_mode_visibility_utility_mixin import SceneModeVisibilityUtilityMixin
from .scene_structural_read_mixin import SceneStructuralReadMixin
from .scene_viewport_mixin import SceneViewportMixin
from .scene_world_render_mixin import SceneWorldRenderMixin


class SceneHandler(
    SceneLifecycleContextMixin,
    SceneCreationUtilityMixin,
    SceneModeVisibilityUtilityMixin,
    SceneCustomPropertyUtilityMixin,
    SceneStructuralReadMixin,
    SceneInspectionMixin,
    SceneMeasureAssertMixin,
    SceneViewportMixin,
    SceneWorldRenderMixin,
):
    """Application service for scene operations."""
