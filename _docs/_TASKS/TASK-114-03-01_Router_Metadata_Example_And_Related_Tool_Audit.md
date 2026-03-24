# TASK-114-03-01: Router Metadata Example and Related-Tool Audit

**Parent:** [TASK-114-03](./TASK-114-03_Metadata_Discovery_And_Public_Surface_Audit.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Router metadata drift has been identified. The strongest remaining issue is not schema mismatch but older example/related-tool language that still implies low-level/manual-first pathways in some capability families.

---

## Objective

Audit tool metadata examples, descriptions, and related-tool links for drift against the new architecture.

---

## Exact Audit Targets

- `server/router/infrastructure/tools_metadata/**`

---

## Focus

- examples that still imply old public surfaces
- related-tools lists that point toward old low-level/manual-first paths
- descriptions that should now point toward macro/workflow/measure/assert patterns

---

## Acceptance Criteria

- metadata audit results are broken down by capability area instead of one giant list

## Audit Result

### Highest Drift Families

- `modeling`
  - several related-tool relationships still encode older “preferred low-level path” assumptions
- `mesh`
  - some metadata still points toward pre-`TASK-113` low-level choice patterns
- `extraction`
  - still strongly framed around older vision/extraction semantics without later measure/assert alignment

### Lower Drift Families

- `sculpt`
  - already significantly cleaned up by the region-tool replacement wave
- `scene`
  - relatively strong overall, but later examples should align more directly with measure/assert direction

### Fix Priorities

- `P0`: modeling + mesh metadata examples/related-tools
- `P1`: extraction metadata alignment with the new vision/truth boundary
