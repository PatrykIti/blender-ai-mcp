# blender-ai-mcp — plan rozwoju modułu Vision i `reference_understanding`

Autor roboczy: Patryk / blender-ai-mcp
Cel dokumentu: rozpisać szczegółowo, jak rozwinąć moduł Vision tak, żeby LLM orkiestrator wiedział **co widzi**, **jaką ścieżką konstrukcyjną ma iść**, **jakich narzędzi nie powinien używać** oraz **jak ma walidować kolejne etapy builda**.

> Uwaga o researchu bibliotek: w tej sesji nie mam aktywnego live web-search. Analiza bibliotek poniżej jest oparta o znane publiczne rozwiązania i stan wiedzy do 2025-08 oraz o aktualnie dostępny kontekst repozytorium `PatrykIti/blender-ai-mcp`. Przed wyborem konkretnego modelu/paczki warto jeszcze zrobić osobny, świeży check licencji, wymagań GPU/CPU, wersji pakietów i jakości na Twoich referencjach.

---

## 1. TL;DR — najważniejsza decyzja

Vision w `blender-ai-mcp` nie powinno być tylko etapem typu:

```text
Mam aktualny viewport. Powiedz, co jest źle.
```

Powinno mieć wcześniejszy etap:

```text
Mam referencje. Powiedz, co to jest, jaki to styl, jakie są wymagane części,
jaką ścieżką konstrukcji powinien iść LLM i czego ma unikać.
```

Docelowy przepływ:

```text
reference_images(...)
  ↓
reference understanding pass through the existing reference/guided-state seam
  ↓
server-owned strategy apply through guided state, visibility, and gate policy
  ↓
LLM dostaje aktywną ścieżkę konstrukcyjną i ograniczoną widoczność narzędzi
  ↓
blockout / modeling / mesh / material stages
  ↓
reference_compare_stage_checkpoint(...)
  ↓
reference_iterate_stage_checkpoint(...)
  ↓
router wybiera refinement_handoff
  ↓
LLM robi tylko dozwolony typ poprawki
```

Uwaga 2026-05-02:

- Ten dokument pozostaje długim szkicem strategicznym, nie bieżącym kontraktem
  publicznej powierzchni MCP.
- `reference_understand(...)` i `router_apply_reference_strategy(...)` są tutaj
  historycznym skrótem planistycznym. Aktualny normatywny kierunek jest opisany
  w `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md` i `TASK-158`.
- `mesh_edit` oznacza bieżące `modeling_mesh`; `material_finish` pozostaje
  hintem/stage concept albo przyszłą rodziną; `macro_create_part`,
  `mesh_shade_flat`, i `macro_low_poly_*` nie są dziś kanonicznymi publicznymi
  narzędziami.

Największa luka obecnie:

```text
Vision pojawia się za późno — dopiero po tym, jak LLM już zbudował pierwszy model.
```

Nowy moduł powinien dodać:

```text
reference_understanding before build
```

Czyli: zanim Claude/Sonnet/Gemini zacznie budować owale/kule/smooth shape, system powinien już wiedzieć, że np. referencja jest:

```text
low-poly faceted squirrel
```

a więc właściwa ścieżka to:

```text
blockout → low-poly form profiling → faceted mesh pass → flat shading → local sculpt only if needed
```

Nie:

```text
smooth organic primitive blockout → global sculpt
```

---

## 2. Problem, który trzeba rozwiązać

Na przykładzie referencji wiewiórki:

```text
Input:
- front reference
- side reference
- stylizowana wiewiórka low-poly
```

Obecny problem:

```text
LLM widzi „zwierzę” i naturalnie idzie w organiczne bryły:
- sphere dla body
- sphere dla head
- smooth tail
- smooth paws
- potem szuka sculpta, bo model wygląda zbyt organicznie
```

A poprawna interpretacja jest inna:

```text
To nie jest przede wszystkim organic sculpt.
To jest low-poly faceted construction.
```

Czyli LLM powinien od początku dostać:

```json
{
  "subject": "low-poly squirrel",
  "style": "faceted low-poly animal, flat shaded, angular planes",
  "construction_path": "low_poly_facet",
  "sculpt_policy": "local_detail_only",
  "non_goals": [
    "do not make smooth organic fur",
    "do not leave body parts as simple spheres",
    "do not prioritize sculpted realism"
  ]
}
```

To jest nie tylko kwestia promptu. To jest kwestia architektury:

```text
Vision opisuje i klasyfikuje referencje.
Router normalizuje rekomendację do typed contract.
Dopiero router odblokowuje tool families.
LLM orkiestruje w ramach widocznych narzędzi.
```

---

## 3. Obecny stan repo — co już jest mocne

Repo ma już sporo elementów, które pasują do tego kierunku:

```text
server/adapters/mcp/contracts/vision.py
server/adapters/mcp/contracts/reference.py
server/adapters/mcp/vision/runner.py
server/adapters/mcp/sampling/result_types.py
_docs/_VISION/README.md
_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md
```

W aktualnych kontraktach istnieją między innymi:

```text
VisionCaptureImageContract
VisionCaptureBundleContract
VisionAssistContract
ReferenceImageRecordContract
GuidedReferenceReadinessContract
ReferenceCompareStageCheckpointResponseContract
ReferenceIterateStageCheckpointResponseContract
ReferenceRefinementRouteContract
ReferenceRefinementHandoffContract
ReferenceSilhouetteAnalysisContract
ReferencePartSegmentationContract
```

Istnieją też elementy loopa:

```text
reference_images(...)
reference_compare_checkpoint(...)
reference_compare_current_view(...)
reference_compare_stage_checkpoint(...)
reference_iterate_stage_checkpoint(...)
```

I bardzo ważne: repo już ma rozróżnienie refinement families:

```text
macro
modeling_mesh
sculpt_region
inspect_only
```

Dla low-poly creature / assembled model oczekiwane jest:

```text
macro albo modeling_mesh
```

A nie domyślny:

```text
sculpt_region
```

To oznacza, że nowy moduł nie musi przebudowywać całego systemu. Powinien wejść jako warstwa przed istniejącym stage compare / iterate.

---

## 4. Docelowa architektura warstw

Proponowany podział odpowiedzialności:

```text
┌─────────────────────────────────────────────────────────────┐
│ User Goal + Reference Images                                 │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│ Reference Understanding Layer                                │
│ - VLM opisuje semantykę                                       │
│ - CV liczy tanie cechy obrazu                                 │
│ - opcjonalnie CLIP/SigLIP klasyfikuje styl/path               │
│ - opcjonalnie SAM/sidecar zwraca maski części                 │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│ Typed ReferenceUnderstandingContract                         │
│ - subject                                                     │
│ - style                                                       │
│ - required parts                                              │
│ - non-goals                                                   │
│ - construction_path                                           │
│ - sculpt_policy                                               │
│ - router_handoff                                              │
│ - verification_requirements                                   │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│ Router / Server Normalization                                │
│ - nie ufa prozie Vision jako truth                            │
│ - mapuje construction_path na dozwolone tool families         │
│ - blokuje niepasujące ścieżki                                 │
│ - ustawia stage plan                                          │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│ LLM Orchestrator                                             │
│ - buduje zgodnie z aktywną ścieżką                            │
│ - widzi tylko właściwe narzędzia                              │
│ - robi checkpointy po etapach                                 │
└──────────────────────────────┬──────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────┐
│ Blender Tooling + Inspection + Compare                       │
│ - macro / modeling_mesh / sculpt_region                       │
│ - reference_compare_stage_checkpoint                          │
│ - reference_iterate_stage_checkpoint                          │
│ - deterministic truth / silhouette / relation checks          │
└─────────────────────────────────────────────────────────────┘
```

Najważniejsza zasada:

```text
Vision może sugerować.
Router decyduje.
Inspection/assertion weryfikuje.
LLM wykonuje.
```

---

## 5. Nowy moduł: `reference_understanding`

### 5.1. Cel modułu

`reference_understanding` ma odpowiedzieć na pytania:

```text
1. Co przedstawiają referencje?
2. Jaki to styl?
3. Jakie części są obowiązkowe?
4. Które widoki są dostępne?
5. Jaką ścieżką konstrukcji powinien iść build?
6. Jakich ścieżek/narzędzi nie używać jako default?
7. Co trzeba sprawdzić po kolejnych etapach?
```

### 5.2. Draft public-surface sketch, not the current MCP contract

Historyczny skrót planistyczny, nie domyślna dostarczona powierzchnia MCP:

```text
reference_understand(...)
```

Proponowany input:

```json
{
  "goal_id": "goal_123",
  "goal": "Create a low-poly squirrel from front and side references",
  "reference_ids": ["ref_front", "ref_side"],
  "expected_subject": null,
  "expected_style": null,
  "target_domain_hint": null
}
```

Proponowany output:

```json
{
  "action": "reference_understand",
  "goal": "Create a low-poly squirrel from front and side references",
  "reference_count": 2,
  "understanding_id": "understanding_goal_123_001",
  "reference_understanding": {},
  "visual_evidence": {},
  "classification_scores": {},
  "segmentation_artifacts": {},
  "construction_strategy": {},
  "router_handoff": {},
  "verification_requirements": {},
  "boundary_policy": {}
}
```

---

## 6. Proponowany kontrakt: `ReferenceUnderstandingContract`

### 6.1. Kontrakt JSON

```json
{
  "subject": {
    "label": "low-poly squirrel",
    "category": "creature",
    "confidence": 0.86,
    "notes": [
      "stylized animal reference",
      "front and side views available"
    ]
  },
  "style": {
    "primary_style": "low_poly_faceted",
    "surface_language": "flat_shaded_angular_planes",
    "organic_level": "low",
    "realism_level": "stylized",
    "material_language": "simple_flat_materials"
  },
  "views": [
    {
      "view_id": "front",
      "detected": true,
      "reference_ids": ["ref_front"],
      "key_features": [
        "large angular head",
        "two tall triangular ears",
        "dark side eyes",
        "small wedge snout",
        "faceted cheeks"
      ]
    },
    {
      "view_id": "side",
      "detected": true,
      "reference_ids": ["ref_side"],
      "key_features": [
        "sitting squirrel",
        "large curled segmented tail",
        "compact body",
        "small front paws holding acorn",
        "thin rear foot"
      ]
    }
  ],
  "required_parts": [
    {
      "part_id": "body",
      "label": "Body",
      "priority": "high",
      "construction_hint": "compact angular torso"
    },
    {
      "part_id": "head",
      "label": "Head",
      "priority": "high",
      "construction_hint": "large angular head with faceted cheek planes"
    },
    {
      "part_id": "tail_curled_segmented",
      "label": "Curled segmented tail",
      "priority": "high",
      "construction_hint": "chain of 4-5 angular segments in upward curl"
    },
    {
      "part_id": "snout_wedge",
      "label": "Snout wedge",
      "priority": "high",
      "construction_hint": "wedge, not sphere"
    },
    {
      "part_id": "ear_left",
      "label": "Left triangular ear",
      "priority": "normal",
      "construction_hint": "triangular cone/wedge"
    },
    {
      "part_id": "ear_right",
      "label": "Right triangular ear",
      "priority": "normal",
      "construction_hint": "triangular cone/wedge"
    },
    {
      "part_id": "front_paws",
      "label": "Front paws holding acorn",
      "priority": "normal",
      "construction_hint": "small angular paw forms near chest"
    },
    {
      "part_id": "acorn",
      "label": "Acorn",
      "priority": "normal",
      "construction_hint": "small object between paws"
    }
  ],
  "non_goals": [
    "do not make smooth organic fur",
    "do not leave body parts as simple spheres",
    "do not prioritize sculpted realism",
    "do not use global sculpt as primary path"
  ],
  "construction_strategy": {
    "construction_path": "low_poly_facet",
    "initial_blockout": "separate primitive masses",
    "primary_refinement_family": "modeling_mesh",
    "secondary_refinement_family": "macro",
    "sculpt_policy": "local_detail_only",
    "finish_policy": "flat_shading_and_faceted_normals",
    "recommended_stage_sequence": [
      "understand_reference",
      "blockout_primary_masses",
      "place_secondary_parts",
      "refine_low_poly_facets",
      "flat_shading_and_materials",
      "local_sculpt_if_needed",
      "final_reference_compare"
    ]
  },
  "router_handoff": {
    "allowed_tool_families": [
      "macro",
      "modeling_mesh",
      "inspect_only"
    ],
    "blocked_tool_families": [
      "global_sculpt",
      "smooth_organic_refinement"
    ],
    "recommended_first_tools": [
      "modeling_create_primitive",
      "guided_register_part",
      "macro_align_part_with_contact",
      "mesh_flatten",
      "mesh_triangulate",
      "mesh_mark_sharp"
    ],
    "recommended_later_tools": [
      "sculpt_pinch_region"
    ]
  },
  "verification_requirements": {
    "must_verify": [
      "tail silhouette matches side reference",
      "head/body proportion matches front and side references",
      "ears are triangular and sharp",
      "snout is wedge-shaped, not spherical",
      "faceted low-poly surface language is visible",
      "flat shading or faceted normals are applied"
    ],
    "checkpoint_tools": [
      "reference_compare_stage_checkpoint",
      "reference_iterate_stage_checkpoint",
      "scene_relation_graph",
      "scene_view_diagnostics"
    ]
  },
  "boundary_policy": {
    "vision_is_advisory": true,
    "router_must_normalize": true,
    "requires_deterministic_checks_for_correctness": true,
    "do_not_unlock_tools_directly_from_vision": true
  }
}
```

### 6.2. Proponowane klasy Python

```python
from typing import Literal

from server.adapters.mcp.contracts.base import MCPContract


ConstructionPath = Literal[
    "low_poly_facet",
    "hard_surface",
    "organic_sculpt",
    "creature_blockout",
    "dental_surface",
    "product_mockup",
    "architectural_mass",
    "unknown",
]

RefinementFamily = Literal[
    "macro",
    "modeling_mesh",
    "sculpt_region",
    "inspect_only",
]

SculptPolicy = Literal[
    "forbidden",
    "local_detail_only",
    "allowed_after_blockout",
    "primary_method",
]


class ReferenceSubjectContract(MCPContract):
    label: str
    category: Literal[
        "creature",
        "character",
        "hard_surface",
        "architecture",
        "product",
        "dental",
        "anatomy",
        "unknown",
    ] = "unknown"
    confidence: float | None = None
    notes: list[str] = []


class ReferenceStyleContract(MCPContract):
    primary_style: Literal[
        "low_poly_faceted",
        "smooth_organic",
        "hard_surface",
        "technical_cad",
        "dental_scan",
        "architectural",
        "unknown",
    ] = "unknown"
    surface_language: str | None = None
    organic_level: Literal["none", "low", "medium", "high", "unknown"] = "unknown"
    realism_level: Literal["abstract", "stylized", "semi_realistic", "realistic", "unknown"] = "unknown"
    material_language: str | None = None


class ReferenceViewUnderstandingContract(MCPContract):
    view_id: Literal["front", "side", "top", "back", "three_quarter", "unknown"] = "unknown"
    detected: bool = False
    reference_ids: list[str] = []
    key_features: list[str] = []
    occlusion_notes: list[str] = []


class ReferenceRequiredPartContract(MCPContract):
    part_id: str
    label: str
    priority: Literal["high", "normal", "low"] = "normal"
    construction_hint: str | None = None
    expected_attachment: str | None = None
    expected_view_evidence: list[str] = []


class ReferenceConstructionStrategyContract(MCPContract):
    construction_path: ConstructionPath = "unknown"
    initial_blockout: str | None = None
    primary_refinement_family: RefinementFamily = "inspect_only"
    secondary_refinement_family: RefinementFamily | None = None
    sculpt_policy: SculptPolicy = "local_detail_only"
    finish_policy: str | None = None
    recommended_stage_sequence: list[str] = []


class ReferenceRouterHandoffContract(MCPContract):
    allowed_tool_families: list[RefinementFamily] = []
    blocked_tool_families: list[str] = []
    recommended_first_tools: list[str] = []
    recommended_later_tools: list[str] = []
    reason: str | None = None


class ReferenceVerificationRequirementsContract(MCPContract):
    must_verify: list[str] = []
    checkpoint_tools: list[str] = []
    stage_exit_criteria: list[str] = []


class ReferenceUnderstandingBoundaryPolicyContract(MCPContract):
    vision_is_advisory: bool = True
    router_must_normalize: bool = True
    requires_deterministic_checks_for_correctness: bool = True
    do_not_unlock_tools_directly_from_vision: bool = True


class ReferenceUnderstandingContract(MCPContract):
    subject: ReferenceSubjectContract
    style: ReferenceStyleContract
    views: list[ReferenceViewUnderstandingContract] = []
    required_parts: list[ReferenceRequiredPartContract] = []
    non_goals: list[str] = []
    construction_strategy: ReferenceConstructionStrategyContract
    router_handoff: ReferenceRouterHandoffContract
    verification_requirements: ReferenceVerificationRequirementsContract
    boundary_policy: ReferenceUnderstandingBoundaryPolicyContract = ReferenceUnderstandingBoundaryPolicyContract()
```

---

## 7. Router: jak normalizować decyzje Vision

Vision nie powinno odblokowywać narzędzi bezpośrednio.

Źle:

```text
Vision says: use sculpt.
Router: OK, expose sculpt tools.
```

Dobrze:

```text
Vision says: style looks organic / local form issue.
Router: classify domain + stage + evidence.
Router: only then expose sculpt_region if policy allows.
```

### 7.1. Mapowanie `construction_path` → tool families

Historyczna normalizacja aliasów dla poniższego szkicu:

```text
mesh_edit -> modeling_mesh
material_finish -> finish/stage guidance, not a canonical refinement family
```

```python
CONSTRUCTION_PATH_ROUTING = {
    "low_poly_facet": {
        "domain": "assembly",
        "allowed": ["macro", "modeling_mesh", "inspect_only"],
        "blocked": ["global_sculpt", "smooth_organic_refinement"],
        "sculpt_policy": "local_detail_only",
        "primary_family": "modeling_mesh",
    },
    "hard_surface": {
        "domain": "hard_surface",
        "allowed": ["macro", "modeling_mesh", "inspect_only"],
        "blocked": ["global_sculpt"],
        "sculpt_policy": "forbidden",
        "primary_family": "modeling_mesh",
    },
    "organic_sculpt": {
        "domain": "organic_form",
        "allowed": ["macro", "modeling_mesh", "sculpt_region", "inspect_only"],
        "blocked": ["global_sculpt_unbounded"],
        "sculpt_policy": "primary_method",
        "primary_family": "sculpt_region",
    },
    "creature_blockout": {
        "domain": "assembly",
        "allowed": ["macro", "modeling_mesh", "sculpt_region", "inspect_only"],
        "blocked": ["global_sculpt_unbounded"],
        "sculpt_policy": "allowed_after_blockout",
        "primary_family": "macro",
    },
    "dental_surface": {
        "domain": "dental",
        "allowed": ["inspect_only", "modeling_mesh"],
        "blocked": ["global_sculpt_unbounded", "medical_claims"],
        "sculpt_policy": "local_detail_only",
        "primary_family": "inspect_only",
    },
    "architectural_mass": {
        "domain": "architecture",
        "allowed": ["macro", "modeling_mesh", "inspect_only"],
        "blocked": ["sculpt_region", "global_sculpt"],
        "sculpt_policy": "forbidden",
        "primary_family": "modeling_mesh",
    },
}
```

### 7.2. Router output dla orkiestratora

```json
{
  "active_build_mode": "reference_guided_low_poly",
  "active_construction_path": "low_poly_facet",
  "current_stage": "blockout_primary_masses",
  "allowed_tool_families": [
    "macro",
    "modeling_mesh",
    "inspect_only"
  ],
  "blocked_tool_families": [
    "global_sculpt",
    "smooth_organic_refinement"
  ],
  "sculpt_visibility": "hidden_until_low_poly_facets_established",
  "stage_success_criteria": [
    "primary masses exist",
    "required parts are represented",
    "no final smooth sphere-only result",
    "tail is planned as segmented angular chain"
  ],
  "next_checkpoint": "reference_compare_stage_checkpoint"
}
```

---

## 8. Stage flow dla low-poly squirrel

### 8.1. Stage 0 — Reference attach

```text
Tool:
reference_images(action="attach", ...)
```

Cel:

```text
Dodać front/side reference do aktywnego goal/session.
```

Exit criteria:

```text
- reference_count >= 1
- front/side labels są opisane albo wykrywalne
- guided_reference_readiness.compare_ready == true
```

---

### 8.2. Stage 1 — Reference understanding before build

```text
Draft shorthand:
reference understanding pass through the existing reference/guided surface
```

Cel:

```text
Zrozumieć referencje zanim LLM zacznie budować model.
```

Expected output dla wiewiórki:

```json
{
  "subject": "low-poly squirrel",
  "style": "faceted low-poly animal",
  "construction_path": "low_poly_facet",
  "sculpt_policy": "local_detail_only",
  "required_parts": [
    "body",
    "head",
    "ears",
    "snout_wedge",
    "curled_segmented_tail",
    "front_paws",
    "rear_foot",
    "acorn"
  ],
  "non_goals": [
    "smooth organic fur",
    "sphere-only final body parts",
    "global sculpt as primary method"
  ]
}
```

Exit criteria:

```text
- construction_path != unknown
- required_parts nie jest puste
- bounded guided/reference handoff exists
- verification_requirements istnieje
```

---

### 8.3. Stage 2 — Server-owned strategy apply, not a public MCP tool

```text
No public tool by default:
server applies strategy through guided state, visibility, and gate policy
```

Cel:

```text
Zamienić vision understanding na aktywną politykę narzędziową.
```

Dla low-poly:

```text
Allowed:
- macro
- modeling_mesh
- inspect_only

Blocked/default-hidden:
- global_sculpt
- smooth_organic_refinement

Sculpt:
- only local_detail_only
- only after faceted form exists
```

Exit criteria:

```text
- active_construction_path == low_poly_facet
- current_stage == blockout_primary_masses
- sculpt_region nie jest primary family
```

---

### 8.4. Stage 3 — Blockout primary masses

Cel:

```text
Zbudować podstawową strukturę z oddzielnych brył, ale jeszcze nie traktować kul jako finalnej formy.
```

Narzędzia:

```text
macro_create_part
macro_align_part_with_contact
primitive add tools
basic transforms
scene inspection
```

LLM powinien utworzyć:

```text
- Body
- Head
- Tail placeholder as planned segmented chain
- Ear_L
- Ear_R
- Snout placeholder
- FrontPaw_L
- FrontPaw_R
- RearFoot
- Acorn
```

Czego nie robić:

```text
- nie kończyć na smooth UV spheres
- nie robić tail jako jedna wydłużona kula
- nie wchodzić w global sculpt
```

Exit criteria:

```text
- wymagane części istnieją
- head/body/tail są mniej więcej ustawione
- tail ma plan segmentacji albo pierwsze angular segments
- brak claimu, że model jest finalny
```

Checkpoint:

```text
reference_compare_stage_checkpoint(stage="blockout_primary_masses")
```

---

### 8.5. Stage 4 — Secondary parts placement

Cel:

```text
Dodać/ustawić cechy rozpoznawcze.
```

Dla wiewiórki:

```text
- ears as triangular forms
- snout as wedge
- paws around acorn
- rear foot as thin angular shape
- eyes as dark side features
```

Narzędzia:

```text
macro_create_part
macro_align_part_with_contact
modeling_mesh transforms
mesh primitive cones/wedges
```

Exit criteria:

```text
- ears are triangular/sharp
- snout is wedge-like
- front paws visually hold acorn
- side silhouette still reserves space for curled tail
```

Checkpoint:

```text
reference_compare_stage_checkpoint(stage="place_secondary_parts")
```

---

### 8.6. Stage 5 — Low-poly facet refinement

To jest najważniejszy brakujący etap.

Cel:

```text
Zamienić owalne primitive blockouty w low-poly faceted construction.
```

Narzędzia docelowe:

```text
mesh_flatten
mesh_triangulate
mesh_mark_sharp
mesh_bevel
mesh_dissolve
mesh_transform_selected
mesh_shade_flat
macro_low_poly_facet_refine
```

Jeśli części tych narzędzi jeszcze nie ma, warto dodać przynajmniej makra:

```text
macro_low_poly_facet_refine
macro_low_poly_tail_segments
macro_low_poly_head_planes
macro_low_poly_finish
```

Dla wiewiórki:

```text
- head: faceted cheek planes
- snout: wedge, not ball
- ears: sharp triangular wedges/cones
- body: compact angular torso
- tail: 4-5 angular segments in curled arc
- paws: small angular forms
```

Exit criteria:

```text
- faceted geometry is visible
- smooth sphere look is reduced
- silhouette matches references better
- sculpt is still not needed except tiny local fixes
```

Checkpoint:

```text
reference_iterate_stage_checkpoint(stage="refine_low_poly_facets")
```

---

### 8.7. Stage 6 — Flat shading and materials

Cel:

```text
Dopiąć low-poly look przez shading/materials, nie przez dalsze organiczne modelowanie.
```

Narzędzia:

```text
mesh_shade_flat
mesh_mark_sharp
macro_low_poly_finish
material assign tools
```

Dla wiewiórki:

```text
- warm brown/orange body material
- darker eyes
- acorn material
- flat shaded facets
- no smooth fur material as default
```

Exit criteria:

```text
- flat shading visible
- faceted planes czytelne
- material groups support visual reading
```

Checkpoint:

```text
reference_compare_stage_checkpoint(stage="flat_shading_and_materials")
```

---

### 8.8. Stage 7 — Local sculpt if needed

Sculpt dopiero tutaj i tylko lokalnie.

Dozwolone przypadki:

```text
- sculpt_pinch_region on ear tips
- sculpt_pinch_region on snout tip
- sculpt_crease_region on inner tail curve
- sculpt_deform_region for tiny cheek/snouth adjustment
```

Niedozwolone jako default:

```text
- global sculpting body
- smoothing faceted low-poly planes
- organic fur sculpt
```

Exit criteria:

```text
- local sculpt nie niszczy low-poly character
- no smooth organic drift
```

Checkpoint:

```text
reference_iterate_stage_checkpoint(stage="local_sculpt_if_needed")
```

---

### 8.9. Stage 8 — Final reference compare

Cel:

```text
Sprawdzić, czy model odpowiada referencjom i czy nie uciekł ze ścieżki low-poly.
```

Sprawdzane elementy:

```text
- subject match
- front silhouette
- side silhouette
- required parts
- tail curl
- head/body ratio
- faceted style
- flat shading
- no smooth sphere-only final shapes
```

Output:

```text
continue_build / inspect_validate / stop
```

---

## 9. Prompt dla Vision Reference Understanding

### 9.1. Prompt systemowy / instrukcja backendu Vision

```text
You are a bounded reference-understanding assistant for a Blender MCP server.

Your job is not to decide final correctness and not to unlock tools directly.
Your job is to analyze reference images before the scene build starts and return
strict JSON describing:

1. subject
2. style
3. required parts
4. visible views
5. construction path
6. non-goals
7. recommended staged strategy
8. router handoff hints
9. verification requirements

Important boundaries:
- Do not invent MCP tools.
- Use only known construction_path vocabulary.
- Use only known refinement family vocabulary.
- Treat your output as advisory.
- Prefer explicit uncertainty over confident guesses.
- For low-poly/faceted references, do not recommend organic sculpt as primary path.
- For hard-surface references, do not recommend sculpt as primary path.
- For organic local-form references, sculpt_region can be valid.

Return only JSON.
```

### 9.2. Controlled vocabulary

```json
{
  "construction_path_values": [
    "low_poly_facet",
    "hard_surface",
    "organic_sculpt",
    "creature_blockout",
    "dental_surface",
    "product_mockup",
    "architectural_mass",
    "unknown"
  ],
  "refinement_family_values": [
    "macro",
    "modeling_mesh",
    "sculpt_region",
    "inspect_only"
  ],
  "sculpt_policy_values": [
    "forbidden",
    "local_detail_only",
    "allowed_after_blockout",
    "primary_method"
  ]
}
```

Historyczny alias note:

```text
mesh_edit -> modeling_mesh
material_finish -> stage/finish guidance, not a current canonical family
```

---

## 10. Analiza bibliotek / modeli Vision — co najlepiej siądzie

### 10.1. Kryteria wyboru

Dla `blender-ai-mcp` biblioteka/model powinna dobrze wspierać:

```text
1. Semantyczne rozumienie referencji:
   - co to jest?
   - jaki styl?
   - jakie części są ważne?

2. Klasyfikację ścieżki konstrukcyjnej:
   - low_poly_facet
   - hard_surface
   - organic_sculpt
   - dental_surface
   - architectural_mass

3. Deterministyczne cechy obrazu:
   - silhouette
   - bbox
   - aspect ratio
   - edge/facet density
   - dominant colors

4. Segmentację obiektu / części:
   - object mask
   - part masks
   - cropy dla head/tail/ears/etc.

5. Integrację z repo:
   - opcjonalność
   - Docker friendliness
   - brak wymogu ciężkiego GPU dla MVP
   - sidecar zamiast twardej zależności
   - bounded output
```

---

### 10.2. Najlepszy stack MVP

Najlepszy wybór na teraz:

```text
MVP:
- VLM przez istniejący backend: OpenRouter / Gemini / MLX / Transformers
- Pillow + numpy jako deterministic baseline
- opcjonalnie OpenCV albo scikit-image dla edge/facet/color metrics
- bez SAM/CLIP jako twardej zależności w MVP
```

Dlaczego:

```text
- Masz już VLM runner i kontrakty.
- Problem na dziś to nie brak SAM, tylko brak pre-build understanding contract.
- Python CV może szybko dodać tanie evidence bez dużych modeli.
- CLIP/SAM warto przygotować kontraktowo, ale wdrożyć jako optional later.
```

---

### 10.3. Biblioteki deterministic CV

#### Pillow + numpy

Status:

```text
Najlepsze jako baseline.
```

Do czego:

```text
- load image
- alpha/threshold masks
- Otsu-like threshold
- largest component
- bbox
- aspect ratio
- crop
- simple color analysis
```

Plusy:

```text
- lekkie
- już pasuje do repo
- łatwe w Dockerze
- szybkie
- dobre do deterministic evidence
```

Minusy:

```text
- nie rozumie semantyki
- nie rozdzieli head/tail/ears bez dodatkowej logiki/modelu
- low-poly facet detection będzie ograniczone
```

Rekomendacja:

```text
Zostawić jako core dependency i rozwinąć.
```

---

#### OpenCV / opencv-python-headless

Status:

```text
Bardzo dobry kandydat na Phase 2.
```

Do czego:

```text
- Canny edges
- contour detection
- polygon approximation
- Hough lines
- convex hull
- color histograms
- edge density
- facet/plane hint metrics
- image alignment preprocessing
```

Plusy:

```text
- świetne do geometrii 2D i konturów
- dobre do low-poly/facet hints
- dużo gotowych algorytmów
- opencv-python-headless nadaje się do serwera
```

Minusy:

```text
- cięższe niż Pillow
- nie rozumie semantyki
- może zwiększyć rozmiar obrazu Docker
- trzeba uważać z wersjami system dependencies
```

Najlepsze użycie w projekcie:

```text
server/adapters/mcp/vision/cv_features.py
```

Przykładowe metrics:

```json
{
  "edge_density": 0.31,
  "polygonal_contour_ratio": 0.72,
  "dominant_color_count": 5,
  "facet_likelihood": "medium_high",
  "silhouette_aspect_ratio": 1.42
}
```

Rekomendacja:

```text
Dodać jako optional extra, np. poetry install --with cv.
Nie robić jako twarda zależność core na start.
```

---

#### scikit-image

Status:

```text
Dobry kandydat alternatywny albo uzupełniający OpenCV.
```

Do czego:

```text
- thresholding
- regionprops
- morphology
- contours
- segmentation basics
- texture features
```

Plusy:

```text
- bardzo dobry do naukowego image processing
- czytelne API
- dobre region metrics
```

Minusy:

```text
- dependency chain bywa cięższy
- mniej „produkcyjno-CV” niż OpenCV dla Hough/Canny/pipelines
- nadal nie daje semantyki
```

Rekomendacja:

```text
Jeśli chcesz minimalnie: OpenCV wystarczy.
Jeśli chcesz czytelniejsze region metrics: scikit-image jako optional.
```

---

### 10.4. Biblioteki do segmentacji

#### rembg / U2-Net style foreground extraction

Status:

```text
Dobry kandydat do prostego usuwania tła, ale nie do part segmentation.
```

Do czego:

```text
- foreground object mask
- reference crop
- lepsze silhouette porównanie
```

Plusy:

```text
- często dobre do jednego obiektu na obrazku
- prostsze niż SAM
```

Minusy:

```text
- nie rozdziela części obiektu
- jakość zależy od typu obrazka
- model dependency
```

Rekomendacja:

```text
Może być przydatne jako optional foreground mask sidecar,
ale nie jest priorytetem, bo masz już alpha/Otsu/largest-component baseline.
```

---

#### SAM / Segment Anything

Status:

```text
Najlepszy kierunek dla optional segmentation sidecar.
```

Do czego:

```text
- object masks
- region masks
- part crops
- mask proposals
- silhouette refinement
```

Plusy:

```text
- świetne maski regionów
- dobre do oddzielenia sylwetki od tła
- może dawać wiele candidate masks
- pasuje do sidecar architecture
```

Minusy:

```text
- SAM sam nie powie „to jest ogon”
- potrzebuje promptów: box/point/text przez inny model
- cięższy runtime
- może wymagać GPU dla komfortowej pracy
- nie powinien być core dependency
```

Najlepsze użycie w projekcie:

```text
ReferencePartSegmentationContract jako advisory-only sidecar.
```

Przykład outputu:

```json
{
  "status": "available",
  "provider_name": "sam_sidecar",
  "advisory_only": true,
  "parts": [
    {
      "part_label": "main_object",
      "mask_path": "/tmp/ref_main_object_mask.png",
      "crop_path": "/tmp/ref_main_object_crop.png",
      "confidence": 0.91
    }
  ]
}
```

Rekomendacja:

```text
Nie dodawać do MVP jako twarda zależność.
Przygotować kontrakt i config już teraz.
Wdrożyć jako optional sidecar w Phase 4.
```

---

#### FastSAM / YOLO segmentation variants

Status:

```text
Możliwe jako lżejsza alternatywa dla SAM, ale trzeba testować jakość.
```

Do czego:

```text
- szybka segmentacja obiektu
- prostsze deploymenty GPU/CPU zależnie od modelu
```

Plusy:

```text
- może być szybsze / prostsze
- może pasować do sidecar
```

Minusy:

```text
- jakość part masks może być gorsza niż SAM
- może być bardziej dataset-dependent
- nadal nie robi semantycznego part naming bez innego modelu
```

Rekomendacja:

```text
Tylko jako porównanie sidecar, nie pierwszy wybór.
```

---

### 10.5. Biblioteki/model do klasyfikacji stylu i routingu

#### CLIP / OpenCLIP

Status:

```text
Najlepszy klasyczny kandydat do image-text routing.
```

Do czego:

```text
- klasyfikacja stylu referencji
- scoring tekstów typu:
  - low-poly faceted squirrel
  - smooth organic squirrel
  - hard-surface product model
  - dental crown scan
  - architectural facade
- wybór construction_path
```

Plusy:

```text
- dobrze pasuje do routingu
- nie musi generować tekstu
- można mieć kontrolowaną listę promptów
- daje scores zamiast prozy
```

Minusy:

```text
- nie daje strukturalnego opisu części
- może mylić podobne style
- trzeba kalibrować prompt labels
- lokalny model to dodatkowa zależność
```

Najlepszy flow:

```text
VLM opisuje referencję.
CLIP daje classification_scores.
Router łączy oba sygnały.
```

Przykład:

```json
{
  "classification_scores": [
    {
      "label": "low-poly faceted animal reference",
      "score": 0.82,
      "suggested_construction_path": "low_poly_facet"
    },
    {
      "label": "smooth organic animal sculpt reference",
      "score": 0.31,
      "suggested_construction_path": "organic_sculpt"
    }
  ]
}
```

Rekomendacja:

```text
Dodać jako Phase 3 optional classifier.
Nie zastępować VLM — używać jako drugi sygnał routingu.
```

---

#### SigLIP

Status:

```text
Bardzo interesująca alternatywa dla CLIP.
```

Do czego:

```text
- image-text classification
- style/path routing
```

Plusy:

```text
- często mocny embedding model
- podobna rola do CLIP
```

Minusy:

```text
- trzeba sprawdzić dostępność i integrację w Twoim runtime
- nadal nie daje masek ani pełnej semantyki części
```

Rekomendacja:

```text
Warto porównać z OpenCLIP w harnessie.
```

---

### 10.6. VLM / multimodal models

#### OpenRouter / Gemini / OpenAI-compatible external

Status:

```text
Najlepszy obecny sposób na semantic reference understanding.
```

Do czego:

```text
- rozumienie subject/style
- opis części
- rozumienie front/side reference
- generowanie structured JSON
- porównanie aktualnego viewportu z referencją
```

Plusy:

```text
- najlepsza semantyka
- szybki rozwój bez lokalnego GPU
- już masz integrację transport/profiles
- dobry do prompt/schema-first approach
```

Minusy:

```text
- koszt
- latency
- zależność od providerów
- niestabilność structured output między modelami
- czasem proza zamiast JSON
```

Rekomendacja:

```text
Użyć jako primary semantic layer w MVP.
Wzmocnić parser, schema i contract profile.
```

---

#### MLX local / Transformers local

Status:

```text
Dobry kierunek lokalny, ale jakość trzeba mierzyć scenario harnessami.
```

Do czego:

```text
- lokalne VLM smoke/dev testing
- prywatność / brak kosztu per request
- fallback semantic analysis
```

Plusy:

```text
- lokalny runtime
- brak vendor lock-in
- dobra ścieżka dla Apple Silicon przez MLX
```

Minusy:

```text
- jakość może być słabsza niż duże external VLM
- structured output bywa niestabilny
- większe modele wymagają zasobów
```

Rekomendacja:

```text
Zostawić jako backend, ale promotion robić tylko przez harness scoring.
```

---

#### BLIP / BLIP-2

Status:

```text
Może pomagać w captioningu, ale raczej nie jako główny moduł.
```

Do czego:

```text
- image caption
- prosty opis obiektu
```

Plusy:

```text
- przydatny do caption baseline
```

Minusy:

```text
- słabszy niż nowsze VLM-y w złożonym reasoning
- nie daje łatwo router-ready contract
- dodatkowy runtime
```

Rekomendacja:

```text
Nie priorytet. VLM external/local + CLIP/SigLIP daje lepszy kierunek.
```

---

#### Florence-2 / vision-language detection/caption style models

Status:

```text
Ciekawy kandydat do detection/caption/region tasks, ale jako later eval.
```

Do czego:

```text
- captioning
- object detection-ish outputs
- region description
```

Plusy:

```text
- może łączyć caption i region grounding lepiej niż klasyczny captioner
```

Minusy:

```text
- trzeba sprawdzić licencję, runtime, jakość structured output
- może być za ciężkie na MVP
```

Rekomendacja:

```text
Dodać do listy modeli do harness evaluation, ale nie blokować MVP.
```

---

### 10.7. Object grounding / detection

#### Grounding DINO

Status:

```text
Dobry kandydat, jeśli chcesz text-prompted detection + SAM.
```

Do czego:

```text
- znaleźć box dla „tail”, „head”, „ear”, „acorn”
- potem SAM robi maskę z boxa
```

Plusy:

```text
- bardzo pasuje do pipeline GroundingDINO → SAM
- może dać part boxes na podstawie tekstu
```

Minusy:

```text
- cięższy stack
- jakość zależy od promptów
- kolejne ryzyko dependency
```

Rekomendacja:

```text
Phase 5, gdy part segmentation stanie się realną potrzebą.
Nie MVP.
```

---

#### OWL-ViT / OWLv2 style open-vocabulary detection

Status:

```text
Alternatywa dla text-prompted detection.
```

Do czego:

```text
- wykrywanie obiektów/części z tekstowych promptów
```

Plusy:

```text
- open-vocabulary detection
- może wspierać part crops
```

Minusy:

```text
- wymaga testów jakości na stylizowanych low-poly referencjach
- nie daje samych masek
```

Rekomendacja:

```text
Optional eval, nie pierwszy wybór.
```

---

#### YOLO detection/segmentation

Status:

```text
Dobre dla znanych klas, słabsze dla ogólnego reference understanding.
```

Do czego:

```text
- wykrywanie znanych obiektów
- segmentation dla znanych klas
```

Plusy:

```text
- szybkie
- produkcyjne
- dobra dokumentacja i tooling
```

Minusy:

```text
- low-poly squirrel parts nie będą standardową klasą
- mniej pasuje do otwartego stylu referencji
- wymaga treningu/fine-tune dla custom parts
```

Rekomendacja:

```text
Nie priorytet dla tego problemu.
Możliwe dla przyszłych domen z zamkniętą klasą obiektów.
```

---

### 10.8. Depth / 3D hints

#### MiDaS / ZoeDepth / depth estimation models

Status:

```text
Potencjalnie ciekawe, ale nie dla MVP.
```

Do czego:

```text
- approximate depth map z referencji
- lepsze spatial hints przy pojedynczym widoku
```

Plusy:

```text
- może pomóc przy form understanding
```

Minusy:

```text
- referencje stylizowane low-poly mogą dawać słabe depth maps
- to nadal nie jest prawda 3D
- dodatkowy ciężar runtime
```

Rekomendacja:

```text
Nie teraz. Najpierw reference_understanding + routing + stage validation.
```

---

## 11. Najlepsza rekomendowana kombinacja

### 11.1. Faza MVP

```text
1. Existing VLM backend
   - OpenRouter/Gemini/MLX/Transformers
   - strict reference_understanding JSON

2. Existing Pillow/numpy silhouette
   - bbox
   - aspect ratio
   - mask extraction
   - dominant color baseline

3. Router normalization
   - construction_path → allowed families
   - sculpt_policy
   - stage plan

4. Existing reference_compare / iterate
   - after each build stage
```

Dlaczego to najlepiej siądzie:

```text
- minimalny koszt zmian
- największy wpływ na błąd orkiestratora
- pasuje do obecnych kontraktów
- nie blokuje późniejszego SAM/CLIP
- rozwiązuje dokładnie problem: LLM zaczyna złą ścieżką
```

### 11.2. Faza 2

```text
Add optional OpenCV/scikit-image feature extraction:
- edge_density
- contour polygonality
- color palette
- facet_likelihood
- front/side silhouette hints
```

### 11.3. Faza 3

```text
Add optional CLIP/SigLIP classifier:
- classify construction path
- score style labels
- compare VLM suggestion vs embedding score
```

### 11.4. Faza 4

```text
Add SAM sidecar:
- object masks
- optional part masks
- crop artifacts
- still advisory only
```

### 11.5. Faza 5

```text
Add GroundingDINO/OWL-ViT style part localization if needed:
- text-prompted boxes for head/tail/ear/acorn
- SAM mask from boxes
```

---

## 12. Konfiguracja runtime

Proponowane env vars:

```bash
# Core
VISION_REFERENCE_UNDERSTANDING_ENABLED=true
VISION_REFERENCE_UNDERSTANDING_PROVIDER=default_vision_backend
VISION_REFERENCE_UNDERSTANDING_MAX_IMAGES=4
VISION_REFERENCE_UNDERSTANDING_MAX_TOKENS=900

# Optional deterministic CV
VISION_CV_FEATURES_ENABLED=false
VISION_CV_PROVIDER=opencv
VISION_CV_FEATURES_MAX_IMAGE_SIZE=1024

# Optional CLIP/SigLIP classification
VISION_CLASSIFIER_ENABLED=false
VISION_CLASSIFIER_PROVIDER=openclip
VISION_CLASSIFIER_MODEL=ViT-B-32
VISION_CLASSIFIER_DEVICE=auto

# Optional segmentation sidecar
VISION_SEGMENTATION_ENABLED=false
VISION_SEGMENTATION_PROVIDER=generic_sidecar
VISION_SEGMENTATION_ENDPOINT=http://localhost:8091/segment
VISION_SEGMENTATION_TIMEOUT_SECONDS=10
VISION_SEGMENTATION_MAX_PARTS=12
```

Poetry extras:

```toml
[tool.poetry.extras]
vision = ["transformers", "torch", "torchvision"]
mlx = ["mlx", "mlx-vlm"]
cv = ["opencv-python-headless", "scikit-image"]
clip = ["open-clip-torch"]
segmentation = []
```

Uwaga:

```text
Segmentation najlepiej jako sidecar, a nie dependency w głównym serwerze.
```

---

## 13. Proponowane pliki do dodania / zmiany

### 13.1. Kontrakty

```text
server/adapters/mcp/contracts/reference_understanding.py
```

Albo jako rozszerzenie:

```text
server/adapters/mcp/contracts/reference.py
```

Lepsze na czysto:

```text
contracts/reference_understanding.py
```

Bo `reference.py` już jest duży.

---

### 13.2. Vision prompt/schema/parser

```text
server/adapters/mcp/vision/reference_understanding.py
server/adapters/mcp/vision/reference_understanding_prompt.py
server/adapters/mcp/vision/reference_understanding_parser.py
```

---

### 13.3. CV features

```text
server/adapters/mcp/vision/cv_features.py
server/adapters/mcp/vision/facet_detection.py
server/adapters/mcp/vision/color_features.py
```

---

### 13.4. Classifier

```text
server/adapters/mcp/vision/classification/__init__.py
server/adapters/mcp/vision/classification/base.py
server/adapters/mcp/vision/classification/clip_backend.py
server/adapters/mcp/vision/classification/prompt_labels.py
```

---

### 13.5. Guided/router integration aligned to current seams

Stary owner sketch z `server/adapters/mcp/router/...` i
`server/application/router/...` jest dziś nieaktualny. W aktualnym checkoutcie
ten follow-up powinien przechodzić przez istniejące guided/reference seams:

```text
server/adapters/mcp/areas/reference.py
server/adapters/mcp/contracts/reference.py
server/adapters/mcp/session_capabilities.py
server/adapters/mcp/transforms/visibility_policy.py
server/adapters/mcp/guided_mode.py
server/adapters/mcp/areas/router.py
server/router/application/session_phase_hints.py
server/router/infrastructure/tools_metadata/reference/reference_compare_stage_checkpoint.json
server/router/infrastructure/tools_metadata/reference/reference_iterate_stage_checkpoint.json
```

Jeśli kiedyś pojawi się osobny helper dla reference understanding, powinien
wisieć na tych seamach zamiast przywracać nieistniejące ścieżki z tego
historycznego szkicu.

---

### 13.6. MCP area/surface

```text
server/adapters/mcp/areas/reference_understanding.py
```

Albo w istniejącym:

```text
server/adapters/mcp/areas/reference.py
```

Rekomendacja:

```text
Domyślnie rozszerzać istniejące areas/reference.py.
Oddzielne areas/reference_understanding.py dopiero po osobnym public-surface review.
```

---

## 14. Testy i eval pack

### 14.1. Unit tests

```text
tests/unit/adapters/mcp/test_vision_prompting.py
tests/unit/adapters/mcp/test_vision_parsing.py
tests/unit/adapters/mcp/test_reference_images.py
tests/unit/adapters/mcp/test_contract_payload_parity.py
tests/unit/adapters/mcp/test_quality_gate_intake.py
tests/unit/adapters/mcp/test_guided_flow_state_contract.py
tests/unit/adapters/mcp/test_visibility_policy.py
tests/unit/adapters/mcp/test_guided_mode.py
tests/unit/adapters/mcp/test_cv_features.py
```

Testy powinny sprawdzać:

```text
- low_poly_facet nie daje sculpt_region jako primary
- hard_surface blokuje sculpt_region jako default
- organic_sculpt może dać sculpt_region
- unknown path daje inspect_only albo macro-safe fallback
- parser naprawia common JSON drift
- invented tools są odrzucane albo mapowane aliasami
```

---

### 14.2. Golden scenarios

Proponowane fixtures:

```text
tests/fixtures/vision_eval/reference_understanding_low_poly_squirrel_front_side/
tests/fixtures/vision_eval/reference_understanding_smooth_organic_creature/
tests/fixtures/vision_eval/reference_understanding_hard_surface_phone/
tests/fixtures/vision_eval/reference_understanding_architectural_facade/
tests/fixtures/vision_eval/reference_understanding_dental_crown_mockup/
```

Każdy folder:

```text
front.png
side.png
golden.json
notes.md
```

Przykładowy `golden.json` dla low-poly squirrel:

```json
{
  "expected_subject_contains": ["squirrel"],
  "expected_style": "low_poly_faceted",
  "expected_construction_path": "low_poly_facet",
  "expected_primary_family": "modeling_mesh",
  "forbidden_primary_family": "sculpt_region",
  "expected_required_parts": [
    "body",
    "head",
    "tail_curled_segmented",
    "ear_left",
    "ear_right",
    "snout_wedge"
  ]
}
```

---

### 14.3. Harness scoring

Jeżeli kiedyś do `scripts/vision_harness.py` dojdzie providerless fixture mode,
powinien być jawnie opt-in i korzystać z istniejącego drzewa `vision_eval`,
zamiast zmieniać domyślną ścieżkę backend-executing. Historyczny szkic CLI:

```bash
poetry run python scripts/vision_harness.py \
  --fixture-only reference-understanding \
  --backend openai_compatible_external \
  --golden-json tests/fixtures/vision_eval/reference_understanding_low_poly_squirrel_front_side/golden.json
```

Scoring:

```text
+ subject match
+ style match
+ construction_path match
+ primary family match
+ sculpt policy match
+ required parts recall
+ non-goals present
- invented tools
- sculpt primary on low-poly/hard-surface
- missing router_handoff
```

Przykładowe score output:

```json
{
  "scenario": "low_poly_squirrel_front_side",
  "score": 0.91,
  "grade": "strong",
  "passed": true,
  "failures": [],
  "warnings": [
    "missing acorn in required_parts"
  ]
}
```

---

## 15. Acceptance criteria

MVP uznajemy za gotowe, gdy:

```text
1. Reference understanding może działać na attached references przez istniejący
   guided/reference seam; osobna publiczna akcja pozostaje opcjonalna.
2. Zwraca typed ReferenceUnderstandingContract albo równoważny typed summary w
   istniejącym response payloadzie.
3. Router mapuje construction_path na allowed/blocked tool families.
4. Low-poly squirrel scenario daje:
   - construction_path = low_poly_facet
   - primary_refinement_family = modeling_mesh albo macro
   - sculpt_policy = local_detail_only
   - sculpt_region nie jest primary
5. Orchestrator może odczytać:
   - current_stage
   - allowed_tool_families
   - required_parts
   - non_goals
   - next_checkpoint
6. Stage compare / iterate dalej działa bez zmiany publicznego flow.
7. Brak Vision backendu nie psuje normalnego builda — fallback do inspect_only / safe macro.
```

---

## 16. Ryzyka i guardrails

### 16.1. Vision hallucinuje tool names

Ryzyko:

```text
Vision zwraca „mesh_magic_flatten_super_tool”.
```

Guardrail:

```text
- allowed tool ids whitelist
- alias map
- unknown tool names dropped
- router maps family, not raw tool name
```

---

### 16.2. Vision myli styl

Ryzyko:

```text
Vision uzna low-poly za organic sculpt.
```

Guardrail:

```text
- CLIP/SigLIP classification later
- deterministic edge/facet metrics
- conservative router policy
- low confidence → inspect_only / macro-safe fallback
```

---

### 16.3. LLM ignoruje non-goals

Ryzyko:

```text
LLM mimo wszystko używa smooth spheres jako finalu.
```

Guardrail:

```text
- stage exit criteria
- reference_iterate_stage_checkpoint
- action_hints
- refinement_handoff
- test: sphere-only low-poly final should fail
```

---

### 16.4. SAM/CLIP robią się ciężkim chaosem

Ryzyko:

```text
Za dużo modeli, zbyt trudny runtime, Docker puchnie.
```

Guardrail:

```text
- contract-first
- optional extras
- sidecar pattern
- core server działa bez segmentacji/classifierów
```

---

### 16.5. Dental/medical overclaim

Ryzyko:

```text
Vision/LLM zaczyna sugerować kliniczną poprawność.
```

Guardrail:

```text
- dental_surface jako visualization/mockup/design-support only
- no clinical authority
- deterministic measurements required
- explicit boundary policy
```

---

## 17. Roadmap tasków

### TASK 1 — Add ReferenceUnderstandingContract

```markdown
## Goal
Add typed contract for pre-build reference understanding.

## Files
- server/adapters/mcp/contracts/reference_understanding.py
- tests/unit/adapters/mcp/test_reference_understanding_contract.py

## Done when
- contract validates JSON output
- controlled vocabularies exist
- boundary_policy is explicit
```

---

### TASK 2 — Add pre-build reference-understanding entry path

```markdown
## Goal
Historical draft only. A public `reference_understand(...)` MCP surface requires
separate public-tool review; the default implementation target remains the
existing reference/guided-state seam.

## Files
- server/adapters/mcp/areas/reference.py
- server/adapters/mcp/vision/prompting.py
- server/adapters/mcp/vision/parsing.py

## Done when
- attached references can be analyzed before build
- output contains ReferenceUnderstandingContract
- no references → readiness-style blocked response
```

---

### TASK 3 — Add router construction path policy

```markdown
## Goal
Normalize construction_path into allowed/blocked tool families.

## Files
- server/adapters/mcp/session_capabilities.py
- server/adapters/mcp/transforms/visibility_policy.py
- server/adapters/mcp/guided_mode.py
- server/router/application/session_phase_hints.py

## Done when
- low_poly_facet → modeling_mesh/macro, sculpt local only
- hard_surface → modeling_mesh/macro, sculpt forbidden/default-hidden
- organic_sculpt → sculpt_region allowed
- unknown → inspect_only/safe fallback
```

---

### TASK 4 — Add orchestrator handoff payload

```markdown
## Goal
Expose active reference strategy to LLM orchestrator.

## Files
- server/adapters/mcp/contracts/reference.py
- server/adapters/mcp/areas/reference.py
- server/adapters/mcp/session_capabilities.py
- server/adapters/mcp/areas/router.py
- server/adapters/mcp/guided_mode.py

## Output fields
- active_construction_path
- current_stage
- allowed_tool_families
- blocked_tool_families
- required_parts
- non_goals
- stage_success_criteria
- next_checkpoint

## Done when
LLM can build stage 1 without guessing the style/tool family.
```

---

### TASK 5 — Add low-poly facet stage

```markdown
## Goal
Introduce explicit low-poly faceted refinement stage.

## New stage
refine_low_poly_facets

## Suggested tools/macros
- mesh_flatten
- mesh_triangulate
- mesh_mark_sharp
- mesh_shade_flat
- macro_low_poly_facet_refine
- macro_low_poly_tail_segments
- macro_low_poly_finish

## Done when
Squirrel flow no longer jumps from smooth spheres to sculpt as primary correction.
```

---

### TASK 6 — Add deterministic CV features optional extra

```markdown
## Goal
Add optional image feature extraction for routing evidence.

## Metrics
- edge_density
- contour_count
- polygonal_contour_ratio
- dominant_colors
- silhouette_aspect_ratio
- facet_likelihood

## Done when
ReferenceUnderstandingContract can include visual_evidence from Python CV.
```

---

### TASK 7 — Add CLIP/SigLIP optional classifier

```markdown
## Goal
Add image-text classifier for construction_path scoring.

## Labels
- low-poly faceted animal reference
- smooth organic creature sculpt reference
- hard-surface product reference
- dental crown scan/mockup
- architectural massing reference

## Done when
classification_scores can support or challenge VLM construction_path.
```

---

### TASK 8 — Add SAM sidecar support

```markdown
## Goal
Use existing part_segmentation contract as optional sidecar.

## Done when
- missing sidecar does not break flow
- sidecar output is advisory-only
- masks/crops can be attached to compare payloads
```

---

## 18. Proponowana kolejność implementacji

Najkrótsza ścieżka z największym efektem:

```text
1. ReferenceUnderstandingContract
2. reference-understanding prompt + parser on existing vision/reference owners
3. construction-path mapping through current guided/session/visibility seams
4. orchestrator handoff payload on existing reference/guided responses
5. low_poly_facet stage name + stage guidance
6. low-poly squirrel golden eval
7. optional OpenCV feature extraction
8. optional CLIP/SigLIP classifier
9. optional SAM sidecar
```

Nie zaczynać od:

```text
- SAM
- GroundingDINO
- fine-tuningu YOLO
- ciężkiego local VLM jako blocker
```

Bo największy problem nie jest jeszcze w segmentacji. Największy problem to:

```text
LLM nie dostaje typed construction strategy przed pierwszym buildem.
```

---

## 19. Finalny przykład: idealny handoff dla orkiestratora

```json
{
  "goal": "Create a low-poly squirrel from attached front and side references",
  "active_reference_strategy": {
    "understanding_id": "understanding_goal_123_001",
    "subject": "low-poly squirrel",
    "construction_path": "low_poly_facet",
    "sculpt_policy": "local_detail_only",
    "current_stage": "blockout_primary_masses"
  },
  "allowed_tool_families": [
    "macro",
    "modeling_mesh",
    "inspect_only"
  ],
  "blocked_tool_families": [
    "global_sculpt",
    "smooth_organic_refinement"
  ],
  "required_parts": [
    "body",
    "head",
    "ear_left",
    "ear_right",
    "snout_wedge",
    "tail_curled_segmented",
    "front_paws",
    "rear_foot",
    "acorn"
  ],
  "non_goals": [
    "do not make smooth organic fur",
    "do not leave body parts as simple spheres",
    "do not use sculpt as the main construction method"
  ],
  "stage_success_criteria": [
    "all required primary parts exist",
    "tail is planned or created as multiple angular segments",
    "head/body/tail proportions roughly match front and side references",
    "no claim that smooth primitive spheres are final low-poly geometry"
  ],
  "next_checkpoint": "reference_compare_stage_checkpoint"
}
```

---

## 20. Konkluzja

Najlepsze podejście:

```text
Contract-first, not model-first.
```

Czyli:

```text
Najpierw zdefiniować, co Vision ma zwracać.
Potem router ma to normalizować.
Dopiero potem dobierać biblioteki i modele.
```

Dla Twojego przypadku najlepszy stack na start:

```text
1. Existing VLM backend for semantic understanding.
2. Pillow/numpy for deterministic baseline.
3. Router construction_path policy.
4. Explicit low_poly_facet guided stage.
5. Existing reference_compare/reference_iterate loop.
```

Biblioteki później:

```text
OpenCV/scikit-image → deterministic visual evidence
CLIP/SigLIP → construction path scoring
SAM → masks/parts sidecar
GroundingDINO/OWL-ViT → optional part boxes before SAM
```

Najważniejszy efekt:

```text
Orkiestrator przestaje zgadywać.
Dostaje typed plan:
- co budować
- w jakim stylu
- jaką ścieżką
- jakich narzędzi nie używać
- kiedy robić checkpoint
- kiedy wolno wejść w sculpt
```

To powinno znacząco poprawić jakość flow dla referencji typu low-poly squirrel, ale też stworzyć bazę pod kolejne domeny: hard-surface, architekturę, product mockupy, organic sculpt i dental visualization.
