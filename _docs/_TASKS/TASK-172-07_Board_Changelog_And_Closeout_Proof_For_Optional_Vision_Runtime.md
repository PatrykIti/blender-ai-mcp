# TASK-172-07: Board, Changelog, And Closeout Proof For Optional Vision Runtime

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High
**Objective:** Close the `TASK-172` family with board/changelog synchronization and explicit proof-lane accounting after the implementation leaves have shipped.
**Repository Touchpoints:** `_docs/_TASKS/README.md`, `_docs/_CHANGELOG/README.md`, `_docs/_CHANGELOG/*`, `_docs/_TASKS/TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md`, `_docs/_TASKS/TASK-172-0*.md`
**Acceptance Criteria:**
- board state, child-task state, and umbrella state close together with no open child left under a closed `TASK-172`
- closeout records which lanes were unit, transport, Blender-backed, and optional live-provider proof
- historical changelog entries name the shipped optional-capability, localization, segmentation, and lifecycle slices accurately

## Implementation Notes

- this leaf does not own new runtime behavior; it closes documentation and
  governance after the implementation leaves finish
- closeout should explicitly distinguish:
  - unit proof
  - transport/integration proof
  - Blender-backed proof
  - optional live-provider proof
- if some planned `TASK-172` leaves are intentionally deferred, record them as
  explicit follow-on work before closing the umbrella

## Tests To Add/Update

- no new primary implementation tests; consume the proof from the landed child
  leaves and record it accurately

## Docs To Update

- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`
- one or more `_docs/_CHANGELOG/*` entries
- the `TASK-172*.md` files whose statuses or completion summaries change

## Changelog Impact

- add the historical closeout entry or entries when the first `TASK-172`
  implementation slice lands and extend them as the family closes

## Status / Board Update

- close the umbrella and child-task state together; do not leave open children
  under a closed `TASK-172`

## Validation Commands

- `git diff --check`
- `rg -n "TASK-172|optional vision|localized perception|GroundingDINO|SAM|TTL|unload" _docs/_TASKS/README.md _docs/_CHANGELOG/README.md _docs/_CHANGELOG/* _docs/_TASKS/TASK-172*.md`

## Validation Category

- governance and historical closeout proof
