# 197. Hybrid loop pairing anchor and canonical check quality

Date: 2026-04-02

## Summary

Closed the first post-`TASK-122` hybrid-loop quality follow-on by improving
primary anchor selection for assembled scopes and canonicalizing vision-side
recommended check tool names.

## What Changed

- collection/object-set assembled scopes now avoid obviously accessory-first
  anchors when a more structural target is present
- this reduces awkward pair labels such as `EarLeft -> Head` when the intended
  structure should anchor on `Head` or `Body`
- vision parsing now:
  - normalizes a small set of common follow-up aliases onto canonical MCP tool
    ids
  - drops invented / non-canonical tool labels instead of preserving them
- added unit coverage for:
  - structural-anchor selection when accessory names appear first
  - canonicalization of common check aliases
  - dropping non-canonical free-form check names

## Why

Real hybrid-loop outputs were structurally correct but still low quality in two
ways: poor pairing anchors and pseudo-tool names in follow-up checks. This
follow-on tightens both issues without reopening the larger loop architecture.
