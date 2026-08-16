# 126 - 2026-03-20: Runtime Boundaries + FastMCP 3.x strategy docs

## Summary

Documented the intended runtime responsibility split for the project:

- FastMCP as the platform/presentation layer
- LaBSE as the semantic retrieval/generalization layer
- Router as the deterministic policy/safety layer
- Inspection/assertion tools as the Blender truth layer

This update also aligns project docs with the planned FastMCP 3.x migration work and clarifies that semantic confidence must not be treated as proof of Blender correctness.

## Updated docs

- Added `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- Updated `README.md`
- Updated `ARCHITECTURE.md`
- Updated `CONTRIBUTING.md`
- Updated `_docs/_MCP_SERVER/README.md`
- Updated `_docs/_MCP_SERVER/clean_architecture.md`
- Updated `_docs/_ADDON/README.md`
- Updated `_docs/_ROUTER/README.md`
- Updated `_docs/_ROUTER/ROUTER_HIGH_LEVEL_OVERVIEW.md`
- Updated `_docs/_ROUTER/ROUTER_ARCHITECTURE.md`
- Updated `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- Updated `AGENTS.md`
