from __future__ import annotations

from typing import Any, Callable

from fastmcp import Context

from server.adapters.mcp.context_utils import ctx_info
from server.adapters.mcp.contracts.scene import (
    SceneAssertContactContract,
    SceneAssertContainmentContract,
    SceneAssertDimensionsContract,
    SceneAssertionPayloadContract,
    SceneAssertProportionContract,
    SceneAssertSymmetryContract,
    SceneMeasureAlignmentContract,
    SceneMeasureDimensionsContract,
    SceneMeasureDistanceContract,
    SceneMeasureGapContract,
    SceneMeasureOverlapContract,
)
from server.adapters.mcp.router_helper import route_tool_call
from server.adapters.mcp.utils import parse_coordinate
from server.infrastructure.di import get_scene_handler


def execute_scene_measure_distance(
    *,
    ctx: Context,
    from_object: str,
    to_object: str,
    reference: str,
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> SceneMeasureDistanceContract:
    handler = get_scene_handler()
    try:
        result = SceneMeasureDistanceContract(payload=handler.measure_distance(from_object, to_object, reference))
        info(ctx, f"Measured distance between '{from_object}' and '{to_object}'")
        return result
    except RuntimeError as exc:
        return SceneMeasureDistanceContract(error=str(exc))


def execute_scene_measure_dimensions(
    *,
    ctx: Context,
    object_name: str,
    world_space: bool,
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> SceneMeasureDimensionsContract:
    handler = get_scene_handler()
    try:
        result = SceneMeasureDimensionsContract(payload=handler.measure_dimensions(object_name, world_space))
        info(ctx, f"Measured dimensions for '{object_name}'")
        return result
    except RuntimeError as exc:
        return SceneMeasureDimensionsContract(error=str(exc))


def execute_scene_measure_gap(
    *,
    ctx: Context,
    from_object: str,
    to_object: str,
    tolerance: float,
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> SceneMeasureGapContract:
    handler = get_scene_handler()
    try:
        result = SceneMeasureGapContract(payload=handler.measure_gap(from_object, to_object, tolerance))
        info(ctx, f"Measured gap between '{from_object}' and '{to_object}'")
        return result
    except RuntimeError as exc:
        return SceneMeasureGapContract(error=str(exc))


def execute_scene_measure_alignment(
    *,
    ctx: Context,
    from_object: str,
    to_object: str,
    axes: list[str] | None,
    reference: str,
    tolerance: float,
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> SceneMeasureAlignmentContract:
    handler = get_scene_handler()
    try:
        result = SceneMeasureAlignmentContract(
            payload=handler.measure_alignment(from_object, to_object, axes, reference, tolerance)
        )
        info(ctx, f"Measured alignment between '{from_object}' and '{to_object}'")
        return result
    except RuntimeError as exc:
        return SceneMeasureAlignmentContract(error=str(exc))


def execute_scene_measure_overlap(
    *,
    ctx: Context,
    from_object: str,
    to_object: str,
    tolerance: float,
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> SceneMeasureOverlapContract:
    handler = get_scene_handler()
    try:
        result = SceneMeasureOverlapContract(payload=handler.measure_overlap(from_object, to_object, tolerance))
        info(ctx, f"Measured overlap between '{from_object}' and '{to_object}'")
        return result
    except RuntimeError as exc:
        return SceneMeasureOverlapContract(error=str(exc))


def execute_scene_assert_contact(
    *,
    ctx: Context,
    from_object: str,
    to_object: str,
    max_gap: float,
    allow_overlap: bool,
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> SceneAssertContactContract:
    handler = get_scene_handler()
    try:
        payload = SceneAssertionPayloadContract.model_validate(
            handler.assert_contact(from_object, to_object, max_gap, allow_overlap)
        )
        info(ctx, f"Asserted contact between '{from_object}' and '{to_object}'")
        return SceneAssertContactContract(payload=payload)
    except (RuntimeError, ValueError) as exc:
        return SceneAssertContactContract(error=str(exc))


def execute_scene_assert_dimensions(
    *,
    ctx: Context,
    object_name: str,
    expected_dimensions: Any,
    tolerance: float,
    world_space: bool,
    parse_coordinate: Callable[[Any], list[float] | None],
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> SceneAssertDimensionsContract:
    handler = get_scene_handler()
    try:
        parsed_dimensions = parse_coordinate(expected_dimensions)
        if parsed_dimensions is None:
            raise ValueError("expected_dimensions must contain exactly 3 numeric values")
        payload = SceneAssertionPayloadContract.model_validate(
            handler.assert_dimensions(object_name, parsed_dimensions, tolerance, world_space)
        )
        info(ctx, f"Asserted dimensions for '{object_name}'")
        return SceneAssertDimensionsContract(payload=payload)
    except (RuntimeError, ValueError) as exc:
        return SceneAssertDimensionsContract(error=str(exc))


def execute_scene_assert_containment(
    *,
    ctx: Context,
    inner_object: str,
    outer_object: str,
    min_clearance: float,
    tolerance: float,
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> SceneAssertContainmentContract:
    handler = get_scene_handler()
    try:
        payload = SceneAssertionPayloadContract.model_validate(
            handler.assert_containment(inner_object, outer_object, min_clearance, tolerance)
        )
        info(ctx, f"Asserted containment of '{inner_object}' inside '{outer_object}'")
        return SceneAssertContainmentContract(payload=payload)
    except (RuntimeError, ValueError) as exc:
        return SceneAssertContainmentContract(error=str(exc))


def execute_scene_assert_symmetry(
    *,
    ctx: Context,
    left_object: str,
    right_object: str,
    axis: str,
    mirror_coordinate: float,
    tolerance: float,
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> SceneAssertSymmetryContract:
    handler = get_scene_handler()
    try:
        payload = SceneAssertionPayloadContract.model_validate(
            handler.assert_symmetry(left_object, right_object, axis, mirror_coordinate, tolerance)
        )
        info(ctx, f"Asserted symmetry between '{left_object}' and '{right_object}'")
        return SceneAssertSymmetryContract(payload=payload)
    except (RuntimeError, ValueError) as exc:
        return SceneAssertSymmetryContract(error=str(exc))


def execute_scene_assert_proportion(
    *,
    ctx: Context,
    object_name: str,
    axis_a: str,
    expected_ratio: float,
    axis_b: str | None,
    reference_object: str | None,
    reference_axis: str | None,
    tolerance: float,
    world_space: bool,
    get_scene_handler: Callable[[], Any],
    info: Callable[[Context, str], None],
) -> SceneAssertProportionContract:
    handler = get_scene_handler()
    try:
        payload = SceneAssertionPayloadContract.model_validate(
            handler.assert_proportion(
                object_name,
                axis_a,
                expected_ratio,
                axis_b,
                reference_object,
                reference_axis,
                tolerance,
                world_space,
            )
        )
        info(ctx, f"Asserted proportion for '{object_name}'")
        return SceneAssertProportionContract(payload=payload)
    except (RuntimeError, ValueError) as exc:
        return SceneAssertProportionContract(error=str(exc))


def route_scene_measure_distance(
    ctx: Context,
    *,
    from_object: str,
    to_object: str,
    reference: str,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    ctx_info_fn=ctx_info,
) -> SceneMeasureDistanceContract:
    def execute():
        return execute_scene_measure_distance(
            ctx=ctx,
            from_object=from_object,
            to_object=to_object,
            reference=reference,
            get_scene_handler=get_scene_handler_fn,
            info=ctx_info_fn,
        )

    result = route_tool_call_fn(
        tool_name="scene_measure_distance",
        params={"from_object": from_object, "to_object": to_object, "reference": reference},
        direct_executor=execute,
    )
    if isinstance(result, SceneMeasureDistanceContract):
        return result
    if isinstance(result, dict):
        return SceneMeasureDistanceContract(payload=result)
    return SceneMeasureDistanceContract(error=str(result))


def route_scene_measure_dimensions(
    ctx: Context,
    *,
    object_name: str,
    world_space: bool,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    ctx_info_fn=ctx_info,
) -> SceneMeasureDimensionsContract:
    def execute():
        return execute_scene_measure_dimensions(
            ctx=ctx,
            object_name=object_name,
            world_space=world_space,
            get_scene_handler=get_scene_handler_fn,
            info=ctx_info_fn,
        )

    result = route_tool_call_fn(
        tool_name="scene_measure_dimensions",
        params={"object_name": object_name, "world_space": world_space},
        direct_executor=execute,
    )
    if isinstance(result, SceneMeasureDimensionsContract):
        return result
    if isinstance(result, dict):
        return SceneMeasureDimensionsContract(payload=result)
    return SceneMeasureDimensionsContract(error=str(result))


def route_scene_measure_gap(
    ctx: Context,
    *,
    from_object: str,
    to_object: str,
    tolerance: float,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    ctx_info_fn=ctx_info,
) -> SceneMeasureGapContract:
    def execute():
        return execute_scene_measure_gap(
            ctx=ctx,
            from_object=from_object,
            to_object=to_object,
            tolerance=tolerance,
            get_scene_handler=get_scene_handler_fn,
            info=ctx_info_fn,
        )

    result = route_tool_call_fn(
        tool_name="scene_measure_gap",
        params={"from_object": from_object, "to_object": to_object, "tolerance": tolerance},
        direct_executor=execute,
    )
    if isinstance(result, SceneMeasureGapContract):
        return result
    if isinstance(result, dict):
        return SceneMeasureGapContract(payload=result)
    return SceneMeasureGapContract(error=str(result))


def route_scene_measure_alignment(
    ctx: Context,
    *,
    from_object: str,
    to_object: str,
    axes: list[str] | None,
    reference: str,
    tolerance: float,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    ctx_info_fn=ctx_info,
) -> SceneMeasureAlignmentContract:
    def execute():
        return execute_scene_measure_alignment(
            ctx=ctx,
            from_object=from_object,
            to_object=to_object,
            axes=axes,
            reference=reference,
            tolerance=tolerance,
            get_scene_handler=get_scene_handler_fn,
            info=ctx_info_fn,
        )

    result = route_tool_call_fn(
        tool_name="scene_measure_alignment",
        params={
            "from_object": from_object,
            "to_object": to_object,
            "axes": axes,
            "reference": reference,
            "tolerance": tolerance,
        },
        direct_executor=execute,
    )
    if isinstance(result, SceneMeasureAlignmentContract):
        return result
    if isinstance(result, dict):
        return SceneMeasureAlignmentContract(payload=result)
    return SceneMeasureAlignmentContract(error=str(result))


def route_scene_measure_overlap(
    ctx: Context,
    *,
    from_object: str,
    to_object: str,
    tolerance: float,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    ctx_info_fn=ctx_info,
) -> SceneMeasureOverlapContract:
    def execute():
        return execute_scene_measure_overlap(
            ctx=ctx,
            from_object=from_object,
            to_object=to_object,
            tolerance=tolerance,
            get_scene_handler=get_scene_handler_fn,
            info=ctx_info_fn,
        )

    result = route_tool_call_fn(
        tool_name="scene_measure_overlap",
        params={"from_object": from_object, "to_object": to_object, "tolerance": tolerance},
        direct_executor=execute,
    )
    if isinstance(result, SceneMeasureOverlapContract):
        return result
    if isinstance(result, dict):
        return SceneMeasureOverlapContract(payload=result)
    return SceneMeasureOverlapContract(error=str(result))


def route_scene_assert_contact(
    ctx: Context,
    *,
    from_object: str,
    to_object: str,
    max_gap: float,
    allow_overlap: bool,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    ctx_info_fn=ctx_info,
) -> SceneAssertContactContract:
    def execute():
        return execute_scene_assert_contact(
            ctx=ctx,
            from_object=from_object,
            to_object=to_object,
            max_gap=max_gap,
            allow_overlap=allow_overlap,
            get_scene_handler=get_scene_handler_fn,
            info=ctx_info_fn,
        )

    result = route_tool_call_fn(
        tool_name="scene_assert_contact",
        params={
            "from_object": from_object,
            "to_object": to_object,
            "max_gap": max_gap,
            "allow_overlap": allow_overlap,
        },
        direct_executor=execute,
    )
    if isinstance(result, SceneAssertContactContract):
        return result
    if isinstance(result, dict):
        return SceneAssertContactContract(payload=SceneAssertionPayloadContract.model_validate(result))
    return SceneAssertContactContract(error=str(result))


def route_scene_assert_dimensions(
    ctx: Context,
    *,
    object_name: str,
    expected_dimensions: Any,
    tolerance: float,
    world_space: bool,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    ctx_info_fn=ctx_info,
    parse_coordinate_fn=parse_coordinate,
) -> SceneAssertDimensionsContract:
    def execute():
        return execute_scene_assert_dimensions(
            ctx=ctx,
            object_name=object_name,
            expected_dimensions=expected_dimensions,
            tolerance=tolerance,
            world_space=world_space,
            parse_coordinate=parse_coordinate_fn,
            get_scene_handler=get_scene_handler_fn,
            info=ctx_info_fn,
        )

    result = route_tool_call_fn(
        tool_name="scene_assert_dimensions",
        params={
            "object_name": object_name,
            "expected_dimensions": expected_dimensions,
            "tolerance": tolerance,
            "world_space": world_space,
        },
        direct_executor=execute,
    )
    if isinstance(result, SceneAssertDimensionsContract):
        return result
    if isinstance(result, dict):
        return SceneAssertDimensionsContract(payload=SceneAssertionPayloadContract.model_validate(result))
    return SceneAssertDimensionsContract(error=str(result))


def route_scene_assert_containment(
    ctx: Context,
    *,
    inner_object: str,
    outer_object: str,
    min_clearance: float,
    tolerance: float,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    ctx_info_fn=ctx_info,
) -> SceneAssertContainmentContract:
    def execute():
        return execute_scene_assert_containment(
            ctx=ctx,
            inner_object=inner_object,
            outer_object=outer_object,
            min_clearance=min_clearance,
            tolerance=tolerance,
            get_scene_handler=get_scene_handler_fn,
            info=ctx_info_fn,
        )

    result = route_tool_call_fn(
        tool_name="scene_assert_containment",
        params={
            "inner_object": inner_object,
            "outer_object": outer_object,
            "min_clearance": min_clearance,
            "tolerance": tolerance,
        },
        direct_executor=execute,
    )
    if isinstance(result, SceneAssertContainmentContract):
        return result
    if isinstance(result, dict):
        return SceneAssertContainmentContract(payload=SceneAssertionPayloadContract.model_validate(result))
    return SceneAssertContainmentContract(error=str(result))


def route_scene_assert_symmetry(
    ctx: Context,
    *,
    left_object: str,
    right_object: str,
    axis: str,
    mirror_coordinate: float,
    tolerance: float,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    ctx_info_fn=ctx_info,
) -> SceneAssertSymmetryContract:
    def execute():
        return execute_scene_assert_symmetry(
            ctx=ctx,
            left_object=left_object,
            right_object=right_object,
            axis=axis,
            mirror_coordinate=mirror_coordinate,
            tolerance=tolerance,
            get_scene_handler=get_scene_handler_fn,
            info=ctx_info_fn,
        )

    result = route_tool_call_fn(
        tool_name="scene_assert_symmetry",
        params={
            "left_object": left_object,
            "right_object": right_object,
            "axis": axis,
            "mirror_coordinate": mirror_coordinate,
            "tolerance": tolerance,
        },
        direct_executor=execute,
    )
    if isinstance(result, SceneAssertSymmetryContract):
        return result
    if isinstance(result, dict):
        return SceneAssertSymmetryContract(payload=SceneAssertionPayloadContract.model_validate(result))
    return SceneAssertSymmetryContract(error=str(result))


def route_scene_assert_proportion(
    ctx: Context,
    *,
    object_name: str,
    axis_a: str,
    expected_ratio: float,
    axis_b: str | None,
    reference_object: str | None,
    reference_axis: str | None,
    tolerance: float,
    world_space: bool,
    get_scene_handler_fn=get_scene_handler,
    route_tool_call_fn=route_tool_call,
    ctx_info_fn=ctx_info,
) -> SceneAssertProportionContract:
    def execute():
        return execute_scene_assert_proportion(
            ctx=ctx,
            object_name=object_name,
            axis_a=axis_a,
            expected_ratio=expected_ratio,
            axis_b=axis_b,
            reference_object=reference_object,
            reference_axis=reference_axis,
            tolerance=tolerance,
            world_space=world_space,
            get_scene_handler=get_scene_handler_fn,
            info=ctx_info_fn,
        )

    result = route_tool_call_fn(
        tool_name="scene_assert_proportion",
        params={
            "object_name": object_name,
            "axis_a": axis_a,
            "expected_ratio": expected_ratio,
            "axis_b": axis_b,
            "reference_object": reference_object,
            "reference_axis": reference_axis,
            "tolerance": tolerance,
            "world_space": world_space,
        },
        direct_executor=execute,
    )
    if isinstance(result, SceneAssertProportionContract):
        return result
    if isinstance(result, dict):
        return SceneAssertProportionContract(payload=SceneAssertionPayloadContract.model_validate(result))
    return SceneAssertProportionContract(error=str(result))
