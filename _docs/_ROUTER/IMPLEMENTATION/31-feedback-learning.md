# 31 - Feedback Learning

> **Task:** TASK-046-6 | **Status:** ✅ Done

---

## Overview

Collects user feedback to improve workflow matching over time. Stores prompt-to-workflow mappings, failed matches, and user corrections for future learning.

## Interface

```python
@dataclass
class FeedbackEntry:
    """Single feedback entry."""
    timestamp: str
    prompt: str
    matched_workflow: Optional[str]
    match_confidence: float
    match_type: str  # exact, semantic, generalized, none
    user_correction: Optional[str]  # If user corrected the match
    was_helpful: Optional[bool]
    metadata: Dict[str, Any]


class FeedbackCollector:
    """Collects and stores feedback for learning."""

    def record_match(self, prompt: str, matched_workflow: Optional[str],
                     confidence: float, match_type: str) -> None:
        """Record a workflow match."""

    def record_correction(self, prompt: str, original_match: Optional[str],
                          correct_workflow: str) -> None:
        """Record user correction."""

    def get_new_sample_prompts(self, workflow_name: str, min_corrections: int = 3) -> List[str]:
        """Get prompts that should be added as sample_prompts."""

    def get_statistics(self) -> Dict[str, Any]:
        """Get feedback statistics."""
```

## Implementation

**File:** `server/router/application/learning/feedback_collector.py`

### Storage Format

```
~/.blender-mcp/feedback.jsonl

{"timestamp": "2024-01-15T10:30:00", "prompt": "zrób krzesło", "matched_workflow": "table_workflow", "match_confidence": 0.72, "match_type": "generalized", "user_correction": null, "was_helpful": null, "metadata": {}}
{"timestamp": "2024-01-15T10:35:00", "prompt": "create a chair", "matched_workflow": "table_workflow", "match_confidence": 0.68, "match_type": "semantic", "user_correction": "chair_workflow", "was_helpful": false, "metadata": {}}
```

### Learning from Corrections

```python
def get_new_sample_prompts(self, workflow_name: str, min_corrections: int = 3) -> List[str]:
    """Get prompts that should be added as sample_prompts.

    Returns prompts that were corrected to this workflow multiple times.
    These prompts indicate gaps in the workflow's sample_prompts.
    """
    prompt_counts: Dict[str, int] = {}

    for entry in self._entries:
        if entry.user_correction == workflow_name:
            prompt_counts[entry.prompt] = prompt_counts.get(entry.prompt, 0) + 1

    return [
        prompt for prompt, count in prompt_counts.items()
        if count >= min_corrections
    ]
```

### MCP Tool Integration

```python
@mcp.tool()
def router_feedback(ctx: Context, prompt: str, correct_workflow: str) -> str:
    """
    [SYSTEM][SAFE] Provide feedback to improve workflow matching.

    Call this when the router matched the wrong workflow.
    The feedback is stored and used to improve future matching.

    Args:
        prompt: The original prompt/description.
        correct_workflow: The workflow that should have matched.

    Returns:
        Confirmation message.
    """
    collector = get_feedback_collector()
    collector.record_correction(prompt, None, correct_workflow)
    return f"Feedback recorded: '{prompt}' → {correct_workflow}"
```

## Configuration

```python
@dataclass
class RouterConfig:
    feedback_storage_path: Optional[Path] = None  # Default: ~/.blender-mcp/feedback.jsonl
    max_feedback_entries: int = 10000             # Max entries to keep
    min_corrections_for_learning: int = 3         # Min corrections before suggesting sample_prompt
```

## Tests

```python
# tests/unit/router/application/learning/test_feedback_collector.py

def test_record_match():
    collector = FeedbackCollector(storage_path=tmp_path / "feedback.jsonl")

    collector.record_match("create a phone", "phone_workflow", 0.95, "exact")

    assert len(collector._entries) == 1
    assert collector._entries[0].prompt == "create a phone"

def test_record_correction():
    collector = FeedbackCollector(storage_path=tmp_path / "feedback.jsonl")

    collector.record_correction("create a chair", "table_workflow", "chair_workflow")

    entry = collector._entries[-1]
    assert entry.user_correction == "chair_workflow"
    assert entry.was_helpful == False

def test_get_new_sample_prompts():
    collector = FeedbackCollector(storage_path=tmp_path / "feedback.jsonl")

    # Record same correction 3 times
    for _ in range(3):
        collector.record_correction("zrób fotel", None, "chair_workflow")

    prompts = collector.get_new_sample_prompts("chair_workflow", min_corrections=3)

    assert "zrób fotel" in prompts

def test_get_statistics():
    collector = FeedbackCollector(storage_path=tmp_path / "feedback.jsonl")
    collector.record_match("a", "phone_workflow", 1.0, "exact")
    collector.record_match("b", "phone_workflow", 0.8, "semantic")
    collector.record_correction("c", "table_workflow", "chair_workflow")

    stats = collector.get_statistics()

    assert stats["total_entries"] == 3
    assert stats["corrections"] == 1
    assert stats["by_match_type"]["exact"] == 1
```

## Usage

```python
from server.router.application.learning import FeedbackCollector

collector = FeedbackCollector()

# Record automatic match
collector.record_match(
    prompt="create a smartphone",
    matched_workflow="phone_workflow",
    confidence=0.95,
    match_type="exact",
)

# User corrects a match
collector.record_correction(
    prompt="make a tablet device",
    original_match="phone_workflow",
    correct_workflow="tablet_workflow",
)

# Get suggestions for improving workflows
new_prompts = collector.get_new_sample_prompts("tablet_workflow")
# → ["make a tablet device", "create a large tablet", ...]
# Add these to tablet_workflow.sample_prompts
```

## Future Improvements

1. **Automatic Sample Prompt Addition** - Automatically add frequently corrected prompts
2. **Threshold Adjustment** - Learn optimal similarity thresholds from feedback
3. **Workflow Gap Detection** - Identify when new workflows should be created
4. **Active Learning** - Ask for confirmation on low-confidence matches

## See Also

- [29-semantic-workflow-matcher.md](./29-semantic-workflow-matcher.md) - Records matches
- [28-workflow-intent-classifier.md](./28-workflow-intent-classifier.md) - Benefits from learned prompts
