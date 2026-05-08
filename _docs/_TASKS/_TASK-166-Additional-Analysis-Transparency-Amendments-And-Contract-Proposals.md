# TASK-166 Transparency Amendments And Contract Proposals

**Type:** Analysis / Amendment proposal for [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)
**Status:** 📝 Draft — reviewed 2026-05-08; merge target is the canonical `TASK-166*` family
**Audience:** task-writing agent + maintainers of `_docs/_TASKS/TASK-166*`
**Goal:** Tighten TASK-166 so vision-module feedback becomes transparent **on the public contract**, not only inside the engine.

## Review Outcome

- The canonical implementation/planning target is now the `TASK-166*` family,
  not this standalone note.
- Accepted merge points:
  - additive packet provenance/conflict visibility on the existing staged
    compare / iterate contracts
  - explicit extraction/ranking pass status and skip/failure semantics
  - additive per-run budget diagnostics
  - packet transparency feeding the existing compact
    `reference_orchestrator_feedback` owner seam
- Adjusted during merge:
  - authority wording in the canonical task docs stays aligned with the repo's
    existing boundary and gate vocabulary instead of introducing a second
    competing authority taxonomy as the canonical enum source
  - `compare_diagnostics` extends rather than duplicates
    `silhouette_analysis`, `part_segmentation`, `planner_detail`, and
    `budget_control`
- Rejected as-is:
  - any path that bypasses the existing staged compare contracts or creates a
    second planner/evidence flow for clients

The remaining sections below are preserved as historical proposal text for
review context. Where they differ from the merged `TASK-166*` docs, the task
family is canonical.

Do not implement the following from the historical draft below:

- the alternative authority taxonomy `first / support / advisory / derived`
- the older attach-time trigger story that normalized strategy primarily in
  `router_set_goal(...) after attach`
- the older compare-time owner assumption that concentrated packet CV / sidecar
  execution primarily in `vision/reference_support.py`
- the idea that new packet evidence should supersede existing staged candidate
  vocabulary such as `source_signals`, `vision_evidence`, or `truth_evidence`

---

## 1. Problem Statement

TASK-166 introduces:

- packet decomposition by view and active scope (TASK-166-01)
- truth-first two-pass compare (TASK-166-02)
- always-on lightweight CV plus optional PyTorch sidecars (TASK-166-03)
- complexity tiers and multi-reference scaling (TASK-166-04)
- configurable vision-assist budgets (TASK-166-05)

These are correct architectural moves and they will make the internal compare
engine substantially cleaner.

The umbrella, however, explicitly preserves the public surface:

> "the public tool names stay the same"
>
> "project that synthesis back onto the existing staged compare / iterate
> contracts so downstream clients still read: `reference_understanding_summary`,
> `truth_followup`, `correction_candidates`, `planner_summary`,
> `budget_control`, `reference_orchestrator_feedback`"

This means transparency improvements land **inside** the engine, while the
**client-facing contract** still flattens packet results, mixes deterministic
truth with VLM output, and merges support-only sidecars with first-authority
findings into the same string lists.

After TASK-166 as currently specified, the LLM/operator reading
`reference_compare_stage_checkpoint(...)` still cannot tell:

- which evidence item came from deterministic truth vs. lightweight CV vs. VLM
  extraction (pass 1) vs. VLM ranking (pass 2) vs. an optional classifier or
  segmentation sidecar
- which packet (`view:front`, `view:side`, `scope:Tail`, `scope:Body+Head`, ...)
  produced a given finding
- whether two packets disagreed and how the synthesis resolved it
- whether the second pass actually ran or was intentionally skipped
- which configured vs. effective budget applied, on a per-run basis

This document captures three concrete gaps and proposes:

- additive Pydantic contract extensions that fit the existing
  `server/adapters/mcp/contracts/reference.py` patterns
- targeted amendments to existing TASK-166 leaves
- one new leaf (TASK-166-06) covering public-contract transparency
- a draft Runtime Trigger Matrix for the umbrella

All contract additions are **additive and optional** so existing clients keep
working without a flag-day migration.

---

## 2. Three Gaps In TASK-166 As Specified

### 2.1. Gap 1 — No source/authority tagging on evidence items

Today and after TASK-166-as-specified, fields like `correction_candidates`,
`correction_focus`, `shape_mismatches`, `proportion_mismatches`,
`next_corrections` are essentially flat strings (or thin wrappers around flat
strings).

The downstream consumer cannot distinguish:

- a finding grounded in deterministic truth (`scene_relation_graph`,
  `scene_view_diagnostics`, `scene_scope_graph`)
- a finding produced by lightweight CV (silhouette, contour, aspect ratio,
  edge density)
- a finding extracted by the VLM in pass 1
- a finding ranked or synthesized by the VLM in pass 2
- an advisory finding from an optional classifier or segmentation sidecar

This matters because:

- the umbrella already states *"Vision output is advisory"* and that sidecars
  must be *"support-only, never authoritative by default"*
- without a per-item source/authority tag, that policy is invisible at
  consumption time and there is no contract-level mechanism to enforce it

### 2.2. Gap 2 — Per-packet diagnostics are not surfaced in the public contract

After TASK-166, internally there will be N packets per compare run:

- 1–2 for simple
- 2–6 for complex
- 6–12 for super-complex

The synthesis layer collapses these into the existing flat fields. Without
per-packet diagnostics in the public contract:

- a failed front-view packet looks identical to a successful one (both
  contribute to one collapsed list)
- packet conflicts ("front says tail too short, side says tail too long") are
  smoothed away by synthesis instead of surfacing as uncertainty
- there is no way to retry a single failed packet without re-running the whole
  compare
- debugging "why did the LLM act on correction X" requires re-running compare
  with verbose logging, since the correction has no provenance back to a packet

TASK-166-01-03 *does* mention "Synthesis should preserve provenance back to
packet ids/reference ids" — but only in implementation notes. This must be
elevated to a contract obligation, not left as internal advice.

### 2.3. Gap 3 — Umbrella has no Runtime Trigger Matrix

The umbrella explains the new flow narratively but does not include an explicit
table of:

```
event → what runs → owner module → outputs → authority level
```

Without this table, every implementer (and every reader of a future bug
report) has to reconstruct the trigger model from prose. This is exactly the
documentation gap that breeds confusion when the same module needs to
participate in two different events with different roles — most obviously the
classifier, which should run as **global bootstrap support** at attach time
and as **packet-local advisory** at compare time, and **never** as the main
mid-flow engine.

---

## 3. Proposed Contract Extensions

The following extensions follow the existing patterns in
`server/adapters/mcp/contracts/reference.py`:

- inherit from `MCPContract` (which sets `extra="forbid"`)
- use `Literal[...]` for closed enums
- prefer optional fields with sensible defaults
- keep new fields additive on existing response contracts

### 3.1. New literals

```python
EvidenceSourceLiteral = Literal[
    "deterministic_truth",   # scene_scope_graph, scene_relation_graph,
                             # scene_view_diagnostics, measure/assert results
    "lightweight_cv",        # always-on heuristic CV (silhouette, contour,
                             # edge density, aspect ratio, components)
    "vlm_extraction",        # pass 1: narrow packet-question extraction
    "vlm_ranking",           # pass 2: correction ranking / synthesis output
    "classifier_sidecar",    # optional CLIP/SigLIP/DINOv2-style adapter
    "segmentation_sidecar",  # optional SAM2 / GroundingDINO-style adapter
    "synthesis",             # produced by the multi-packet synthesis layer
]

EvidenceAuthorityLiteral = Literal[
    "first",      # deterministic; can decide gate state on its own
    "support",    # corroborates or weakens first-authority findings
    "advisory",   # hint-only; never sufficient on its own
]
```

Authority semantics are deliberately small:

- **first** — deterministic truth and budget enforcement. Gate verifier still
  owns final pass/fail.
- **support** — pass-1 VLM extraction and lightweight CV. Sufficient to
  influence ranking and synthesis, not sufficient to mark a gate complete.
- **advisory** — pass-2 VLM ranking artifacts that have no first/support
  backing, classifier and segmentation sidecars. Rejected by synthesis if
  unbacked.

### 3.2. Typed evidence item

```python
class EvidenceItemContract(MCPContract):
    """One typed piece of evidence with explicit source and authority."""

    summary: str
    source: EvidenceSourceLiteral
    authority: EvidenceAuthorityLiteral
    packet_id: str | None = None
    reference_ids: list[str] = []
    confidence: float | None = None  # 0.0..1.0 if the source can express it
    notes: str | None = None
```

### 3.3. Additive extension to `ReferenceCorrectionCandidateContract`

The existing contract stays as-is; one optional field is added.

```python
class ReferenceCorrectionCandidateContract(MCPContract):
    # --- existing fields (unchanged) ---
    candidate_id: str
    summary: str
    priority_rank: int
    priority: Literal["high", "normal"] = "normal"
    candidate_kind: Literal["vision_only", "truth_only", "hybrid"] = "vision_only"
    target_object: str | None = None
    target_objects: list[str] = []
    focus_pairs: list[str] = []
    source_signals: list[Literal["vision", "truth", "macro"]] = []
    vision_evidence: ReferenceCorrectionVisionEvidenceContract | None = None
    truth_evidence: ReferenceCorrectionTruthEvidenceContract | None = None

    # --- new (additive, optional) ---
    typed_evidence: list[EvidenceItemContract] = []
```

The existing `source_signals` field stays for backwards compatibility but is
effectively superseded by `typed_evidence` once consumers adopt it.

### 3.4. Packet-level diagnostics

```python
PacketKindLiteral = Literal["view", "scope", "view_scope_paired"]

PacketStatusLiteral = Literal[
    "ok",               # extraction succeeded and produced evidence
    "clean",            # extraction succeeded with no mismatches
    "low_information",  # extraction succeeded but yielded too little to rank
    "skipped",          # planner intentionally skipped (e.g., tier policy)
    "blocked",          # preconditions not met (missing view/reference/...)
    "failed",           # extraction or sidecar produced an error
]


class PacketQuestionContract(MCPContract):
    """The narrow question this packet asked the LLM or deterministic check."""

    text: str
    target_view: Literal["front", "side", "top", "silhouette"] | None = None
    target_scope: list[str] = []  # e.g., ["Body", "Head"], ["Tail"]


class PacketDiagnosticsContract(MCPContract):
    """One inspectable packet from a compare/iterate run."""

    packet_id: str
    kind: PacketKindLiteral
    question: PacketQuestionContract
    reference_ids: list[str] = []

    # pass 1 outcome
    extraction_status: PacketStatusLiteral
    extraction_evidence: list[EvidenceItemContract] = []

    # pass 2 outcome (skipped is a normal value, not an error)
    ranking_status: Literal["ok", "skipped", "failed"] = "skipped"
    ranking_evidence: list[EvidenceItemContract] = []
    ranking_skip_reason: str | None = None

    # support inputs that fed this packet
    deterministic_inputs: list[str] = []
    # e.g. ["scene_view_diagnostics:front", "scene_relation_graph:Body-Tail"]

    cv_metrics_keys: list[str] = []
    # which always-on CV metrics were attached, by name

    sidecars_used: list[EvidenceSourceLiteral] = []
    # subset of {"classifier_sidecar", "segmentation_sidecar"}

    # honest disagreement reporting
    conflicts_with_packet_ids: list[str] = []
    conflict_notes: str | None = None
```

### 3.5. Compare-run diagnostics

```python
class CompareDiagnosticsContract(MCPContract):
    """Top-level compare-run diagnostics."""

    compare_run_id: str
    complexity_tier: Literal["simple", "complex", "super_complex"]
    packet_count: int
    packets: list[PacketDiagnosticsContract] = []

    synthesis_status: Literal["ok", "skipped", "uncertain", "failed"] = "ok"
    synthesis_notes: str | None = None

    # operator-facing budget visibility (links to TASK-166-05)
    configured_input_char_budget: int | None = None
    effective_input_char_budget: int | None = None
    budget_clipped: bool = False
```

### 3.6. Additive extension to staged compare/iterate response contracts

```python
class ReferenceCompareStageCheckpointResponseContract(MCPContract):
    # --- all existing fields kept as-is ---
    ...
    # --- new (additive, optional) ---
    compare_diagnostics: CompareDiagnosticsContract | None = None


class ReferenceIterateStageCheckpointResponseContract(MCPContract):
    # --- all existing fields kept as-is ---
    ...
    # --- new (additive, optional) ---
    compare_diagnostics: CompareDiagnosticsContract | None = None
```

### 3.7. Surfacing rules for `compare_diagnostics`

To keep payload size bounded and consistent with the existing `planner_detail`
rich-profile pattern:

- **omitted** in `preset_profile="compact"` (default), so the normal payload
  size stays unchanged
- **always included** in `preset_profile="rich"`
- **force-included regardless of profile** when at least one packet has
  `extraction_status="failed"` or when `synthesis_status` is
  `"uncertain"` or `"failed"`, so transparency is automatic when something
  went wrong

### 3.8. Synthesis-layer rule for advisory-only candidates

To make "support-only sidecars" enforceable instead of policy-only, the
synthesis layer should reject (or downgrade) any correction candidate whose
`typed_evidence` contains **only** items with `authority="advisory"`.

Concretely, in the synthesis path:

```text
if all(item.authority == "advisory" for item in candidate.typed_evidence):
    # do not emit as a correction candidate;
    # may still be retained as advisory note in compare_diagnostics
    drop_or_demote(candidate)
```

This bakes the policy "Vision output is advisory; deterministic checks decide
correctness" into the contract instead of leaving it as documentation.

---

## 4. Targeted Amendments To Existing TASK-166 Leaves

These amendments do not add a second umbrella; they tighten existing leaves so
that "transparency to the client" stops being implicit.

### 4.1. TASK-166-01-03 (Multi-Reference Packet Synthesis) — elevate provenance

**Current implementation note:**
> "Synthesis should preserve provenance back to packet ids/reference ids."

**Proposed change:** Move from implementation notes to acceptance criteria as:

> Synthesis output must surface packet-id provenance and packet conflicts in
> the public compare contract under `compare_diagnostics`
> (rich profile and on failure). Conflicting packet conclusions must produce
> explicit `conflicts_with_packet_ids` entries and surface in
> `synthesis_status="uncertain"`, never silently merged.

### 4.2. TASK-166-02-02 (Visual Extraction And Correction Ranking Split) — explicit pass status

**Add to acceptance criteria:**

> Each packet's extraction and ranking outcomes must be independently
> representable in `PacketDiagnosticsContract.extraction_status` and
> `PacketDiagnosticsContract.ranking_status`.
>
> Ranking-skipped on a clean or low-information packet must carry
> `ranking_status="skipped"` with `ranking_skip_reason` populated; it must not
> appear as `failed` or as a missing field.

### 4.3. TASK-166-03-01 (Always-On Heuristic CV Metrics) — tag outputs as `lightweight_cv`

**Add to acceptance criteria:**

> All CV-derived evidence items in compare/iterate responses carry
> `source="lightweight_cv"` and `authority="support"`. The CV path may not emit
> evidence with `authority="first"`.

This prevents drift where heuristic CV starts being treated as authoritative
just because it is "always on."

### 4.4. TASK-166-03-02 (Optional PyTorch Perceiver Adapters) — tag outputs as advisory

**Add to acceptance criteria:**

> All sidecar-derived evidence items carry `source="classifier_sidecar"` or
> `source="segmentation_sidecar"` and `authority="advisory"`.
>
> The synthesis layer rejects or demotes any correction candidate whose
> `typed_evidence` contains only items with `authority="advisory"`. Such
> candidates may still be retained as advisory entries inside
> `compare_diagnostics`, but they must not surface in `correction_candidates`.

This bakes "support-only, never authoritative by default" into the contract.

### 4.5. TASK-166-05-02 (Runtime Diagnostics And Fail-Safe Budget Caps) — surface budgets in compare diagnostics

**Add to acceptance criteria:**

> `CompareDiagnosticsContract` exposes `configured_input_char_budget`,
> `effective_input_char_budget`, and `budget_clipped` so operators can
> correlate compare quality with budget pressure on a per-run basis.

This connects TASK-166-05 budget config to the per-run transparency surface.

---

## 5. Proposed New Leaf — TASK-166-06: Public Contract Transparency

The contract additions in §3 span multiple existing leaves and need their own
coherent acceptance bar. A new leaf is justified.

```markdown
# TASK-166-06: Public Contract Transparency For Hierarchical Compare

**Parent:** TASK-166
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Expose source/authority/packet-provenance metadata in the
public staged compare/iterate response so the LLM/operator can distinguish
deterministic, support, and advisory evidence and inspect per-packet outcomes
without re-running compare.

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
  (new typed evidence + diagnostics contracts)
- `server/adapters/mcp/areas/reference.py`
  (response assembly)
- `server/adapters/mcp/areas/reference_planner.py`
  (synthesis provenance and advisory-rejection rule)
- `tests/unit/adapters/mcp/test_reference_images.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Implementation Notes

- Additive only: existing fields stay, new fields default to `None` / `[]`.
- Compact profile keeps current payload size unchanged.
- Rich profile always includes `compare_diagnostics`.
- `compare_diagnostics` is force-included on `extraction_status="failed"`
  or `synthesis_status in {"uncertain", "failed"}`, regardless of profile.
- Synthesis layer rejects or demotes candidates whose `typed_evidence` is
  advisory-only.

## Acceptance Criteria

- `correction_candidates` carry `typed_evidence` with `source` and `authority`.
- `compare_diagnostics` is reachable from staged compare/iterate responses.
- Packet conflicts surface as explicit `conflicts_with_packet_ids` entries
  plus `synthesis_status="uncertain"`.
- Advisory-only candidates cannot displace deterministic findings.
- Budget visibility (`configured_input_char_budget`,
  `effective_input_char_budget`, `budget_clipped`) is reachable per-run.

## Tests To Add/Update

- contract-shape unit tests for `EvidenceItemContract`,
  `PacketDiagnosticsContract`, `CompareDiagnosticsContract`
- staged compare/iterate tests asserting `compare_diagnostics` is omitted in
  compact, present in rich, force-included on failure
- synthesis-layer test that an advisory-only candidate does not appear in
  `correction_candidates`
```

---

## 6. Draft Runtime Trigger Matrix

This is intended as a new section in the umbrella
`TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md`,
inserted between *Integration With Existing Flow* and *Execution Structure*.

### 6.1. Matrix

| Event | What Runs | Owner Module | Outputs | Authority |
|------|------|------|------|------|
| `reference_images(action="attach", ...)` | bootstrap reference understanding pass | `vision/reference_support.py`, `areas/reference_understanding.py` | `reference_understanding_summary`, optional global classifier signal | global support |
| `router_set_goal(...)` after attach | normalize understanding into active strategy + gate proposals | `areas/reference.py`, `session_capabilities.py` | `active_construction_path`, `allowed_tool_families`, gate proposals | first (verifier owns gate authority) |
| `reference_compare_stage_checkpoint(...)` — packet planning | build `compare_plan` from guided state, scope, references | `areas/reference.py`, `areas/reference_planner.py` | `view_packets`, `scope_packets`, `packet_order`, `synthesis_required` | first (deterministic) |
| per-packet preflight | deterministic truth slice for the packet's view/scope | `scene_scope_graph`, `scene_relation_graph`, `scene_view_diagnostics` | per-packet truth findings (`source="deterministic_truth"`) | first |
| per-packet always-on CV | silhouette, contour, edge density, components | `vision/reference_support.py` (CV path) | `EvidenceItemContract` with `source="lightweight_cv"` | support |
| per-packet optional classifier sidecar (when enabled) | CLIP/SigLIP/DINOv2-style adapter | `vision/reference_support.py` (sidecar path) | `EvidenceItemContract` with `source="classifier_sidecar"` | advisory |
| per-packet optional segmentation sidecar (when enabled) | SAM2 / GroundingDINO-style adapter | `vision/reference_support.py` (sidecar path) | `EvidenceItemContract` with `source="segmentation_sidecar"` | advisory |
| per-packet pass 1 — narrow VLM extraction | one narrow question per packet | `vision/runner.py`, `vision/prompting.py` | `EvidenceItemContract` with `source="vlm_extraction"`, `extraction_status` | support |
| per-packet pass 2 — VLM correction ranking | bounded ranking on top of pass 1 (skippable) | `vision/runner.py` | `EvidenceItemContract` with `source="vlm_ranking"`, `ranking_status` | support |
| compare-run synthesis | merge packet results, surface conflicts | `areas/reference_planner.py` | `correction_candidates` (with `typed_evidence`), `compare_diagnostics`, `synthesis_status` | derived |
| `reference_iterate_stage_checkpoint(...)` consumption | read packet synthesis, decide loop disposition | `areas/reference.py` | `correction_focus`, `loop_disposition`, `planner_summary`, `budget_control`, `reference_orchestrator_feedback` | derived |
| budget enforcement | apply configured/effective char budgets, fail-safe caps | `vision/runner.py`, `vision/config.py` | `budget_control`, `compare_diagnostics.budget_clipped` | first |

### 6.2. Reading rules

- **first** — can stand alone and decide gate state. Deterministic truth and
  budget enforcement.
- **support** — corroborates or weakens first-authority findings. Sufficient
  to influence ranking and synthesis, not sufficient to mark a gate complete.
- **advisory** — hint-only. Rejected by synthesis if it has no first/support
  backing.
- **derived** — computed from the items above and inherits the lowest
  authority of its inputs. Cannot be promoted above its weakest input.
- **global support** — produced once at attach time, applies as background
  context for the whole session, not per-packet. The classifier should appear
  here. Mid-flow it appears only as advisory.

### 6.3. Classifier role clarification

The classifier (CLIP / SigLIP / DINOv2) appears in the matrix in **two**
distinct roles, and **only** in those two roles:

- at attach time, as **global support** for style/domain hints
- at compare time, as a **per-packet advisory** sidecar (default-off)

The classifier is **never** the main mid-flow engine. Mid-flow authority
belongs to deterministic truth + lightweight CV + segmentation cues, in that
order. The matrix makes this explicit so that a future "let's just bump the
classifier to first authority" change has to fight the table, not just the
prose.

---

## 7. Why These Amendments Close The Transparency Story

Together, the contract extensions, the new TASK-166-06 leaf, and the trigger
matrix produce three concrete improvements that the current umbrella does not
guarantee:

1. **Every evidence item carries its origin and weight.** The LLM reads
   `typed_evidence` and decides whether to act now (deterministic + support)
   or escalate to inspection (advisory-only). The synthesis layer enforces
   this at the contract level instead of relying on prompt discipline.

2. **Per-packet diagnostics are inspectable without re-running compare.** Rich
   profile shows the full packet decomposition. Compact profile stays small
   but flips to verbose automatically on failure or uncertainty. Operators
   can correlate `correction_focus` back to a specific packet, view, scope,
   and pass.

3. **The trigger matrix removes ambiguity about classifier role.** Listed
   explicitly twice — global bootstrap support at attach time and packet-local
   advisory at compare time — closing the door on "classifier as the main
   mid-flow engine."

These additions are **additive**: existing clients keep reading the same flat
fields they read today; transparency-aware clients gain typed access without
forcing a flag-day migration.

---

## 8. Suggested Review Checklist For The Task-Writing Agent

When folding this analysis into TASK-166, please confirm:

- [ ] §3 contract names do not collide with existing names in
      `server/adapters/mcp/contracts/reference.py`
- [ ] §3.7 surfacing rules align with the existing
      `preset_profile="compact" | "rich"` policy and the `planner_detail`
      precedent
- [ ] §4 amendments are added to the right leaves and do not contradict
      existing acceptance criteria
- [ ] §5 new leaf TASK-166-06 references valid sibling task numbers and is
      added to the umbrella *Execution Structure* table as order item 6
- [ ] §6 Runtime Trigger Matrix is inserted in the umbrella between
      *Integration With Existing Flow* and *Execution Structure*
- [ ] terminology used here (`first` / `support` / `advisory` / `derived`)
      matches or extends, but does not silently rename, the umbrella's
      existing language about "advisory only" sidecars and "first authority"
      truth
- [ ] all contract additions stay additive; no existing field is renamed,
      retyped, or removed in this round

---

**End of analysis. Ready for task-writing-agent review.**
