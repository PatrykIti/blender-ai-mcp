import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

from blender_addon.application.handlers.scene import SceneHandler


def _make_socket(name, default_value=None):
    socket = MagicMock()
    socket.name = name
    socket.default_value = default_value
    return socket


def test_configure_render_settings_applies_nested_render_payload():
    bpy = sys.modules["bpy"]

    image_settings = SimpleNamespace(file_format="PNG", color_mode="RGBA", color_depth="8")
    render = SimpleNamespace(
        engine="BLENDER_EEVEE_NEXT",
        resolution_x=1920,
        resolution_y=1080,
        resolution_percentage=100,
        filepath="/tmp/original.png",
        use_file_extension=True,
        film_transparent=False,
        image_settings=image_settings,
    )
    cycles = SimpleNamespace(device="CPU", samples=64, preview_samples=16)
    bpy.context.scene = SimpleNamespace(render=render, cycles=cycles)

    handler = SceneHandler()
    result = handler.configure_render_settings(
        {
            "render_engine": "CYCLES",
            "resolution": {"x": 1280, "y": 720, "percentage": 50},
            "filepath": "/tmp/final.exr",
            "use_file_extension": False,
            "film_transparent": True,
            "image_settings": {"file_format": "OPEN_EXR", "color_mode": "RGB", "color_depth": "16"},
            "cycles": {"device": "GPU", "samples": 256, "preview_samples": 32},
        }
    )

    assert render.engine == "CYCLES"
    assert render.resolution_x == 1280
    assert render.resolution_y == 720
    assert render.resolution_percentage == 50
    assert render.filepath == "/tmp/final.exr"
    assert render.use_file_extension is False
    assert render.film_transparent is True
    assert image_settings.file_format == "OPEN_EXR"
    assert cycles.samples == 256
    assert result["render_engine"] == "CYCLES"
    assert result["cycles"]["device"] == "GPU"


def test_configure_color_management_applies_grouped_payload():
    bpy = sys.modules["bpy"]

    display_settings = SimpleNamespace(display_device="sRGB")
    view_settings = SimpleNamespace(
        view_transform="Standard",
        look="None",
        exposure=0.0,
        gamma=1.0,
        use_curve_mapping=False,
    )
    sequencer_settings = SimpleNamespace(name="sRGB")
    bpy.context.scene = SimpleNamespace(
        display_settings=display_settings,
        view_settings=view_settings,
        sequencer_colorspace_settings=sequencer_settings,
    )

    handler = SceneHandler()
    result = handler.configure_color_management(
        {
            "display_device": "Display P3",
            "view_transform": "AgX",
            "look": "Medium High Contrast",
            "exposure": 1.25,
            "gamma": 0.95,
            "use_curve_mapping": True,
            "sequencer_color_space": "ACEScg",
        }
    )

    assert display_settings.display_device == "Display P3"
    assert view_settings.view_transform == "AgX"
    assert view_settings.look == "Medium High Contrast"
    assert view_settings.exposure == 1.25
    assert view_settings.gamma == 0.95
    assert view_settings.use_curve_mapping is True
    assert sequencer_settings.name == "ACEScg"
    assert result["view_transform"] == "AgX"
    assert result["sequencer_color_space"] == "ACEScg"


def test_configure_world_assigns_world_and_updates_background_node():
    bpy = sys.modules["bpy"]

    background_color = _make_socket("Color", [0.0, 0.0, 0.0, 1.0])
    background_strength = _make_socket("Strength", 1.0)
    background_node = SimpleNamespace(
        type="BACKGROUND",
        bl_idname="ShaderNodeBackground",
        name="Background",
        inputs=[background_color, background_strength],
    )
    world = SimpleNamespace(
        name="Studio",
        use_nodes=True,
        color=[0.0, 0.0, 0.0],
        node_tree=SimpleNamespace(nodes=[background_node], links=MagicMock()),
    )
    bpy.data.worlds = {"Studio": world}
    bpy.context.scene = SimpleNamespace(world=None)

    handler = SceneHandler()
    result = handler.configure_world(
        {
            "world_name": "Studio",
            "color": [0.1, 0.2, 0.3],
            "background": {"color": [0.4, 0.5, 0.6], "strength": 0.75, "node_name": "Background"},
        }
    )

    assert bpy.context.scene.world is world
    assert world.color == [0.1, 0.2, 0.3]
    assert background_color.default_value == [0.4, 0.5, 0.6, 1.0]
    assert background_strength.default_value == 0.75
    assert result["world_name"] == "Studio"
    assert result["background"]["strength"] == 0.75
    assert result["node_graph_reference"] is None
    assert result["node_graph_handoff"]["required"] is False


def test_configure_world_rejects_background_when_use_nodes_is_false():
    bpy = sys.modules["bpy"]

    world = SimpleNamespace(name="Studio", use_nodes=False, color=[0.0, 0.0, 0.0], node_tree=SimpleNamespace(nodes=[]))
    bpy.context.scene = SimpleNamespace(world=world)

    handler = SceneHandler()

    try:
        handler.configure_world({"use_nodes": False, "background": {"strength": 0.5}})
    except ValueError as exc:
        assert "use_nodes" in str(exc)
    else:
        raise AssertionError("Expected configure_world to reject background settings when use_nodes=False")


def test_inspect_world_exposes_node_graph_handoff_for_node_based_worlds():
    bpy = sys.modules["bpy"]

    background_color = _make_socket("Color", [0.0, 0.0, 0.0, 1.0])
    background_strength = _make_socket("Strength", 1.0)
    background_node = SimpleNamespace(
        type="BACKGROUND",
        bl_idname="ShaderNodeBackground",
        name="Background",
        inputs=[background_color, background_strength],
    )
    world = SimpleNamespace(
        name="Studio",
        use_nodes=True,
        color=[0.0, 0.0, 0.0],
        node_tree=SimpleNamespace(name="World Nodetree", nodes=[background_node]),
    )
    bpy.context.scene = SimpleNamespace(world=world)

    handler = SceneHandler()
    result = handler.inspect_world()

    assert result["node_graph_reference"]["graph_type"] == "world"
    assert result["node_graph_reference"]["node_tree_name"] == "World Nodetree"
    assert result["node_graph_handoff"]["required"] is True
    assert "full_node_topology_rebuild" in result["node_graph_handoff"]["unsupported_scope"]


def test_configure_world_rejects_explicit_node_graph_payload():
    bpy = sys.modules["bpy"]
    bpy.context.scene = SimpleNamespace(world=SimpleNamespace(name="Studio", use_nodes=False, color=[0.0, 0.0, 0.0]))

    handler = SceneHandler()

    try:
        handler.configure_world({"node_graph": {"nodes": []}})
    except ValueError as exc:
        assert "node_graph" in str(exc)
    else:
        raise AssertionError("Expected configure_world to reject explicit node_graph payloads")
