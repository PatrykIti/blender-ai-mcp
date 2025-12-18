# Releasing

This project uses GitHub Actions + `python-semantic-release` to:
- bump versions
- create Git tags + GitHub Releases
- attach the Blender addon ZIP artifact
- build and push a Docker image to GHCR

## Prerequisites (before merge to `main`)

Locally (recommended):
- Run unit tests:
  ```bash
  PYTHONPATH=. poetry run pytest tests/unit/ -v
  ```
- Run E2E tests (requires Blender):
  ```bash
  python3 scripts/run_e2e_tests.py
  ```

## Versioning

Versioning is driven by **conventional commits** via `python-semantic-release`.
Configuration lives in:
- `pyproject.toml` (`[tool.semantic_release]`)

## CI Release Pipeline

Workflow file:
- `.github/workflows/release.yml`

On **push to `main`**:
1. `build-and-test`: runs unit tests and builds `outputs/blender_ai_mcp.zip`
2. `release`: runs `python-semantic-release` to tag + publish a GitHub Release
3. `docker`: checks out the latest tag, builds and pushes Docker images:
   - `ghcr.io/<owner>/blender-ai-mcp:<tag>`
   - `ghcr.io/<owner>/blender-ai-mcp:latest`

## Manual Docker Rebuild (Workflow Dispatch)

`release.yml` supports `workflow_dispatch` with `manual_tag`:
- `latest` → build/push `latest`
- `1.2.3` → checkout tag `1.2.3` and build/push that version + `latest`

## Addon Build Notes

Addon packaging is handled by:
- `scripts/build_addon.py`

It produces:
- `outputs/blender_ai_mcp.zip`

