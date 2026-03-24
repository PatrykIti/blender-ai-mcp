# TASK-114-04-02: Measurement and Assertion Gap Register

**Parent:** [TASK-114-04](./TASK-114-04_Verification_And_Truth_Model_Audit.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The first measure/assert gap register is now explicit and ready to drive the first implementation wave after the audit.

---

## Objective

Produce the explicit gap register for the first measure/assert atomic family.

---

## Exact Audit Targets

- current inspection tool set
- current geometry/scene verification patterns in prompt docs
- current bounding-box/origin/hierarchy usage patterns

---

## Required Output

- list of missing atomics:
  - distance
  - dimensions
  - gap/contact
  - overlap/intersection
  - alignment
  - proportion
  - symmetry
  - containment
- likely first implementation order

---

## Acceptance Criteria

- the first measure/assert implementation wave can start directly from this audit output

## Gap Register

### Missing P0 Atomics

- `scene_measure_distance`
- `scene_measure_dimensions`
- `scene_measure_gap`
- `scene_measure_overlap`
- `scene_measure_alignment`

### Missing P1 Atomics

- `scene_assert_contact`
- `scene_assert_dimensions`
- `scene_assert_symmetry`
- `scene_assert_containment`
- `scene_assert_proportion`

### Likely First Implementation Order

1. distance
2. dimensions
3. gap/contact
4. alignment
5. overlap/intersection

These five would cover the biggest proportion/fit/connection failures the current LLM flows still miss.
