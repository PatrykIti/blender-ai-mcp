# TASK-114-03: Metadata, Discovery, and Public Surface Audit

**Parent:** [TASK-114](./TASK-114_Existing_Tool_Surface_Audit_And_Alignment.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Metadata/discovery drift is now explicitly recorded. The main remaining problems are stale metadata examples/related-tools that still point toward old low-level/manual-first paths, and user-facing docs that still normalize “mega tool / context optimization” language instead of the new layered surface model.

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

## Audit Findings

### P0 Metadata Drift

- router metadata examples and related-tool links still reflect older action choices in multiple areas
- the sculpt metadata family is now much cleaner, but other families still use old “related tool” assumptions that predate `TASK-113`

### P0 Discovery/Public-Surface Drift

- public docs still contain older framing such as:
  - `LLM Context Optimization - Mega Tools`
  - “Total savings” language
  - “deprecated (now internal, use mega tools)” wording
- this keeps reinforcing the old context-compression story instead of the new:
  - macro/workflow-first
  - hidden atomic layer
  - explicit escape hatches

### P1 Technical Drift

- capability discovery docs still describe shaped public surfaces well, but the surrounding wording does not yet fully separate:
  - inventory existence
  - public-default exposure
  - hidden atomic eligibility

### Next Action

- rewrite the highest-signal public inventory/discovery wording first
- then audit metadata related-tools/examples by capability family
