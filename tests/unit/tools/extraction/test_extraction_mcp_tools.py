from __future__ import annotations

import asyncio
from unittest.mock import MagicMock


def test_extraction_deep_topology_formats_json(monkeypatch):
    from server.adapters.mcp.areas.extraction import extraction_deep_topology

    handler = MagicMock()
    handler.deep_topology.return_value = {"base_primitive": "CUBE", "edge_loops": 4}

    monkeypatch.setattr("server.adapters.mcp.areas.extraction.get_extraction_handler", lambda: handler)
    monkeypatch.setattr("server.adapters.mcp.areas.extraction.ctx_info", lambda ctx, message: None)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.extraction.route_tool_call",
        lambda **kwargs: kwargs["direct_executor"](),
    )

    result = extraction_deep_topology(MagicMock(), object_name="Cube")

    assert '"base_primitive": "CUBE"' in result
    assert '"edge_loops": 4' in result


def test_extraction_detect_symmetry_mentions_axes(monkeypatch):
    from server.adapters.mcp.areas.extraction import extraction_detect_symmetry

    handler = MagicMock()
    handler.detect_symmetry.return_value = {"x_symmetric": True, "y_symmetric": False, "z_symmetric": True}

    monkeypatch.setattr("server.adapters.mcp.areas.extraction.get_extraction_handler", lambda: handler)
    monkeypatch.setattr("server.adapters.mcp.areas.extraction.ctx_info", lambda ctx, message: None)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.extraction.route_tool_call",
        lambda **kwargs: kwargs["direct_executor"](),
    )

    result = extraction_detect_symmetry(MagicMock(), object_name="Cube")

    assert '"x_symmetric": true' in result
    assert '"z_symmetric": true' in result


def test_extraction_render_angles_direct_path_formats_render_output(monkeypatch):
    from server.adapters.mcp.areas.extraction import extraction_render_angles

    handler = MagicMock()
    handler.render_angles.return_value = {
        "renders": [{"angle": "front", "path": "/tmp/front.png"}],
        "object_name": "Cube",
    }

    monkeypatch.setattr("server.adapters.mcp.areas.extraction.get_extraction_handler", lambda: handler)
    monkeypatch.setattr("server.adapters.mcp.areas.extraction.ctx_info", lambda ctx, message: None)
    monkeypatch.setattr("server.adapters.mcp.areas.extraction.is_background_task_context", lambda ctx: False)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.extraction.route_tool_call",
        lambda **kwargs: kwargs["direct_executor"](),
    )

    result = asyncio.run(extraction_render_angles(MagicMock(), object_name="Cube"))

    assert '"angle": "front"' in result
    assert '"path": "/tmp/front.png"' in result
