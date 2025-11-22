# 9. Konteneryzacja Serwera (Docker)

**Data:** 2025-11-22  
**Wersja:** 0.1.8  
**Zadania:** TASK-005_Dockerize_Server

## 🚀 Główne Zmiany

### Infrastructure
- **Dockerfile**: Dodano plik budujący lekki obraz oparty na `python:3.10-slim`. Obraz zawiera wszystkie zależności i kod serwera.
- **Konfiguracja**: Zaimplementowano `server/infrastructure/config.py`, który wczytuje zmienne środowiskowe (`BLENDER_RPC_HOST`, `BLENDER_RPC_PORT`). Pozwala to na dynamiczną konfigurację połączenia (niezbędne dla Dockera).
- **DI**: Zaktualizowano `di.py`, aby wstrzykiwał konfigurację do `RpcClient`.

### Testing
- Zweryfikowano połączenie z kontenera Docker do Blendera działającego na hoście (macOS) używając `host.docker.internal`.

### Deployment
- Serwer jest teraz gotowy do dystrybucji jako obraz Docker, co eliminuje konieczność lokalnej instalacji Pythona i Poetry u użytkownika końcowego (poza środowiskiem developerskim).
