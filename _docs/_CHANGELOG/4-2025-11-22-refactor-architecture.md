# 4. Refaktoryzacja Clean Architecture

**Data:** 2025-11-22  
**Wersja:** 0.1.3  
**Zadania:** TASK-003_1_Refactor_Architecture

## 🚀 Główne Zmiany

### Server Architecture (Clean Architecture Refactor)
Przebudowano architekturę serwera MCP, aby ściśle przestrzegać zasad separacji warstw.

- **Domain Layer (`server/domain/`)**
  - Dodano interfejsy: `interfaces/rpc.py` (`IRpcClient`) oraz `tools/scene.py` (`ISceneTool`).
  - Od teraz warstwa domeny nie zależy od implementacji.

- **Application Layer (`server/application/`)**
  - Dodano `tool_handlers/scene_handler.py`: Implementacja `ISceneTool`.
  - Handler przejmuje logikę biznesową, która wcześniej znajdowała się w `main.py`.

- **Adapters Layer (`server/adapters/`)**
  - Zaktualizowano `rpc/client.py`: `RpcClient` implementuje teraz `IRpcClient`.
  - Oczyszczono `main.py`: Teraz pełni rolę wyłącznie "Composition Root" (Dependency Injection) i Adaptera wejściowego (MCP). Nie zawiera logiki biznesowej.

### Testing
- Zweryfikowano poprawność refaktoryzacji testami (`test_scene_tools.py`, `test_rpc_connection.py`).
