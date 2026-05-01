# TASK-158-02: Creature Gate Truth Boundary Alignment

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-158](./TASK-158_Vision_And_Creature_Gate_Boundary_Doc_Alignment.md)
**Category:** Documentation / Creature Gate Boundary
**Estimated Effort:** Small

## Objective

Align the creature reconstruction task docs with the `TASK-157` rule that
Vision, reference, and perception outputs are advisory proposal/support context,
while scene, spatial, mesh, assertion, and verifier evidence owns gate status
and final completion truth.

## Repository Touchpoints

| Path / Module | Expected Change |
|---------------|-----------------|
| `_docs/_TASKS/TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md` | Replace reference/perception truth wording with verifier-owned truth |
| `_docs/_TASKS/TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md` | Replace standalone reference-evidence wording with normalized gate evidence and verifier-supported support refs |
| `_docs/_TASKS/TASK-157_Goal_Derived_Quality_Gates_And_Deterministic_Verification.md` | Read-only source of the generic gate/verifier boundary |

## Implementation Notes

- `TASK-135` should remain the domain consumer. Do not move creature-specific
  relation policy into `TASK-157`.
- Vision Mode may define labels, relation vocabulary, and candidate findings,
  but it must not decide true attachment or cleanup status by itself.
- Shape-profile child gates in `TASK-135-03` should come from normalized gate
  evidence and verifier-supported support refs.
- Preserve the low-poly creature product goal; only tighten authority wording.

## Runtime / Security Contract Notes

- This is a docs-only cleanup. It must not change guided runtime behavior,
  public MCP parameters, router metadata, visibility policy, or verifier code.
- Stdio and Streamable HTTP behavior must remain unchanged.
- No provider call, perception sidecar activation, SAM/CLIP/SigLIP adapter, or
  model download is part of this task.
- Documentation examples must not include raw provider payloads, secrets, local
  private paths, or unredacted debug transcripts.
- The cleanup must preserve verifier-owned gate truth: creature Vision Mode may
  propose relation findings, but scene/spatial/mesh/assertion evidence,
  evaluated by the quality-gate verifier, owns pass/fail status.

## Line-Level Targets

| Range | Required Work |
|-------|---------------|
| `_docs/_TASKS/TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md:68-77` | Replace pass/fail authority wording with scene/spatial/mesh/assertion/verifier truth |
| `_docs/_TASKS/TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md:162-183` | Rewrite Vision Mode true-error wording as advisory relation findings bound by verifier/spatial/assertion policy |
| `_docs/_TASKS/TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md:90-98` | Replace `reference evidence requires them` with normalized gate evidence and verifier-supported support refs |

## Rewrite Pattern

```text
Before:
deterministic scene/spatial/mesh/reference evidence decides whether the gate passed

After:
scene/spatial/mesh/assertion evidence, evaluated by the quality-gate verifier,
decides whether the gate passed; reference and perception outputs may seed
proposals or attach bounded support refs when the verifier strategy accepts
them.
```

```text
Before:
Vision defines true attachment errors and true cleanup/intersection errors.

After:
Vision records advisory relation-mismatch candidates; verifier, spatial, and
assertion policy bind those findings to attachment or cleanup gate status.
```

```text
Before:
shape-profile child gates apply where reference evidence requires them.

After:
shape-profile child gates come from normalized gate evidence and
verifier-supported support refs, not standalone reference evidence.
```

## Tests / Validation

- `git diff --check`
- `rg -n "scene/spatial/mesh/reference evidence|true attachment errors|true cleanup/intersection errors|reference evidence requires" _docs/_TASKS/TASK-135*.md`
  - expected result after completion: no hits, unless explicitly quoted as a
    before/after pattern in completed task notes
- `rg -n "scene/spatial/mesh/assertion|verifier-supported|advisory relation" _docs/_TASKS/TASK-135*.md`
  - expected result after completion: confirms replacement wording is present

## Docs To Update

- `_docs/_TASKS/TASK-135_Anatomy_Aware_Reference_Guided_Low_Poly_Creature_Reconstruction.md`
- `_docs/_TASKS/TASK-135-03_Low_Poly_Form_Refinement_Mesh_Window_And_Profile_Macros.md`

## Changelog Impact

- Roll this slice into the single
  `_docs/_CHANGELOG/279-...task-158-...completion.md` entry created during
  `TASK-158-03` closeout; do not create a separate child changelog entry.
  Changelog 278 remains the creation/plan entry.

## Acceptance Criteria

- TASK-135 no longer grants reference/perception evidence pass/fail authority.
- TASK-135 Vision Mode is advisory until verifier/spatial/assertion policy
  binds a finding to gate status.
- TASK-135-03 uses normalized gate evidence and verifier-supported refs for
  shape-profile gates.
