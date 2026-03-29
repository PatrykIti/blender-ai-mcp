"""Tests for the goal-scoped reference image MCP surface."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from server.adapters.mcp.areas.reference import reference_images
from server.adapters.mcp.session_capabilities import update_session_from_router_goal


@dataclass
class FakeContext:
    state: dict[str, object] = field(default_factory=dict)

    def get_state(self, key: str):
        return self.state.get(key)

    def set_state(self, key: str, value, *, serializable: bool = True) -> None:
        self.state[key] = value

    def info(self, message, logger_name=None, extra=None):
        return None


def test_reference_images_attach_without_active_goal_is_staged_for_next_goal(tmp_path, monkeypatch):
    image = tmp_path / "ref.png"
    image.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    result = asyncio.run(reference_images(ctx, action="attach", source_path=str(image), label="front_ref"))

    assert result.error is None
    assert result.goal is None
    assert result.reference_count == 1
    assert result.references[0].goal == "__pending_goal__"
    assert "pending reference image" in (result.message or "")

    state = update_session_from_router_goal(ctx, "low poly squirrel", {"status": "no_match"})
    assert state.reference_images is not None
    assert state.reference_images[0]["goal"] == "low poly squirrel"
    assert state.pending_reference_images is None


def test_reference_images_attach_list_remove_and_clear(tmp_path, monkeypatch):
    image = tmp_path / "ref.png"
    image.write_bytes(b"fake")
    monkeypatch.setenv("BLENDER_AI_TMP_INTERNAL_DIR", str(tmp_path / "internal"))
    monkeypatch.setenv("BLENDER_AI_TMP_EXTERNAL_DIR", str(tmp_path / "external"))

    ctx = FakeContext()
    update_session_from_router_goal(ctx, "rounded housing", {"status": "ready"})

    attached = asyncio.run(
        reference_images(
            ctx,
            action="attach",
            source_path=str(image),
            label="main_ref",
            notes="front silhouette",
            target_object="Housing",
            target_view="front",
        )
    )

    assert attached.reference_count == 1
    ref = attached.references[0]
    assert ref.goal == "rounded housing"
    assert ref.label == "main_ref"
    assert ref.target_object == "Housing"
    assert ref.stored_path.endswith(".png")

    listed = asyncio.run(reference_images(ctx, action="list"))
    assert listed.reference_count == 1
    assert listed.references[0].reference_id == ref.reference_id

    removed = asyncio.run(reference_images(ctx, action="remove", reference_id=ref.reference_id))
    assert removed.reference_count == 0
    assert removed.removed_reference_id == ref.reference_id

    attached_again = asyncio.run(reference_images(ctx, action="attach", source_path=str(image)))
    assert attached_again.reference_count == 1
    cleared = asyncio.run(reference_images(ctx, action="clear"))
    assert cleared.reference_count == 0
