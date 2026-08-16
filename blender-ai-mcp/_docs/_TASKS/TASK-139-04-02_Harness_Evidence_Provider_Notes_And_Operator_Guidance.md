# TASK-139-04-02: Harness Evidence, Provider Notes, and Vision-Contract-Profile Operator Guidance

**Parent:** [TASK-139-04](./TASK-139-04_Regression_Harness_And_Documentation_For_Contract_Profiles.md)
**Depends On:** [TASK-139-04-01](./TASK-139-04-01_Unit_And_Integration_Coverage_For_Profile_Routing.md)
**Status:** ✅ Done
**Priority:** 🟠 High

**Completion Summary:** Harness config, launch helpers, provider notes, MCP
client examples, and vision operator docs now describe the same external
contract-profile model, including explicit override knobs, auto-match
behavior, and the distinction between harness-ranked evidence and
operator-reported instability.

## Objective

Keep the provider/model notes table, operator guidance, and harness evidence in
sync with the new vision-contract-profile architecture and with the difference
between scored evidence and operator-reported failures.

This leaf does not own the automated runtime-routing regression seam. Focused
unit plus targeted compare-loop integration/e2e coverage stays on
`TASK-139-04-01`.

## Business Problem

Operator reports are useful and should be captured, but they should not be
presented as formal ranking evidence unless they are reproduced in the harness.

At the same time, the docs need to say clearly:

- which provider/model paths are recommended
- which are unstable
- whether the instability appears transport-related,
  vision-contract-profile-related, or model-behavior-related

## Repository Touchpoints

- `scripts/vision_harness.py`
- `scripts/run_streamable_openrouter.sh`
- `tests/unit/scripts/test_script_tooling.py`
- `_docs/_VISION/README.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `README.md`
- `tests/e2e/vision/`

## Acceptance Criteria

- docs distinguish harness-ranked evidence from operator-reported observations
- provider/model notes call out vision-contract-profile caveats where relevant
- the harness config surface and script coverage stay aligned with the
  documented provider/model guidance
- operator-facing launch helpers such as `scripts/run_streamable_openrouter.sh`
  stay aligned with the same vision-contract-profile-sensitive env/config story
  documented in runtime docs and client examples
- vision eval/operator-guidance docs stay aligned with the same
  vision-contract-profile-sensitive evidence story as provider notes and
  harness guidance
- the harness plan includes richer assembled stage loops, not only simpler
  compare cases

## Leaf Work Items

- update harness config/build expectations so vision-contract-profile-sensitive
  provider paths are represented explicitly
- update provider/model notes to mention vision-contract-profile-sensitive
  failures
- update client-config examples so local and Docker snippets reflect the same
  vision-contract-profile-sensitive env/config guidance as the runtime docs
- update operator-facing launch helpers so shell entrypoints reflect the same
  vision-contract-profile-sensitive env/config guidance as the runtime docs
- update the linked vision eval/operator-guidance docs so richer assembled-loop
  review guidance reflects the same vision-contract-profile-sensitive evidence
  model
- define harness scenarios for richer assembled reference loops
- document how operator reports should be recorded before a model is promoted

## Tests To Add/Update

- `tests/unit/scripts/test_script_tooling.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md`
- `_docs/_VISION/REFERENCE_GUIDED_CREATURE_TEST_PROMPT.md`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `README.md`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on the parent regression/docs slice unless this leaf is
  promoted independently
- when this leaf closes, update the parent task summary so the harness-evidence
  and operator-guidance alignment is recorded explicitly
