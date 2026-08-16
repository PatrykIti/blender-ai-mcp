# TASK-122-02-05-01: Public Naming Generalization For Chain Arc Adjustment

**Parent:** [TASK-122-02-05](./TASK-122-02-05_macro_adjust_segment_chain_arc.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** The chain-arc tool was generalized immediately from creature-biased public naming to `macro_adjust_segment_chain_arc`. The public tool now fits non-tail ordered segment chains without relying on hidden implementation semantics.

## Objective

Generalize the public naming of the chain-arc macro so it works cleanly beyond
tail-specific workflows.

## Acceptance Criteria

- the public tool name is generic enough for non-tail segment-chain use cases
- docs and tests are aligned with the generalized naming
