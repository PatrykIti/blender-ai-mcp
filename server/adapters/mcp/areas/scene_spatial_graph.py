from __future__ import annotations

from fastmcp import Context

from server.adapters.mcp.context_utils import ctx_info
from server.adapters.mcp.contracts.scene import (
    SceneAssembledTargetScopeContract,
    SceneRelationGraphPayloadContract,
    SceneRelationGraphResponseContract,
    SceneScopeGraphPayloadContract,
    SceneScopeGraphResponseContract,
)
from server.adapters.mcp.router_helper import route_tool_call, route_tool_call_async
from server.adapters.mcp.session_capabilities import (
    describe_guided_flow_feedback,
    get_session_capability_state_async,
    record_guided_flow_spatial_check_completion,
    record_guided_flow_spatial_check_completion_async,
    update_quality_gate_plan_from_relation_graph,
    update_quality_gate_plan_from_relation_graph_async,
)
from server.infrastructure.di import get_scene_handler

from .scene_guided_runtime import (
    guided_scope_mismatch_message,
    guided_scope_requirement_error,
    hydrate_sync_route_session,
    should_require_explicit_guided_scope,
)


def route_scene_scope_graph(
    ctx: Context,
    *,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    guided_scope_requirement_error_fn=guided_scope_requirement_error,
    should_require_explicit_guided_scope_fn=should_require_explicit_guided_scope,
    guided_scope_mismatch_message_fn=guided_scope_mismatch_message,
    record_guided_flow_spatial_check_completion_fn=record_guided_flow_spatial_check_completion,
) -> SceneScopeGraphResponseContract:
    def execute() -> SceneScopeGraphResponseContract:
        if not any([target_object, target_objects, collection_name]) and should_require_explicit_guided_scope_fn(ctx):
            return SceneScopeGraphResponseContract(error=guided_scope_requirement_error_fn("scene_scope_graph"))

        handler = get_scene_handler_fn()
        try:
            payload = SceneScopeGraphPayloadContract(
                scope=SceneAssembledTargetScopeContract.model_validate(
                    handler.get_scope_graph(
                        target_object=target_object,
                        target_objects=target_objects,
                        collection_name=collection_name,
                    )
                ),
                message="Scope graph derived from explicit targets plus deterministic role/anchor heuristics.",
            )
            mismatch_message = guided_scope_mismatch_message_fn(
                ctx,
                tool_name="scene_scope_graph",
                resolved_scope=payload.scope.model_dump(mode="json"),
            )
            if mismatch_message:
                payload.message = mismatch_message
            record_guided_flow_spatial_check_completion_fn(
                ctx,
                tool_name="scene_scope_graph",
                resolved_scope=payload.scope.model_dump(mode="json"),
            )
            return SceneScopeGraphResponseContract(payload=payload)
        except (RuntimeError, ValueError) as exc:
            return SceneScopeGraphResponseContract(error=str(exc))

    result = route_tool_call_fn(
        tool_name="scene_scope_graph",
        params={
            "target_object": target_object,
            "target_objects": target_objects,
            "collection_name": collection_name,
        },
        direct_executor=execute,
    )
    if isinstance(result, SceneScopeGraphResponseContract):
        return result
    if isinstance(result, dict):
        return SceneScopeGraphResponseContract.model_validate(result)
    return SceneScopeGraphResponseContract(error=str(result))


async def route_scene_scope_graph_async(
    ctx: Context,
    *,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_async_fn=route_tool_call_async,
    hydrate_sync_route_session_fn=hydrate_sync_route_session,
    guided_scope_requirement_error_fn=guided_scope_requirement_error,
    should_require_explicit_guided_scope_fn=should_require_explicit_guided_scope,
    guided_scope_mismatch_message_fn=guided_scope_mismatch_message,
    get_session_capability_state_async_fn=get_session_capability_state_async,
    record_guided_flow_spatial_check_completion_async_fn=record_guided_flow_spatial_check_completion_async,
    describe_guided_flow_feedback_fn=describe_guided_flow_feedback,
    ctx_info_fn=ctx_info,
) -> SceneScopeGraphResponseContract:
    await hydrate_sync_route_session_fn(ctx)

    def execute() -> SceneScopeGraphResponseContract:
        if not any([target_object, target_objects, collection_name]) and should_require_explicit_guided_scope_fn(ctx):
            return SceneScopeGraphResponseContract(error=guided_scope_requirement_error_fn("scene_scope_graph"))

        handler = get_scene_handler_fn()
        try:
            payload = SceneScopeGraphPayloadContract(
                scope=SceneAssembledTargetScopeContract.model_validate(
                    handler.get_scope_graph(
                        target_object=target_object,
                        target_objects=target_objects,
                        collection_name=collection_name,
                    )
                ),
                message="Scope graph derived from explicit targets plus deterministic role/anchor heuristics.",
            )
            mismatch_message = guided_scope_mismatch_message_fn(
                ctx,
                tool_name="scene_scope_graph",
                resolved_scope=payload.scope.model_dump(mode="json"),
            )
            if mismatch_message:
                payload.message = mismatch_message
            return SceneScopeGraphResponseContract(payload=payload)
        except (RuntimeError, ValueError) as exc:
            return SceneScopeGraphResponseContract(error=str(exc))

    result = await route_tool_call_async_fn(
        ctx,
        tool_name="scene_scope_graph",
        params={
            "target_object": target_object,
            "target_objects": target_objects,
            "collection_name": collection_name,
        },
        direct_executor=execute,
    )
    if isinstance(result, SceneScopeGraphResponseContract):
        contract = result
    elif isinstance(result, dict):
        contract = SceneScopeGraphResponseContract.model_validate(result)
    else:
        contract = SceneScopeGraphResponseContract(error=str(result))

    if contract.payload is not None:
        previous_state = await get_session_capability_state_async_fn(ctx)
        await record_guided_flow_spatial_check_completion_async_fn(
            ctx,
            tool_name="scene_scope_graph",
            resolved_scope=contract.payload.scope.model_dump(mode="json"),
        )
        feedback = describe_guided_flow_feedback_fn(previous_state, await get_session_capability_state_async_fn(ctx))
        if feedback:
            contract.payload.message = (
                f"{contract.payload.message} {feedback}" if contract.payload.message else feedback
            )
            ctx_info_fn(ctx, feedback)
    return contract


def route_scene_relation_graph(
    ctx: Context,
    *,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    goal_hint: str | None = None,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    guided_scope_requirement_error_fn=guided_scope_requirement_error,
    should_require_explicit_guided_scope_fn=should_require_explicit_guided_scope,
    guided_scope_mismatch_message_fn=guided_scope_mismatch_message,
    record_guided_flow_spatial_check_completion_fn=record_guided_flow_spatial_check_completion,
    update_quality_gate_plan_from_relation_graph_fn=update_quality_gate_plan_from_relation_graph,
) -> SceneRelationGraphResponseContract:
    def execute() -> SceneRelationGraphResponseContract:
        if not any([target_object, target_objects, collection_name]) and should_require_explicit_guided_scope_fn(ctx):
            return SceneRelationGraphResponseContract(error=guided_scope_requirement_error_fn("scene_relation_graph"))

        handler = get_scene_handler_fn()
        try:
            payload = SceneRelationGraphPayloadContract.model_validate(
                handler.get_relation_graph(
                    target_object=target_object,
                    target_objects=target_objects,
                    collection_name=collection_name,
                    goal_hint=goal_hint,
                    include_truth_payloads=False,
                )
            )
            mismatch_message = guided_scope_mismatch_message_fn(
                ctx,
                tool_name="scene_relation_graph",
                resolved_scope=payload.scope.model_dump(mode="json"),
            )
            if mismatch_message:
                payload.message = mismatch_message
            record_guided_flow_spatial_check_completion_fn(
                ctx,
                tool_name="scene_relation_graph",
                resolved_scope=payload.scope.model_dump(mode="json"),
            )
            return SceneRelationGraphResponseContract(payload=payload)
        except (RuntimeError, ValueError) as exc:
            return SceneRelationGraphResponseContract(error=str(exc))

    result = route_tool_call_fn(
        tool_name="scene_relation_graph",
        params={
            "target_object": target_object,
            "target_objects": target_objects,
            "collection_name": collection_name,
            "goal_hint": goal_hint,
        },
        direct_executor=execute,
    )
    if isinstance(result, SceneRelationGraphResponseContract):
        contract = result
    elif isinstance(result, dict):
        contract = SceneRelationGraphResponseContract.model_validate(result)
    else:
        contract = SceneRelationGraphResponseContract(error=str(result))

    if contract.payload is not None:
        update_quality_gate_plan_from_relation_graph_fn(ctx, contract.payload.model_dump(mode="json"))
    return contract


async def route_scene_relation_graph_async(
    ctx: Context,
    *,
    target_object: str | None = None,
    target_objects: list[str] | None = None,
    collection_name: str | None = None,
    goal_hint: str | None = None,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_async_fn=route_tool_call_async,
    hydrate_sync_route_session_fn=hydrate_sync_route_session,
    guided_scope_requirement_error_fn=guided_scope_requirement_error,
    should_require_explicit_guided_scope_fn=should_require_explicit_guided_scope,
    guided_scope_mismatch_message_fn=guided_scope_mismatch_message,
    get_session_capability_state_async_fn=get_session_capability_state_async,
    record_guided_flow_spatial_check_completion_async_fn=record_guided_flow_spatial_check_completion_async,
    update_quality_gate_plan_from_relation_graph_async_fn=update_quality_gate_plan_from_relation_graph_async,
    describe_guided_flow_feedback_fn=describe_guided_flow_feedback,
    ctx_info_fn=ctx_info,
) -> SceneRelationGraphResponseContract:
    await hydrate_sync_route_session_fn(ctx)

    def execute() -> SceneRelationGraphResponseContract:
        if not any([target_object, target_objects, collection_name]) and should_require_explicit_guided_scope_fn(ctx):
            return SceneRelationGraphResponseContract(error=guided_scope_requirement_error_fn("scene_relation_graph"))

        handler = get_scene_handler_fn()
        try:
            payload = SceneRelationGraphPayloadContract.model_validate(
                handler.get_relation_graph(
                    target_object=target_object,
                    target_objects=target_objects,
                    collection_name=collection_name,
                    goal_hint=goal_hint,
                    include_truth_payloads=False,
                )
            )
            mismatch_message = guided_scope_mismatch_message_fn(
                ctx,
                tool_name="scene_relation_graph",
                resolved_scope=payload.scope.model_dump(mode="json"),
            )
            if mismatch_message:
                payload.message = mismatch_message
            return SceneRelationGraphResponseContract(payload=payload)
        except (RuntimeError, ValueError) as exc:
            return SceneRelationGraphResponseContract(error=str(exc))

    result = await route_tool_call_async_fn(
        ctx,
        tool_name="scene_relation_graph",
        params={
            "target_object": target_object,
            "target_objects": target_objects,
            "collection_name": collection_name,
            "goal_hint": goal_hint,
        },
        direct_executor=execute,
    )
    if isinstance(result, SceneRelationGraphResponseContract):
        contract = result
    elif isinstance(result, dict):
        contract = SceneRelationGraphResponseContract.model_validate(result)
    else:
        contract = SceneRelationGraphResponseContract(error=str(result))

    if contract.payload is not None:
        previous_state = await get_session_capability_state_async_fn(ctx)
        await record_guided_flow_spatial_check_completion_async_fn(
            ctx,
            tool_name="scene_relation_graph",
            resolved_scope=contract.payload.scope.model_dump(mode="json"),
        )
        await update_quality_gate_plan_from_relation_graph_async_fn(ctx, contract.payload.model_dump(mode="json"))
        feedback = describe_guided_flow_feedback_fn(previous_state, await get_session_capability_state_async_fn(ctx))
        if feedback:
            contract.payload.message = (
                f"{contract.payload.message} {feedback}" if contract.payload.message else feedback
            )
            ctx_info_fn(ctx, feedback)
    return contract
