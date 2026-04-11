# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Shared guided-surface contract hardening helpers."""

from __future__ import annotations

from typing import Any

from server.adapters.mcp.platform.name_resolution import resolve_canonical_tool_name
from server.adapters.mcp.version_policy import CONTRACT_LINE_LLM_GUIDED_V2


def canonicalize_collection_manage_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Normalize guided `collection_manage(...)` arguments or raise actionable guidance."""

    canonical_arguments = dict(arguments)
    legacy_name = canonical_arguments.pop("name", None)
    if legacy_name is None:
        return canonical_arguments

    if "collection_name" in canonical_arguments:
        collection_name = canonical_arguments["collection_name"]
        if isinstance(legacy_name, str) and isinstance(collection_name, str) and legacy_name == collection_name:
            return canonical_arguments
        raise ValueError(
            "collection_manage(...) uses the canonical public argument `collection_name`. "
            "Compatibility alias `name` is allowed only when it matches `collection_name`."
        )

    if not isinstance(legacy_name, str) or not legacy_name.strip():
        raise ValueError(
            "collection_manage(...) compatibility alias `name` must be a non-empty string. "
            "Canonical public form: `collection_name`."
        )

    canonical_arguments["collection_name"] = legacy_name
    return canonical_arguments


def canonicalize_reference_images_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Normalize guided `reference_images(...)` attach arguments or raise guidance."""

    canonical_arguments = dict(arguments)
    action = str(canonical_arguments.get("action") or "").lower()
    if action != "attach":
        return canonical_arguments

    if canonical_arguments.get("images") is not None:
        raise ValueError(
            "reference_images(action='attach', ...) accepts exactly one reference per call using "
            "`source_path`. Do not pass `images=[...]`; attach each reference in its own call."
        )
    if canonical_arguments.get("source_paths") is not None:
        raise ValueError(
            "reference_images(action='attach', ...) uses one `source_path` per call. "
            "Do not pass `source_paths=[...]`; call `reference_images(...)` once for each reference."
        )
    return canonical_arguments


def canonicalize_modeling_create_primitive_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Normalize guided `modeling_create_primitive(...)` args or raise guidance."""

    canonical_arguments = dict(arguments)

    primitive_aliases = {
        "cube": "Cube",
        "sphere": "Sphere",
        "uv_sphere": "Sphere",
        "uv sphere": "Sphere",
        "icosphere": "Sphere",
        "ico_sphere": "Sphere",
        "ico sphere": "Sphere",
        "cylinder": "Cylinder",
        "plane": "Plane",
        "cone": "Cone",
        "torus": "Torus",
        "monkey": "Monkey",
        "suzanne": "Monkey",
    }
    primitive_value = canonical_arguments.get("primitive_type")
    if isinstance(primitive_value, str):
        normalized = primitive_value.strip().lower()
        canonical_arguments["primitive_type"] = primitive_aliases.get(normalized, primitive_value)

    unsupported_arguments = [
        name
        for name in ("scale", "segments", "rings", "subdivisions", "collection_name")
        if canonical_arguments.get(name) is not None
    ]
    if unsupported_arguments:
        unsupported_list = ", ".join(f"`{name}`" for name in unsupported_arguments)
        raise ValueError(
            "modeling_create_primitive(...) uses the public arguments "
            "`primitive_type`, `radius`, `size`, `location`, `rotation`, and optional `name`. "
            f"Unsupported on this public surface: {unsupported_list}. "
            "Create the primitive first, then use `modeling_transform_object(scale=...)` for non-uniform scale, "
            "`collection_manage(action='move_object', collection_name=..., object_name=...)` for collection placement, "
            "and mesh-edit tools after creation instead of primitive-only topology knobs such as `segments`, `rings`, or `subdivisions`."
        )
    return canonical_arguments


def canonicalize_scene_clean_scene_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Normalize guided cleanup flags or raise actionable guidance."""

    canonical_arguments = dict(arguments)
    split_keep_lights = canonical_arguments.pop("keep_lights", None)
    split_keep_cameras = canonical_arguments.pop("keep_cameras", None)
    split_present = split_keep_lights is not None or split_keep_cameras is not None

    if not split_present:
        return canonical_arguments

    if "keep_lights_and_cameras" in canonical_arguments:
        combined = canonical_arguments["keep_lights_and_cameras"]
        if (isinstance(combined, bool) and isinstance(split_keep_lights, bool) and split_keep_lights != combined) or (
            isinstance(combined, bool) and isinstance(split_keep_cameras, bool) and split_keep_cameras != combined
        ):
            raise ValueError(
                "scene_clean_scene(...) uses the canonical public flag "
                "`keep_lights_and_cameras`. Legacy `keep_lights` / `keep_cameras` "
                "values must agree with it when both forms are provided."
            )
        return canonical_arguments

    if not isinstance(split_keep_lights, bool) or not isinstance(split_keep_cameras, bool):
        raise ValueError(
            "scene_clean_scene(...) accepts legacy split cleanup flags only when "
            "both `keep_lights` and `keep_cameras` are provided as booleans. "
            "Canonical public form: `keep_lights_and_cameras`."
        )

    if split_keep_lights != split_keep_cameras:
        raise ValueError(
            "scene_clean_scene(...) no longer supports separate light/camera cleanup "
            "choices on `llm-guided`. Use the canonical public flag "
            "`keep_lights_and_cameras`, or provide legacy `keep_lights` and "
            "`keep_cameras` with the same boolean value."
        )

    canonical_arguments["keep_lights_and_cameras"] = split_keep_lights
    return canonical_arguments


def canonicalize_macro_attach_part_to_surface_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Normalize common guided seating macro aliases into the public contract."""

    canonical_arguments = dict(arguments)
    legacy_reference_object = canonical_arguments.pop("reference_object", None)
    if legacy_reference_object is not None:
        if canonical_arguments.get("surface_object") not in {None, legacy_reference_object}:
            raise ValueError(
                "macro_attach_part_to_surface(...) uses `surface_object`; legacy `reference_object` is accepted "
                "only when it matches `surface_object`."
            )
        canonical_arguments["surface_object"] = legacy_reference_object

    surface_axis = canonical_arguments.get("surface_axis")
    if isinstance(surface_axis, str):
        stripped_axis = surface_axis.strip().upper()
        if stripped_axis in {"+X", "+Y", "+Z", "-X", "-Y", "-Z"}:
            canonical_arguments["surface_axis"] = stripped_axis[-1]
            canonical_arguments.setdefault(
                "surface_side",
                "negative" if stripped_axis.startswith("-") else "positive",
            )
        elif stripped_axis in {"X", "Y", "Z"}:
            canonical_arguments["surface_axis"] = stripped_axis

    return canonical_arguments


def canonicalize_scene_assert_proportion_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Normalize a narrow `axis` alias into the canonical `axis_a` field."""

    canonical_arguments = dict(arguments)
    legacy_axis = canonical_arguments.pop("axis", None)
    if legacy_axis is None:
        return canonical_arguments
    if canonical_arguments.get("axis_a") not in {None, legacy_axis}:
        raise ValueError(
            "scene_assert_proportion(...) uses `axis_a` for the numerator axis. "
            "Compatibility alias `axis` is accepted only when it matches `axis_a`."
        )
    canonical_arguments["axis_a"] = legacy_axis
    return canonical_arguments


def canonicalize_guided_tool_arguments(
    name: str,
    arguments: dict[str, Any] | None,
    *,
    contract_line: str = CONTRACT_LINE_LLM_GUIDED_V2,
) -> dict[str, Any] | None:
    """Apply guided contract hardening for one tool call."""

    if arguments is None:
        return None

    canonical_name = resolve_canonical_tool_name(name, contract_line=contract_line)
    if canonical_name == "collection_manage":
        return canonicalize_collection_manage_arguments(arguments)
    if canonical_name == "reference_images":
        return canonicalize_reference_images_arguments(arguments)
    if canonical_name == "modeling_create_primitive":
        return canonicalize_modeling_create_primitive_arguments(arguments)
    if canonical_name == "scene_clean_scene":
        return canonicalize_scene_clean_scene_arguments(arguments)
    if canonical_name == "macro_attach_part_to_surface":
        return canonicalize_macro_attach_part_to_surface_arguments(arguments)
    if canonical_name == "scene_assert_proportion":
        return canonicalize_scene_assert_proportion_arguments(arguments)
    return arguments
