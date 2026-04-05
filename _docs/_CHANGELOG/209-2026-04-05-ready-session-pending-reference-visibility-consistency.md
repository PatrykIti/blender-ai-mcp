# 209. Ready-session pending reference visibility consistency

Date: 2026-04-05

## Summary

Hardened `reference_images(...)` so the ready-session merged visible-set
behavior stays consistent when explicit pending refs for another goal are still
present.

## What Changed

- updated ready-session `reference_images(action="remove"| "clear", ...)` to
  update both the active and pending stores when the visible reference set
  includes explicit pending refs
- kept the merged visible-list behavior consistent with those mutations, so a
  ref shown by `list` can also be removed cleanly from the same surface
- added focused regression coverage for:
  - removing a visible pending ref during a ready session while preserving the
    active ref
  - clearing a ready-session merged visible set without leaving broken pending
    records behind
- updated task lineage and public docs to describe the ready-session
  visible-set contract more precisely

## Why

The earlier blocked-session isolation fix stopped active refs from being copied
into pending storage, but ready-session `clear` still deleted files for the
merged visible set while only clearing active state. That left pending records
behind with dead `stored_path` values.

## Validation

- `poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
