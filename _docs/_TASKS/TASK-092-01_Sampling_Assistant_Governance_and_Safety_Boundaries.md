# TASK-092-01: Sampling Assistant Governance and Safety Boundaries

**Parent:** [TASK-092](./TASK-092_Server_Side_Sampling_Assistants.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-095](./TASK-095_LaBSE_Semantic_Layer_Boundaries.md)

---

## Objective

Define exactly where server-orchestrated sampling assistants are allowed and where they are forbidden by the repository's responsibility boundaries.

---

## Allowed First Use Cases

- inspection summarization
- repair suggestion drafting
- compact explanation of large structured diagnostics

## Forbidden First Use Cases

- autonomous geometry-destructive planning
- hidden substitution for router safety policy
- scene-truth decisions without inspection contracts
- detached background reasoning outside an active request

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-092-01-01](./TASK-092-01-01_Core_Sampling_Assistant_Governance_Safety.md) | Core Sampling Assistant Governance and Safety Boundaries | Core implementation layer |
| [TASK-092-01-02](./TASK-092-01-02_Tests_Sampling_Assistant_Governance_Safety.md) | Tests and Docs Sampling Assistant Governance and Safety Boundaries | Tests, docs, and QA |

---

## Acceptance Criteria

- assistant usage boundaries are explicit and aligned with the semantic/safety/truth split
