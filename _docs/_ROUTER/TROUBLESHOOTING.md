# Router Troubleshooting

Common issues and solutions for Router Supervisor.

---

## Quick Diagnostic

```python
from server.router.application.router import SupervisorRouter

router = SupervisorRouter()
status = router.get_component_status()
print(status)
# {
#     "interceptor": True,
#     "analyzer": False,    # ← RPC not set
#     "detector": True,
#     "correction_engine": True,
#     "override_engine": True,
#     "expansion_engine": True,
#     "firewall": True,
#     "classifier": False,  # ← Embeddings not loaded
# }
```

---

## Common Issues

### 1. LaBSE Model Not Loading

**Symptoms:**
- `classifier: False` in component status
- Warning: `sentence-transformers not installed`
- Error: `Failed to load model`

**Solutions:**

**1a. Install sentence-transformers:**
```bash
poetry add sentence-transformers
```

**1b. Check RAM availability:**
LaBSE requires ~1.8GB RAM. Check available memory:
```bash
# macOS/Linux
free -h

# Or in Python
import psutil
print(f"Available: {psutil.virtual_memory().available / 1024**3:.1f} GB")
```

**1c. Check model download:**
First run downloads model (~500MB). Ensure internet connection.

**1d. Use fallback (TF-IDF):**
If RAM is limited, router falls back to TF-IDF automatically:
```python
info = classifier.get_model_info()
if info["using_fallback"]:
    print("Using TF-IDF fallback (lower accuracy)")
```

---

### 2. RPC Connection Failed

**Symptoms:**
- `analyzer: False` in component status
- Error: `RPC connection refused`
- Error: `Connection timed out`

**Solutions:**

**2a. Check Blender is running:**
Ensure Blender is open with the addon enabled.

**2b. Check addon is loaded:**
In Blender: Edit → Preferences → Add-ons → Search "AI MCP"

**2c. Verify RPC port:**
Default port is `9876`. Check if in use:
```bash
lsof -i :9876
```

**2d. Test connection manually:**
```python
from server.infrastructure.rpc_client import RpcClient

client = RpcClient()
try:
    response = client.send_request("system.ping", {})
    print(f"Connected: {response}")
except Exception as e:
    print(f"Connection failed: {e}")
```

---

### 3. Tool Not Found in Metadata

**Symptoms:**
- Warning: `Tool 'xyz' not found in metadata`
- Router returns unchanged tool call

**Solutions:**

**3a. Check metadata file exists:**
```bash
ls server/router/infrastructure/tools_metadata/{category}/
```

**3b. Validate JSON syntax:**
```bash
python -m json.tool server/router/infrastructure/tools_metadata/mesh/mesh_extrude_region.json
```

**3c. Reload metadata:**
```python
from server.router.infrastructure.metadata_loader import MetadataLoader

loader = MetadataLoader()
metadata = loader.load_all()
print(f"Loaded {len(metadata)} tools")

# Check if specific tool loaded
if "mesh_extrude_region" in metadata:
    print("Tool found!")
else:
    print("Tool missing from metadata")
```

---

### 4. Pattern Not Detected

**Symptoms:**
- Expected pattern workflow not triggered
- Router returns only corrected tool (no expansion)

**Solutions:**

**4a. Check object proportions:**
```python
from server.router.application.analyzers.proportion_calculator import calculate_proportions

# For phone-like: flat rectangular
dimensions = [0.4, 0.8, 0.05]
props = calculate_proportions(dimensions)
print(f"is_flat: {props.is_flat}")
print(f"aspect_xy: {props.aspect_xy}")  # Should be 0.4-0.7 for phone
```

**4b. Verify pattern rules:**
```python
from server.router.domain.entities.pattern import PATTERN_RULES, PatternType

rules = PATTERN_RULES[PatternType.PHONE_LIKE]
print(f"Rules: {rules['rules']}")
# ['is_flat', '0.4 < aspect_xy < 0.7', 'z < 0.15']
```

**4c. Manual pattern detection:**
```python
from server.router.application.analyzers.geometry_pattern_detector import GeometryPatternDetector
from server.router.domain.entities.scene_context import SceneContext, ProportionInfo

# Create test context
proportions = ProportionInfo(
    aspect_xy=0.5,
    aspect_xz=0.1,
    aspect_yz=0.1,
    dominant_axis="y",
    is_flat=True,
    is_tall=False,
    is_wide=False,
    is_cubic=False,
)
context = SceneContext(mode="EDIT", proportions=proportions)

detector = GeometryPatternDetector()
result = detector.detect(context)
print(f"Best match: {result.best_pattern_name}")
print(f"Confidence: {result.best_match.confidence if result.best_match else 0}")
```

---

### 5. Firewall Blocking Valid Operations

**Symptoms:**
- Tool calls blocked unexpectedly
- Error: `Operation blocked by firewall`

**Solutions:**

**5a. Check firewall rules:**
```python
router = SupervisorRouter()
# Disable blocking temporarily
router.update_config(block_invalid_operations=False)
```

**5b. Debug firewall validation:**
```python
from server.router.application.engines.error_firewall import ErrorFirewall
from server.router.domain.entities.tool_call import CorrectedToolCall
from server.router.domain.entities.scene_context import SceneContext

firewall = ErrorFirewall()
tool = CorrectedToolCall(tool_name="mesh_extrude_region", params={"move": [0.0, 0.0, 0.5]})
context = SceneContext(mode="OBJECT")  # Wrong mode

result = firewall.validate(tool, context)
print(f"Action: {result.action}")
print(f"Violations: {result.violations}")
print(f"Pre-steps: {result.pre_steps}")
```

**5c. Use auto-fix mode:**
```python
config = RouterConfig(
    block_invalid_operations=True,
    auto_fix_mode_violations=True,  # Fix instead of block
)
router = SupervisorRouter(config=config)
```

---

### 6. Scene Context Cache Issues

**Symptoms:**
- Router using stale data
- Changes in Blender not reflected

**Solutions:**

**6a. Invalidate cache manually:**
```python
router.invalidate_cache()
```

**6b. Disable caching for debugging:**
```python
config = RouterConfig(cache_scene_context=False)
router = SupervisorRouter(config=config)
```

**6c. Reduce cache TTL:**
```python
config = RouterConfig(cache_ttl_seconds=0.1)  # 100ms cache
```

---

### 7. Intent Classification Inaccurate

**Symptoms:**
- Wrong tool matched for prompt
- Low confidence scores

**Solutions:**

**7a. Lower threshold:**
```python
config = RouterConfig(embedding_threshold=0.3)  # Default is 0.4
```

**7b. Add more sample prompts:**
In tool metadata JSON:
```json
{
  "tool_name": "mesh_bevel",
  "sample_prompts": [
    "bevel the edges",
    "round the corners",
    "chamfer edges",
    "smooth the edges",
    "add bevel to selection"
  ]
}
```

**7c. Clear embedding cache:**
```python
classifier.clear_cache()
classifier.load_tool_embeddings(metadata)
```

**7d. Check embeddings loaded:**
```python
info = classifier.get_model_info()
print(f"Num tools: {info['num_tools']}")
print(f"Using fallback: {info['using_fallback']}")
```

---

### 8. Workflow Expansion Not Working

**Symptoms:**
- Pattern detected but no workflow triggered
- Single tool returned instead of workflow

**Solutions:**

**8a. Check config:**
```python
config = RouterConfig(enable_workflow_expansion=True)
```

**8b. Verify workflow exists:**
```bash
ls server/router/infrastructure/workflows/
# Should contain workflow YAML/JSON files
```

**8c. Check pattern-workflow mapping:**
```python
from server.router.domain.entities.pattern import PATTERN_RULES, PatternType

rules = PATTERN_RULES[PatternType.PHONE_LIKE]
print(f"Workflow: {rules.get('suggested_workflow')}")
# Should print: 'phone_workflow'
```

---

## Debug Logging

### Enable Verbose Logging

```python
import logging

# Enable router logging
logging.getLogger("server.router").setLevel(logging.DEBUG)

# Or enable all logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Router Decisions

```python
config = RouterConfig(log_decisions=True)
router = SupervisorRouter(config=config)

# Process a call
tools = router.process_llm_tool_call("mesh_extrude_region", {"move": [0.0, 0.0, 0.5]})

# Check stats
stats = router.get_stats()
print(f"Corrections: {stats['corrections_applied']}")
print(f"Overrides: {stats['overrides_triggered']}")
print(f"Workflows: {stats['workflows_expanded']}")
print(f"Blocked: {stats['blocked_calls']}")
```

---

## Testing

### Run Unit Tests

```bash
PYTHONPATH=. poetry run pytest tests/unit/router/ -v
```

### Run E2E Tests (requires Blender)

```bash
PYTHONPATH=. poetry run pytest tests/e2e/router/ -v
```

### Test Specific Component

```bash
# Test classifier
PYTHONPATH=. poetry run pytest tests/unit/router/application/test_intent_classifier.py -v

# Test firewall
PYTHONPATH=. poetry run pytest tests/unit/router/application/test_error_firewall.py -v

# Test patterns
PYTHONPATH=. poetry run pytest tests/unit/router/application/test_geometry_pattern_detector.py -v
```

---

## Reporting Issues

If you encounter issues not covered here:

1. **Collect diagnostic info:**
   ```python
   router = SupervisorRouter()
   print(router.get_component_status())
   print(router.get_stats())
   if router.classifier:
       print(router.classifier.get_model_info())
   ```

2. **Enable debug logging** (see above)

3. **Report at:** https://github.com/anthropics/claude-code/issues

Include:
- Python version
- Blender version
- Error message / stack trace
- Steps to reproduce
- Diagnostic info from step 1

---

## See Also

- [QUICK_START.md](./QUICK_START.md) - Getting started
- [CONFIGURATION.md](./CONFIGURATION.md) - Configuration options
- [PATTERNS.md](./PATTERNS.md) - Pattern detection
- [API.md](./API.md) - API reference
