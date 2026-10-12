# 316. Project discontinued

Date: 2026-10-12
Version: -

## Summary

- discontinued `blender-ai-mcp`: the repository is no longer maintained and
  will not be developed further
- the project is being replaced by an entirely new and significantly better
  solution with much stronger 3D scene understanding, deeper and more reliable
  cooperation with Blender, far better workflow control, and more; the new
  add-on will be released soon
- added a canonical discontinuation notice to the documentation and reworded
  forward-looking wording (roadmap, planned, coming next, active development,
  contributions welcome) into historical or "will not be implemented in this
  project" terms
- closed all open, active, and follow-on tasks on `_docs/_TASKS/README.md` as
  won't-do at board level; individual task files and board rows are kept
  unchanged as a historical record
- removed sponsorship and funding content: the sponsor badge and sponsorship
  section in `README.md`, the funding callout in `CONTRIBUTING.md`, and the
  `.github/FUNDING.yml` file
- added a discontinuation note to the GitHub issue and pull request templates
- no code, tool contract, or runtime behaviour changed

## Validation

- docs-only change
- `git diff --check`
- `pre-commit run --files <changed docs>`
