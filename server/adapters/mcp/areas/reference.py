# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""Goal-scoped reference image intake and lifecycle tools."""

from __future__ import annotations

import mimetypes
import shutil
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastmcp import Context

from server.adapters.mcp.context_utils import ctx_info
from server.adapters.mcp.contracts.reference import ReferenceImagesResponseContract
from server.adapters.mcp.session_capabilities import (
    get_session_capability_state_async,
    replace_session_pending_reference_images_async,
    replace_session_reference_images_async,
)
from server.adapters.mcp.visibility.tags import get_capability_tags
from server.infrastructure.tmp_paths import get_reference_image_storage_path

REFERENCE_PUBLIC_TOOL_NAMES = ("reference_images",)
_ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def _register_existing_tool(target, tool_name: str):
    tool = globals()[tool_name]
    fn = getattr(tool, "fn", tool)
    return target.tool(fn, name=tool_name, tags=set(get_capability_tags("reference")))


def register_reference_tools(target):
    return {tool_name: _register_existing_tool(target, tool_name) for tool_name in REFERENCE_PUBLIC_TOOL_NAMES}


def _sorted_references(references: list[dict]) -> list[dict]:
    return sorted(references, key=lambda item: str(item.get("added_at") or ""))


def _as_response(
    *,
    action: str,
    goal: str | None,
    references: list[dict],
    removed_reference_id: str | None = None,
    message: str | None = None,
    error: str | None = None,
) -> ReferenceImagesResponseContract:
    return ReferenceImagesResponseContract(
        action=action,
        goal=goal,
        reference_count=len(references),
        references=references,
        removed_reference_id=removed_reference_id,
        message=message,
        error=error,
    )


def _validate_local_reference_path(source_path: str) -> Path:
    path = Path(source_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise ValueError(f"Reference image path does not exist: {source_path}")
    if path.suffix.lower() not in _ALLOWED_IMAGE_SUFFIXES:
        raise ValueError("Reference image must be one of: .png, .jpg, .jpeg, .webp")
    return path


def _copy_reference_image(source_path: Path) -> tuple[str, str]:
    filename = f"ref_{uuid4().hex[:10]}{source_path.suffix.lower()}"
    internal_path, host_visible_path = get_reference_image_storage_path(filename)
    shutil.copy2(source_path, internal_path)
    return str(internal_path), host_visible_path


async def reference_images(
    ctx: Context,
    action: str,
    source_path: str | None = None,
    reference_id: str | None = None,
    label: str | None = None,
    notes: str | None = None,
    target_object: str | None = None,
    target_view: str | None = None,
) -> ReferenceImagesResponseContract:
    """Manage goal-scoped reference images for later vision/capture interpretation."""

    normalized_action = str(action).lower()
    if normalized_action not in {"attach", "list", "remove", "clear"}:
        return _as_response(action="list", goal=None, references=[], error="action must be attach, list, remove, or clear")

    session = await get_session_capability_state_async(ctx)
    active_references = list(session.reference_images or [])
    pending_references = list(session.pending_reference_images or [])
    references = active_references if session.goal is not None else pending_references

    if normalized_action == "list":
        return _as_response(action="list", goal=session.goal, references=_sorted_references(references))

    if normalized_action == "clear":
        for item in references:
            stored_path = item.get("stored_path")
            if isinstance(stored_path, str):
                try:
                    Path(stored_path).unlink(missing_ok=True)
                except Exception:
                    pass
        if session.goal is None:
            await replace_session_pending_reference_images_async(ctx, [])
            ctx_info(ctx, "[REFERENCE] Cleared pending reference images")
            return _as_response(action="clear", goal=None, references=[], message="Cleared pending reference images.")

        await replace_session_reference_images_async(ctx, [])
        ctx_info(ctx, "[REFERENCE] Cleared session reference images")
        return _as_response(action="clear", goal=session.goal, references=[], message="Cleared session reference images.")

    if normalized_action == "remove":
        if not reference_id:
            return _as_response(
                action="remove",
                goal=session.goal,
                references=_sorted_references(references),
                error="reference_id is required for remove",
            )
        remaining: list[dict] = []
        removed: dict | None = None
        for item in references:
            if item.get("reference_id") == reference_id and removed is None:
                removed = item
                continue
            remaining.append(item)
        if removed is None:
            return _as_response(
                action="remove",
                goal=session.goal,
                references=_sorted_references(references),
                error=f"Reference image not found: {reference_id}",
            )
        stored_path = removed.get("stored_path")
        if isinstance(stored_path, str):
            try:
                Path(stored_path).unlink(missing_ok=True)
            except Exception:
                pass
        if session.goal is None:
            await replace_session_pending_reference_images_async(ctx, remaining)
        else:
            await replace_session_reference_images_async(ctx, remaining)
        ctx_info(ctx, f"[REFERENCE] Removed reference image {reference_id}")
        return _as_response(
            action="remove",
            goal=session.goal,
            references=_sorted_references(remaining),
            removed_reference_id=reference_id,
            message=f"Removed reference image '{reference_id}'.",
        )

    if not source_path:
        return _as_response(
            action="attach",
            goal=session.goal,
            references=_sorted_references(references),
            error="source_path is required for attach",
        )

    try:
        source = _validate_local_reference_path(source_path)
        stored_path, host_visible_path = _copy_reference_image(source)
    except ValueError as exc:
        return _as_response(
            action="attach",
            goal=session.goal,
            references=_sorted_references(references),
            error=str(exc),
        )

    reference = {
        "reference_id": f"ref_{uuid4().hex[:8]}",
        "goal": session.goal or "__pending_goal__",
        "label": label,
        "notes": notes,
        "target_object": target_object,
        "target_view": target_view,
        "media_type": mimetypes.guess_type(str(source))[0] or "image/png",
        "source_kind": "local_path",
        "original_path": str(source),
        "stored_path": stored_path,
        "host_visible_path": host_visible_path,
        "added_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    updated = [*references, reference]
    if session.goal is None:
        await replace_session_pending_reference_images_async(ctx, updated)
        ctx_info(ctx, f"[REFERENCE] Attached pending reference image {reference['reference_id']}")
        return _as_response(
            action="attach",
            goal=None,
            references=_sorted_references(updated),
            message=(
                f"Attached pending reference image '{reference['reference_id']}'. "
                "It will be adopted automatically when the next active goal is set."
            ),
        )

    await replace_session_reference_images_async(ctx, updated)
    ctx_info(ctx, f"[REFERENCE] Attached reference image {reference['reference_id']} for goal '{session.goal}'")
    return _as_response(
        action="attach",
        goal=session.goal,
        references=_sorted_references(updated),
        message=f"Attached reference image '{reference['reference_id']}'.",
    )
