# 172. Multi-object reference loop scope

Date: 2026-03-30

## Summary

Extended the new reference correction loop so it can evaluate assembled
multi-part models without being forced to target only one mesh.

## What Changed

- `reference_compare_stage_checkpoint(...)` now accepts:
  - `target_objects=[...]`
  - `collection_name="..."`
  - or no target scope for a full-scene/full-silhouette compare
- `reference_iterate_stage_checkpoint(...)` now supports the same scope model
- collection-aware compare resolves collection members through the existing
  collection handler
- multi-object stage capture now isolates the whole resolved object set without
  forcing autofocus onto a single mesh

## Why

The first loop version worked technically, but on multi-part builds such as the
low-poly squirrel it could be too narrow when pointed at only `Squirrel_Body`.
This change lets the loop look at the whole assembled silhouette instead of one
piece at a time.
