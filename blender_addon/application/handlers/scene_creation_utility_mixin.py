import bpy


class SceneCreationUtilityMixin:
    """Creation helpers for scene utility RPC methods."""

    def create_light(self, type="POINT", energy=1000.0, color=(1.0, 1.0, 1.0), location=(0.0, 0.0, 0.0), name=None):
        """Creates a light source."""
        light_data = bpy.data.lights.new(name=name if name else "Light", type=type)
        light_data.energy = energy
        light_data.color = color

        light_obj = bpy.data.objects.new(name=name if name else "Light", object_data=light_data)
        light_obj.location = location
        bpy.context.collection.objects.link(light_obj)
        return light_obj.name

    def create_camera(
        self,
        location=(0.0, -10.0, 0.0),
        rotation=(1.57, 0.0, 0.0),
        lens=50.0,
        clip_start=0.1,
        clip_end=100.0,
        name=None,
    ):
        """Creates a camera."""
        cam_data = bpy.data.cameras.new(name=name if name else "Camera")
        cam_data.lens = lens
        if clip_start is not None:
            cam_data.clip_start = clip_start
        if clip_end is not None:
            cam_data.clip_end = clip_end

        cam_obj = bpy.data.objects.new(name=name if name else "Camera", object_data=cam_data)
        cam_obj.location = location
        cam_obj.rotation_euler = rotation
        bpy.context.collection.objects.link(cam_obj)
        return cam_obj.name

    def create_empty(self, type="PLAIN_AXES", size=1.0, location=(0.0, 0.0, 0.0), name=None):
        """Creates an empty object."""
        empty_obj = bpy.data.objects.new(name if name else "Empty", None)
        empty_obj.empty_display_type = type
        empty_obj.empty_display_size = size
        empty_obj.location = location
        bpy.context.collection.objects.link(empty_obj)
        return empty_obj.name
