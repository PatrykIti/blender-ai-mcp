# 322. TASK-164 local SigLIP2 classifier sidecar and operator scripts

Shipped a repo-local `generic_sidecar` classifier endpoint and matching
operator scripts for reference-understanding support experiments.

## What Changed

- added `scripts/reference_classifier_sidecar.py`
  - exposes `POST /classify`
  - accepts the current repo classifier payload with `references[*].image_path`
  - returns bounded `classification_scores`
- added `scripts/run_reference_classifier_sidecar.sh`
  - starts the sidecar with one command
  - reuses `VISION_REFERENCE_CLASSIFIER_MODEL` when that env is already set
  - prints both local-process and Docker-guided MCP endpoint wiring hints
- kept the initial local serving path macOS-friendly through
  `transformers` + `torch` and a SigLIP2 default model
- documented the operator flow in `README.md`, `_docs/_VISION/README.md`, and
  `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit -q`
- `bash -n scripts/run_reference_classifier_sidecar.sh scripts/run_streamable_openrouter.sh`
- `poetry run python scripts/reference_classifier_sidecar.py --help`
