# 357. TASK-170 reference target canonicalization and support latency stabilization

Date: 2026-05-20

## Summary

TASK-170 closes the immediate follow-on drift that remained after `TASK-169`
on the squirrel front/side reference flow. This slice:

- canonicalizes common creature RU labels such as `body`, `head`, `ears`, and
  `tail` into the repo-owned creature vocabulary before summary, proposal, and
  gate-plan ingestion consume them
- keeps more specific labels such as `tail_tip` distinct instead of collapsing
  them into generic creature masses
- preloads the auto-start SigLIP2 reference-classifier sidecar before it
  reports healthy, so the first live attach request does not pay classifier
  cold-start latency
- runs optional classifier and segmentation support collection in parallel when
  both sidecars are enabled

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/scripts/test_script_tooling.py -q`
