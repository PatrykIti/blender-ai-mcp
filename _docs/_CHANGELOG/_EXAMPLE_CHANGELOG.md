# 398. TASK-200 mesh bevel mega-tool action

Date: 2026-06-25

> Example changelog entry for `blender-ai-mcp`. It follows the repository's real
> format (see `AGENTS.md` → Changelog Policy): file name
> `<N>-<YYYY-MM-DD>-<kebab-slug>.md` (next integer, not zero-padded), `# N. Title`
> heading, a plain `Date:` line, a prose lede, then `## Changed` and
> `## Validation`. Copy this shape; do not copy the example content.

Added a deterministic `bevel` action to the `mesh_*` mega tool so LLM clients can
chamfer or round selected edges without raw `bpy` code. Edit-mode selection is
preserved across the operation. No external-provider egress was added; execution
stays on local Blender RPC. The standalone curve-bevel surface was intentionally
left out of scope and tracked as a follow-on task.

## Changed

- Added the `bevel` action contract in `server/domain/tools/mesh.py` with a typed
  parameter model and structured errors (`mesh_wrong_mode`, `mesh_no_selection`,
  `mesh_invalid_parameters`).
- Implemented the RPC-backed server handler and the addon-side bmesh execution,
  registered the new RPC action, and exposed it on the `mesh_*` mega tool.
- Added router metadata `mesh/mesh_bevel.json` so the action is router-aware.

## Validation

All validation passed on 2026-06-25:

- `PYTHONPATH=. poetry run pytest tests/unit/ -v`
  - `3650 passed`
- `git diff --check`
- `poetry run pre-commit run --all-files --show-diff-on-failure`
- `poetry run python scripts/run_e2e_tests.py`
  - mesh bevel E2E: selection preserved, expected face/edge counts
