# TASK-165-02-01: Interactive Profile Selection And Runtime Wiring

**Status:** 🚧 In Progress
**Priority:** 🔴 High
**Parent:** [TASK-165-02](./TASK-165-02_Interactive_Run_MCP_Server_Wizard_And_Script_Modularization.md)
**Related:** [TASK-167](./TASK-167_Cross_Module_Debug_Profile_Registry_And_Runtime_Logging.md)
**Objective:** Implement the interactive prompts that decide which runtime/profile paths the current launcher should wire together, starting from the shipped `run_mcp_server.py` seam and its current Docker-guided OpenRouter plus optional classifier-sidecar path.
**Repository Touchpoints:** `scripts/run_mcp_server.sh`, `scripts/run_mcp_server.py`, `scripts/run_streamable_openrouter.sh`, `scripts/RUN_MCP_SERVER.md`, `scripts/_RUN_DOCKER_MCP.md`, script helper modules under `scripts/`, `tests/unit/scripts/test_script_tooling.py`
**Acceptance Criteria:** the launcher can guide the operator through the current supported macOS-first runtime path, derive a concrete final launch plan from the real `run_mcp_server.py` owner seam, and remain extensible for adjacent selector/runtime follow-ons without inventing a parallel prompt/plan surface.

## Implementation Notes

- current live owner seam is `scripts/run_mcp_server.py`; task wording should
  follow the existing prompt/plan flow there before proposing broader future
  profile matrices
- current shipped path is the Docker-guided OpenRouter launcher with optional
  classifier-sidecar decisions; if broader local/MLX matrices return later,
  they should be explicit follow-on expansion rather than assumed baseline here
- if the user declines a prerequisite install or update, the derived runtime
  plan must adapt rather than pretending the declined feature is available
- print the final plan before launch so the user can see the resolved command,
  endpoints, and enabled options
- keep the runtime/profile wiring extensible enough that the central `TASK-167`
  debug selector can be passed through this same launcher seam instead of
  inventing a parallel launcher-specific debug contract
- the shared debug-selector overlap landed on 2026-05-13 under
  [TASK-167](./TASK-167_Cross_Module_Debug_Profile_Registry_And_Runtime_Logging.md);
  the remaining launcher-family work here stays open
- if the shared debug-selector pass-through changes again here, preserve the
  landed `TASK-167` contract instead of reopening a launcher-only variant

## Current Owner / Likely Edit Map

| Path | Current owner seam | Likely edit anchors | Why this leaf owns it |
|------|--------------------|---------------------|-----------------------|
| `scripts/run_mcp_server.py` | interactive launcher prompt/plan orchestration | current prompt flow and final plan assembly | this is the canonical owner for the current runtime/profile selection path |
| `scripts/run_streamable_openrouter.sh` | Docker-guided OpenRouter env pass-through | current container/env wrapper | the shared runtime plan still terminates at this shipped launcher seam |
| `scripts/run_mcp_server.sh` | operator shell entrypoint | current wrapper seam | the derived plan must still reach the real shell entrypoint operators run |
| `scripts/RUN_MCP_SERVER.md` | colocated launcher runbook | current operator doc seam | launcher docs must stay aligned with prompt and plan behavior |
| `scripts/_RUN_DOCKER_MCP.md` | Docker helper runbook | current Docker snippets | the overlapping Docker launch surface must stay aligned when the shared seam changes |
| `tests/unit/scripts/test_script_tooling.py` | launcher/script contract lane | current script env tests | prompt-plan wiring and env pass-through should prove themselves here |

## Pseudocode

```python
choices = collect_runtime_and_prerequisite_choices()
plan = build_launch_plan_from_current_script_owners(choices)

if choices.debug_selector:
    plan.env["BLENDER_AI_DEBUG"] = choices.debug_selector

print_launch_plan(plan)
launch(plan)
```

## Runtime / Security Contract Notes

- the printed launch plan must reflect declined prerequisites honestly instead
  of implying unavailable features are active
- no secrets or raw tokens should be echoed in prompt summaries or final plan
  output
- launcher pass-through must preserve current runtime defaults when optional
  selectors such as the shared debug selector are unset

## Tests To Add/Update

- `tests/unit/scripts/test_script_tooling.py`

## Docs To Update

- `scripts/RUN_MCP_SERVER.md`
- `scripts/_RUN_DOCKER_MCP.md`
- if the shared debug-selector launcher seam changes materially, update the
  `TASK-167` family docs in the same branch

## Changelog Impact

- if this seam is advanced only through the `TASK-167` debug-selector overlap,
  fold the historical note into
  [TASK-167-03-02](./TASK-167-03-02_Debug_Profile_Docs_Board_Changelog_And_Final_Proof.md)
- otherwise keep final history ownership with the eventual `TASK-165` family
  closeout

## Validation Commands

- `git diff --check`
- `bash -n scripts/run_streamable_openrouter.sh scripts/run_mcp_server.sh`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`

## Status / Board Update

- stays nested under `TASK-165-02`
- if the shared launcher seam changes here, keep the landed `TASK-167` debug
  contract aligned and update `_docs/_TASKS/README.md` only if promoted board
  state changes
