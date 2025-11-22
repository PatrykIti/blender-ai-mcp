# 10. Standaryzacja Projektu i CI/CD

**Data:** 2025-11-22  
**Wersja:** 0.1.9  
**Zadania:** TASK-006_Project_Standardization_and_CICD

## 🚀 Główne Zmiany

### Dokumentacja
- **Język**: Przejście na język angielski w głównych plikach (`README.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`).
- **ARCHITECTURE.md**: Szczegółowy opis techniczny (Clean Architecture, RPC Protocol) przetłumaczony z wcześniejszych notatek.
- **CONTRIBUTING.md**: Nowy przewodnik dla kontrybutorów z naciskiem na workflow zadaniowy i architekturę.
- **README.md**: Profesjonalny wygląd, statusy CI, instrukcja Docker.

### Automatyzacja (CI/CD)
- **GitHub Actions (`.github/workflows/release.yml`)**:
  - Automatyczne testy (`unittest`).
  - Budowanie artefaktu Addona (`blender_ai_mcp.zip`).
  - Semantic Release: Automatyczne wersjonowanie, tagowanie i tworzenie Release'a na GitHubie.
  - Docker: Budowanie i push obrazu do GHCR (GitHub Container Registry).
- **Szablony**: Dodano szablony Issue (`Bug`, `Feature`) i Pull Request.

Projekt jest teraz w pełni przygotowany do publikacji jako profesjonalne narzędzie Open Source.
