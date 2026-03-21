# TASK-093-01-01: Core Telemetry Model and OpenTelemetry Bootstrap

**Parent:** [TASK-093-01](./TASK-093-01_Telemetry_Model_and_OpenTelemetry_Bootstrap.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-083-03](./TASK-083-03_Server_Factory_and_Composition_Root.md)

---

## Objective

Implement the core code changes for **Telemetry Model and OpenTelemetry Bootstrap**.

---

## Repository Touchpoints

- `server/main.py`
- `server/router/infrastructure/logger.py`
- `server/infrastructure/config.py`

---

## Planned Work

- create:
  - `server/infrastructure/telemetry.py`
  - `tests/unit/infrastructure/test_telemetry.py`

### Bootstrap Rule

FastMCP already provides native tool, prompt, and resource spans.
This task should:

- bootstrap OTEL SDK/exporter configuration early enough in startup
- add repo-specific router and addon-job attributes/spans
- avoid rebuilding baseline MCP operation tracing from scratch

The startup path must account for OTEL initialization before FastMCP import/bootstrap takes effect.
---

## Acceptance Criteria

- request, tool, and router spans can be exported through OpenTelemetry
---

## Atomic Work Items

1. Add OTEL bootstrap helper and configuration wiring.
2. Ensure startup initializes telemetry before server construction.
3. Add router-specific span helpers and in-memory exporter tests.