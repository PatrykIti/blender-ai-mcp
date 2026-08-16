# TASK-069: Repo Professionalization - SECURITY/SUPPORT/CoC + Support Matrix + Release/Dev Docs

**Status**: ✅ Done  
**Priority**: 🟡 Medium  
**Category**: Repo / Docs / Community
**Completed**: 2025-12-18

## Objective

Make the repository feel **production-grade** for external contributors and adopters by adding standard community/security docs, clarifying the supported Blender/Python versions, and documenting the release/development workflow in one obvious place.

## Current State (Audit)

- ✅ GitHub templates exist:
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - `.github/ISSUE_TEMPLATE/bug_report.md`
  - `.github/ISSUE_TEMPLATE/feature_request.md`
- ❌ Missing common repo standards files:
  - `SECURITY.md`
  - `CODE_OF_CONDUCT.md`
  - `SUPPORT.md`
  - `CODEOWNERS`
- ⚠️ Support matrix is not explicit/consistent:
  - Some docs mention **Blender 4.0+**, but the project is currently tested on **Blender 5.0**.
- ⚠️ Release/dev info exists but is scattered:
  - E2E runner and addon build are documented under `_docs/_TESTS/README.md`
  - Release automation exists in `.github/workflows/release.yml` + `python-semantic-release`

## Deliverables

### 1) Add `SECURITY.md`

Include:
- how to report vulnerabilities (private channel + what details to include)
- what is considered a vulnerability vs bug
- version scope (what versions are supported)

### 2) Add `CODE_OF_CONDUCT.md`

Use a standard template (e.g., Contributor Covenant) and keep it short/clear.

### 3) Add `SUPPORT.md`

Document:
- where to ask questions vs file bugs
- required diagnostic info for issues (OS, Blender version, Python version, LOG_LEVEL, ROUTER_ENABLED, minimal repro, logs)

### 4) Add `CODEOWNERS`

Add `.github/CODEOWNERS` with at least:
- `* @PatrykIti`

### 5) Add a Support Matrix section (root docs)

Decide and document:
- **Supported Blender version** (currently tested on Blender **5.0+**)
- supported Python version(s) for the server (project uses `requires-python` in `pyproject.toml`)
- OS expectations / known limitations

Update any docs that claim “Blender 4.0+” if the official stance is “5.0+ tested”.

Suggested places to update:
- `README.md` (new “Support Matrix” section)
- `_docs/_ROUTER/QUICK_START.md` (version line)
- `blender_addon/__init__.py` (`bl_info["blender"]` min version) — if we want the addon to declare 5.0+ explicitly

### 6) Add “Release & Development” docs

Create a small doc set (suggested):
- `_docs/_DEV/README.md` (entrypoint)
- `_docs/_DEV/RELEASING.md` (release flow)

Must include:
- how to set up local dev env (`poetry install`)
- how to build addon zip (`python scripts/build_addon.py`)
- how to run E2E (`python scripts/run_e2e_tests.py`)
- how releases are made (conventional commits / semantic-release + `release.yml` behavior)

Optionally link these from:
- `CONTRIBUTING.md`
- `README.md`

## Acceptance Criteria

- [x] `SECURITY.md`, `CODE_OF_CONDUCT.md`, `SUPPORT.md` exist and are linked from the repo root.
- [x] `.github/CODEOWNERS` exists and assigns code owner(s).
- [x] `README.md` contains a clear Support Matrix (Blender/Python/OS).
- [x] Version statements are consistent across docs (no contradictory “4.0+” vs “5.0+ tested”).
- [x] `_docs/_DEV/*` documents build/release/E2E in one place.

## Implementation Completed

### Files Added

- `SECURITY.md`
- `SUPPORT.md`
- `CODE_OF_CONDUCT.md`
- `.github/CODEOWNERS`
- `_docs/_DEV/README.md`
- `_docs/_DEV/RELEASING.md`

### Files Updated

- `README.md` (Support Matrix + links to Support/Security/CoC)
- `CONTRIBUTING.md` (updated contribution workflow + dev/release doc links)
- `_docs/_ROUTER/QUICK_START.md` (updated prerequisites: Blender 5.0 tested, Python 3.11+ for router)
