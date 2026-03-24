# TASK-114-03: Metadata, Discovery, and Public Surface Audit

**Parent:** [TASK-114](./TASK-114_Existing_Tool_Surface_Audit_And_Alignment.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Audit whether router metadata, discovery wording, and public-vs-hidden surface behavior still encode old assumptions.

---

## Repository Touchpoints

- `server/router/infrastructure/tools_metadata/**`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/transforms/*`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

---

## Planned Work

- classify metadata drift
- classify discovery/search wording drift
- find mismatches between policy-level surface intent and actual public descriptions/examples

---

## Acceptance Criteria

- metadata/discovery mismatches are explicitly enumerated before code-fix waves begin
