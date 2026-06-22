# TASK-185-01: Provider And Legal Verification Boundary

**Parent:** [TASK-185](./TASK-185_Optional_Generative_3D_Seed_Asset_Intake.md)
**Status:** ⏳ To Do
**Priority:** 🟡 Medium
**Objective:** Select the first optional generative-3D seed provider or local sidecar only after verifying current official API, licensing, privacy, region, and content terms.

**Repository Touchpoints:** `server/infrastructure/config.py`, `server/infrastructure/di.py`, `_docs/_MCP_SERVER/README.md`, `_docs/_ADDON/README.md`, provider/operator setup docs created by the implementation

## Implementation Notes

- Check current official provider docs during implementation; do not rely on the
  June 2026 audit text or model landscape notes as legal/API authority.
- Record the selected provider/sidecar, allowed input types, output asset format,
  region restrictions, commercial-use status, privacy posture, and known
  failure modes.
- Prefer a local fixture-backed implementation path before live-provider proof.

## Runtime / Security Contract Notes

- provider keys must come from approved env/config paths and be redacted from
  logs, debug payloads, and stored task/job state
- provider use is default-off and must expose unavailable/disabled states
- source reference assets and generated assets are untrusted until imported and
  inspected

## Tests To Add/Update

- config validation tests for disabled, missing-key, unsupported-provider, and
  redaction behavior
- docs/operator checks for provider setup once a concrete provider is selected

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_ADDON/README.md`
- provider setup docs if implementation chooses a provider

## Acceptance Criteria

- implementation notes cite current official provider docs reviewed at that time
- selected provider or sidecar is explicitly default-off
- no provider key or private asset path can leak in normal status/debug payloads

## Validation Commands

- `git diff --check`
- targeted config/redaction tests added by the implementation
