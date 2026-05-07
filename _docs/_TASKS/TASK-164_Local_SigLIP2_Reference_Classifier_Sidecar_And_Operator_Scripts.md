# TASK-164: Local SigLIP2 Reference Classifier Sidecar And Operator Scripts

**Status:** ✅ Done
**Priority:** 🔴 High
**Follow-on After:** [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)
**Objective:** Ship one repo-local `generic_sidecar` reference-classifier endpoint plus operator scripts so MCP users can run the optional classifier path alongside the main server without inventing their own service wrapper.
**Repository Touchpoints:** `scripts/reference_classifier_sidecar.py`, `scripts/run_reference_classifier_sidecar.sh`, `scripts/run_streamable_openrouter.sh`, `tests/unit/scripts/test_script_tooling.py`, `server/adapters/mcp/vision/reference_support.py`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`, `_docs/_TASKS/README.md`
**Acceptance Criteria:** users can start a local sidecar from `./scripts/`; the endpoint accepts the repo’s current classifier payload and returns bounded `classification_scores`; docs explain how to run it with the MCP server on local host and Docker-guided paths.

## Completion Summary

- added a repo-local `generic_sidecar` classifier endpoint in
  `scripts/reference_classifier_sidecar.py`
- added `scripts/run_reference_classifier_sidecar.sh` so operators can start
  the sidecar with one command and reuse classifier env names already familiar
  from the MCP server config
- kept the wire contract aligned with the current MCP classifier path:
  `POST /classify` accepts the repo payload with `references[*].image_path` and
  returns bounded `classification_scores`
- used a local SigLIP2 default (`google/siglip2-base-patch16-224`) that stays
  macOS-friendly through `transformers` + `torch`
- documented both local-process and Docker-guided MCP wiring paths

## Implementation Notes

- keep the wire contract aligned with the current `generic_sidecar` path in
  `server/adapters/mcp/vision/reference_support.py`; do not invent a second
  request/response shape
- the initial local implementation should target macOS-friendly
  `transformers` + `torch` + SigLIP2, not a new MLX or llama.cpp serving stack
- keep the endpoint bounded to `POST /classify` and one small health/readiness
  surface
- reuse current classifier config env names where that improves operator
  ergonomics, but keep sidecar-local bind/runtime flags explicit
- the output should stay support-only and label-scoped; do not move gate or
  tool-unlock authority into the sidecar

## Pseudocode

```python
load_siglip2_classifier_once()
serve_post_classify()
extract_reference_images_from_repo_payload()
score_fixed_bounded_label_space()
return_top_classification_scores()
```

## Runtime / Security Contract Notes

- visibility level: local/operator-owned support sidecar only
- read-only behavior: no Blender mutation, no file writes outside normal model
  cache behavior
- bind host/port must stay explicit so Docker-guided MCP users can route to the
  sidecar safely
- do not log raw image bytes, provider secrets, or full local private paths in
  normal success responses

## Tests To Add/Update

- `tests/unit/scripts/test_script_tooling.py`
- targeted server-side contract/unit checks only when the generic sidecar
  request/response shape changes

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
- `_docs/_TASKS/README.md`

## Changelog Impact

- covered by [322. TASK-164 local SigLIP2 classifier sidecar and operator scripts](../_CHANGELOG/322-2026-05-07-task-164-local-siglip2-classifier-sidecar-and-operator-scripts.md)

## Status / Board Update

- tracked as a standalone board-level follow-on after `TASK-163`
- moved to `✅ Done` in `_docs/_TASKS/README.md`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit -q`
- `bash -n scripts/run_reference_classifier_sidecar.sh`
- optional live smoke after install with vision deps:
  - `poetry run python scripts/reference_classifier_sidecar.py --help`
