# 17. Logging & Telemetry

**Task:** TASK-039-18
**Status:** Done
**Layer:** Infrastructure

---

## Overview

Router Logging & Telemetry provides comprehensive event tracking and statistics for the Router Supervisor. It records all router decisions for debugging, analysis, and monitoring.

---

## Implementation

**File:** `server/router/infrastructure/logger.py`

### Event Types

```python
class EventType(Enum):
    INTERCEPT = "intercept"
    CONTEXT_ANALYZED = "context_analyzed"
    PATTERN_DETECTED = "pattern_detected"
    CORRECTION_APPLIED = "correction_applied"
    OVERRIDE_TRIGGERED = "override_triggered"
    WORKFLOW_EXPANDED = "workflow_expanded"
    FIREWALL_DECISION = "firewall_decision"
    EXECUTION_COMPLETE = "execution_complete"
    ERROR = "error"
```

### RouterEvent

```python
@dataclass
class RouterEvent:
    event_type: EventType
    timestamp: datetime
    tool_name: Optional[str]
    data: Dict[str, Any]
    session_id: Optional[str]
```

### RouterLogger

Main logging class with:
- Event recording
- Statistics tracking
- Session management
- Event filtering
- JSON export

---

## Features

1. **Comprehensive Event Logging**
   - Tool interception
   - Context analysis
   - Pattern detection
   - Corrections applied
   - Overrides triggered
   - Workflow expansions
   - Firewall decisions
   - Execution completion
   - Errors

2. **Statistics Tracking**
   ```python
   stats = logger.get_stats()
   # {
   #     "total_events": 150,
   #     "intercepts": 50,
   #     "corrections": 30,
   #     "overrides": 10,
   #     "workflow_expansions": 5,
   #     "firewall_blocks": 2,
   #     "firewall_fixes": 8,
   #     "errors": 3
   # }
   ```

3. **Session Management**
   - Group events by session
   - Session summaries
   - Duration tracking

4. **Event Filtering**
   - By event type
   - By session ID
   - Limit results

5. **Export**
   - JSON export to file
   - Dictionary conversion

---

## Usage

### Basic Logging

```python
from server.router.infrastructure.logger import RouterLogger

logger = RouterLogger()

# Log events
logger.log_intercept("mesh_extrude", {"depth": 0.5}, prompt="extrude top")
logger.log_correction("mesh_extrude", ["mode_switch"], [...])
logger.log_firewall("mesh_extrude", "allow", "Valid operation")
```

### Session Tracking

```python
logger.set_session_id("session_abc")
logger.log_intercept("tool1", {})
logger.log_intercept("tool2", {})

summary = logger.get_session_summary()
# {
#     "session_id": "session_abc",
#     "event_count": 2,
#     "event_types": {"intercept": 2},
#     "duration_seconds": 0.5
# }
```

### Event Retrieval

```python
# Get recent events
events = logger.get_events(limit=50)

# Filter by type
corrections = logger.get_events(event_type=EventType.CORRECTION_APPLIED)

# Filter by session
session_events = logger.get_events(session_id="session_abc")
```

### Export

```python
logger.export_events("/path/to/events.json")
```

### Global Logger

```python
from server.router.infrastructure.logger import (
    get_router_logger,
    configure_router_logging,
)

# Get default instance
logger = get_router_logger()

# Configure logging
logger = configure_router_logging(
    level=logging.DEBUG,
    enabled=True,
    max_events=5000,
)
```

---

## Tests

**File:** `tests/unit/router/infrastructure/test_logger.py`

30 unit tests covering:
- Event creation
- All log methods
- Session management
- Event retrieval & filtering
- Statistics
- Export functionality
- Global logger functions

---

## See Also

- [15-supervisor-router.md](./15-supervisor-router.md) - SupervisorRouter
- [16-mcp-integration.md](./16-mcp-integration.md) - MCP Integration
