---
type: task
id: TASK-004
title: Narzędzia Modelowania (Mesh Ops)
status: todo
priority: medium
assignee: unassigned
depends_on: TASK-003
---

# 🎯 Cel
Implementacja kluczowych narzędzi do edycji geometrii, które pozwolą AI tworzyć proste modele 3D.

# 📋 Zakres prac

1. **Tworzenie Prymitywów**
   - `model.create_cube(size, location)`
   - `model.create_sphere(radius, location)`

2. **Edycja Mesha (Edit Mode Wrappers)**
   - **Wyzwanie:** Automatyczne przełączanie `Object Mode` <-> `Edit Mode`.
   - `mesh.extrude(distance)`: Wytłoczenie zaznaczonych ścian.
   - `mesh.select_all()` / `mesh.select_random()` (dla testów).
   - `mesh.bevel(amount)`.

3. **Walidacja Kontekstu**
   - Upewnienie się, że operacje są wykonywane na aktywnym obiekcie.
   - Zabezpieczenie przed wywołaniem operacji mesh na obiekcie typu Camera/Light.

# ✅ Kryteria Akceptacji
- AI może stworzyć sześcian i go zmodyfikować (np. extrude).
- Błędy kontekstu (np. "context is incorrect") są przechwytywane i zamieniane na czytelne komunikaty dla AI ("Please select a mesh object first").
