# 3. Ulepszenie Scene Tools

**Data:** 2025-11-22  
**Wersja:** 0.1.2  
**Zadania:** TASK-003 (Improvement)

## 🚀 Zmiany

### Scene Tools
- Zaktualizowano narzędzie `clean_scene` o parametr `keep_lights_and_cameras` (domyślnie `True`).
- Dodano logikę "Hard Reset": Ustawienie parametru na `False` usuwa wszystkie obiekty (w tym kamery i światła) oraz czyści nieużywane kolekcje. Pozwala to na rozpoczęcie pracy od całkowicie pustego projektu ("Factory Reset" dla sceny).
