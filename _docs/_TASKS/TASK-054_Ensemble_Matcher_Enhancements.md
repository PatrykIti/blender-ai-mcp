# TASK-054: Ensemble Matcher Enhancements

**Priority:** 🟡 Medium
**Category:** Router Supervisor Enhancement
**Estimated Effort:** Medium
**Dependencies:** TASK-053 (Ensemble Matcher System)
**Status:** 🚧 **IN PROGRESS**

---

## Overview

Enhance the Ensemble Matcher System (TASK-053) with observability and performance improvements:

1. **~~Normalized Weight System~~** - ✅ **Already Implemented in TASK-055-FIX Bug 3** (Score Normalization)
2. **Ensemble Telemetry & Metrics** - Add comprehensive observability for matcher performance analysis
3. **Async Parallel Execution** - Optimize matcher execution with asyncio for reduced latency

**Why These Enhancements?**

After TASK-053 implementation review, these improvements were identified:
- ~~Current weights (0.40 + 0.40 + 0.15 = 0.95) leave 5% undefined~~ ✅ **SOLVED** - See TASK-055-FIX Bug 3
- No visibility into individual matcher performance for debugging/tuning
- Sequential execution could be optimized with async parallelism

**Impact:**
- ~~Better mathematical foundation for score aggregation~~ ✅ **DONE** via score normalization
- Easier debugging and performance tuning (telemetry)
- ~30-50% latency reduction for complex prompts (async)

**Related Tasks:**
- [TASK-055-FIX](./TASK-055-FIX_Unified_Parameter_Resolution.md) Bug 3 - Score normalization fix
- See `_docs/_CHANGELOG/102-2025-12-08-ensemble-modifier-fixes.md` for implementation details

---

## ✅ Score Normalization (TASK-055-FIX Bug 3) - Already Implemented

**Original TASK-054-1 Proposal:** Create `WeightNormalizer` class to normalize weights to sum to 1.0:
```python
# Proposed approach (not implemented):
weights = {"keyword": 0.40, "semantic": 0.40, "pattern": 0.15}  # Sum = 0.95
normalized = {"keyword": 0.421, "semantic": 0.421, "pattern": 0.158}  # Sum = 1.0
```

**Actual Implementation (TASK-055-FIX Bug 3):** Different approach - normalize SCORES relative to contributing matchers:

```python
# server/router/application/matcher/ensemble_aggregator.py:173-262

def _calculate_max_possible_score(self, contributions: Dict[str, float]) -> float:
    """Calculate maximum possible score based on which matchers contributed.

    When only semantic matcher contributes, max is 0.40 (not 0.95).
    This allows proper normalization for single-matcher scenarios.

    TASK-055-FIX: Critical for multilingual prompts where keyword matcher
    may not fire due to language mismatch.
    """
    WEIGHTS = {
        "keyword": 0.40,
        "semantic": 0.40,
        "pattern": 0.15 * self.PATTERN_BOOST,
    }

    max_score = 0.0
    for matcher_name in contributions.keys():
        max_score += WEIGHTS.get(matcher_name, 0.40)

    return max_score if max_score > 0 else 0.95

def _determine_confidence_level(
    self, score: float, prompt: str, max_possible_score: float = 0.95
) -> str:
    """Determine confidence level from score and prompt analysis.

    TASK-055-FIX: Now normalizes score relative to max_possible_score.
    This fixes the bug where Polish prompts only matched semantic matcher
    (max 0.40) but thresholds were calibrated for full score (0.95).
    """
    # TASK-055-FIX: Normalize score relative to max possible
    normalized_score = score / max_possible_score if max_possible_score > 0 else 0.0

    # Use NORMALIZED thresholds
    # HIGH: normalized >= 0.70 (e.g., 0.28/0.40 = 70%)
    # MEDIUM: normalized >= 0.50 (e.g., 0.20/0.40 = 50%)
    if normalized_score >= 0.70:
        return "HIGH"
    elif normalized_score >= 0.50:
        return "MEDIUM"
    else:
        return "LOW"
```

**Why This Approach is Better:**

| Scenario | TASK-054-1 Proposal (Weight Norm) | TASK-055-FIX Implementation (Score Norm) |
|----------|-----------------------------------|------------------------------------------|
| Polish prompt (semantic only) | score = 0.336 / 1.0 = 33% → LOW | score = 0.336 / 0.40 = 84% → **HIGH** ✅ |
| English prompt (all matchers) | score = 0.74 / 1.0 = 74% → HIGH | score = 0.74 / 0.80 = 92% → **HIGH** ✅ |
| Cross-language support | ❌ Fails for single-matcher | ✅ Adapts to contributing matchers |

**Conclusion:** TASK-054-1 (Weight Normalizer) is **NOT NEEDED** - the problem was already solved more elegantly through score normalization.

**References:**
- Implementation: `server/router/application/matcher/ensemble_aggregator.py:173-262`
- Changelog: `_docs/_CHANGELOG/102-2025-12-08-ensemble-modifier-fixes.md` (Bug 3)
- Tests: Polish prompt "utworz stol piknikowy" now returns HIGH confidence (was LOW before fix)

---

## Architecture Overview

### Current TASK-053 Architecture (Sequential)

```
┌────────────────────────────────────────────────────────────────┐
│                    ENSEMBLE MATCHER                             │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│   for matcher in [keyword, semantic, pattern]:                  │
│       result = matcher.match(prompt)  ← SEQUENTIAL (~150ms)     │
│       results.append(result)                                    │
│                                                                 │
│   final = aggregator.aggregate(results)                         │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Enhanced Architecture (TASK-054)

```
┌────────────────────────────────────────────────────────────────┐
│                 ENHANCED ENSEMBLE MATCHER                       │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                WEIGHT NORMALIZER                          │  │
│  │  keyword: 0.421, semantic: 0.421, pattern: 0.158          │  │
│  │  (normalized from 0.40, 0.40, 0.15 → sum = 1.0)           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              ASYNC PARALLEL EXECUTOR                      │  │
│  │                                                           │  │
│  │   asyncio.gather(                                         │  │
│  │       keyword.match_async(prompt),   ─┐                   │  │
│  │       semantic.match_async(prompt),  ─┼─→ PARALLEL ~50ms  │  │
│  │       pattern.match_async(prompt),   ─┘                   │  │
│  │   )                                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               ENSEMBLE TELEMETRY                          │  │
│  │                                                           │  │
│  │   {                                                       │  │
│  │     "request_id": "abc123",                               │  │
│  │     "timestamp": "2025-01-08T12:00:00Z",                  │  │
│  │     "prompt": "prosty stół z prostymi nogami",            │  │
│  │     "matchers": {                                         │  │
│  │       "keyword": {"latency_ms": 12, "score": 0.0},        │  │
│  │       "semantic": {"latency_ms": 45, "score": 0.84},      │  │
│  │       "pattern": {"latency_ms": 8, "score": 0.0}          │  │
│  │     },                                                    │  │
│  │     "total_latency_ms": 52,                               │  │
│  │     "final_workflow": "table_workflow",                   │  │
│  │     "final_score": 0.354                                  │  │
│  │   }                                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              NORMALIZED AGGREGATOR                        │  │
│  │  final_score = Σ(confidence × normalized_weight)         │  │
│  │  → 0.0×0.421 + 0.84×0.421 + 0.0×0.158 = 0.354            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Current Code Analysis

### Files to Modify (from TASK-053)

| Component | Location | Current State | TASK-054 Changes |
|-----------|----------|---------------|------------------|
| `EnsembleAggregator` | `server/router/application/matcher/ensemble_aggregator.py` | ~~Hardcoded weights~~ Score normalization (TASK-055-FIX Bug 3) | ~~Add `WeightNormalizer`~~ ✅ Already done |
| `EnsembleMatcher` | `server/router/application/matcher/ensemble_matcher.py` | Sequential loop | Add async parallel (TASK-054-2) |
| `IMatcher` | `server/router/domain/interfaces/matcher.py` | Sync only | Add `match_async()` (TASK-054-2) |
| `RouterConfig` | `server/router/infrastructure/config.py` | Basic config | Add telemetry flags (TASK-054-1) |
| `RouterLogger` | `server/router/infrastructure/logger.py` | Basic logging | Add metrics collection (TASK-054-1) |

### New Files to Create

| File | Content |
|------|---------|
| ~~`server/router/application/matcher/weight_normalizer.py`~~ | ~~Weight normalization logic~~ ✅ NOT NEEDED |
| `server/router/application/matcher/ensemble_telemetry.py` | Telemetry collector (TASK-054-1) |
| `server/router/application/matcher/async_executor.py` | Async parallel executor (TASK-054-2) |
| `server/router/infrastructure/metrics.py` | Metrics storage and export (TASK-054-1) |
| ~~`tests/unit/router/application/matcher/test_weight_normalizer.py`~~ | ~~Unit tests~~ ✅ NOT NEEDED |
| `tests/unit/router/application/matcher/test_ensemble_telemetry.py` | Unit tests (TASK-054-1) |
| `tests/unit/router/application/matcher/test_async_executor.py` | Unit tests (TASK-054-2) |
| `tests/unit/router/infrastructure/test_metrics.py` | Unit tests |

---

## Sub-Tasks

### ~~TASK-054-1: Weight Normalizer~~ ✅ **OBSOLETE** - Replaced by TASK-055-FIX Bug 3

**Status:** ✅ **NOT NEEDED** - Different solution implemented

**Original Goal:** Create `WeightNormalizer` class to normalize weights (0.40, 0.40, 0.15) to sum to 1.0.

**What Was Actually Done (TASK-055-FIX Bug 3):**
- Implemented **score normalization** instead of weight normalization
- Normalizes final score relative to `max_possible_score` from contributing matchers
- Solves the same problem (correct confidence levels) with better cross-language support
- See section above for implementation details

**Decision:** This sub-task is **cancelled** as the underlying issue was solved differently.

---

### TASK-054-1: Ensemble Telemetry (was TASK-054-2)

**Status:** 🚨 To Do

Create a comprehensive telemetry system for monitoring ensemble matcher performance.

```python
# server/router/application/matcher/ensemble_telemetry.py

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


@dataclass
class MatcherTiming:
    """Timing information for a single matcher.

    Attributes:
        matcher_name: Name of the matcher.
        start_time: When matcher started.
        end_time: When matcher finished.
        latency_ms: Duration in milliseconds.
        success: Whether matcher completed successfully.
        error: Error message if failed.
    """
    matcher_name: str
    start_time: datetime
    end_time: datetime
    latency_ms: float
    success: bool = True
    error: Optional[str] = None


@dataclass
class MatcherScore:
    """Score information for a single matcher.

    Attributes:
        matcher_name: Name of the matcher.
        workflow_name: Matched workflow (or None).
        raw_confidence: Raw confidence score (0.0-1.0).
        weight: Matcher weight.
        weighted_score: raw_confidence × weight.
        metadata: Additional matcher-specific metadata.
    """
    matcher_name: str
    workflow_name: Optional[str]
    raw_confidence: float
    weight: float
    weighted_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnsembleTrace:
    """Complete trace of an ensemble matching operation.

    Attributes:
        trace_id: Unique identifier for this trace.
        timestamp: When the matching started.
        prompt: User prompt.
        context_hash: Hash of scene context (for deduplication).

        matcher_timings: Timing info for each matcher.
        matcher_scores: Score info for each matcher.

        total_latency_ms: Total time for ensemble matching.
        parallel_execution: Whether async parallel was used.

        final_workflow: Selected workflow.
        final_score: Aggregated score.
        confidence_level: HIGH, MEDIUM, LOW, NONE.
        modifiers_extracted: List of modifier keywords matched.

        aggregation_details: Details of score aggregation.
    """
    trace_id: str
    timestamp: datetime
    prompt: str
    context_hash: Optional[str] = None

    matcher_timings: List[MatcherTiming] = field(default_factory=list)
    matcher_scores: List[MatcherScore] = field(default_factory=list)

    total_latency_ms: float = 0.0
    parallel_execution: bool = False

    final_workflow: Optional[str] = None
    final_score: float = 0.0
    confidence_level: str = "NONE"
    modifiers_extracted: List[str] = field(default_factory=list)

    aggregation_details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "timestamp": self.timestamp.isoformat(),
            "prompt": self.prompt,
            "context_hash": self.context_hash,
            "matchers": {
                "timings": [
                    {
                        "name": t.matcher_name,
                        "latency_ms": t.latency_ms,
                        "success": t.success,
                        "error": t.error,
                    }
                    for t in self.matcher_timings
                ],
                "scores": [
                    {
                        "name": s.matcher_name,
                        "workflow": s.workflow_name,
                        "raw_confidence": s.raw_confidence,
                        "weight": s.weight,
                        "weighted_score": s.weighted_score,
                        "metadata": s.metadata,
                    }
                    for s in self.matcher_scores
                ],
            },
            "execution": {
                "total_latency_ms": self.total_latency_ms,
                "parallel": self.parallel_execution,
            },
            "result": {
                "workflow": self.final_workflow,
                "score": self.final_score,
                "confidence_level": self.confidence_level,
                "modifiers": self.modifiers_extracted,
            },
            "aggregation": self.aggregation_details,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


@dataclass
class TelemetryConfig:
    """Configuration for ensemble telemetry.

    Attributes:
        enabled: Whether telemetry is enabled.
        max_traces: Maximum traces to keep in memory.
        log_all_traces: Log every trace to logger.
        log_slow_traces: Log traces exceeding slow_threshold_ms.
        slow_threshold_ms: Threshold for "slow" classification.
        export_format: Format for trace export (json, csv).
    """
    enabled: bool = True
    max_traces: int = 1000
    log_all_traces: bool = False
    log_slow_traces: bool = True
    slow_threshold_ms: float = 100.0
    export_format: str = "json"


class EnsembleTelemetry:
    """Collects and manages ensemble matching telemetry.

    Provides:
    - Per-matcher timing and score tracking
    - Trace history with rolling window
    - Performance statistics and aggregations
    - Export capabilities for analysis

    Thread-safe for concurrent access.

    Example:
        ```python
        telemetry = EnsembleTelemetry()

        # Start trace
        trace = telemetry.start_trace("create a table")

        # Record matcher timing
        with telemetry.time_matcher(trace, "semantic"):
            result = semantic_matcher.match(prompt)

        # Record matcher score
        telemetry.record_score(trace, "semantic", result)

        # Finalize trace
        telemetry.finalize_trace(trace, ensemble_result)

        # Get statistics
        stats = telemetry.get_statistics()
        ```
    """



class EnsembleTelemetry:
    """Collects and manages ensemble matching telemetry.

    Provides:
    - Per-matcher timing and score tracking
    - Trace history with rolling window
    - Performance statistics and aggregations
    - Export capabilities for analysis

    Thread-safe for concurrent access.

    Example:
        ```python
        telemetry = EnsembleTelemetry()

        # Start trace
        trace = telemetry.start_trace("create a table")

        # Record matcher timing
        with telemetry.time_matcher(trace, "semantic"):
            result = semantic_matcher.match(prompt)

        # Record matcher score
        telemetry.record_score(trace, "semantic", result)

        # Finalize trace
        telemetry.finalize_trace(trace, ensemble_result)

        # Get statistics
        stats = telemetry.get_statistics()
        ```
    """

    def __init__(self, config: Optional[TelemetryConfig] = None):
        """Initialize telemetry collector.

        Args:
            config: Telemetry configuration.
        """
        self._config = config or TelemetryConfig()
        self._traces: deque[EnsembleTrace] = deque(maxlen=self._config.max_traces)
        self._lock = threading.RLock()
        self._active_traces: Dict[str, EnsembleTrace] = {}

        # Aggregate counters
        self._total_matches: int = 0
        self._total_latency_ms: float = 0.0
        self._matcher_stats: Dict[str, Dict[str, float]] = {}

    def start_trace(
        self,
        prompt: str,
        context_hash: Optional[str] = None,
    ) -> EnsembleTrace:
        """Start a new trace for an ensemble matching operation.

        Args:
            prompt: User prompt being matched.
            context_hash: Optional hash of scene context.

        Returns:
            New EnsembleTrace instance.
        """
        if not self._config.enabled:
            # Return stub trace that won't be recorded
            return EnsembleTrace(
                trace_id="disabled",
                timestamp=datetime.now(timezone.utc),
                prompt=prompt,
            )

        trace = EnsembleTrace(
            trace_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(timezone.utc),
            prompt=prompt,
            context_hash=context_hash,
        )

        with self._lock:
            self._active_traces[trace.trace_id] = trace

        logger.debug(f"Started trace {trace.trace_id} for prompt: {prompt[:50]}...")

        return trace

    def time_matcher(
        self,
        trace: EnsembleTrace,
        matcher_name: str,
    ) -> "MatcherTimingContext":
        """Context manager for timing a matcher.

        Args:
            trace: Active trace.
            matcher_name: Name of matcher being timed.

        Returns:
            Context manager for timing.
        """
        return MatcherTimingContext(self, trace, matcher_name)

    def record_timing(
        self,
        trace: EnsembleTrace,
        timing: MatcherTiming,
    ) -> None:
        """Record timing for a matcher.

        Args:
            trace: Active trace.
            timing: Timing information.
        """
        if trace.trace_id == "disabled":
            return

        with self._lock:
            trace.matcher_timings.append(timing)

            # Update aggregate stats
            if timing.matcher_name not in self._matcher_stats:
                self._matcher_stats[timing.matcher_name] = {
                    "total_calls": 0,
                    "total_latency_ms": 0.0,
                    "errors": 0,
                }

            stats = self._matcher_stats[timing.matcher_name]
            stats["total_calls"] += 1
            stats["total_latency_ms"] += timing.latency_ms
            if not timing.success:
                stats["errors"] += 1

    def record_score(
        self,
        trace: EnsembleTrace,
        matcher_name: str,
        workflow_name: Optional[str],
        raw_confidence: float,
        weight: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record score from a matcher.

        Args:
            trace: Active trace.
            matcher_name: Name of matcher.
            workflow_name: Matched workflow or None.
            raw_confidence: Raw confidence score.
            weight: Matcher weight.
            metadata: Additional metadata.
        """
        if trace.trace_id == "disabled":
            return

        score = MatcherScore(
            matcher_name=matcher_name,
            workflow_name=workflow_name,
            raw_confidence=raw_confidence,
            weight=weight,
            weighted_score=raw_confidence * weight,
            metadata=metadata or {},
        )

        with self._lock:
            trace.matcher_scores.append(score)

    def finalize_trace(
        self,
        trace: EnsembleTrace,
        final_workflow: Optional[str],
        final_score: float,
        confidence_level: str,
        modifiers: List[str],
        parallel_execution: bool = False,
        aggregation_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Finalize a trace with final results.

        Args:
            trace: Active trace to finalize.
            final_workflow: Selected workflow.
            final_score: Aggregated score.
            confidence_level: Confidence classification.
            modifiers: Extracted modifiers.
            parallel_execution: Whether async was used.
            aggregation_details: Details of aggregation.
        """
        if trace.trace_id == "disabled":
            return

        # Calculate total latency
        if trace.matcher_timings:
            if parallel_execution:
                # Parallel: total = max of individual latencies
                trace.total_latency_ms = max(
                    t.latency_ms for t in trace.matcher_timings
                )
            else:
                # Sequential: total = sum of individual latencies
                trace.total_latency_ms = sum(
                    t.latency_ms for t in trace.matcher_timings
                )

        trace.final_workflow = final_workflow
        trace.final_score = final_score
        trace.confidence_level = confidence_level
        trace.modifiers_extracted = modifiers
        trace.parallel_execution = parallel_execution
        trace.aggregation_details = aggregation_details or {}

        with self._lock:
            # Remove from active
            self._active_traces.pop(trace.trace_id, None)

            # Add to history
            self._traces.append(trace)

            # Update aggregates
            self._total_matches += 1
            self._total_latency_ms += trace.total_latency_ms

        # Log if configured
        if self._config.log_all_traces:
            logger.info(f"Trace {trace.trace_id}: {trace.to_json()}")
        elif self._config.log_slow_traces and trace.total_latency_ms > self._config.slow_threshold_ms:
            logger.warning(
                f"Slow trace {trace.trace_id}: {trace.total_latency_ms:.1f}ms > "
                f"{self._config.slow_threshold_ms}ms threshold"
            )

    def get_trace(self, trace_id: str) -> Optional[EnsembleTrace]:
        """Get a specific trace by ID.

        Args:
            trace_id: Trace identifier.

        Returns:
            EnsembleTrace or None if not found.
        """
        with self._lock:
            # Check active first
            if trace_id in self._active_traces:
                return self._active_traces[trace_id]

            # Search history
            for trace in self._traces:
                if trace.trace_id == trace_id:
                    return trace

        return None

    def get_recent_traces(self, count: int = 10) -> List[EnsembleTrace]:
        """Get most recent traces.

        Args:
            count: Number of traces to return.

        Returns:
            List of recent traces (newest first).
        """
        with self._lock:
            traces = list(self._traces)

        return list(reversed(traces[-count:]))

    def get_statistics(self) -> Dict[str, Any]:
        """Get aggregate statistics.

        Returns:
            Dictionary with performance statistics.
        """
        with self._lock:
            if self._total_matches == 0:
                return {
                    "total_matches": 0,
                    "avg_latency_ms": 0.0,
                    "matchers": {},
                }

            avg_latency = self._total_latency_ms / self._total_matches

            matcher_stats = {}
            for name, stats in self._matcher_stats.items():
                if stats["total_calls"] > 0:
                    matcher_stats[name] = {
                        "total_calls": stats["total_calls"],
                        "avg_latency_ms": stats["total_latency_ms"] / stats["total_calls"],
                        "error_rate": stats["errors"] / stats["total_calls"],
                    }

            return {
                "total_matches": self._total_matches,
                "avg_latency_ms": avg_latency,
                "matchers": matcher_stats,
                "traces_in_memory": len(self._traces),
                "active_traces": len(self._active_traces),
            }

    def get_matcher_statistics(self, matcher_name: str) -> Dict[str, float]:
        """Get statistics for a specific matcher.

        Args:
            matcher_name: Name of matcher.

        Returns:
            Dictionary with matcher-specific stats.
        """
        with self._lock:
            stats = self._matcher_stats.get(matcher_name, {})

            if not stats or stats.get("total_calls", 0) == 0:
                return {
                    "total_calls": 0,
                    "avg_latency_ms": 0.0,
                    "avg_confidence": 0.0,
                    "hit_rate": 0.0,
                    "error_rate": 0.0,
                }

            # Calculate from recent traces
            hits = 0
            total_confidence = 0.0
            trace_count = 0

            for trace in self._traces:
                for score in trace.matcher_scores:
                    if score.matcher_name == matcher_name:
                        trace_count += 1
                        total_confidence += score.raw_confidence
                        if score.workflow_name:
                            hits += 1

            return {
                "total_calls": stats["total_calls"],
                "avg_latency_ms": stats["total_latency_ms"] / stats["total_calls"],
                "avg_confidence": total_confidence / trace_count if trace_count > 0 else 0.0,
                "hit_rate": hits / trace_count if trace_count > 0 else 0.0,
                "error_rate": stats["errors"] / stats["total_calls"],
            }

    def export_traces(
        self,
        filepath: str,
        format: Optional[str] = None,
    ) -> int:
        """Export traces to file.

        Args:
            filepath: Output file path.
            format: Export format (json or csv). Uses config default if None.

        Returns:
            Number of traces exported.
        """
        format = format or self._config.export_format

        with self._lock:
            traces = list(self._traces)

        if format == "json":
            data = [t.to_dict() for t in traces]
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2, default=str)

        elif format == "csv":
            import csv

            fieldnames = [
                "trace_id", "timestamp", "prompt", "total_latency_ms",
                "final_workflow", "final_score", "confidence_level",
                "parallel_execution",
            ]

            with open(filepath, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for trace in traces:
                    writer.writerow({
                        "trace_id": trace.trace_id,
                        "timestamp": trace.timestamp.isoformat(),
                        "prompt": trace.prompt[:100],
                        "total_latency_ms": trace.total_latency_ms,
                        "final_workflow": trace.final_workflow,
                        "final_score": trace.final_score,
                        "confidence_level": trace.confidence_level,
                        "parallel_execution": trace.parallel_execution,
                    })

        else:
            raise ValueError(f"Unknown export format: {format}")

        logger.info(f"Exported {len(traces)} traces to {filepath}")
        return len(traces)

    def clear(self) -> None:
        """Clear all traces and reset statistics."""
        with self._lock:
            self._traces.clear()
            self._active_traces.clear()
            self._total_matches = 0
            self._total_latency_ms = 0.0
            self._matcher_stats.clear()

        logger.info("Telemetry cleared")


class MatcherTimingContext:
    """Context manager for timing matcher execution."""

    def __init__(
        self,
        telemetry: EnsembleTelemetry,
        trace: EnsembleTrace,
        matcher_name: str,
    ):
        self._telemetry = telemetry
        self._trace = trace
        self._matcher_name = matcher_name
        self._start_time: Optional[datetime] = None
        self._error: Optional[str] = None

    def __enter__(self) -> "MatcherTimingContext":
        self._start_time = datetime.now(timezone.utc)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        end_time = datetime.now(timezone.utc)

        if self._start_time is None:
            return False

        latency_ms = (end_time - self._start_time).total_seconds() * 1000

        timing = MatcherTiming(
            matcher_name=self._matcher_name,
            start_time=self._start_time,
            end_time=end_time,
            latency_ms=latency_ms,
            success=exc_type is None,
            error=str(exc_val) if exc_val else None,
        )

        self._telemetry.record_timing(self._trace, timing)

        # Don't suppress exceptions
        return False
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/matcher/ensemble_telemetry.py` | `EnsembleTelemetry`, `EnsembleTrace`, `MatcherTiming`, `MatcherScore` |
| Tests | `tests/unit/router/application/matcher/test_ensemble_telemetry.py` | Unit tests for telemetry |

---

### TASK-054-2: Async Parallel Executor (was TASK-054-3)

**Status:** 🚨 To Do

Create an async executor for parallel matcher execution.

```python
# server/router/application/matcher/async_executor.py

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Callable, TypeVar, Generic
from datetime import datetime, timezone
import logging
import functools

from server.router.domain.interfaces.matcher import IMatcher
from server.router.domain.entities.ensemble import MatcherResult
from server.router.application.matcher.ensemble_telemetry import (
    EnsembleTelemetry,
    EnsembleTrace,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ExecutorConfig:
    """Configuration for async executor.

    Attributes:
        max_workers: Maximum thread pool workers.
        timeout_seconds: Timeout for matcher execution.
        fallback_on_timeout: Return empty result on timeout vs raise.
        enable_parallel: Enable async parallel execution.
    """
    max_workers: int = 4
    timeout_seconds: float = 5.0
    fallback_on_timeout: bool = True
    enable_parallel: bool = True


@dataclass
class ExecutionResult(Generic[T]):
    """Result of executing a single matcher.

    Attributes:
        matcher_name: Name of the matcher.
        result: Matcher result (or None if failed).
        success: Whether execution succeeded.
        error: Error message if failed.
        latency_ms: Execution time in milliseconds.
    """
    matcher_name: str
    result: Optional[T]
    success: bool
    error: Optional[str] = None
    latency_ms: float = 0.0


class AsyncParallelExecutor:
    """Executes matchers in parallel using asyncio.

    Problem: Sequential matcher execution in TASK-053 takes ~150ms
    (keyword: ~10ms + semantic: ~100ms + pattern: ~40ms)

    Solution: Run all matchers in parallel, total time = max(individual times)
    Expected improvement: 150ms → ~100ms (33% faster)

    Implementation:
    - Uses ThreadPoolExecutor for CPU-bound LaBSE operations
    - asyncio.gather for parallel coordination
    - Timeout handling for hung matchers
    - Graceful fallback if async unavailable

    Example:
        ```python
        executor = AsyncParallelExecutor()

        matchers = [keyword_matcher, semantic_matcher, pattern_matcher]

        # Async execution
        results = await executor.execute_parallel_async(
            matchers=matchers,
            prompt="create a table",
            context=scene_context,
        )

        # Or sync wrapper
        results = executor.execute_parallel(
            matchers=matchers,
            prompt="create a table",
            context=scene_context,
        )
        ```
    """

    def __init__(
        self,
        config: Optional[ExecutorConfig] = None,
        telemetry: Optional[EnsembleTelemetry] = None,
    ):
        """Initialize executor.

        Args:
            config: Executor configuration.
            telemetry: Optional telemetry collector.
        """
        self._config = config or ExecutorConfig()
        self._telemetry = telemetry
        self._executor: Optional[ThreadPoolExecutor] = None

    def _get_executor(self) -> ThreadPoolExecutor:
        """Get or create thread pool executor."""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(
                max_workers=self._config.max_workers,
                thread_name_prefix="matcher_",
            )
        return self._executor

    async def execute_parallel_async(
        self,
        matchers: List[IMatcher],
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        trace: Optional[EnsembleTrace] = None,
    ) -> List[ExecutionResult[MatcherResult]]:
        """Execute all matchers in parallel (async version).

        Args:
            matchers: List of matchers to execute.
            prompt: User prompt.
            context: Scene context.
            trace: Optional telemetry trace.

        Returns:
            List of ExecutionResult for each matcher.
        """
        if not self._config.enable_parallel:
            # Fallback to sequential
            return await self._execute_sequential_async(
                matchers, prompt, context, trace
            )

        loop = asyncio.get_event_loop()
        executor = self._get_executor()

        # Create tasks for each matcher
        tasks = []
        for matcher in matchers:
            task = self._execute_matcher_async(
                loop, executor, matcher, prompt, context, trace
            )
            tasks.append(task)

        # Execute all in parallel with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self._config.timeout_seconds,
            )
        except asyncio.TimeoutError:
            logger.error(f"Matcher execution timed out after {self._config.timeout_seconds}s")
            if self._config.fallback_on_timeout:
                # Return empty results for all matchers
                return [
                    ExecutionResult(
                        matcher_name=m.name,
                        result=None,
                        success=False,
                        error="Timeout",
                    )
                    for m in matchers
                ]
            raise

        # Process results
        execution_results: List[ExecutionResult[MatcherResult]] = []

        for matcher, result in zip(matchers, results):
            if isinstance(result, Exception):
                execution_results.append(ExecutionResult(
                    matcher_name=matcher.name,
                    result=None,
                    success=False,
                    error=str(result),
                ))
            elif isinstance(result, ExecutionResult):
                execution_results.append(result)
            else:
                # Unexpected type
                execution_results.append(ExecutionResult(
                    matcher_name=matcher.name,
                    result=result if isinstance(result, MatcherResult) else None,
                    success=isinstance(result, MatcherResult),
                    error=None if isinstance(result, MatcherResult) else f"Unexpected type: {type(result)}",
                ))

        return execution_results

    async def _execute_matcher_async(
        self,
        loop: asyncio.AbstractEventLoop,
        executor: ThreadPoolExecutor,
        matcher: IMatcher,
        prompt: str,
        context: Optional[Dict[str, Any]],
        trace: Optional[EnsembleTrace],
    ) -> ExecutionResult[MatcherResult]:
        """Execute a single matcher asynchronously.

        Args:
            loop: Event loop.
            executor: Thread pool executor.
            matcher: Matcher to execute.
            prompt: User prompt.
            context: Scene context.
            trace: Telemetry trace.

        Returns:
            ExecutionResult with matcher result.
        """
        start_time = datetime.now(timezone.utc)

        try:
            # Check if matcher has async version
            if hasattr(matcher, 'match_async'):
                result = await matcher.match_async(prompt, context)
            else:
                # Run sync matcher in thread pool
                func = functools.partial(matcher.match, prompt, context)
                result = await loop.run_in_executor(executor, func)

            end_time = datetime.now(timezone.utc)
            latency_ms = (end_time - start_time).total_seconds() * 1000

            # Record telemetry
            if self._telemetry and trace:
                self._telemetry.record_score(
                    trace=trace,
                    matcher_name=matcher.name,
                    workflow_name=result.workflow_name,
                    raw_confidence=result.confidence,
                    weight=matcher.weight,
                    metadata=result.metadata,
                )

            return ExecutionResult(
                matcher_name=matcher.name,
                result=result,
                success=True,
                latency_ms=latency_ms,
            )

        except Exception as e:
            end_time = datetime.now(timezone.utc)
            latency_ms = (end_time - start_time).total_seconds() * 1000

            logger.exception(f"Matcher '{matcher.name}' failed: {e}")

            return ExecutionResult(
                matcher_name=matcher.name,
                result=None,
                success=False,
                error=str(e),
                latency_ms=latency_ms,
            )

    async def _execute_sequential_async(
        self,
        matchers: List[IMatcher],
        prompt: str,
        context: Optional[Dict[str, Any]],
        trace: Optional[EnsembleTrace],
    ) -> List[ExecutionResult[MatcherResult]]:
        """Execute matchers sequentially (fallback mode).

        Args:
            matchers: List of matchers.
            prompt: User prompt.
            context: Scene context.
            trace: Telemetry trace.

        Returns:
            List of ExecutionResult.
        """
        results: List[ExecutionResult[MatcherResult]] = []

        for matcher in matchers:
            start_time = datetime.now(timezone.utc)

            try:
                result = matcher.match(prompt, context)

                end_time = datetime.now(timezone.utc)
                latency_ms = (end_time - start_time).total_seconds() * 1000

                if self._telemetry and trace:
                    self._telemetry.record_score(
                        trace=trace,
                        matcher_name=matcher.name,
                        workflow_name=result.workflow_name,
                        raw_confidence=result.confidence,
                        weight=matcher.weight,
                        metadata=result.metadata,
                    )

                results.append(ExecutionResult(
                    matcher_name=matcher.name,
                    result=result,
                    success=True,
                    latency_ms=latency_ms,
                ))

            except Exception as e:
                end_time = datetime.now(timezone.utc)
                latency_ms = (end_time - start_time).total_seconds() * 1000

                logger.exception(f"Matcher '{matcher.name}' failed: {e}")

                results.append(ExecutionResult(
                    matcher_name=matcher.name,
                    result=None,
                    success=False,
                    error=str(e),
                    latency_ms=latency_ms,
                ))

        return results

    def execute_parallel(
        self,
        matchers: List[IMatcher],
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        trace: Optional[EnsembleTrace] = None,
    ) -> List[ExecutionResult[MatcherResult]]:
        """Execute all matchers in parallel (sync wrapper).

        Convenience method that handles event loop creation for sync code.

        Args:
            matchers: List of matchers to execute.
            prompt: User prompt.
            context: Scene context.
            trace: Telemetry trace.

        Returns:
            List of ExecutionResult for each matcher.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is not None:
            # Already in async context - create nested task
            # This shouldn't happen in normal usage
            logger.warning("execute_parallel called from async context - using sequential")
            return self._execute_sequential_sync(matchers, prompt, context, trace)

        # Create new event loop
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.execute_parallel_async(matchers, prompt, context, trace)
            )
        finally:
            loop.close()

    def _execute_sequential_sync(
        self,
        matchers: List[IMatcher],
        prompt: str,
        context: Optional[Dict[str, Any]],
        trace: Optional[EnsembleTrace],
    ) -> List[ExecutionResult[MatcherResult]]:
        """Execute matchers sequentially (sync version).

        Args:
            matchers: List of matchers.
            prompt: User prompt.
            context: Scene context.
            trace: Telemetry trace.

        Returns:
            List of ExecutionResult.
        """
        results: List[ExecutionResult[MatcherResult]] = []

        for matcher in matchers:
            start_time = datetime.now(timezone.utc)

            try:
                result = matcher.match(prompt, context)

                end_time = datetime.now(timezone.utc)
                latency_ms = (end_time - start_time).total_seconds() * 1000

                results.append(ExecutionResult(
                    matcher_name=matcher.name,
                    result=result,
                    success=True,
                    latency_ms=latency_ms,
                ))

            except Exception as e:
                end_time = datetime.now(timezone.utc)
                latency_ms = (end_time - start_time).total_seconds() * 1000

                results.append(ExecutionResult(
                    matcher_name=matcher.name,
                    result=None,
                    success=False,
                    error=str(e),
                    latency_ms=latency_ms,
                ))

        return results

    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the thread pool executor.

        Args:
            wait: Wait for pending tasks to complete.
        """
        if self._executor is not None:
            self._executor.shutdown(wait=wait)
            self._executor = None
            logger.info("AsyncParallelExecutor shutdown complete")

    def get_info(self) -> Dict[str, Any]:
        """Get executor information.

        Returns:
            Dictionary with executor status.
        """
        return {
            "config": {
                "max_workers": self._config.max_workers,
                "timeout_seconds": self._config.timeout_seconds,
                "fallback_on_timeout": self._config.fallback_on_timeout,
                "enable_parallel": self._config.enable_parallel,
            },
            "executor_active": self._executor is not None,
            "telemetry_enabled": self._telemetry is not None,
        }
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/matcher/async_executor.py` | `AsyncParallelExecutor`, `ExecutorConfig`, `ExecutionResult` |
| Tests | `tests/unit/router/application/matcher/test_async_executor.py` | Unit tests for async execution |

---

### TASK-054-3: IMatcher Interface Extension (was TASK-054-4)

**Status:** 🚨 To Do

Extend the IMatcher interface with optional async method.

```python
# Changes to: server/router/domain/interfaces/matcher.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from server.router.domain.entities.ensemble import MatcherResult


class IMatcher(ABC):
    """Abstract interface for workflow matchers.

    All matchers implement this interface to enable ensemble matching.
    Each matcher runs independently and returns a MatcherResult.

    TASK-054: Added optional match_async() for parallel execution.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Matcher name for logging and aggregation."""
        pass

    @property
    @abstractmethod
    def weight(self) -> float:
        """Weight for score aggregation (0.0-1.0).

        Note: TASK-055-FIX Bug 3 uses score normalization relative to contributing matchers.
        """
        pass

    @abstractmethod
    def match(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> "MatcherResult":
        """Match prompt to workflow (synchronous).

        Args:
            prompt: User prompt/goal.
            context: Optional scene context dict.

        Returns:
            MatcherResult with workflow and confidence.
        """
        pass

    async def match_async(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> "MatcherResult":
        """Match prompt to workflow (asynchronous).

        TASK-054: Optional async version for parallel execution.
        Default implementation calls sync match().

        Override this for matchers with async I/O (e.g., remote embedding service).

        Args:
            prompt: User prompt/goal.
            context: Optional scene context dict.

        Returns:
            MatcherResult with workflow and confidence.
        """
        # Default: delegate to sync version
        return self.match(prompt, context)

    def supports_async(self) -> bool:
        """Check if matcher has native async support.

        Returns:
            True if match_async is overridden with native async.
        """
        # Check if match_async is overridden
        return type(self).match_async is not IMatcher.match_async
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Domain | `server/router/domain/interfaces/matcher.py` | Add `match_async()`, `supports_async()` to `IMatcher` |
| Tests | `tests/unit/router/domain/test_interfaces.py` | Test async interface |

---

### TASK-054-4: EnsembleMatcher Integration (was TASK-054-5)

**Status:** 🚨 To Do

Update EnsembleMatcher to use the new components.

```python
# Changes to: server/router/application/matcher/ensemble_matcher.py

from typing import List, Optional, Dict, Any, TYPE_CHECKING
import logging

from server.router.domain.interfaces.matcher import IMatcher
from server.router.domain.entities.ensemble import MatcherResult, EnsembleResult
from server.router.domain.entities.scene_context import SceneContext
from server.router.application.matcher.keyword_matcher import KeywordMatcher
from server.router.application.matcher.semantic_matcher import SemanticMatcher
from server.router.application.matcher.pattern_matcher import PatternMatcher
from server.router.application.matcher.ensemble_aggregator import EnsembleAggregator
# TASK-054 imports:
from server.router.application.matcher.ensemble_telemetry import EnsembleTelemetry  # TASK-054-1
from server.router.application.matcher.async_executor import AsyncParallelExecutor  # TASK-054-2
from server.router.infrastructure.config import RouterConfig
from server.router.infrastructure.logger import RouterLogger

if TYPE_CHECKING:
    from server.router.application.workflows.registry import WorkflowRegistry

logger = logging.getLogger(__name__)


class EnsembleMatcher:
    """Orchestrates parallel matching using multiple matchers.

    TASK-053: Core ensemble matching functionality.
    TASK-054: Enhanced with:
        - ~~WeightNormalizer~~ ✅ NOT NEEDED - Score normalization in TASK-055-FIX Bug 3
        - EnsembleTelemetry for observability (TASK-054-1)
        - AsyncParallelExecutor for parallel execution (TASK-054-2)
    """

    def __init__(
        self,
        keyword_matcher: KeywordMatcher,
        semantic_matcher: SemanticMatcher,
        pattern_matcher: PatternMatcher,
        aggregator: EnsembleAggregator,
        config: Optional[RouterConfig] = None,
        # TASK-054 additions:
        telemetry: Optional[EnsembleTelemetry] = None,
        async_executor: Optional[AsyncParallelExecutor] = None,
    ):
        """Initialize ensemble matcher.

        Args:
            keyword_matcher: Matcher for keyword-based matching.
            semantic_matcher: Matcher for LaBSE semantic matching.
            pattern_matcher: Matcher for geometry pattern matching.
            aggregator: Aggregator for combining results.
            config: Router configuration.
            telemetry: TASK-054-1 telemetry collector.
            async_executor: TASK-054-2 async parallel executor.
        """
        self._matchers: List[IMatcher] = [
            keyword_matcher,
            semantic_matcher,
            pattern_matcher,
        ]
        self._aggregator = aggregator
        self._config = config or RouterConfig()
        self._router_logger = RouterLogger()
        self._is_initialized = False

        # TASK-054 components
        self._telemetry = telemetry or EnsembleTelemetry()
        self._async_executor = async_executor or AsyncParallelExecutor(
            telemetry=self._telemetry
        )

    # NOTE: _normalize_matcher_weights() removed - score normalization now handled
    # by EnsembleAggregator._calculate_max_possible_score() (TASK-055-FIX Bug 3)

    def match(
        self,
        prompt: str,
        context: Optional[SceneContext] = None,
    ) -> EnsembleResult:
        """Run all matchers and aggregate results.

        TASK-054: Uses async parallel execution and telemetry.

        Args:
            prompt: User prompt/goal.
            context: Optional scene context.

        Returns:
            EnsembleResult with workflow, confidence, and modifiers.
        """
        # Convert context to dict for matchers
        context_dict: Optional[Dict[str, Any]] = None
        if context:
            context_dict = context.to_dict()

        # Start telemetry trace
        trace = self._telemetry.start_trace(
            prompt=prompt,
            context_hash=str(hash(str(context_dict))) if context_dict else None,
        )

        # Execute matchers in parallel
        if self._config.enable_parallel_matching:
            execution_results = self._async_executor.execute_parallel(
                matchers=self._matchers,
                prompt=prompt,
                context=context_dict,
                trace=trace,
            )
        else:
            # Sequential fallback
            execution_results = self._async_executor._execute_sequential_sync(
                matchers=self._matchers,
                prompt=prompt,
                context=context_dict,
                trace=trace,
            )

        # Convert to MatcherResult list for aggregator
        results: List[MatcherResult] = []
        for exec_result in execution_results:
            if exec_result.success and exec_result.result:
                # Update weight with normalized value
                result = exec_result.result
                normalized_weight = self._normalized_weights.get(
                    result.matcher_name, result.weight
                )

                # Create new result with normalized weight
                results.append(MatcherResult(
                    matcher_name=result.matcher_name,
                    workflow_name=result.workflow_name,
                    confidence=result.confidence,
                    weight=normalized_weight,  # TASK-054: Use normalized
                    metadata=result.metadata,
                ))

                self._router_logger.log_info(
                    f"Matcher '{result.matcher_name}': "
                    f"{result.workflow_name or 'None'} "
                    f"(confidence: {result.confidence:.2f}, "
                    f"normalized_weight: {normalized_weight:.3f}, "
                    f"weighted: {result.confidence * normalized_weight:.3f})"
                )
            else:
                # Failed matcher - add empty result
                normalized_weight = self._normalized_weights.get(
                    exec_result.matcher_name, 0.0
                )
                results.append(MatcherResult(
                    matcher_name=exec_result.matcher_name,
                    workflow_name=None,
                    confidence=0.0,
                    weight=normalized_weight,
                    metadata={"error": exec_result.error},
                ))

                self._router_logger.log_error(
                    exec_result.matcher_name,
                    exec_result.error or "Unknown error",
                )

        # Aggregate results
        ensemble_result = self._aggregator.aggregate(results, prompt)

        # Finalize telemetry
        parallel = self._config.enable_parallel_matching
        self._telemetry.finalize_trace(
            trace=trace,
            final_workflow=ensemble_result.workflow_name,
            final_score=ensemble_result.final_score,
            confidence_level=ensemble_result.confidence_level,
            modifiers=list(ensemble_result.modifiers.keys()),
            parallel_execution=parallel,
            aggregation_details={
                "matcher_contributions": ensemble_result.matcher_contributions,
                "composition_mode": ensemble_result.composition_mode,
            },
        )

        self._router_logger.log_info(
            f"Ensemble result: {ensemble_result.workflow_name} "
            f"(score: {ensemble_result.final_score:.3f}, "
            f"level: {ensemble_result.confidence_level}, "
            f"modifiers: {list(ensemble_result.modifiers.keys())}, "
            f"parallel: {parallel})"
        )

        return ensemble_result

    def get_telemetry_statistics(self) -> Dict[str, Any]:
        """Get telemetry statistics.

        TASK-054: Access to telemetry data for debugging/monitoring.

        Returns:
            Dictionary with telemetry stats.
        """
        return self._telemetry.get_statistics()

    def get_info(self) -> Dict[str, Any]:
        """Get ensemble matcher information.

        Returns:
            Dictionary with matcher status and configuration.
        """
        return {
            "is_initialized": self._is_initialized,
            "matchers": [
                {
                    "name": m.name,
                    "original_weight": m.weight,
                    "normalized_weight": self._normalized_weights.get(m.name, m.weight),
                    "initialized": getattr(m, 'is_initialized', lambda: True)(),
                    "supports_async": m.supports_async(),
                }
                for m in self._matchers
            ],
            "telemetry": self._telemetry.get_statistics(),
            "async_executor": self._async_executor.get_info(),
        }

    def shutdown(self) -> None:
        """Shutdown the ensemble matcher.

        Cleans up resources (thread pool, telemetry).
        """
        self._async_executor.shutdown()
        logger.info("EnsembleMatcher shutdown complete")
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/matcher/ensemble_matcher.py` | Integrate ~~`WeightNormalizer`~~, `EnsembleTelemetry`, `AsyncParallelExecutor` |
| Tests | `tests/unit/router/application/matcher/test_ensemble_matcher.py` | Update tests for TASK-054 features |

---

### TASK-054-5: Configuration Updates (was TASK-054-6)

**Status:** 🚨 To Do

Add configuration fields for TASK-054 enhancements.

```python
# Changes to: server/router/infrastructure/config.py

@dataclass
class RouterConfig:
    # ... existing fields from TASK-053 ...

    # Ensemble matching (TASK-053)
    use_ensemble_matching: bool = True
    keyword_weight: float = 0.40
    semantic_weight: float = 0.40
    pattern_weight: float = 0.15
    pattern_boost_factor: float = 1.3
    composition_threshold: float = 0.15
    enable_composition_mode: bool = False
    ensemble_high_threshold: float = 0.7
    ensemble_medium_threshold: float = 0.4

    # TASK-054: Weight normalization
    normalize_weights: bool = True  # Auto-normalize to sum=1.0
    weight_validation_mode: str = "warn"  # "warn", "error", "silent"

    # TASK-054: Parallel execution
    enable_parallel_matching: bool = True  # Use async parallel
    parallel_max_workers: int = 4  # Thread pool size
    parallel_timeout_seconds: float = 5.0  # Matcher timeout
    parallel_fallback_on_timeout: bool = True  # Return empty on timeout

    # TASK-054: Telemetry
    enable_ensemble_telemetry: bool = True  # Enable telemetry
    telemetry_max_traces: int = 1000  # Max traces in memory
    telemetry_log_all_traces: bool = False  # Log every trace
    telemetry_log_slow_traces: bool = True  # Log slow traces
    telemetry_slow_threshold_ms: float = 100.0  # Slow trace threshold
    telemetry_export_format: str = "json"  # Export format
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Infrastructure | `server/router/infrastructure/config.py` | Add TASK-054 config fields |
| Tests | `tests/unit/router/infrastructure/test_config.py` | Test new config fields |

---

### TASK-054-6: Metrics Export (was TASK-054-7)

**Status:** 🚨 To Do

Create metrics infrastructure for external monitoring (Prometheus, etc.).

```python
# server/router/infrastructure/metrics.py

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone
from collections import defaultdict
import threading
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Single metric data point.

    Attributes:
        name: Metric name.
        value: Metric value.
        timestamp: When recorded.
        labels: Metric labels/tags.
    """
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricConfig:
    """Configuration for metrics collection.

    Attributes:
        enabled: Whether metrics collection is enabled.
        prefix: Prefix for all metric names.
        export_interval_seconds: How often to export metrics.
        retention_seconds: How long to keep metrics in memory.
    """
    enabled: bool = True
    prefix: str = "blender_router"
    export_interval_seconds: float = 60.0
    retention_seconds: float = 3600.0


class MetricsRegistry:
    """Central registry for router metrics.

    Collects metrics from various components and provides
    export in multiple formats (Prometheus, JSON, etc.).

    Metric Types:
    - Counter: Monotonically increasing value (e.g., total_matches)
    - Gauge: Value that can go up/down (e.g., active_traces)
    - Histogram: Distribution of values (e.g., latency)

    Example:
        ```python
        registry = MetricsRegistry()

        # Counter
        registry.increment("matches_total", labels={"matcher": "semantic"})

        # Gauge
        registry.set_gauge("active_traces", 5)

        # Histogram
        registry.observe("match_latency_ms", 45.2, labels={"matcher": "semantic"})

        # Export
        prometheus_output = registry.export_prometheus()
        json_output = registry.export_json()
        ```
    """

    def __init__(self, config: Optional[MetricConfig] = None):
        """Initialize registry.

        Args:
            config: Metrics configuration.
        """
        self._config = config or MetricConfig()
        self._lock = threading.RLock()

        # Counters: name → {labels_hash → value}
        self._counters: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

        # Gauges: name → {labels_hash → value}
        self._gauges: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

        # Histograms: name → {labels_hash → [values]}
        self._histograms: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

        # Labels storage: labels_hash → labels_dict
        self._labels: Dict[str, Dict[str, str]] = {}

        # Histogram buckets
        self._histogram_buckets = [
            5, 10, 25, 50, 75, 100, 150, 200, 300, 500, 1000
        ]

    def _labels_hash(self, labels: Dict[str, str]) -> str:
        """Create hash from labels dict."""
        if not labels:
            return ""
        items = sorted(labels.items())
        return ",".join(f"{k}={v}" for k, v in items)

    def increment(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Increment a counter.

        Args:
            name: Metric name.
            value: Amount to increment.
            labels: Optional labels.
        """
        if not self._config.enabled:
            return

        labels = labels or {}
        labels_hash = self._labels_hash(labels)
        full_name = f"{self._config.prefix}_{name}"

        with self._lock:
            self._counters[full_name][labels_hash] += value
            self._labels[labels_hash] = labels

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Set a gauge value.

        Args:
            name: Metric name.
            value: Gauge value.
            labels: Optional labels.
        """
        if not self._config.enabled:
            return

        labels = labels or {}
        labels_hash = self._labels_hash(labels)
        full_name = f"{self._config.prefix}_{name}"

        with self._lock:
            self._gauges[full_name][labels_hash] = value
            self._labels[labels_hash] = labels

    def observe(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Observe a histogram value.

        Args:
            name: Metric name.
            value: Observed value.
            labels: Optional labels.
        """
        if not self._config.enabled:
            return

        labels = labels or {}
        labels_hash = self._labels_hash(labels)
        full_name = f"{self._config.prefix}_{name}"

        with self._lock:
            self._histograms[full_name][labels_hash].append(value)
            self._labels[labels_hash] = labels

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format.

        Returns:
            Prometheus text format string.
        """
        lines: List[str] = []

        with self._lock:
            # Counters
            for name, values in self._counters.items():
                lines.append(f"# TYPE {name} counter")
                for labels_hash, value in values.items():
                    labels_str = self._format_prometheus_labels(labels_hash)
                    lines.append(f"{name}{labels_str} {value}")

            # Gauges
            for name, values in self._gauges.items():
                lines.append(f"# TYPE {name} gauge")
                for labels_hash, value in values.items():
                    labels_str = self._format_prometheus_labels(labels_hash)
                    lines.append(f"{name}{labels_str} {value}")

            # Histograms
            for name, values in self._histograms.items():
                lines.append(f"# TYPE {name} histogram")
                for labels_hash, observations in values.items():
                    labels = self._labels.get(labels_hash, {})

                    # Calculate bucket counts
                    sorted_obs = sorted(observations)
                    for bucket in self._histogram_buckets:
                        count = sum(1 for v in sorted_obs if v <= bucket)
                        bucket_labels = {**labels, "le": str(bucket)}
                        labels_str = self._format_prometheus_labels_dict(bucket_labels)
                        lines.append(f"{name}_bucket{labels_str} {count}")

                    # +Inf bucket
                    inf_labels = {**labels, "le": "+Inf"}
                    labels_str = self._format_prometheus_labels_dict(inf_labels)
                    lines.append(f"{name}_bucket{labels_str} {len(observations)}")

                    # Sum and count
                    labels_str = self._format_prometheus_labels(labels_hash)
                    lines.append(f"{name}_sum{labels_str} {sum(observations)}")
                    lines.append(f"{name}_count{labels_str} {len(observations)}")

        return "\n".join(lines)

    def _format_prometheus_labels(self, labels_hash: str) -> str:
        """Format labels for Prometheus."""
        if not labels_hash:
            return ""
        labels = self._labels.get(labels_hash, {})
        return self._format_prometheus_labels_dict(labels)

    def _format_prometheus_labels_dict(self, labels: Dict[str, str]) -> str:
        """Format labels dict for Prometheus."""
        if not labels:
            return ""
        items = [f'{k}="{v}"' for k, v in sorted(labels.items())]
        return "{" + ",".join(items) + "}"

    def export_json(self) -> Dict[str, Any]:
        """Export metrics as JSON-serializable dict.

        Returns:
            Dictionary with all metrics.
        """
        with self._lock:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "counters": {
                    name: {
                        labels_hash or "default": value
                        for labels_hash, value in values.items()
                    }
                    for name, values in self._counters.items()
                },
                "gauges": {
                    name: {
                        labels_hash or "default": value
                        for labels_hash, value in values.items()
                    }
                    for name, values in self._gauges.items()
                },
                "histograms": {
                    name: {
                        labels_hash or "default": {
                            "count": len(obs),
                            "sum": sum(obs),
                            "min": min(obs) if obs else 0,
                            "max": max(obs) if obs else 0,
                            "avg": sum(obs) / len(obs) if obs else 0,
                        }
                        for labels_hash, obs in values.items()
                    }
                    for name, values in self._histograms.items()
                },
            }

    def clear(self) -> None:
        """Clear all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._labels.clear()


# Global registry instance
_global_registry: Optional[MetricsRegistry] = None


def get_metrics_registry() -> MetricsRegistry:
    """Get global metrics registry.

    Returns:
        Global MetricsRegistry instance.
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = MetricsRegistry()
    return _global_registry
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Infrastructure | `server/router/infrastructure/metrics.py` | `MetricsRegistry`, `MetricPoint`, `MetricConfig` |
| Tests | `tests/unit/router/infrastructure/test_metrics.py` | Unit tests for metrics |

---

### TASK-054-7: Router Integration (was TASK-054-8)

**Status:** 🚨 To Do

Integrate TASK-054 components into SupervisorRouter.

**Changes to `server/router/application/router.py`:**

```python
# Add to __init__:

class SupervisorRouter:
    def __init__(self, ...):
        # ... existing init ...

        # TASK-054: Metrics integration
        from server.router.infrastructure.metrics import get_metrics_registry
        self._metrics = get_metrics_registry()

    def _ensure_ensemble_initialized(self) -> bool:
        """Ensure ensemble matcher is initialized.

        TASK-054: Creates components with telemetry and async support.
        """
        if self._ensemble_matcher is not None:
            return True

        try:
            from server.router.application.workflows.registry import get_workflow_registry
            from server.router.application.matcher.keyword_matcher import KeywordMatcher
            from server.router.application.matcher.semantic_matcher import SemanticMatcher
            from server.router.application.matcher.pattern_matcher import PatternMatcher
            from server.router.application.matcher.modifier_extractor import ModifierExtractor
            from server.router.application.matcher.ensemble_aggregator import EnsembleAggregator
            from server.router.application.matcher.ensemble_matcher import EnsembleMatcher
            # TASK-054 imports
            from server.router.application.matcher.ensemble_telemetry import (
                EnsembleTelemetry, TelemetryConfig
            )
            from server.router.application.matcher.async_executor import (
                AsyncParallelExecutor, ExecutorConfig
            )

            registry = get_workflow_registry()
            registry.ensure_custom_loaded()

            # Create modifier extractor
            modifier_extractor = ModifierExtractor(registry)

            # Create matchers
            keyword_matcher = KeywordMatcher(registry)
            semantic_matcher = SemanticMatcher(
                classifier=self._workflow_classifier,
                registry=registry,
                config=self.config,
            )
            pattern_matcher = PatternMatcher(registry)

            # Create aggregator (includes score normalization from TASK-055-FIX Bug 3)
            aggregator = EnsembleAggregator(modifier_extractor, self.config)

            # TASK-054-1: Create telemetry
            telemetry_config = TelemetryConfig(
                enabled=self.config.enable_ensemble_telemetry,
                max_traces=self.config.telemetry_max_traces,
                log_all_traces=self.config.telemetry_log_all_traces,
                log_slow_traces=self.config.telemetry_log_slow_traces,
                slow_threshold_ms=self.config.telemetry_slow_threshold_ms,
                export_format=self.config.telemetry_export_format,
            )
            telemetry = EnsembleTelemetry(telemetry_config)

            # TASK-054-2: Create async executor
            executor_config = ExecutorConfig(
                max_workers=self.config.parallel_max_workers,
                timeout_seconds=self.config.parallel_timeout_seconds,
                fallback_on_timeout=self.config.parallel_fallback_on_timeout,
                enable_parallel=self.config.enable_parallel_matching,
            )
            async_executor = AsyncParallelExecutor(executor_config, telemetry)

            # Create ensemble matcher with all components
            self._ensemble_matcher = EnsembleMatcher(
                keyword_matcher=keyword_matcher,
                semantic_matcher=semantic_matcher,
                pattern_matcher=pattern_matcher,
                aggregator=aggregator,
                config=self.config,
                telemetry=telemetry,
                async_executor=async_executor,
            )

            # Initialize semantic matcher with registry
            self._ensemble_matcher.initialize(registry)

            # Record metric
            self._metrics.increment("ensemble_init_success")

            self.logger.log_info("Ensemble matcher initialized with TASK-054 enhancements")
            return True

        except Exception as e:
            self._metrics.increment("ensemble_init_failure")
            self.logger.log_error("ensemble_init", str(e))
            return False

    def get_ensemble_telemetry(self) -> Optional[Dict[str, Any]]:
        """Get ensemble telemetry statistics.

        TASK-054: Provides access to matcher performance data.

        Returns:
            Telemetry statistics or None if not initialized.
        """
        if self._ensemble_matcher is None:
            return None
        return self._ensemble_matcher.get_telemetry_statistics()

    def get_ensemble_recent_traces(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent ensemble matching traces.

        TASK-054: Provides access to recent trace data for debugging.

        Args:
            count: Number of traces to return.

        Returns:
            List of trace dictionaries.
        """
        if self._ensemble_matcher is None:
            return []

        traces = self._ensemble_matcher._telemetry.get_recent_traces(count)
        return [t.to_dict() for t in traces]
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Application | `server/router/application/router.py` | Integrate TASK-054 components |
| Tests | `tests/unit/router/application/test_supervisor_router.py` | Test TASK-054 integration |

---

### TASK-054-8: MCP Tools for Telemetry (was TASK-054-9)

**Status:** 🚨 To Do

Add MCP tools for accessing telemetry data.

```python
# server/adapters/mcp/areas/router.py

@mcp.tool()
def router_get_telemetry(ctx: Context) -> str:
    """[SYSTEM][SAFE][READ-ONLY] Get ensemble matcher telemetry statistics.

    TASK-054: Provides visibility into matcher performance.

    Returns:
        JSON with telemetry statistics including:
        - Total matches count
        - Average latency
        - Per-matcher statistics (calls, latency, error rate)
        - Traces in memory
    """
    router = get_supervisor_router()
    stats = router.get_ensemble_telemetry()

    if stats is None:
        return "Ensemble matcher not initialized. Set a goal first."

    return json.dumps(stats, indent=2)


@mcp.tool()
def router_get_recent_traces(
    ctx: Context,
    count: int = 10,
) -> str:
    """[SYSTEM][SAFE][READ-ONLY] Get recent ensemble matching traces.

    TASK-054: Provides detailed trace data for debugging.

    Args:
        count: Number of traces to return (default 10, max 100).

    Returns:
        JSON array of recent traces with timing and score details.
    """
    router = get_supervisor_router()

    count = min(count, 100)  # Limit to prevent huge responses
    traces = router.get_ensemble_recent_traces(count)

    if not traces:
        return "No traces available. Set a goal to generate traces."

    return json.dumps(traces, indent=2)


@mcp.tool()
def router_export_telemetry(
    ctx: Context,
    filepath: str,
    format: str = "json",
) -> str:
    """[SYSTEM][SAFE] Export ensemble telemetry to file.

    TASK-054: Exports traces for external analysis.

    Args:
        filepath: Output file path.
        format: Export format - "json" or "csv".

    Returns:
        Success message with export count.
    """
    router = get_supervisor_router()

    if router._ensemble_matcher is None:
        return "Ensemble matcher not initialized."

    count = router._ensemble_matcher._telemetry.export_traces(filepath, format)
    return f"Exported {count} traces to {filepath}"
```

**Implementation Checklist:**

| Layer | File | What to Add |
|-------|------|-------------|
| Adapters | `server/adapters/mcp/areas/router.py` | Add telemetry MCP tools |
| Tests | `tests/unit/adapters/mcp/test_router_tools.py` | Test new MCP tools |

---

## Files to Create

### New Files

```
server/router/application/matcher/ensemble_telemetry.py          # TASK-054-1
server/router/application/matcher/async_executor.py              # TASK-054-2
server/router/infrastructure/metrics.py                           # TASK-054-6

tests/unit/router/application/matcher/test_ensemble_telemetry.py # TASK-054-1
tests/unit/router/application/matcher/test_async_executor.py     # TASK-054-2
tests/unit/router/infrastructure/test_metrics.py                  # TASK-054-6
```

### Files to Modify

```
server/router/domain/interfaces/matcher.py              # Add match_async()
server/router/application/matcher/ensemble_matcher.py   # Integrate TASK-054 components
server/router/application/router.py                     # Router integration
server/router/infrastructure/config.py                  # Add config fields
server/adapters/mcp/areas/router.py                     # Add telemetry tools
```

---

## Implementation Order

~~1. **TASK-054-1**: Weight Normalizer~~ ✅ NOT NEEDED - Replaced by TASK-055-FIX Bug 3

**Remaining tasks** (renumbered):

1. **TASK-054-1** (was 054-2): Ensemble Telemetry (observability)
2. **TASK-054-2** (was 054-3): Async Parallel Executor (performance)
3. **TASK-054-3** (was 054-4): IMatcher Interface Extension (async support)
4. **TASK-054-4** (was 054-6): Configuration Updates
5. **TASK-054-5** (was 054-7): Metrics Export
6. **TASK-054-6** (was 054-5): EnsembleMatcher Integration
7. **TASK-054-7** (was 054-8): Router Integration
8. **TASK-054-8** (was 054-9): MCP Tools for Telemetry

---

## Testing Requirements

### Unit Tests

- [ ] ~~`test_weight_normalizer.py`~~ ✅ NOT NEEDED
- [ ] `test_ensemble_telemetry.py` - Telemetry collection and export
- [ ] `test_async_executor.py` - Parallel execution
- [ ] `test_metrics.py` - Metrics registry and export

### Integration Tests

- [ ] `test_ensemble_with_telemetry.py` - Full pipeline with telemetry
- [ ] `test_parallel_vs_sequential.py` - Performance comparison
- [ ] ~~`test_weight_normalization_e2e.py`~~ ✅ NOT NEEDED - Score normalization already tested in TASK-055-FIX Bug 3

### Performance Tests

- [ ] `test_parallel_latency.py` - Verify latency improvement
- [ ] `test_telemetry_overhead.py` - Measure telemetry overhead

---

## Success Criteria

1. **Weight Normalization**: All matcher weights sum to exactly 1.0
2. **Telemetry**: Per-matcher timing and score tracking functional
3. **Parallel Execution**: ~30% latency reduction vs sequential
4. **Metrics Export**: Prometheus and JSON export working
5. **MCP Tools**: Telemetry accessible via MCP tools
6. **Backward Compatible**: All TASK-053 tests still pass
7. **Performance**: Telemetry overhead < 5ms per match

---

## Documentation Updates Required

After implementing, update:

| File | What to Update |
|------|----------------|
| `_docs/_TASKS/TASK-054_Ensemble_Matcher_Enhancements.md` | Mark sub-tasks as Done |
| `_docs/_TASKS/README.md` | Move to Done, update statistics |
| `_docs/_CHANGELOG/{NN}-{date}-ensemble-enhancements.md` | Create changelog entry |
| `_docs/_ROUTER/README.md` | Update component status |
| `_docs/_ROUTER/IMPLEMENTATION/35-ensemble-enhancements.md` | Create implementation doc |
| `README.md` | Update Router Supervisor section |

---

## Related Tasks

- [TASK-053](./TASK-053_Ensemble_Matcher_System.md) - Base Ensemble Matcher (prerequisite)
- [TASK-046](./TASK-046_Router_Semantic_Generalization.md) - Semantic matching foundation
- [TASK-047](./TASK-047_Migration_Router_Semantic_Search_To_LanceDB.md) - LanceDB migration

---

## References

- Python asyncio: https://docs.python.org/3/library/asyncio.html
- Prometheus metrics format: https://prometheus.io/docs/concepts/data_model/
- Thread pool executor: https://docs.python.org/3/library/concurrent.futures.html
