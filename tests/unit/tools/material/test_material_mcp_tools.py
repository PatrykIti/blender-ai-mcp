from __future__ import annotations

from unittest.mock import MagicMock


def test_material_list_formats_material_summary(monkeypatch):
    from server.adapters.mcp.areas.material import material_list

    handler = MagicMock()
    handler.list_materials.return_value = [
        {
            "name": "Hero",
            "use_nodes": True,
            "assigned_object_count": 2,
            "base_color": [1.0, 0.0, 0.0, 1.0],
            "roughness": 0.25,
            "metallic": 0.5,
        }
    ]

    monkeypatch.setattr("server.adapters.mcp.areas.material.get_material_handler", lambda: handler)
    monkeypatch.setattr("server.adapters.mcp.areas.material.ctx_info", lambda ctx, message: None)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.material.route_tool_call",
        lambda **kwargs: kwargs["direct_executor"](),
    )

    result = material_list(MagicMock())

    assert "Materials (1):" in result
    assert "Hero" in result
    assert "Roughness: 0.25" in result


def test_material_list_by_object_formats_slots(monkeypatch):
    from server.adapters.mcp.areas.material import material_list_by_object

    handler = MagicMock()
    handler.list_by_object.return_value = {
        "slot_count": 1,
        "slots": [
            {
                "slot_index": 0,
                "slot_name": "Slot 0",
                "material_name": "Hero",
                "uses_nodes": True,
            }
        ],
    }

    monkeypatch.setattr("server.adapters.mcp.areas.material.get_material_handler", lambda: handler)
    monkeypatch.setattr("server.adapters.mcp.areas.material.ctx_info", lambda ctx, message: None)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.material.route_tool_call",
        lambda **kwargs: kwargs["direct_executor"](),
    )

    result = material_list_by_object(MagicMock(), object_name="Cube")

    assert "Material Slots (1):" in result
    assert "[0] Slot 0: Hero [nodes]" in result


def test_material_assign_reports_missing_material(monkeypatch):
    from server.adapters.mcp.areas.material import material_assign

    handler = MagicMock()
    handler.assign_material.side_effect = RuntimeError("Material 'Ghost' not found")

    monkeypatch.setattr("server.adapters.mcp.areas.material.get_material_handler", lambda: handler)
    monkeypatch.setattr("server.adapters.mcp.areas.material.ctx_info", lambda ctx, message: None)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.material.route_tool_call",
        lambda **kwargs: kwargs["direct_executor"](),
    )

    result = material_assign(MagicMock(), material_name="Ghost", object_name="Cube")

    assert "Use material_list to verify the material name" in result
