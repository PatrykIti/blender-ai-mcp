# TASK-121-01-02: Vision, Policy, and Truth Boundary Enforcement

**Parent:** [TASK-121-01](./TASK-121-01_Vision_Assistant_Boundary_And_Delivery_Contract.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Keep the vision layer within a strictly bounded role: visual interpretation,
not router policy or correctness truth.

---

## Implementation Direction

- explicitly forbid vision assistance from:
  - overriding router safety/policy decisions
  - claiming geometric correctness without deterministic checks
  - acting as the primary discovery/catalog authority
  - acting on one ad hoc viewport screenshot as if it were sufficient truth about the scene
- require vision outputs to recommend deterministic follow-up checks when
  correctness matters
- require macro/workflow integrations to pass:
  - deterministic before/after capture bundles
  - active-goal text
  - reference-image context when present
  - compact truth summaries (bbox/dimensions/gap/contact/alignment) when relevant
- keep the responsibility split aligned with
  `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

---

## Repository Touchpoints

- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`
- `server/adapters/mcp/sampling/`
- `tests/unit/adapters/mcp/`
- `_docs/_MCP_SERVER/README.md`

---

## Acceptance Criteria

- the vision layer has an explicit non-truth, non-policy boundary
- future integrations cannot quietly turn it into an authority it should not be
- the product does not regress into “single screenshot guessing” as the default vision path
