from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest
from server.adapters.mcp.execution_context import MCPExecutionContext
from server.adapters.mcp.execution_report import ExecutionStep, MCPExecutionReport
from server.adapters.mcp.session_capabilities import SessionCapabilityState
from server.adapters.mcp.session_phase import SessionPhase


def _direct_route(tool_name, params, direct_executor, prompt=None):
    return direct_executor()


def test_armature_create_main_path_delegates_to_handler(monkeypatch):
    calls = {}

    class Handler:
        def create(self, **kwargs):
            calls["kwargs"] = kwargs
            return "Created armature 'Rig'"

    monkeypatch.setattr("server.adapters.mcp.areas.armature.get_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.armature.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.armature import armature_create

    result = armature_create(MagicMock(), name="Rig", location=[1, 2, 3], bone_name="Root", bone_length=2.0)

    assert result == "Created armature 'Rig'"
    assert calls["kwargs"] == {
        "name": "Rig",
        "location": [1, 2, 3],
        "bone_name": "Root",
        "bone_length": 2.0,
    }


def test_bake_normal_map_main_path_delegates_to_handler(monkeypatch):
    calls = {}

    class Handler:
        def bake_normal_map(self, **kwargs):
            calls["kwargs"] = kwargs
            return "Baked normal map"

    monkeypatch.setattr("server.adapters.mcp.areas.baking.get_baking_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.baking.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.baking import bake_normal_map

    result = bake_normal_map(MagicMock(), object_name="LowPoly", output_path="/tmp/normal.png", resolution=2048)

    assert result == "Baked normal map"
    assert calls["kwargs"]["object_name"] == "LowPoly"
    assert calls["kwargs"]["resolution"] == 2048


def test_curve_create_main_path_delegates_to_handler(monkeypatch):
    calls = {}

    class Handler:
        def create_curve(self, curve_type, location):
            calls["args"] = (curve_type, location)
            return "Created BEZIER curve"

    monkeypatch.setattr("server.adapters.mcp.areas.curve.get_curve_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.curve.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.curve import curve_create

    result = curve_create(MagicMock(), curve_type="BEZIER", location=[0, 1, 2])

    assert result == "Created BEZIER curve"
    assert calls["args"] == ("BEZIER", [0, 1, 2])


def test_lattice_create_parses_string_location_and_delegates(monkeypatch):
    calls = {}

    class Handler:
        def lattice_create(self, **kwargs):
            calls["kwargs"] = kwargs
            return "Created lattice"

    monkeypatch.setattr("server.adapters.mcp.areas.lattice.get_lattice_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.lattice.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.lattice import lattice_create

    result = lattice_create(MagicMock(), name="Cage", location="[1, 2, 3]", points_w=4)

    assert result == "Created lattice"
    assert calls["kwargs"]["location"] == [1.0, 2.0, 3.0]
    assert calls["kwargs"]["points_w"] == 4


def test_modeling_create_primitive_parses_string_vectors_and_delegates(monkeypatch):
    calls = {}

    class Handler:
        def create_primitive(self, primitive_type, radius, size, location, rotation, name):
            calls["args"] = (primitive_type, radius, size, location, rotation, name)
            return "Created Cube named 'Block'"

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_modeling_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.modeling.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.modeling import modeling_create_primitive

    result = modeling_create_primitive(
        MagicMock(),
        primitive_type="Cube",
        location="[1, 2, 3]",
        rotation="[0, 0, 1.57]",
        name="Block",
    )

    assert result == "Created Cube named 'Block'"
    assert calls["args"] == ("Cube", 1.0, 2.0, [1.0, 2.0, 3.0], [0.0, 0.0, 1.57], "Block")


def test_modeling_create_primitive_registers_guided_role_with_actual_created_name(monkeypatch):
    recorded: list[tuple[str, str, str | None]] = []

    class Handler:
        def create_primitive(self, primitive_type, radius, size, location, rotation, name):
            return "Created Monkey named 'Head.001'"

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_modeling_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.modeling.route_tool_call", _direct_route)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state",
        lambda ctx: SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={"flow_id": "guided_creature_flow"},
        ),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role",
        lambda ctx, **kwargs: recorded.append((kwargs["object_name"], kwargs["role"], kwargs.get("role_group"))),
    )

    from server.adapters.mcp.areas.modeling import modeling_create_primitive

    result = modeling_create_primitive(
        MagicMock(),
        primitive_type="Monkey",
        name="Head",
        guided_role="head_mass",
    )

    assert result == "Created Monkey named 'Head.001'"
    assert recorded == [("Head.001", "head_mass", None)]


def test_modeling_create_primitive_registers_guided_role_with_apostrophe_name(monkeypatch):
    recorded: list[tuple[str, str, str | None]] = []

    class Handler:
        def create_primitive(self, primitive_type, radius, size, location, rotation, name):
            return "Created Cube named 'King's Crown'"

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_modeling_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.modeling.route_tool_call", _direct_route)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state",
        lambda ctx: SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={"flow_id": "guided_creature_flow"},
        ),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role",
        lambda ctx, **kwargs: recorded.append((kwargs["object_name"], kwargs["role"], kwargs.get("role_group"))),
    )

    from server.adapters.mcp.areas.modeling import modeling_create_primitive

    result = modeling_create_primitive(
        MagicMock(),
        primitive_type="Cube",
        name="King's Crown",
        guided_role="detail_part",
    )

    assert result == "Created Cube named 'King's Crown'"
    assert recorded == [("King's Crown", "detail_part", None)]


def test_modeling_create_primitive_registers_guided_role_after_multi_step_report(monkeypatch):
    recorded: list[tuple[str, str, str | None]] = []

    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.route_tool_call",
        lambda **kwargs: "[Step 1: scene_set_mode] OK\n[Step 2: modeling_create_primitive] Created Sphere named 'Body'",
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state",
        lambda ctx: SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={"flow_id": "guided_creature_flow"},
        ),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role",
        lambda ctx, **kwargs: recorded.append((kwargs["object_name"], kwargs["role"], kwargs.get("role_group"))),
    )

    from server.adapters.mcp.areas.modeling import modeling_create_primitive

    result = modeling_create_primitive(
        MagicMock(),
        primitive_type="Sphere",
        name="Body",
        guided_role="body_core",
    )

    assert result == "[Step 1: scene_set_mode] OK\n[Step 2: modeling_create_primitive] Created Sphere named 'Body'"
    assert recorded == [("Body", "body_core", None)]


def test_modeling_create_primitive_does_not_register_guided_role_after_failed_string_result(monkeypatch):
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.route_tool_call",
        lambda **kwargs: "Object 'Body' not found",
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state",
        lambda ctx: SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={"flow_id": "guided_creature_flow"},
        ),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role",
        lambda ctx, **kwargs: (_ for _ in ()).throw(AssertionError("guided role should not be registered")),
    )

    from server.adapters.mcp.areas.modeling import modeling_create_primitive

    result = modeling_create_primitive(
        MagicMock(),
        primitive_type="Sphere",
        name="Body",
        guided_role="body_core",
    )

    assert result == "Object 'Body' not found"


def test_modeling_create_primitive_skips_guided_registration_without_active_flow(monkeypatch):
    class Handler:
        def create_primitive(self, primitive_type, radius, size, location, rotation, name):
            return "Created Cube named 'Cube.001'"

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_modeling_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.modeling.route_tool_call", _direct_route)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state",
        lambda ctx: SessionCapabilityState(phase=SessionPhase.BOOTSTRAP, guided_flow_state=None),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role",
        lambda ctx, **kwargs: (_ for _ in ()).throw(AssertionError("guided role should not be registered")),
    )

    from server.adapters.mcp.areas.modeling import modeling_create_primitive

    result = modeling_create_primitive(
        MagicMock(),
        primitive_type="Cube",
        guided_role="body_core",
    )

    assert result == "Created Cube named 'Cube.001'"


def test_modeling_create_primitive_requires_explicit_name_for_guided_role_in_active_flow(monkeypatch):
    class Handler:
        def create_primitive(self, primitive_type, radius, size, location, rotation, name):
            raise AssertionError("Handler should not run when guided create lacks an explicit semantic name")

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_modeling_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.modeling.route_tool_call", _direct_route)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state",
        lambda ctx: SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={
                "flow_id": "guided_creature_flow",
                "domain_profile": "creature",
                "current_step": "create_primary_masses",
            },
        ),
    )

    from server.adapters.mcp.areas.modeling import modeling_create_primitive

    with pytest.raises(ValueError, match="requires an explicit semantic `name`"):
        modeling_create_primitive(
            MagicMock(),
            primitive_type="Sphere",
            guided_role="body_core",
        )


def test_modeling_transform_object_skips_guided_registration_without_active_flow(monkeypatch):
    class Handler:
        def transform_object(self, name, location=None, rotation=None, scale=None):
            return f"Transformed object '{name}'"

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.get_modeling_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.modeling.route_tool_call", _direct_route)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state",
        lambda ctx: SessionCapabilityState(phase=SessionPhase.BOOTSTRAP, guided_flow_state=None),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role",
        lambda ctx, **kwargs: (_ for _ in ()).throw(AssertionError("guided role should not be registered")),
    )

    from server.adapters.mcp.areas.modeling import modeling_transform_object

    result = modeling_transform_object(
        MagicMock(),
        name="Cube.001",
        location=[1, 2, 3],
        guided_role="body_core",
    )

    assert result == "Transformed object 'Cube.001'"


def test_modeling_transform_object_registers_guided_role_after_multi_step_report(monkeypatch):
    recorded: list[tuple[str, str, str | None]] = []

    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.route_tool_call",
        lambda **kwargs: "[Step 1: scene_set_mode] OK\n[Step 2: modeling_transform_object] Transformed object 'Body'",
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state",
        lambda ctx: SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={"flow_id": "guided_creature_flow"},
        ),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role",
        lambda ctx, **kwargs: recorded.append((kwargs["object_name"], kwargs["role"], kwargs.get("role_group"))),
    )

    from server.adapters.mcp.areas.modeling import modeling_transform_object

    result = modeling_transform_object(
        MagicMock(),
        name="Body",
        scale=[1.0, 1.0, 1.0],
        guided_role="body_core",
    )

    assert result == "[Step 1: scene_set_mode] OK\n[Step 2: modeling_transform_object] Transformed object 'Body'"
    assert recorded == [("Body", "body_core", None)]


def test_modeling_transform_object_registers_guided_role_with_apostrophe_name(monkeypatch):
    recorded: list[tuple[str, str, str | None]] = []

    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.route_tool_call",
        lambda **kwargs: (
            "[Step 1: scene_set_mode] OK\n[Step 2: modeling_transform_object] Transformed object 'King's Crown'"
        ),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state",
        lambda ctx: SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={"flow_id": "guided_creature_flow"},
        ),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role",
        lambda ctx, **kwargs: recorded.append((kwargs["object_name"], kwargs["role"], kwargs.get("role_group"))),
    )

    from server.adapters.mcp.areas.modeling import modeling_transform_object

    result = modeling_transform_object(
        MagicMock(),
        name="King's Crown",
        scale=[1.0, 1.0, 1.0],
        guided_role="detail_part",
    )

    assert (
        result == "[Step 1: scene_set_mode] OK\n[Step 2: modeling_transform_object] Transformed object 'King's Crown'"
    )
    assert recorded == [("King's Crown", "detail_part", None)]


def test_modeling_transform_object_registers_guided_role_with_corrected_result_name(monkeypatch):
    recorded: list[tuple[str, str, str | None]] = []

    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.route_tool_call",
        lambda **kwargs: "Transformed object 'TailRoot'",
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state",
        lambda ctx: SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={"flow_id": "guided_creature_flow"},
        ),
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role",
        lambda ctx, **kwargs: recorded.append((kwargs["object_name"], kwargs["role"], kwargs.get("role_group"))),
    )

    from server.adapters.mcp.areas.modeling import modeling_transform_object

    result = modeling_transform_object(
        MagicMock(),
        name="Tail",
        scale=[1.0, 1.0, 1.0],
        guided_role="tail_mass",
    )

    assert result == "Transformed object 'TailRoot'"
    assert recorded == [("TailRoot", "tail_mass", None)]


def test_async_modeling_transform_finalizes_corrected_result_name_and_warning(monkeypatch):
    recorded_roles: list[tuple[str, str, str | None]] = []
    stale_calls: list[tuple[str, str | None]] = []
    warnings: list[str] = []
    offloaded_calls: list[tuple[object, tuple[object, ...], dict[str, object]]] = []

    async def hydrate(ctx):
        return None

    async def get_session_capability_state_async(ctx):
        return SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={"flow_id": "guided_creature_flow"},
        )

    async def mark_guided_spatial_state_stale_async(ctx, **kwargs):
        stale_calls.append((kwargs["tool_name"], kwargs.get("reason")))
        return await get_session_capability_state_async(ctx)

    async def register_guided_part_role_async(ctx, **kwargs):
        recorded_roles.append((kwargs["object_name"], kwargs["role"], kwargs.get("role_group")))
        return await get_session_capability_state_async(ctx)

    report = MCPExecutionReport(
        context=MCPExecutionContext(
            tool_name="modeling_transform_object",
            params={"name": "Tail", "guided_role": "tail_mass"},
            session_phase="build",
            surface_profile="llm-guided",
            guided_tool_family="primary_masses",
            guided_role="tail_mass",
        ),
        router_enabled=True,
        router_applied=True,
        router_disposition="corrected",
        steps=(
            ExecutionStep(
                tool_name="modeling_transform_object",
                params={"name": "TailRoot"},
                result="Transformed object 'TailRoot'",
            ),
        ),
        policy_context={
            "guided_naming": {
                "status": "warning",
                "message": "Use full semantic object names such as TailRoot.",
            }
        },
    )

    monkeypatch.setattr("server.adapters.mcp.areas.modeling._hydrate_sync_route_session", hydrate)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling._route_tool_call_report_for_context",
        lambda *args, **kwargs: report,
    )

    async def to_thread(fn, /, *args, **kwargs):
        offloaded_calls.append((fn, args, kwargs))
        return fn(*args, **kwargs)

    monkeypatch.setattr("server.adapters.mcp.areas.modeling.asyncio.to_thread", to_thread)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state_async",
        get_session_capability_state_async,
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.mark_guided_spatial_state_stale_async",
        mark_guided_spatial_state_stale_async,
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role_async",
        register_guided_part_role_async,
    )
    monkeypatch.setattr("server.adapters.mcp.areas.modeling.ctx_warning", lambda ctx, message: warnings.append(message))

    from server.adapters.mcp.areas.modeling import _modeling_transform_object_impl_async

    result = asyncio.run(
        _modeling_transform_object_impl_async(
            MagicMock(),
            name="Tail",
            scale=[1.0, 1.0, 1.0],
            guided_role="tail_mass",
        )
    )

    assert result == "Transformed object 'TailRoot'"
    assert offloaded_calls
    assert offloaded_calls[0][2]["tool_name"] == "modeling_transform_object"
    assert stale_calls == [("modeling_transform_object", "modeling_transform_object")]
    assert recorded_roles == [("TailRoot", "tail_mass", None)]
    assert warnings == ["Use full semantic object names such as TailRoot."]


def test_async_modeling_transform_finalizes_from_report_steps_when_legacy_text_is_not_parseable(monkeypatch):
    recorded_roles: list[tuple[str, str, str | None]] = []
    stale_calls: list[tuple[str, str | None]] = []

    async def hydrate(ctx):
        return None

    async def get_session_capability_state_async(ctx):
        return SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={"flow_id": "guided_creature_flow"},
        )

    async def mark_guided_spatial_state_stale_async(ctx, **kwargs):
        stale_calls.append((kwargs["tool_name"], kwargs.get("reason")))
        return await get_session_capability_state_async(ctx)

    async def register_guided_part_role_async(ctx, **kwargs):
        recorded_roles.append((kwargs["object_name"], kwargs["role"], kwargs.get("role_group")))
        return await get_session_capability_state_async(ctx)

    report = MCPExecutionReport(
        context=MCPExecutionContext(
            tool_name="modeling_transform_object",
            params={"name": "Tail", "guided_role": "tail_mass"},
            session_phase="build",
            surface_profile="llm-guided",
            guided_tool_family="primary_masses",
            guided_role="tail_mass",
        ),
        router_enabled=True,
        router_applied=True,
        router_disposition="corrected",
        steps=(
            ExecutionStep(tool_name="scene_set_mode", params={"mode": "OBJECT"}, result="OK"),
            ExecutionStep(
                tool_name="modeling_transform_object",
                params={"name": "TailRoot"},
                result="Transformed object 'TailRoot'",
            ),
        ),
    )

    async def to_thread(fn, /, *args, **kwargs):
        return fn(*args, **kwargs)

    monkeypatch.setattr("server.adapters.mcp.areas.modeling._hydrate_sync_route_session", hydrate)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling._route_tool_call_report_for_context",
        lambda *args, **kwargs: report,
    )
    monkeypatch.setattr("server.adapters.mcp.areas.modeling.asyncio.to_thread", to_thread)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling._legacy_route_report_result",
        lambda routed_report: "Corrected route completed.",
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state_async",
        get_session_capability_state_async,
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.mark_guided_spatial_state_stale_async",
        mark_guided_spatial_state_stale_async,
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role_async",
        register_guided_part_role_async,
    )

    from server.adapters.mcp.areas.modeling import _modeling_transform_object_impl_async

    result = asyncio.run(
        _modeling_transform_object_impl_async(
            MagicMock(),
            name="Tail",
            scale=[1.0, 1.0, 1.0],
            guided_role="tail_mass",
        )
    )

    assert result == "Corrected route completed."
    assert stale_calls == [("modeling_transform_object", "modeling_transform_object")]
    assert recorded_roles == [("TailRoot", "tail_mass", None)]


def test_async_modeling_create_offloads_routed_sync_execution(monkeypatch):
    recorded_roles: list[tuple[str, str, str | None]] = []
    stale_calls: list[tuple[str, str | None, str | None]] = []
    offloaded_calls: list[tuple[object, tuple[object, ...], dict[str, object]]] = []

    async def hydrate(ctx):
        return None

    async def get_session_capability_state_async(ctx):
        return SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={"flow_id": "guided_creature_flow"},
        )

    async def mark_guided_spatial_state_stale_async(ctx, **kwargs):
        stale_calls.append((kwargs["tool_name"], kwargs.get("family"), kwargs.get("reason")))
        return await get_session_capability_state_async(ctx)

    async def register_guided_part_role_async(ctx, **kwargs):
        recorded_roles.append((kwargs["object_name"], kwargs["role"], kwargs.get("role_group")))
        return await get_session_capability_state_async(ctx)

    report = MCPExecutionReport(
        context=MCPExecutionContext(
            tool_name="modeling_create_primitive",
            params={"primitive_type": "Sphere", "name": "Body", "guided_role": "body_core"},
            session_phase="build",
            surface_profile="llm-guided",
            guided_tool_family="primary_masses",
            guided_role="body_core",
        ),
        router_enabled=False,
        router_applied=False,
        router_disposition="direct",
        steps=(
            ExecutionStep(
                tool_name="modeling_create_primitive",
                params={"primitive_type": "Sphere", "name": "Body"},
                result="Created Sphere named 'Body'",
            ),
        ),
    )

    async def to_thread(fn, /, *args, **kwargs):
        offloaded_calls.append((fn, args, kwargs))
        return fn(*args, **kwargs)

    monkeypatch.setattr("server.adapters.mcp.areas.modeling._hydrate_sync_route_session", hydrate)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling._route_tool_call_report_for_context",
        lambda *args, **kwargs: report,
    )
    monkeypatch.setattr("server.adapters.mcp.areas.modeling.asyncio.to_thread", to_thread)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state_async",
        get_session_capability_state_async,
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.mark_guided_spatial_state_stale_async",
        mark_guided_spatial_state_stale_async,
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role_async",
        register_guided_part_role_async,
    )

    from server.adapters.mcp.areas.modeling import _modeling_create_primitive_impl_async

    result = asyncio.run(
        _modeling_create_primitive_impl_async(
            MagicMock(),
            primitive_type="Sphere",
            radius=0.5,
            name="Body",
            guided_role="body_core",
        )
    )

    assert result == "Created Sphere named 'Body'"
    assert offloaded_calls
    assert offloaded_calls[0][2]["tool_name"] == "modeling_create_primitive"
    assert stale_calls == [("modeling_create_primitive", "primary_masses", "modeling_create_primitive")]
    assert recorded_roles == [("Body", "body_core", None)]


def test_async_modeling_create_emits_guided_flow_feedback_when_refresh_rearms(monkeypatch):
    infos: list[str] = []

    before_state = SessionCapabilityState(
        phase=SessionPhase.BUILD,
        guided_flow_state={
            "current_step": "create_primary_masses",
            "completed_steps": ["understand_goal", "establish_spatial_context"],
            "spatial_refresh_required": False,
            "next_actions": ["begin_primary_masses"],
            "allowed_families": ["primary_masses", "reference_context"],
            "required_checks": [],
            "completed_roles": ["body_core"],
            "missing_roles": ["head_mass", "tail_mass"],
            "required_role_groups": ["primary_masses"],
        },
    )
    after_state = SessionCapabilityState(
        phase=SessionPhase.BUILD,
        guided_flow_state={
            "current_step": "place_secondary_parts",
            "completed_steps": ["understand_goal", "establish_spatial_context", "create_primary_masses"],
            "spatial_refresh_required": True,
            "next_actions": ["refresh_spatial_context"],
            "allowed_families": ["spatial_context", "reference_context"],
            "required_checks": [
                {"tool_name": "scene_scope_graph", "status": "pending"},
                {"tool_name": "scene_relation_graph", "status": "pending"},
                {"tool_name": "scene_view_diagnostics", "status": "pending"},
            ],
            "completed_roles": ["body_core", "head_mass"],
            "missing_roles": ["tail_mass", "snout_mass", "ear_pair", "foreleg_pair", "hindleg_pair"],
            "required_role_groups": ["secondary_parts"],
            "active_target_scope": {
                "scope_kind": "object_set",
                "primary_target": "Body",
                "object_names": ["Body", "Head"],
                "object_count": 2,
            },
        },
    )
    current_state = before_state

    async def hydrate(ctx):
        return None

    async def get_session_capability_state_async(ctx):
        return current_state

    async def mark_guided_spatial_state_stale_async(ctx, **kwargs):
        return current_state

    async def register_guided_part_role_async(ctx, **kwargs):
        nonlocal current_state
        current_state = after_state
        return current_state

    report = MCPExecutionReport(
        context=MCPExecutionContext(
            tool_name="modeling_create_primitive",
            params={"primitive_type": "Sphere", "name": "Head", "guided_role": "head_mass"},
            session_phase="build",
            surface_profile="llm-guided",
            guided_tool_family="primary_masses",
            guided_role="head_mass",
        ),
        router_enabled=False,
        router_applied=False,
        router_disposition="direct",
        steps=(
            ExecutionStep(
                tool_name="modeling_create_primitive",
                params={"primitive_type": "Sphere", "name": "Head"},
                result="Created Sphere named 'Head'",
            ),
        ),
    )

    async def to_thread(fn, /, *args, **kwargs):
        return fn(*args, **kwargs)

    monkeypatch.setattr("server.adapters.mcp.areas.modeling._hydrate_sync_route_session", hydrate)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling._route_tool_call_report_for_context",
        lambda *args, **kwargs: report,
    )
    monkeypatch.setattr("server.adapters.mcp.areas.modeling.asyncio.to_thread", to_thread)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state_async",
        get_session_capability_state_async,
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.mark_guided_spatial_state_stale_async",
        mark_guided_spatial_state_stale_async,
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role_async",
        register_guided_part_role_async,
    )
    monkeypatch.setattr("server.adapters.mcp.areas.modeling.ctx_info", lambda ctx, message: infos.append(message))

    from server.adapters.mcp.areas.modeling import _modeling_create_primitive_impl_async

    result = asyncio.run(
        _modeling_create_primitive_impl_async(
            MagicMock(),
            primitive_type="Sphere",
            radius=0.35,
            name="Head",
            guided_role="head_mass",
        )
    )

    assert result == "Created Sphere named 'Head'"
    assert infos
    assert "Spatial context refresh required before continuing build tools." in infos[0]
    assert "scene_scope_graph, scene_relation_graph, scene_view_diagnostics" in infos[0]


def test_async_modeling_create_finalizes_from_report_steps_when_legacy_text_is_not_parseable(monkeypatch):
    recorded_roles: list[tuple[str, str, str | None]] = []
    stale_calls: list[tuple[str, str | None, str | None]] = []

    async def hydrate(ctx):
        return None

    async def get_session_capability_state_async(ctx):
        return SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={"flow_id": "guided_creature_flow"},
        )

    async def mark_guided_spatial_state_stale_async(ctx, **kwargs):
        stale_calls.append((kwargs["tool_name"], kwargs.get("family"), kwargs.get("reason")))
        return await get_session_capability_state_async(ctx)

    async def register_guided_part_role_async(ctx, **kwargs):
        recorded_roles.append((kwargs["object_name"], kwargs["role"], kwargs.get("role_group")))
        return await get_session_capability_state_async(ctx)

    report = MCPExecutionReport(
        context=MCPExecutionContext(
            tool_name="modeling_create_primitive",
            params={"primitive_type": "Sphere", "name": "Body", "guided_role": "body_core"},
            session_phase="build",
            surface_profile="llm-guided",
            guided_tool_family="primary_masses",
            guided_role="body_core",
        ),
        router_enabled=True,
        router_applied=True,
        router_disposition="corrected",
        steps=(
            ExecutionStep(tool_name="scene_set_mode", params={"mode": "OBJECT"}, result="OK"),
            ExecutionStep(
                tool_name="modeling_create_primitive",
                params={"primitive_type": "Sphere", "name": "Body"},
                result="Created Sphere named 'Body'",
            ),
        ),
    )

    async def to_thread(fn, /, *args, **kwargs):
        return fn(*args, **kwargs)

    monkeypatch.setattr("server.adapters.mcp.areas.modeling._hydrate_sync_route_session", hydrate)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling._route_tool_call_report_for_context",
        lambda *args, **kwargs: report,
    )
    monkeypatch.setattr("server.adapters.mcp.areas.modeling.asyncio.to_thread", to_thread)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling._legacy_route_report_result",
        lambda routed_report: "Corrected route completed.",
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.get_session_capability_state_async",
        get_session_capability_state_async,
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.mark_guided_spatial_state_stale_async",
        mark_guided_spatial_state_stale_async,
    )
    monkeypatch.setattr(
        "server.adapters.mcp.areas.modeling.register_guided_part_role_async",
        register_guided_part_role_async,
    )

    from server.adapters.mcp.areas.modeling import _modeling_create_primitive_impl_async

    result = asyncio.run(
        _modeling_create_primitive_impl_async(
            MagicMock(),
            primitive_type="Sphere",
            radius=0.5,
            name="Body",
            guided_role="body_core",
        )
    )

    assert result == "Corrected route completed."
    assert stale_calls == [("modeling_create_primitive", "primary_masses", "modeling_create_primitive")]
    assert recorded_roles == [("Body", "body_core", None)]


def test_async_scene_clean_marks_spatial_state_stale_from_report_steps_after_correction(monkeypatch):
    stale_calls: list[tuple[str, str | None]] = []

    async def hydrate(ctx):
        return None

    async def mark_guided_spatial_state_stale_async(ctx, **kwargs):
        stale_calls.append((kwargs["tool_name"], kwargs.get("reason")))
        return SessionCapabilityState(
            phase=SessionPhase.BUILD,
            guided_flow_state={"flow_id": "guided_creature_flow"},
        )

    report = MCPExecutionReport(
        context=MCPExecutionContext(
            tool_name="scene_clean_scene",
            params={"keep_lights_and_cameras": True},
            session_phase="build",
            surface_profile="llm-guided",
            guided_tool_family="utility",
        ),
        router_enabled=True,
        router_applied=True,
        router_disposition="corrected",
        steps=(
            ExecutionStep(tool_name="scene_set_mode", params={"mode": "OBJECT"}, result="OK"),
            ExecutionStep(
                tool_name="scene_clean_scene",
                params={"keep_lights_and_cameras": True},
                result="Scene cleaned.",
            ),
        ),
    )

    async def to_thread(fn, /, *args, **kwargs):
        return fn(*args, **kwargs)

    monkeypatch.setattr("server.adapters.mcp.areas.scene._hydrate_sync_route_session", hydrate)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.scene._route_tool_call_report_for_context",
        lambda *args, **kwargs: report,
    )
    monkeypatch.setattr("server.adapters.mcp.areas.scene.asyncio.to_thread", to_thread)
    monkeypatch.setattr(
        "server.adapters.mcp.areas.scene.mark_guided_spatial_state_stale_async",
        mark_guided_spatial_state_stale_async,
    )

    from server.adapters.mcp.areas.scene import _scene_clean_scene_async

    result = asyncio.run(_scene_clean_scene_async(MagicMock(), keep_lights_and_cameras=True))

    assert result == "[Step 1: scene_set_mode] OK\n[Step 2: scene_clean_scene] Scene cleaned."
    assert stale_calls == [("scene_clean_scene", "scene_clean_scene")]


def test_sculpt_auto_main_path_delegates_to_handler(monkeypatch):
    calls = {}

    class Handler:
        def auto_sculpt(self, **kwargs):
            calls["kwargs"] = kwargs
            return "Applied smooth sculpt"

    monkeypatch.setattr("server.adapters.mcp.areas.sculpt.get_sculpt_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.sculpt.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.sculpt import sculpt_auto

    result = sculpt_auto(MagicMock(), operation="smooth", object_name="Head", strength=0.6, iterations=2)

    assert result == "Applied smooth sculpt"
    assert calls["kwargs"]["object_name"] == "Head"
    assert calls["kwargs"]["iterations"] == 2


def test_text_to_mesh_main_path_delegates_to_handler(monkeypatch):
    calls = {}

    class Handler:
        def to_mesh(self, **kwargs):
            calls["kwargs"] = kwargs
            return "Converted text to mesh"

    monkeypatch.setattr("server.adapters.mcp.areas.text.get_text_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.text.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.text import text_to_mesh

    result = text_to_mesh(MagicMock(), object_name="Logo", keep_original=True)

    assert result == "Converted text to mesh"
    assert calls["kwargs"] == {"object_name": "Logo", "keep_original": True}


def test_uv_list_maps_formats_main_path_payload(monkeypatch):
    class Handler:
        def list_maps(self, **kwargs):
            return {
                "object_name": "Wall",
                "uv_map_count": 2,
                "uv_maps": [
                    {
                        "name": "UVMap",
                        "is_active": True,
                        "is_active_render": True,
                        "uv_loop_count": 24,
                        "island_count": 3,
                    },
                    {
                        "name": "Lightmap",
                        "is_active": False,
                        "is_active_render": False,
                        "uv_loop_count": 24,
                    },
                ],
            }

    monkeypatch.setattr("server.adapters.mcp.areas.uv.get_uv_handler", lambda: Handler())
    monkeypatch.setattr("server.adapters.mcp.areas.uv.ctx_info", lambda ctx, message: None)
    monkeypatch.setattr("server.adapters.mcp.areas.uv.route_tool_call", _direct_route)

    from server.adapters.mcp.areas.uv import uv_list_maps

    result = uv_list_maps(MagicMock(), object_name="Wall", include_island_counts=True)

    assert "Object: Wall" in result
    assert "UV Maps (2):" in result
    assert "UVMap [active, active_render]" in result
    assert "UV loops: 24" in result
    assert "Islands: 3" in result
    assert "Lightmap" in result
