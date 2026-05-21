# TASK-171A / TASK-171B: On-Demand Vision Capabilities, Creature Runtime Repair, And Structured Vision Handoff
## Cel
Celem nie jest wrzucenie wszystkich modeli vision do startu kontenera.
Celem jest zbudowanie runtime, który:
1. wie, jakie zdolności vision są dostępne,
2. wie, kiedy dana zdolność jest potrzebna,
3. potrafi zgłosić brakujące prerequisites użytkownikowi,
4. ładuje ciężkie modele dopiero w odpowiednim momencie,
5. po użyciu potrafi zwolnić zasoby,
6. przekazuje LLM-owi konkretne, wykonawcze instrukcje zamiast luźnego opisu.
Najpierw trzeba naprawić flow/runtime, bo obecnie nawet dobry model może zostać źle użyty, jeśli:
* stage gate odpala się za wcześnie,
* active scope nie zawiera nowo zarejestrowanej części,
* compact feedback wycina konkretny repair plan,
* wymagane role nie zgadzają się z gate’ami,
* vision output jest prose-only zamiast structured handoff.
---
# Rekomendowana kolejność
## Etap 1: TASK-171B — Creature Stage Gate And Active Scope Repair
Ten etap powinien wejść jako pierwszy, bo daje największą poprawę jakości bez dokładania ciężkich modeli.
### Dlaczego najpierw to?
Obecne problemy są głównie runtime/logiczne, nie modelowe:
* `eye_pair` potrafi działać jak hard blocker, ale nie jest spójnie obsłużony jako buildable role.
* `tail_mass` jest allowed w primary wave, ale nie domyka primary prerequisites.
* `snout_mass` jest allowed w secondary wave, ale nie domyka secondary prerequisites.
* `guided_register_part(...)` aktualizuje registry, ale może nie rozszerzać `active_target_scope`.
* compact iterate potrafi wyciąć `correction_candidates`, mimo że truth layer zna konkretny macro repair.
Jeżeli tego nie naprawimy, cięższe vision będzie tylko produkować lepsze sygnały, które runtime nadal może zgubić albo odpalić w złym momencie.
---
## TASK-171B zakres
### 1. Naprawić role prerequisites dla creature
#### Primary wave
`tail_mass` powinien być required dla creature primary stage.
Docelowo:
```
_GUIDED_PRIMARY_REQUIRED_ROLES["creature"] = (
    "body_core",
    "head_mass",
    "tail_mass",
)
```
Efekt:
* system nie przejdzie zbyt wcześnie dalej bez ogona,
* silhouette creature będzie kompletna wcześniej,
* compare nie będzie próbował poprawiać detali na niepełnej bryle.
#### Secondary wave
`snout_mass` powinien być required dla creature secondary stage.
Docelowo:
```
_GUIDED_SECONDARY_REQUIRED_ROLES["creature"] = (
    "snout_mass",
    "ear_pair",
    "foreleg_pair",
    "hindleg_pair",
)
```
Efekt:
* pysk domyka secondary wave,
* creature nie przechodzi do refinement bez kluczowej części twarzy,
* mniej przypadków, gdzie model robi oczy/uszy bez poprawnego head/snout relation.
---
### 2. Zdegradować albo poprawnie wpisać `eye_pair`
Aktualny problem: `eye_pair` jest wymagany przez gate, ale nie jest spójnie wpisany w creature flow roles.
Są dwie sensowne opcje.
#### Opcja A — rekomendowana na teraz
`eye_pair` jako late/detail/advisory role.
Czyli:
* nie blokuje primary wave,
* nie blokuje secondary wave,
* może blokować final polish albo finish,
* nie przerzuca zbyt wcześnie do `inspect_validate`.
Docelowe zachowanie:
```
eye_pair missing:
  stage: finish_or_stop / detail polish
  severity: advisory albo late_required
  no early inspect_validate
```
#### Opcja B
Wpisać `eye_pair` jako pełnoprawną role:
```
"place_secondary_parts": {
    "allowed_roles": [
        "snout_mass",
        "ear_pair",
        "eye_pair",
        "foreleg_pair",
        "hindleg_pair",
    ],
}
```
Plus cardinality:
```
_GUIDED_ROLE_CARDINALITY["creature"]["eye_pair"] = 2
```
Tej opcji nie polecam jako pierwszej, bo oczy są detalem i mogą pchać runtime w złe priorytety.
Lepiej najpierw doprowadzić do poprawnej sylwetki, mas i kontaktów.
---
### 3. `guided_register_part(...)` musi rozszerzać active scope
Po rejestracji parta:
```
guided_register_part(object_name="squirrel_tail", role="tail_mass")
```
runtime powinien:
1. dodać part do `guided_part_registry`,
2. przeliczyć role summary,
3. potencjalnie advance’ować flow,
4. dopisać `squirrel_tail` do `active_target_scope.object_names`,
5. zaktualizować `object_count`,
6. zachować `primary_target`,
7. zachować `collection_name`.
Docelowa helper funkcja:
```
def _extend_active_target_scope_with_registered_part(
    guided_flow_state: dict[str, Any],
    *,
    object_name: str,
) -> dict[str, Any]:
    ...
```
Zasady:
* nie duplikować nazw case-insensitive,
* nie zmieniać primary_target, jeśli już istnieje,
* jeżeli active_target_scope nie istnieje, nie wymyślać sceny na siłę,
* jeżeli object_names istnieją, dopisać nowy part,
* object_count = len(object_names).
Efekt:
* compare widzi nowo utworzoną część od razu,
* blocker/focus może wskazać nowy part,
* last mutation scope nie odpada przez stary workset,
* seam/contact feedback ma realne target objects.
---
### 4. Compact feedback musi przepuszczać top repair plan
Truth layer już potrafi produkować konkretne macro candidates, np.:
* `macro_align_part_with_contact`
* `macro_attach_part_to_surface`
* `macro_place_supported_pair`
Problem: compact iterate wycina nested debug payload, w tym często konkretne `correction_candidates`.
W compact response powinno zostać minimum:
```
repair_plan:
  macro_name: macro_align_part_with_contact
  priority: high
  reason: "Use bounded attachment/contact repair for this seam."
  arguments_hint:
    part_object: squirrel_tail
    reference_object: squirrel_body
    target_relation: contact
    align_mode: none
    preserve_side: true
```
Nie chodzi o pełny debug payload.
Chodzi o jeden najlepszy, wykonawczy kandydat.
Docelowo:
* compact może nadal wycinać heavy diagnostics,
* ale nie może wycinać top repair action,
* feedback musi mówić LLM-owi, jakiego toola/macro użyć i z jakimi argumentami.
---
### 5. Inspect/validate tylko dla prawdziwych blockerów
Nie przełączać do `inspect_validate` tylko dlatego, że brakuje buildable parta.
`inspect_validate` powinno odpalać się dla:
* twardych seam/contact blockerów,
* support blockerów,
* symmetry blockerów,
* stagnation,
* truth-only escalation,
* repeated correction failure.
Nie powinno odpalać się dla:
* brakującego `tail_mass`, jeśli jesteśmy jeszcze w primary build,
* brakującego `snout_mass`, jeśli jesteśmy jeszcze w secondary build,
* brakującego `eye_pair`, jeśli oczy są late detail,
* normalnych buildable blockers.
Docelowa zasada:
```
buildable_missing_part -> continue_build
hard_spatial_blocker -> inspect_validate
```
---
### 6. Testy regresyjne dla creature/squirrel
Dodać testy, które potwierdzą:
* bez `tail_mass` flow zostaje w primary/build phase,
* bez `snout_mass` flow zostaje w secondary/build phase,
* brak `eye_pair` nie przerzuca za wcześnie do inspect_validate,
* po `guided_register_part("squirrel_tail", "tail_mass")` active scope zawiera `squirrel_tail`,
* compact iterate zawiera top `repair_plan`,
* broad-first scope odpuszcza, gdy zostają lokalne seam/contact problemy.
---
# Etap 2: TASK-171A — On-Demand Vision Capability Registry And Structured Handoff
Ten etap przygotowuje architekturę pod cięższe modele bez ładowania wszystkiego na start kontenera.
## Problem
Nie chcemy:
* ładować SAM/GroundingDINO/DINOv2 przy starcie kontenera,
* trzymać wszystkiego stale w RAM/VRAM,
* failować builda, jeśli optional model nie jest zainstalowany,
* odpalać ciężkiego vision, kiedy wystarczy heuristic recipe,
* produkować prose-only output bez wykonawczego payloadu.
Chcemy:
* capability registry,
* lazy loading,
* prerequisite hints,
* TTL/unload,
* structured vision handoff.
---
## TASK-171A zakres
### 1. Dodać `vision_capability_registry`
Minimalny kontrakt:
```
vision_capabilities:
  classification:
    status: available | missing | cold | loaded | failed
    provider: siglip2 | clip | none
    cost: low
    load_state: cold
    activation_triggers:
      - reference_bootstrap
      - subject_ambiguity
  embedding_alignment:
    status: available | missing | cold | loaded | failed
    provider: labse | sentence_transformer | none
    cost: low
    load_state: cold
    activation_triggers:
      - multilingual_part_alias
      - label_normalization
  part_grounding:
    status: available | missing | cold | loaded | failed
    provider: grounding_dino | owl | none
    cost: medium_high
    load_state: cold
    activation_triggers:
      - part_missing
      - attachment_plan_needed
      - local_part_ambiguity
  segmentation:
    status: available | missing | cold | loaded | failed
    provider: sam2 | sam | none
    cost: high
    load_state: cold
    activation_triggers:
      - seam_unclear
      - silhouette_drift
      - local_mask_needed
```
Pola, które warto mieć:
```
capability_id
provider
status
load_state
estimated_cost
memory_budget
activation_triggers
prerequisites
last_used_at
ttl_seconds
failure_reason
```
---
### 2. Dodać prerequisite hints do feedbacku
Runtime powinien umieć powiedzieć:
```
part_grounding unavailable
reason: weights_missing
next_action: install vision-heavy profile or continue heuristic-only
```
Przykładowy payload:
```
prerequisite_hints:
  - capability: part_grounding
    status: missing
    reason: weights_missing
    install_profile: vision-heavy
    fallback: heuristic_attachment_recipe
    blocking: false
```
Ważne:
* brak optional modelu nie powinien automatycznie blokować builda,
* feedback powinien mówić, czy to blocker czy tylko enhancement,
* użytkownik powinien dostać jasny komunikat, co może zainstalować.
---
### 3. Lazy loader z unload/TTL
Dodać prosty manager:
```
ensure_loaded(capability)
run(capability, payload)
release_if_idle()
unload(capability)
```
Zasady:
* nie ładować ciężkich modeli na container start,
* ładować dopiero przy runtime triggerze,
* cache’ować krótko,
* zwalniać po TTL,
* zwalniać po końcu guided session,
* pilnować memory budget.
Przykład:
```
part_grounding:
  ttl_seconds: 300
  unload_on_session_end: true
  allow_cpu_fallback: false
  max_vram_mb: 4096
```
Dla GPU:
```
unload model reference
gc.collect()
torch.cuda.empty_cache()
```
---
### 4. Activation triggers per guided flow step
#### `understand_goal`
Nie odpalać ciężkiego vision.
Dozwolone:
* text normalization,
* LaBSE / aliases,
* wybór domain profile,
* rozpoznanie typu zadania.
Output:
```
domain_profile=creature
expected_recipe_type=attachment_first_creature
```
---
#### `establish_reference_context`
Odpalić lekki vision pass.
Dozwolone:
* classifier,
* subject recognition,
* global image summary,
* coarse silhouette,
* embedding label alignment.
Nie odpalać domyślnie SAM/GroundingDINO.
Output:
```
subject=squirrel
required_parts=[
  body_core,
  head_mass,
  tail_mass,
  snout_mass,
  ear_pair,
  foreleg_pair,
  hindleg_pair
]
part_order=[
  body_core,
  head_mass,
  tail_mass,
  snout_mass,
  ear_pair,
  foreleg_pair,
  hindleg_pair
]
```
---
#### `create_primary_masses`
Nadal bez ciężkiego modelu, chyba że reference jest niejednoznaczny.
Dozwolone:
* mass recipe,
* coarse silhouette landmarks,
* geometry family hints.
Output:
```
body_core:
  geometry_family: ellipsoid
  profile: horizontal_seated_mass
head_mass:
  geometry_family: faceted_sphere
  anchor: body_core
  required_relation: seated_contact
tail_mass:
  geometry_family: curved_appendage_mass
  anchor: body_core
  placement: rear_upper
  profile: wide_arc
  forbid: vertical_oval
```
---
#### `place_secondary_parts`
To jest pierwszy dobry moment na cięższe vision, ale tylko warunkowo.
Trigger dla part grounding:
* brakuje wymaganej części,
* część została stworzona, ale compare nie wie, do czego ją przypiąć,
* seam/contact blocker,
* role ambiguity,
* naming drift, np. `squirrel_forel`, `squirrel_hindl`.
Trigger dla segmentation:
* seam jest niejasny,
* silhouette drift po kilku iteracjach,
* lokalny contact nie daje się naprawić heurystyką,
* potrzebna jest maska ogona/uszu/nóg.
---
#### `checkpoint_iterate`
Cięższe vision tylko na problematycznym obszarze, nie full image.
Dobry payload:
```
focus_parts:
  - tail_mass
  - body_core
issue: attachment_gap
request: local mask/landmark/contact expectation
```
Zły payload:
```
analyze whole reference again
```
---
#### `inspect_validate`
Rich/debug/full diagnostics tylko jeśli:
* stagnation,
* truth-only escalation,
* hard seam/support/symmetry blocker,
* użytkownik prosi o debug,
* kilka lokalnych repair attempts nie zadziałało.
---
### 5. Structured `vision_handoff`
Zamiast prose-only:
```
vision_handoff:
  subject: squirrel
  confidence: 0.92
  recipe_type: attachment_first_creature
  mass_recipe:
    body_core:
      geometry_family: ellipsoid
      profile: horizontal_seated_mass
      priority: required
    head_mass:
      geometry_family: faceted_sphere
      anchor: body_core
      required_relation: seated_contact
      priority: required
    tail_mass:
      geometry_family: curved_appendage_mass
      anchor: body_core
      placement: rear_upper
      profile: wide_arc
      forbid:
        - vertical_oval
      priority: required
  attachment_plan:
    - part: head_mass
      anchor: body_core
      relation: seated_contact
      must_seat_before_next_stage: true
    - part: tail_mass
      anchor: body_core
      relation: rear_upper_attachment
      must_seat_before_next_stage: true
    - part: snout_mass
      anchor: head_mass
      relation: front_attachment
      must_seat_before_next_stage: true
  contact_expectations:
    - part: tail_mass
      anchor: body_core
      expected_contact: true
      gap_tolerance: small
    - part: foreleg_pair
      anchor: body_core
      expected_contact: support_contact
    - part: hindleg_pair
      anchor: body_core
      expected_contact: support_contact
  shape_profile_hints:
    tail_mass:
      should_be:
        - curved
        - wide_arc
        - rear_upper
      should_not_be:
        - vertical_oval
        - detached_blob
  silhouette_landmarks:
    rear_upper:
      expected_part: tail_mass
    front_head:
      expected_part: snout_mass
    top_head:
      expected_part: ear_pair
  part_order:
    - body_core
    - head_mass
    - tail_mass
    - snout_mass
    - ear_pair
    - foreleg_pair
    - hindleg_pair
```
---
# Deployment profile
Nie robić jednego ciężkiego obrazu jako jedynego trybu.
Dodać profile:
```
base:
  includes:
    - runtime
    - heuristics
    - contracts
    - label maps
    - optional text embeddings
vision-light:
  includes:
    - base
    - lightweight classifier
    - coarse image summary backend
vision-heavy:
  includes:
    - vision-light
    - part grounding provider
    - segmentation provider
    - dense feature provider
```
Runtime powinien działać we wszystkich profilach.
Jeżeli user ma tylko `base`:
```
part_grounding unavailable; using attachment-first heuristic recipe
```
Jeżeli user ma `vision-heavy`:
```
part_grounding available but cold; will load on demand
```
---
# Co dać na stałe do obrazu
Na stałe można dać:
* kontrakty,
* heurystyki,
* label maps,
* alias maps,
* mały text embedding model, np. LaBSE, jeśli jest potrzebny,
* lekki classifier tylko jeśli cold start jest mały.
LaBSE ma sens jako:
* multilingual label alignment,
* alias matching,
* normalizacja promptów,
* mapowanie `ogon`, `tail`, `bushy tail`, `tail_mass`,
* mapowanie `foreleg`, `front leg`, `łapa przednia`.
LaBSE nie powinien być używany do:
* seam detection,
* geometrii,
* lokalizacji części na obrazie,
* oceny kontaktów 3D.
---
# Co ładować leniwie
Lazy local:
* GroundingDINO / OWL-style grounding,
* SAM/SAM2,
* DINOv2,
* cięższy classifier typu SigLIP2.
Te modele mogą być w obrazie albo w cache, ale nie powinny być ładowane przy starcie kontenera.
---
# Co jako optional prerequisite
Dla ciężkich modeli:
```
part_grounding:
  provider: local | remote | disabled
  prerequisite:
    - weights present
    - torch cuda available OR cpu_allowed=true
    - model license accepted
  activation:
    on_demand_only
```
Jeżeli prerequisite nie jest spełniony:
```
reference_orchestrator_feedback:
  status: blocked_optional
  message: "Part grounding is not installed. Continue with heuristic recipe, or install grounding provider."
  prerequisite_hint:
    capability: part_grounding
    install_profile: vision-heavy
```
---
# Finalna rekomendacja kolejności
Najpierw:
```
TASK-171B Creature Stage Gate And Active Scope Repair
```
Czyli:
* `tail_mass` required primary,
* `snout_mass` required secondary,
* `eye_pair` late/detail/advisory,
* `guided_register_part` rozszerza active scope,
* compact repair plan passthrough,
* inspect_validate tylko dla prawdziwych blockerów.
Potem:
```
TASK-171A On-Demand Vision Capability Registry And Structured Handoff
```
Czyli:
* `vision_capability_registry`,
* lazy loading,
* prerequisite hints,
* TTL/unload,
* structured `vision_handoff`.
Dopiero potem:
```
TASK-171C Optional Part Grounding And Segmentation Providers
```
Czyli:
* GroundingDINO-like provider,
* SAM/SAM2 provider,
* DINOv2 dense feature provider,
* local-region-only calls,
* no full-image heavy pass unless explicitly needed.
Najważniejsza zasada:
```
Nie dokładać ciężkich modeli, dopóki runtime dalej gubi active scope,
odpala inspect_validate przez buildable missing parts,
albo wycina repair plan w compact feedback.
```
Bo wtedy model będzie drogi, ale jego sygnał i tak nie przełoży się na poprawną akcję.
