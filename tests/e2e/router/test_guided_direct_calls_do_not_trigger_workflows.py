"""E2E router regressions for direct guided calls under manual/no-match goals."""

from __future__ import annotations

from server.application.tool_handlers.router_handler import RouterToolHandler


def _set_guided_manual_creature_goal(router) -> None:
    handler = RouterToolHandler(router=router, enabled=True)
    result = handler.set_goal("create a low-poly squirrel matching front and side reference images")
    assert result["status"] == "no_match"
    assert result["continuation_mode"] == "guided_manual_build"
    assert router.get_pending_workflow() is None


def test_guided_manual_direct_create_primitive_does_not_trigger_workflow(router, clean_scene):
    _set_guided_manual_creature_goal(router)

    corrected = router.process_llm_tool_call(
        "modeling_create_primitive",
        {"primitive_type": "Sphere", "radius": 0.12, "location": [0.0, 0.0, 0.2], "name": "Acorn"},
    )

    assert corrected == [
        {
            "tool": "modeling_create_primitive",
            "params": {"primitive_type": "Sphere", "radius": 0.12, "location": [0.0, 0.0, 0.2], "name": "Acorn"},
        }
    ]


def test_guided_manual_collection_manage_does_not_trigger_workflow(router, clean_scene):
    _set_guided_manual_creature_goal(router)

    corrected = router.process_llm_tool_call(
        "collection_manage",
        {"action": "create", "collection_name": "Squirrel"},
    )

    assert corrected == [
        {
            "tool": "collection_manage",
            "params": {"action": "create", "collection_name": "Squirrel"},
        }
    ]


def test_guided_manual_mesh_dissolve_does_not_trigger_workflow(router, rpc_client, clean_scene):
    _set_guided_manual_creature_goal(router)

    rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE", "name": "BlockoutCube"})
    rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
    rpc_client.send_request("mesh.select", {"action": "all"})

    corrected = router.process_llm_tool_call(
        "mesh_dissolve",
        {"dissolve_type": "limited", "angle_limit": 30.0},
    )

    assert corrected == [
        {
            "tool": "mesh_dissolve",
            "params": {"dissolve_type": "limited", "angle_limit": 30.0},
        }
    ]
