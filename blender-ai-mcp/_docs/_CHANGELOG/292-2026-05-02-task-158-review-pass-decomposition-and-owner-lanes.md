# 292. TASK-158 review pass decomposition and owner lanes

Date: 2026-05-02

## Summary

- split `TASK-158-04` into three narrower physical leaves so contract/parser,
  session/checkpoint threading, and guided-visibility/transport work no longer
  sit in one oversized execution slice
- aligned `TASK-158-04` wording with the roadmap-owned `understanding_id`
  naming and the current owner test lanes for intake, guided state, visibility,
  and transport parity
- re-anchored `TASK-158-05` to the shipped optional-perception seams in
  `vision/config.py`, `vision/runtime.py`, `areas/reference.py`,
  `test_vision_runtime_config.py`, `test_reference_images.py`, and the current
  compare/iterate envelope behavior instead of a parallel abstract registry
- added local `Status / Board Update` guidance to the active `TASK-158` child
  slices so closeout expectations are explicit at the file that implementers
  will actually close

## Validation

- `git diff --check`
- `rg -n "summary_id|OptionalEvidence|test_optional_perception_adapter_registry|test_optional_perception_evidence_boundary" _docs/_TASKS/TASK-158*.md`
  - result on this machine: no hits
- `rg -n "test_vision_runtime_config.py|test_guided_surface_contract_parity.py|test_guided_gate_state_transport.py|Status / Board Update" _docs/_TASKS/TASK-158*.md`
  - result on this machine: expected hits only in the refined task slices
