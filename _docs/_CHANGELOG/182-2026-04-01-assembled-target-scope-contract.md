# 182. Assembled target scope contract

Date: 2026-04-01

## Summary

Started the `TASK-122` reliability wave by adding a canonical assembled-target
scope contract for stage compare and iterate flows.

## What Changed

- added a structured `assembled_target_scope` contract for assembled-model
  targeting
- wired that scope into `reference_compare_stage_checkpoint(...)` and
  `reference_iterate_stage_checkpoint(...)` responses
- classified current targeting modes into:
  - `single_object`
  - `object_set`
  - `collection`
  - `scene`
- added unit coverage for:
  - the new scene contract types
  - stage compare response scope classification
  - capture-bundle compatibility defaults

## Why

The upcoming `TASK-122` truth-bundle and hybrid-loop work needs one stable
scope envelope for assembled targets. Without it, downstream consumers still
have to infer semantics ad hoc from `target_object`, `target_objects`, and
`collection_name`.
