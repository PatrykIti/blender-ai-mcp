import bpy


class SceneWorldRenderMixin:
    """World, render, and color-management helpers for scene appearance RPC methods."""

    def inspect_render_settings(self):
        """Returns structured render settings for the active scene."""
        scene = bpy.context.scene
        render = scene.render
        image_settings = getattr(render, "image_settings", None)
        cycles = getattr(scene, "cycles", None)

        return {
            "render_engine": getattr(render, "engine", None),
            "resolution": {
                "x": getattr(render, "resolution_x", None),
                "y": getattr(render, "resolution_y", None),
                "percentage": getattr(render, "resolution_percentage", None),
            },
            "filepath": getattr(render, "filepath", None),
            "use_file_extension": getattr(render, "use_file_extension", None),
            "film_transparent": getattr(render, "film_transparent", None),
            "image_settings": {
                "file_format": getattr(image_settings, "file_format", None),
                "color_mode": getattr(image_settings, "color_mode", None),
                "color_depth": getattr(image_settings, "color_depth", None),
            },
            "cycles": {
                "device": getattr(cycles, "device", None),
                "samples": getattr(cycles, "samples", None),
                "preview_samples": getattr(cycles, "preview_samples", None),
            },
        }

    def inspect_color_management(self):
        """Returns structured color-management settings for the active scene."""
        scene = bpy.context.scene
        display_settings = getattr(scene, "display_settings", None)
        view_settings = getattr(scene, "view_settings", None)
        sequencer_settings = getattr(scene, "sequencer_colorspace_settings", None)

        return {
            "display_device": getattr(display_settings, "display_device", None),
            "view_transform": getattr(view_settings, "view_transform", None),
            "look": getattr(view_settings, "look", None),
            "exposure": getattr(view_settings, "exposure", None),
            "gamma": getattr(view_settings, "gamma", None),
            "use_curve_mapping": getattr(view_settings, "use_curve_mapping", None),
            "sequencer_color_space": getattr(sequencer_settings, "name", None),
        }

    def inspect_world(self):
        """Returns structured world/background settings for the active scene."""
        scene = bpy.context.scene
        world = getattr(scene, "world", None)
        if world is None:
            return {
                "world_name": None,
                "use_nodes": False,
                "color": None,
                "node_tree_name": None,
                "background": None,
                "node_graph_reference": None,
                "node_graph_handoff": self._build_world_node_graph_handoff(
                    world_name=None,
                    node_tree_name=None,
                    use_nodes=False,
                    background=None,
                ),
            }

        background = None
        if getattr(world, "use_nodes", False) and getattr(world, "node_tree", None) is not None:
            background = self._inspect_world_background_node(world.node_tree)

        node_tree_name = getattr(getattr(world, "node_tree", None), "name", None)
        world_name = getattr(world, "name", None)
        use_nodes = getattr(world, "use_nodes", False)

        return {
            "world_name": world_name,
            "use_nodes": use_nodes,
            "color": self._vec_to_list(getattr(world, "color", (0.0, 0.0, 0.0))),
            "node_tree_name": node_tree_name,
            "background": background,
            "node_graph_reference": self._build_world_node_graph_reference(
                world_name=world_name,
                node_tree_name=node_tree_name,
                background=background,
            ),
            "node_graph_handoff": self._build_world_node_graph_handoff(
                world_name=world_name,
                node_tree_name=node_tree_name,
                use_nodes=use_nodes,
                background=background,
            ),
        }

    def configure_render_settings(self, settings):
        """Applies grouped render settings and returns the resulting render snapshot."""
        settings = self._require_mapping(settings, "settings")
        scene = bpy.context.scene
        render = scene.render

        if "render_engine" in settings and settings["render_engine"] is not None:
            render.engine = self._require_string(settings["render_engine"], "render_engine")

        resolution = settings.get("resolution")
        if resolution is not None:
            resolution = self._require_mapping(resolution, "resolution")
            if "x" in resolution and resolution["x"] is not None:
                render.resolution_x = self._require_int(resolution["x"], "resolution.x")
            if "y" in resolution and resolution["y"] is not None:
                render.resolution_y = self._require_int(resolution["y"], "resolution.y")
            if "percentage" in resolution and resolution["percentage"] is not None:
                render.resolution_percentage = self._require_int(resolution["percentage"], "resolution.percentage")

        if "filepath" in settings and settings["filepath"] is not None:
            render.filepath = self._require_string(settings["filepath"], "filepath")
        if "use_file_extension" in settings and settings["use_file_extension"] is not None:
            render.use_file_extension = self._require_bool(settings["use_file_extension"], "use_file_extension")
        if "film_transparent" in settings and settings["film_transparent"] is not None:
            render.film_transparent = self._require_bool(settings["film_transparent"], "film_transparent")

        image_settings = settings.get("image_settings")
        if image_settings is not None:
            image_settings = self._require_mapping(image_settings, "image_settings")
            target = getattr(render, "image_settings", None)
            if target is None:
                raise ValueError("Render image_settings are not available on this scene.")
            if "file_format" in image_settings and image_settings["file_format"] is not None:
                target.file_format = self._require_string(
                    settings["image_settings"]["file_format"], "image_settings.file_format"
                )
            if "color_mode" in image_settings and image_settings["color_mode"] is not None:
                target.color_mode = self._require_string(
                    settings["image_settings"]["color_mode"], "image_settings.color_mode"
                )
            if "color_depth" in image_settings and image_settings["color_depth"] is not None:
                target.color_depth = self._require_string(
                    settings["image_settings"]["color_depth"], "image_settings.color_depth"
                )

        cycles_settings = settings.get("cycles")
        if cycles_settings is not None:
            cycles_settings = self._require_mapping(cycles_settings, "cycles")
            cycles = getattr(scene, "cycles", None)
            if cycles is None:
                raise ValueError("Cycles settings are not available on this scene.")
            if "device" in cycles_settings and cycles_settings["device"] is not None:
                cycles.device = self._require_string(cycles_settings["device"], "cycles.device")
            if "samples" in cycles_settings and cycles_settings["samples"] is not None:
                cycles.samples = self._require_int(cycles_settings["samples"], "cycles.samples")
            if "preview_samples" in cycles_settings and cycles_settings["preview_samples"] is not None:
                cycles.preview_samples = self._require_int(cycles_settings["preview_samples"], "cycles.preview_samples")

        return self.inspect_render_settings()

    def configure_color_management(self, settings):
        """Applies grouped color-management settings and returns the resulting snapshot."""
        settings = self._require_mapping(settings, "settings")
        scene = bpy.context.scene
        display_settings = getattr(scene, "display_settings", None)
        view_settings = getattr(scene, "view_settings", None)
        sequencer_settings = getattr(scene, "sequencer_colorspace_settings", None)

        if "display_device" in settings and settings["display_device"] is not None:
            if display_settings is None:
                raise ValueError("display_settings are not available on this scene.")
            display_settings.display_device = self._require_string(settings["display_device"], "display_device")
        if "view_transform" in settings and settings["view_transform"] is not None:
            if view_settings is None:
                raise ValueError("view_settings are not available on this scene.")
            view_settings.view_transform = self._require_string(settings["view_transform"], "view_transform")
        if "look" in settings and settings["look"] is not None:
            if view_settings is None:
                raise ValueError("view_settings are not available on this scene.")
            view_settings.look = self._require_string(settings["look"], "look")
        if "exposure" in settings and settings["exposure"] is not None:
            if view_settings is None:
                raise ValueError("view_settings are not available on this scene.")
            view_settings.exposure = self._require_float(settings["exposure"], "exposure")
        if "gamma" in settings and settings["gamma"] is not None:
            if view_settings is None:
                raise ValueError("view_settings are not available on this scene.")
            view_settings.gamma = self._require_float(settings["gamma"], "gamma")
        if "use_curve_mapping" in settings and settings["use_curve_mapping"] is not None:
            if view_settings is None:
                raise ValueError("view_settings are not available on this scene.")
            view_settings.use_curve_mapping = self._require_bool(settings["use_curve_mapping"], "use_curve_mapping")
        if "sequencer_color_space" in settings and settings["sequencer_color_space"] is not None:
            if sequencer_settings is None:
                raise ValueError("sequencer_colorspace_settings are not available on this scene.")
            sequencer_settings.name = self._require_string(settings["sequencer_color_space"], "sequencer_color_space")

        return self.inspect_color_management()

    def configure_world(self, settings):
        """Applies grouped world/background settings and returns the resulting world snapshot."""
        settings = self._require_mapping(settings, "settings")
        scene = bpy.context.scene
        self._validate_world_settings_boundary(settings)

        if "world_name" in settings:
            world_name = settings["world_name"]
            if world_name is None:
                scene.world = None
            else:
                name = self._require_string(world_name, "world_name")
                worlds = getattr(bpy.data, "worlds", None)
                resolved_world = worlds.get(name) if worlds is not None else None
                if resolved_world is None:
                    raise ValueError(f"World '{name}' not found")
                scene.world = resolved_world

        world = getattr(scene, "world", None)
        remaining_keys = {key for key in settings if key != "world_name"}
        if world is None:
            if remaining_keys:
                raise ValueError("Scene has no world assigned. Provide 'world_name' before applying world settings.")
            return self.inspect_world()

        use_nodes_requested = None
        if "use_nodes" in settings and settings["use_nodes"] is not None:
            use_nodes_requested = self._require_bool(settings["use_nodes"], "use_nodes")
            world.use_nodes = use_nodes_requested

        if "color" in settings and settings["color"] is not None:
            world.color = self._require_color(settings["color"], "color", allow_alpha=False)

        background = settings.get("background")
        if background is not None:
            background = self._require_mapping(background, "background")
            unknown_background_keys = set(background) - {"color", "strength", "node_name"}
            if unknown_background_keys:
                keys = ", ".join(sorted(unknown_background_keys))
                raise ValueError(
                    f"Unsupported background fields: {keys}. Use future node_graph tooling for arbitrary world nodes."
                )
            if use_nodes_requested is False:
                raise ValueError("background settings require 'use_nodes' to be true.")
            if not getattr(world, "use_nodes", False):
                world.use_nodes = True
            background_node = self._ensure_world_background_node(world)
            if "color" in background and background["color"] is not None:
                color = self._require_color(background["color"], "background.color", allow_alpha=True)
                if len(color) == 3:
                    color = [color[0], color[1], color[2], 1.0]
                self._set_node_input_default(background_node, "Color", color)
            if "strength" in background and background["strength"] is not None:
                self._set_node_input_default(
                    background_node,
                    "Strength",
                    self._require_float(background["strength"], "background.strength"),
                )

        return self.inspect_world()

    def _require_mapping(self, value, field_name):
        if not isinstance(value, dict):
            raise ValueError(f"'{field_name}' must be an object/dict")
        return value

    def _require_string(self, value, field_name):
        if not isinstance(value, str):
            raise ValueError(f"'{field_name}' must be a string")
        return value

    def _require_bool(self, value, field_name):
        if not isinstance(value, bool):
            raise ValueError(f"'{field_name}' must be a boolean")
        return value

    def _require_int(self, value, field_name):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"'{field_name}' must be a number")
        return int(value)

    def _require_float(self, value, field_name):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"'{field_name}' must be a number")
        return float(value)

    def _require_color(self, value, field_name, *, allow_alpha):
        expected_lengths = {3, 4} if allow_alpha else {3}
        if not isinstance(value, (list, tuple)) or len(value) not in expected_lengths:
            lengths = "3 or 4" if allow_alpha else "3"
            raise ValueError(f"'{field_name}' must be a list of {lengths} numeric values")
        return [self._require_float(component, field_name) for component in value]

    def _validate_world_settings_boundary(self, settings):
        """Rejects world payloads that try to cross into full node-graph authorship."""
        bounded_keys = {
            "world_name",
            "use_nodes",
            "color",
            "background",
            "node_tree_name",
            "node_graph_reference",
            "node_graph_handoff",
        }
        graph_keys = {"node_tree", "nodes", "links", "node_graph", "graph"}

        if graph_keys & set(settings):
            keys = ", ".join(sorted(graph_keys & set(settings)))
            raise ValueError(
                f"Unsupported world node-graph fields: {keys}. Use future node_graph tooling for graph rebuilds."
            )

        unknown_keys = set(settings) - bounded_keys
        if unknown_keys:
            keys = ", ".join(sorted(unknown_keys))
            raise ValueError(
                f"Unsupported world settings: {keys}. Allowed keys: world_name, use_nodes, color, background."
            )

    def _build_world_node_graph_reference(self, *, world_name, node_tree_name, background):
        if node_tree_name is None:
            return None
        reference = {
            "graph_type": "world",
            "owner_name": world_name,
            "node_tree_name": node_tree_name,
        }
        if background is not None:
            reference["background_node_name"] = background.get("node_name")
        return reference

    def _build_world_node_graph_handoff(self, *, world_name, node_tree_name, use_nodes, background):
        required = bool(use_nodes and node_tree_name)
        payload = {
            "required": required,
            "target_tool_family": "node_graph",
            "reason": "world_uses_nodes" if required else None,
            "world_name": world_name,
            "node_tree_name": node_tree_name,
            "supported_scene_configure_fields": [
                "world_name",
                "use_nodes",
                "color",
                "background.color",
                "background.strength",
            ],
            "unsupported_scope": (
                [
                    "arbitrary_world_nodes",
                    "custom_links",
                    "full_node_topology_rebuild",
                ]
                if required
                else []
            ),
        }
        if background is not None:
            payload["background_node_name"] = background.get("node_name")
        return payload

    def _ensure_world_background_node(self, world):
        """Returns a world Background node and creates a minimal one when absent."""
        node_tree = getattr(world, "node_tree", None)
        if node_tree is None:
            raise ValueError("World node tree is not available.")

        background_node = None
        output_node = None
        for node in getattr(node_tree, "nodes", []) or []:
            node_type = getattr(node, "type", None)
            node_idname = getattr(node, "bl_idname", None)
            if background_node is None and (node_type == "BACKGROUND" or node_idname == "ShaderNodeBackground"):
                background_node = node
            if output_node is None and (node_type == "OUTPUT_WORLD" or node_idname == "ShaderNodeOutputWorld"):
                output_node = node

        if background_node is None and hasattr(node_tree.nodes, "new"):
            background_node = node_tree.nodes.new("ShaderNodeBackground")
        if output_node is None and hasattr(node_tree.nodes, "new"):
            output_node = node_tree.nodes.new("ShaderNodeOutputWorld")

        if background_node is None:
            raise ValueError("World background node is not available.")

        if output_node is not None and hasattr(node_tree, "links") and hasattr(node_tree.links, "new"):
            try:
                node_tree.links.new(background_node.outputs["Background"], output_node.inputs["Surface"])
            except Exception:
                pass

        return background_node

    def _inspect_world_background_node(self, node_tree):
        """Extracts a compact summary of the first world background node when present."""
        for node in getattr(node_tree, "nodes", []) or []:
            node_type = getattr(node, "type", None)
            node_idname = getattr(node, "bl_idname", None)
            if node_type != "BACKGROUND" and node_idname != "ShaderNodeBackground":
                continue

            color_input = self._get_node_input_default(node, "Color")
            strength_input = self._get_node_input_default(node, "Strength")
            return {
                "node_name": getattr(node, "name", None),
                "color": self._vec_to_list(color_input) if color_input is not None else None,
                "strength": round(float(strength_input), 6)
                if isinstance(strength_input, (int, float))
                else strength_input,
            }
        return None

    def _get_node_input_default(self, node, input_name):
        """Returns a node input default value by socket name when available."""
        for socket in getattr(node, "inputs", []) or []:
            if getattr(socket, "name", None) == input_name:
                return getattr(socket, "default_value", None)
        return None

    def _set_node_input_default(self, node, input_name, value):
        """Sets a node input default value by socket name when available."""
        for socket in getattr(node, "inputs", []) or []:
            if getattr(socket, "name", None) == input_name:
                socket.default_value = value
                return
        raise ValueError(f"World background node is missing '{input_name}' input.")
