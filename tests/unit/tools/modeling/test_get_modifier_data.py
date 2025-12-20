import sys
from unittest.mock import MagicMock

from blender_addon.application.handlers.modeling import ModelingHandler


class TestModelingGetModifierData:
    def setup_method(self):
        self.mock_bpy = sys.modules["bpy"]
        self.handler = ModelingHandler()

    def test_get_modifier_data_with_object_ref(self):
        obj = MagicMock()
        obj.name = "Cube"

        target = MagicMock()
        target.name = "Empty"

        prop_object = MagicMock()
        prop_object.identifier = "object"
        prop_object.type = "POINTER"

        prop_width = MagicMock()
        prop_width.identifier = "width"
        prop_width.type = "FLOAT"

        prop_rna = MagicMock()
        prop_rna.identifier = "rna_type"
        prop_rna.type = "POINTER"

        mod = MagicMock()
        mod.name = "Bevel"
        mod.type = "BEVEL"
        mod.object = target
        mod.width = 0.2
        mod.bl_rna.properties = [prop_object, prop_width, prop_rna]

        obj.modifiers = [mod]
        self.mock_bpy.data.objects = {"Cube": obj}

        result = self.handler.get_modifier_data("Cube")

        assert result["modifier_count"] == 1
        entry = result["modifiers"][0]
        assert entry["name"] == "Bevel"
        assert entry["properties"]["object"] == "Empty"
        assert entry["properties"]["width"] == 0.2
        assert entry["object_refs"] == [{"property": "object", "object_name": "Empty"}]

    def test_get_modifier_data_includes_node_tree(self):
        obj = MagicMock()
        obj.name = "Cube"

        prop_enabled = MagicMock()
        prop_enabled.identifier = "show_viewport"
        prop_enabled.type = "BOOLEAN"

        mod = MagicMock()
        mod.name = "GeometryNodes"
        mod.type = "NODES"
        mod.show_viewport = True
        mod.bl_rna.properties = [prop_enabled]

        node_group = MagicMock()
        node_group.name = "GN_Shell"
        node_group.library = None

        input_socket = MagicMock()
        input_socket.name = "Bevel"
        input_socket.identifier = "Input_2"
        input_socket.bl_socket_idname = "NodeSocketFloat"
        input_socket.default_value = 0.002
        input_socket.min_value = 0.0
        input_socket.max_value = 0.1
        input_socket.subtype = "DISTANCE"

        output_socket = MagicMock()
        output_socket.name = "Geometry"
        output_socket.identifier = "Output_1"
        output_socket.bl_socket_idname = "NodeSocketGeometry"

        node_group.inputs = [input_socket]
        node_group.outputs = [output_socket]
        mod.node_group = node_group

        obj.modifiers = [mod]
        self.mock_bpy.data.objects = {"Cube": obj}

        result = self.handler.get_modifier_data("Cube", include_node_tree=True)

        entry = result["modifiers"][0]
        assert entry["node_tree"]["name"] == "GN_Shell"
        assert entry["node_tree"]["inputs"][0]["name"] == "Bevel"
        assert entry["node_tree"]["outputs"][0]["name"] == "Geometry"

