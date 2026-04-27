# 217. Guided spatial scope and relation graphs

Date: 2026-04-07

## Summary

Completed TASK-143 by shipping one explicit read-only spatial-state layer for
guided sessions: reusable scope/relation graph builders, public
`scene_scope_graph(...)` / `scene_relation_graph(...)` tools, bounded guided
disclosure, and matching regression/docs coverage.

## What Changed

- added `server/application/services/spatial_graph.py` as the shared builder
  for:
  - structural scope derivation
  - anchor selection
  - deterministic object-role hints
  - compact pair-relation derivation
- extended `assembled_target_scope` with explicit `object_roles`
- added public read-only scene artifacts:
  - `scene_scope_graph(...)`
  - `scene_relation_graph(...)`
- registered router metadata for both new scene tools and routed them through
  the normal handler/dispatcher path
- kept the guided bootstrap surface small while allowing on-demand spatial
  graph access through inspect visibility and creature handoff supporting tools
- updated the staged reference loop so `truth_bundle`, `truth_followup`, and
  `correction_candidates` reuse the same relation vocabulary without embedding
  a heavyweight graph payload into the default compare/iterate contracts
- updated task files, board state, MCP/docs/prompt guidance, and Blender-backed
  regression coverage to describe the shipped scope/relation graph layer

## Why

The repo already had strong truth primitives, but guided sessions still had to
reconstruct structural anchors and pair relations from scattered measurements,
assertions, and prose. Shipping explicit scope/relation graph artifacts makes
that spatial state directly legible to LLMs without reopening the large-catalog
or heavyweight-stage-payload problems that `llm-guided` was designed to avoid.
