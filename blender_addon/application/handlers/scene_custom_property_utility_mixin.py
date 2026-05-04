import bpy


class SceneCustomPropertyUtilityMixin:
    """Custom-property helpers for scene utility RPC methods."""

    def get_custom_properties(self, object_name):
        """Gets custom properties (metadata) from an object."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object '{object_name}' not found")

        properties = {}
        try:
            for key in obj.keys():
                if key.startswith("_"):
                    continue
                value = obj.get(key)
                if isinstance(value, (int, float, str, bool)):
                    properties[key] = value
                elif hasattr(value, "__iter__") and not isinstance(value, str):
                    try:
                        properties[key] = list(value)
                    except Exception:
                        properties[key] = str(value)
                else:
                    properties[key] = str(value)
        except Exception as exc:
            raise ValueError(f"Failed to read custom properties: {exc}")

        return {"object_name": object_name, "property_count": len(properties), "properties": properties}

    def set_custom_property(self, object_name, property_name, property_value, delete=False):
        """Sets or deletes a custom property on an object."""
        obj = bpy.data.objects.get(object_name)
        if obj is None:
            raise ValueError(f"Object '{object_name}' not found")

        if delete:
            if property_name in obj.keys():
                del obj[property_name]
                return f"Deleted property '{property_name}' from '{object_name}'"
            return f"Property '{property_name}' not found on '{object_name}'"

        obj[property_name] = property_value
        return f"Set property '{property_name}' = {property_value} on '{object_name}'"
