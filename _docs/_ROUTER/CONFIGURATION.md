# Router Configuration

Complete reference for all Router Supervisor configuration options.

---

## RouterConfig Dataclass

```python
from server.router.infrastructure.config import RouterConfig

config = RouterConfig(
    # Correction settings
    auto_mode_switch=True,
    auto_selection=True,
    clamp_parameters=True,

    # Override settings
    enable_overrides=True,
    enable_workflow_expansion=True,

    # Firewall settings
    block_invalid_operations=True,
    auto_fix_mode_violations=True,

    # Thresholds
    embedding_threshold=0.40,
    bevel_max_ratio=0.5,
    subdivide_max_cuts=6,

    # Advanced settings
    cache_scene_context=True,
    cache_ttl_seconds=1.0,
    max_workflow_steps=20,
    log_decisions=True,
)
```

---

## Configuration Options

### Correction Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `auto_mode_switch` | bool | `True` | Automatically switch Blender mode (OBJECT/EDIT/SCULPT) if tool requires different mode |
| `auto_selection` | bool | `True` | Automatically select geometry if tool requires selection |
| `clamp_parameters` | bool | `True` | Clamp parameter values to valid ranges based on object dimensions |

**Example: Disable auto-selection**
```python
config = RouterConfig(auto_selection=False)
# Now tools requiring selection will fail if nothing selected
```

---

### Override Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable_overrides` | bool | `True` | Enable tool override rules (e.g., extrude on phone → inset + extrude) |
| `enable_workflow_expansion` | bool | `True` | Enable workflow expansion for detected patterns |

**Example: Disable pattern-based workflows**
```python
config = RouterConfig(
    enable_overrides=False,
    enable_workflow_expansion=False,
)
# Router will only do corrections, no smart replacements
```

---

### Firewall Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `block_invalid_operations` | bool | `True` | Block operations that would definitely fail |
| `auto_fix_mode_violations` | bool | `True` | Auto-fix mode violations instead of blocking |

**Firewall Actions:**
- `auto_fix` - Add pre-steps to fix the issue (e.g., mode switch)
- `modify` - Modify parameters (e.g., clamp values)
- `block` - Block the operation entirely

**Example: Strict mode (block instead of fix)**
```python
config = RouterConfig(
    auto_fix_mode_violations=False,
    block_invalid_operations=True,
)
# Invalid operations will be blocked, not auto-fixed
```

---

### Threshold Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `embedding_threshold` | float | `0.40` | Minimum confidence for intent classification (0.0-1.0) |
| `bevel_max_ratio` | float | `0.5` | Maximum bevel width as ratio of smallest object dimension |
| `subdivide_max_cuts` | int | `6` | Maximum subdivision cuts allowed |

**Example: Stricter intent matching**
```python
config = RouterConfig(
    embedding_threshold=0.60,  # Only match intents with 60%+ confidence
)
```

**Example: Allow larger bevels**
```python
config = RouterConfig(
    bevel_max_ratio=0.8,  # Allow bevel up to 80% of smallest dimension
)
```

---

### Advanced Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `cache_scene_context` | bool | `True` | Cache scene context analysis between calls |
| `cache_ttl_seconds` | float | `1.0` | How long to cache scene context (seconds) |
| `max_workflow_steps` | int | `20` | Maximum steps in a workflow expansion |
| `log_decisions` | bool | `True` | Log router decisions for debugging |

**Example: Disable caching (for testing)**
```python
config = RouterConfig(
    cache_scene_context=False,
)
# Scene will be re-analyzed on every call
```

---

## Configuration Presets

### Default (Recommended)
```python
config = RouterConfig()  # All defaults
```

### Performance Mode
```python
config = RouterConfig(
    cache_scene_context=True,
    cache_ttl_seconds=2.0,
    log_decisions=False,
)
```

### Debug Mode
```python
config = RouterConfig(
    cache_scene_context=False,
    log_decisions=True,
)
```

### Strict Mode
```python
config = RouterConfig(
    auto_mode_switch=False,
    auto_selection=False,
    auto_fix_mode_violations=False,
    block_invalid_operations=True,
)
```

### Minimal (Corrections Only)
```python
config = RouterConfig(
    enable_overrides=False,
    enable_workflow_expansion=False,
    # Only mode switching, selection, and parameter clamping
)
```

---

## Using Configuration

### With SupervisorRouter
```python
from server.router.application.router import SupervisorRouter
from server.router.infrastructure.config import RouterConfig

config = RouterConfig(auto_mode_switch=True)
router = SupervisorRouter(config=config, rpc_client=rpc_client)
```

### From Dictionary
```python
config_dict = {
    "auto_mode_switch": True,
    "embedding_threshold": 0.5,
}
config = RouterConfig.from_dict(config_dict)
```

### To Dictionary
```python
config = RouterConfig()
config_dict = config.to_dict()
# Returns all settings as dictionary
```

---

## See Also

- [QUICK_START.md](./QUICK_START.md) - Getting started
- [API.md](./API.md) - Full API reference
- [PATTERNS.md](./PATTERNS.md) - Pattern detection settings
