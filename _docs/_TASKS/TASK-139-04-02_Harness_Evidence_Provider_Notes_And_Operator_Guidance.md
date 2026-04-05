# TASK-139-04-02: Harness Evidence, Provider Notes, and Operator Guidance

**Parent:** [TASK-139-04](./TASK-139-04_Regression_Harness_And_Documentation_For_Contract_Profiles.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High

## Objective

Keep the provider/model notes table, operator guidance, and harness evidence in
sync with the new contract-profile architecture and with the difference between
scored evidence and operator-reported failures.

## Business Problem

Operator reports are useful and should be captured, but they should not be
presented as formal ranking evidence unless they are reproduced in the harness.

At the same time, the docs need to say clearly:

- which provider/model paths are recommended
- which are unstable
- whether the instability appears transport-related, contract-profile-related,
  or model-behavior-related

## Repository Touchpoints

- `scripts/vision_harness.py`
- `tests/unit/scripts/test_script_tooling.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `tests/e2e/vision/`

## Acceptance Criteria

- docs distinguish harness-ranked evidence from operator-reported observations
- provider/model notes call out contract-profile caveats where relevant
- the harness config surface and script coverage stay aligned with the
  documented provider/model guidance
- the harness plan includes richer assembled stage loops, not only simpler
  compare cases

## Leaf Work Items

- update harness config/build expectations so contract-profile-sensitive
  provider paths are represented explicitly
- update provider/model notes to mention contract-profile-sensitive failures
- define harness scenarios for richer assembled reference loops
- document how operator reports should be recorded before a model is promoted

## Tests To Add/Update

- `tests/unit/scripts/test_script_tooling.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on the parent regression/docs slice unless this leaf is
  promoted independently
- when this leaf closes, update the parent task summary so the harness-evidence
  and operator-guidance alignment is recorded explicitly
