# TASK-167-03-02: Debug Profile Docs, Board, Changelog, And Final Proof

**Status:** ⏳ To Do
**Priority:** 🔴 High
**Parent:** [TASK-167-03](./TASK-167-03_Docker_Launcher_Docs_Validation_And_Closeout_For_Debug_Profiles.md)
**Objective:** Close the `TASK-167` family only after docs, board/changelog sync, and the final repo-standard proof bundle confirm that the shipped debug profiles are visible on the promised runtime surfaces.
**Repository Touchpoints:** `README.md`, `_docs/_MCP_SERVER/README.md`, `scripts/_RUN_DOCKER_MCP.md`, `_docs/_DEV/README.md`, `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/README.md`, new `_docs/_CHANGELOG/*`
**Acceptance Criteria:**
- operator docs explain `all` vs targeted scopes and match the shipped selector vocabulary
- board and changelog state are synchronized with the final implementation status
- final proof records the exact focused lanes plus the repo-standard validation bundle needed for a runtime-contract family

## Current Owner / Likely Edit Map

| Path | Current owner seam | Likely edit anchors | Why this leaf owns it |
|------|--------------------|---------------------|-----------------------|
| `README.md` | top-level operator docs | current Docker/OpenRouter sections | top-level operator guidance must expose the selector clearly |
| `_docs/_MCP_SERVER/README.md` | detailed MCP/operator docs | current Streamable/Docker sections | detailed selector/profile guidance belongs here |
| `scripts/_RUN_DOCKER_MCP.md` | launcher snippets/runbook | current Docker helper snippets | examples must match the shipped selector names and launcher contract |
| `_docs/_DEV/README.md` | developer workflow docs | runtime/dev debugging guidance | future implementers need one canonical debug-profile explanation here |
| `_docs/_TASKS/README.md` | board state | current promoted rows | board state must match the family closeout |
| `_docs/_CHANGELOG/README.md` and new `_docs/_CHANGELOG/*` | historical tracking | new final family entry | runtime-contract work needs proper historical closeout |

## Implementation Notes

- do not close this family on docs-only proof; the final validation record must
  include the runtime lanes required to trust the shipped selector behavior
- use this leaf as the single closeout owner so board/changelog/docs do not
  drift across multiple branches

## Runtime / Security Contract Notes

- docs must say clearly that debug logs are diagnostic and can be noisy under
  `all`
- examples must not encourage logging or copying secrets

## Tests To Add/Update

- docs/grep audits only as a supplement to the final runtime proof bundle

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `scripts/_RUN_DOCKER_MCP.md`
- `_docs/_DEV/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`
- new `_docs/_CHANGELOG/*`

## Changelog Impact

- add the historical `_docs/_CHANGELOG/*` entry when the first `TASK-167`
  implementation slice ships and index it in `_docs/_CHANGELOG/README.md`

## Status / Board Update

- remains nested under `TASK-167-03`
- owns final promotion/closure bookkeeping for the family

## Validation Commands

- `git diff --check`
- `bash -n scripts/run_streamable_openrouter.sh scripts/run_mcp_server.sh scripts/run_reference_classifier_sidecar.sh`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
- targeted grep/audit for accepted profile names across:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  - `scripts/_RUN_DOCKER_MCP.md`
  - `_docs/_DEV/README.md`
  - `_docs/_TASKS/README.md`
  - `_docs/_CHANGELOG/README.md`

## Validation Category

- final repo-standard proof bundle for a runtime-contract family
- `git diff --check`
