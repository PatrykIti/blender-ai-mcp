# TASK-068: License - BUSL 1.1 Compliance + Apache Change License File

**Status**: ✅ Done  
**Priority**: 🔴 High  
**Category**: Legal / Docs  
**Completed**: 2025-12-17

## Objective

Make the repository licensing **internally consistent** and closer to a legally robust **Business Source License 1.1 (BUSL-1.1)** setup:
- include the canonical BUSL-1.1 license text (unmodified)
- move custom restrictions into a BUSL-compatible **Additional Use Grant** (production use only)
- include the full **Apache 2.0** text referenced as the Change License
- remove misleading “MIT” signaling from the root README badge

## Changes

### 1) Replace `LICENSE.md` with BUSL-1.1 compliant layout

**File:** `LICENSE.md`

- Add a clear BUSL parameter block (Licensor, Licensed Work, Change Date, Change License)
- Rework custom terms into a BUSL-compatible **Additional Use Grant** (production use only) that:
  - allows internal production use
  - prohibits production use that offers the Licensed Work to third parties on a hosted/embedded basis to operate a *Competing Offering*
- Include the **canonical BUSL-1.1 license text** below, unmodified

### 2) Add the Change License text (Apache 2.0)

**File:** `LICENSE-APACHE-2.0.txt`

- Add the full Apache 2.0 license text referenced by the BUSL Change License field.

### 3) Fix README license badge + link the Change License

**File:** `README.md`

- Replace the MIT badge with a BUSL-1.1 badge linked to `LICENSE.md`
- Add a direct link to `LICENSE-APACHE-2.0.txt` in the License section

### 4) Add packaging metadata pointing at the license file

**File:** `pyproject.toml`

- Add `license = { file = "LICENSE.md" }` under `[project]` so published metadata does not imply MIT/Apache pre-change.

## Acceptance Criteria

- [x] Root README no longer claims MIT (badge).
- [x] `LICENSE.md` contains the canonical BUSL-1.1 text unmodified and a BUSL-compatible Additional Use Grant.
- [x] Apache 2.0 (Change License) full text is present in repo.
- [x] Packaging metadata references `LICENSE.md`.
