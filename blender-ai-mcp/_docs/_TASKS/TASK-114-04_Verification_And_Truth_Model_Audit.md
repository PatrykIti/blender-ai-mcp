# TASK-114-04: Verification and Truth Model Audit

**Parent:** [TASK-114](./TASK-114_Existing_Tool_Surface_Audit_And_Alignment.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The verification/truth-model audit is complete. The repo already has a useful before/after/snapshot base, but still lacks the deterministic measure/assert atomics needed to turn visual verification from a discipline into a productized truth layer.

---

## Objective

Audit the current tool surface for missing or misleading verification/truth cues before measure/assert tools are added.

---

## Repository Touchpoints

- `server/adapters/mcp/areas/*.py`
- `_docs/_PROMPTS/*.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

---

## Planned Work

- identify tools that imply “looks correct” without any verification discipline
- identify places where vision wording could be mistaken for truth
- identify where measure/assert hooks will need to be inserted later

---

## Acceptance Criteria

- the repo has a concrete verification/truth audit before measure/assert implementation starts

## Audit Findings

### Existing Strengths

- `scene_snapshot_state`
- `scene_compare_snapshot`
- `scene_get_viewport`
- `extraction_render_angles`
- prompt guidance already encourages snapshots and visual QA in several places

### Main Gaps

- there is still no explicit measure/assert atomic family for:
  - distance
  - dimensions
  - gap/contact
  - overlap/intersection
  - alignment
  - proportion
  - symmetry
  - containment
- because of that, prompts still have to simulate some checks manually with bounding boxes and prose reasoning

### Risk

- current flows can verify “better than before”, but not yet with a compact deterministic truth layer
- vision wording is much better after `TASK-113`, but the repo still lacks the concrete atomics that would let vision defer to assertions instead of judgment calls
