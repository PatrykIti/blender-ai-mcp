# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""Reference-image lifecycle and staged-session helpers for the reference MCP surface."""

from __future__ import annotations

import mimetypes
import shutil
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, cast
from uuid import uuid4

from fastmcp import Context

from server.adapters.mcp.context_utils import ctx_info
from server.adapters.mcp.contracts.reference import (
    ReferenceImageRecordContract,
    ReferenceImagesResponseContract,
)
from server.adapters.mcp.guided_contract import canonicalize_reference_images_arguments
from server.adapters.mcp.session_capabilities import (
    SessionCapabilityState,
    get_session_capability_state_async,
    replace_session_pending_reference_images_async,
    replace_session_reference_images_async,
    session_has_ready_guided_reference_goal,
)
from server.infrastructure.tmp_paths import get_reference_image_storage_path

_ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}

_ReferenceResponseAction = Literal["attach", "list", "remove", "clear"]
_RefreshReferenceUnderstandingFn = Callable[[Context, SessionCapabilityState], Awaitable[SessionCapabilityState]]


@dataclass(frozen=True)
class _ReferenceImageStore:
    session: SessionCapabilityState
    stage_for_later_adoption: bool
    active_references: list[dict[str, Any]]
    pending_references: list[dict[str, Any]]
    visible_references: list[dict[str, Any]]


def _sorted_references(references: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(references, key=lambda item: str(item.get("added_at") or ""))


def _merge_visible_references(*reference_groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return one stable visible view across active and staged reference stores."""

    merged: list[dict[str, Any]] = []
    seen_reference_ids: set[str] = set()

    for group in reference_groups:
        for item in group:
            reference_id = item.get("reference_id")
            if isinstance(reference_id, str) and reference_id:
                if reference_id in seen_reference_ids:
                    continue
                seen_reference_ids.add(reference_id)
            merged.append(item)

    return merged


def _delete_reference_files(references: list[dict[str, Any]]) -> None:
    """Best-effort cleanup for stored reference files without double-unlinking."""

    deleted_paths: set[str] = set()
    for item in references:
        stored_path = item.get("stored_path")
        if not isinstance(stored_path, str) or stored_path in deleted_paths:
            continue
        deleted_paths.add(stored_path)
        try:
            Path(stored_path).unlink(missing_ok=True)
        except Exception:
            pass


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


def _as_response(
    *,
    action: _ReferenceResponseAction,
    goal: str | None,
    references: list[dict[str, Any]],
    removed_reference_id: str | None = None,
    message: str | None = None,
    error: str | None = None,
) -> ReferenceImagesResponseContract:
    return ReferenceImagesResponseContract(
        action=action,
        goal=goal,
        reference_count=len(references),
        references=[ReferenceImageRecordContract.model_validate(item) for item in references],
        removed_reference_id=removed_reference_id,
        message=message,
        error=error,
    )


def _reference_store(session: SessionCapabilityState) -> _ReferenceImageStore:
    stage_for_later_adoption = not session_has_ready_guided_reference_goal(session)
    active_references = list(session.reference_images or [])
    pending_references = list(session.pending_reference_images or [])
    visible_references = (
        _merge_visible_references(active_references, pending_references)
        if session.goal is not None
        else list(pending_references)
    )
    return _ReferenceImageStore(
        session=session,
        stage_for_later_adoption=stage_for_later_adoption,
        active_references=active_references,
        pending_references=pending_references,
        visible_references=visible_references,
    )


def _build_reference_record(
    *,
    session: SessionCapabilityState,
    source: Path,
    stored_path: str,
    host_visible_path: str,
    label: str | None,
    notes: str | None,
    target_object: str | None,
    target_view: str | None,
) -> dict[str, Any]:
    return {
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


async def _clear_reference_images(
    ctx: Context,
    *,
    store: _ReferenceImageStore,
    refresh_reference_understanding: _RefreshReferenceUnderstandingFn,
) -> ReferenceImagesResponseContract:
    session = store.session
    _delete_reference_files(store.visible_references)

    if store.active_references:
        session = await replace_session_reference_images_async(ctx, [])
        if session.goal is not None:
            session = await refresh_reference_understanding(ctx, session)
    if store.pending_references:
        await replace_session_pending_reference_images_async(ctx, [])

    if store.active_references and store.pending_references:
        message = "Cleared active and pending reference images."
    elif store.pending_references or session.goal is None:
        message = "Cleared pending reference images."
    else:
        message = "Cleared session reference images."

    if store.stage_for_later_adoption or store.pending_references:
        ctx_info(ctx, "[REFERENCE] Cleared visible session reference images")
    else:
        ctx_info(ctx, "[REFERENCE] Cleared session reference images")
    return _as_response(action="clear", goal=session.goal, references=[], message=message)


async def _remove_reference_image(
    ctx: Context,
    *,
    store: _ReferenceImageStore,
    reference_id: str | None,
    refresh_reference_understanding: _RefreshReferenceUnderstandingFn,
) -> ReferenceImagesResponseContract:
    session = store.session
    if not reference_id:
        return _as_response(
            action="remove",
            goal=session.goal,
            references=_sorted_references(store.visible_references),
            error="reference_id is required for remove",
        )

    remaining: list[dict[str, Any]] = []
    remaining_pending: list[dict[str, Any]] = []
    removed_records: list[dict[str, Any]] = []
    for item in store.active_references:
        if item.get("reference_id") == reference_id:
            removed_records.append(item)
            continue
        remaining.append(item)
    for item in store.pending_references:
        if item.get("reference_id") == reference_id:
            removed_records.append(item)
            continue
        remaining_pending.append(item)

    if not removed_records:
        return _as_response(
            action="remove",
            goal=session.goal,
            references=_sorted_references(store.visible_references),
            error=f"Reference image not found: {reference_id}",
        )

    _delete_reference_files(removed_records)
    if len(remaining) != len(store.active_references):
        session = await replace_session_reference_images_async(ctx, remaining)
        if session.goal is not None:
            session = await refresh_reference_understanding(ctx, session)
    if len(remaining_pending) != len(store.pending_references):
        await replace_session_pending_reference_images_async(ctx, remaining_pending)

    remaining_visible = (
        _merge_visible_references(remaining, remaining_pending) if session.goal is not None else remaining_pending
    )
    if store.stage_for_later_adoption or len(remaining_pending) != len(store.pending_references):
        ctx_info(ctx, f"[REFERENCE] Removed visible session reference image {reference_id}")
    else:
        ctx_info(ctx, f"[REFERENCE] Removed reference image {reference_id}")
    return _as_response(
        action="remove",
        goal=session.goal,
        references=_sorted_references(remaining_visible),
        removed_reference_id=reference_id,
        message=f"Removed reference image '{reference_id}'.",
    )


async def _attach_reference_image(
    ctx: Context,
    *,
    store: _ReferenceImageStore,
    source_path: str | None,
    images: list[dict[str, Any]] | None,
    source_paths: list[str] | None,
    label: str | None,
    notes: str | None,
    target_object: str | None,
    target_view: str | None,
    refresh_reference_understanding: _RefreshReferenceUnderstandingFn,
) -> ReferenceImagesResponseContract:
    try:
        canonical_arguments = canonicalize_reference_images_arguments(
            {
                key: value
                for key, value in {
                    "action": "attach",
                    "source_path": source_path,
                    "images": images,
                    "source_paths": source_paths,
                }.items()
                if value is not None
            }
        )
    except ValueError as exc:
        return _as_response(
            action="attach",
            goal=store.session.goal,
            references=_sorted_references(store.visible_references),
            error=str(exc),
        )

    resolved_source_path = cast(str | None, canonical_arguments.get("source_path"))
    if not resolved_source_path:
        return _as_response(
            action="attach",
            goal=store.session.goal,
            references=_sorted_references(store.visible_references),
            error="source_path is required for attach",
        )

    try:
        source = _validate_local_reference_path(resolved_source_path)
        stored_path, host_visible_path = _copy_reference_image(source)
    except ValueError as exc:
        return _as_response(
            action="attach",
            goal=store.session.goal,
            references=_sorted_references(store.visible_references),
            error=str(exc),
        )

    reference = _build_reference_record(
        session=store.session,
        source=source,
        stored_path=stored_path,
        host_visible_path=host_visible_path,
        label=label,
        notes=notes,
        target_object=target_object,
        target_view=target_view,
    )

    if store.stage_for_later_adoption:
        pending_updated = [*store.pending_references, reference]
        await replace_session_pending_reference_images_async(ctx, pending_updated)
        visible_updated = (
            _merge_visible_references(store.active_references, pending_updated)
            if store.session.goal is not None
            else pending_updated
        )
        ctx_info(ctx, f"[REFERENCE] Attached pending reference image {reference['reference_id']}")
        return _as_response(
            action="attach",
            goal=store.session.goal,
            references=_sorted_references(visible_updated),
            message=(
                f"Attached pending reference image '{reference['reference_id']}'. "
                "It will be adopted automatically when the guided goal session becomes ready."
            ),
        )

    updated_active = [*store.active_references, reference]
    session = await replace_session_reference_images_async(ctx, updated_active)
    session = await refresh_reference_understanding(ctx, session)
    ctx_info(ctx, f"[REFERENCE] Attached reference image {reference['reference_id']} for goal '{session.goal}'")
    return _as_response(
        action="attach",
        goal=session.goal,
        references=_sorted_references(updated_active),
        message=f"Attached reference image '{reference['reference_id']}'.",
    )


async def handle_reference_images(
    ctx: Context,
    *,
    action: str,
    source_path: str | None = None,
    images: list[dict[str, Any]] | None = None,
    source_paths: list[str] | None = None,
    reference_id: str | None = None,
    label: str | None = None,
    notes: str | None = None,
    target_object: str | None = None,
    target_view: str | None = None,
    refresh_reference_understanding: _RefreshReferenceUnderstandingFn,
) -> ReferenceImagesResponseContract:
    """Handle the public reference-image facade against active and pending session stores."""

    normalized_action = str(action).lower()
    if normalized_action not in {"attach", "list", "remove", "clear"}:
        return _as_response(
            action="list",
            goal=None,
            references=[],
            error="action must be attach, list, remove, or clear",
        )

    store = _reference_store(await get_session_capability_state_async(ctx))

    if normalized_action == "list":
        return _as_response(
            action="list",
            goal=store.session.goal,
            references=_sorted_references(store.visible_references),
        )
    if normalized_action == "clear":
        return await _clear_reference_images(
            ctx,
            store=store,
            refresh_reference_understanding=refresh_reference_understanding,
        )
    if normalized_action == "remove":
        return await _remove_reference_image(
            ctx,
            store=store,
            reference_id=reference_id,
            refresh_reference_understanding=refresh_reference_understanding,
        )
    return await _attach_reference_image(
        ctx,
        store=store,
        source_path=source_path,
        images=images,
        source_paths=source_paths,
        label=label,
        notes=notes,
        target_object=target_object,
        target_view=target_view,
        refresh_reference_understanding=refresh_reference_understanding,
    )
