"""
Feedback Collector.

Collects user feedback to improve workflow matching over time.
Stores:
- Prompt -> Workflow mappings (correct matches)
- Failed matches (for improvement)
- User corrections

TASK-046-6
"""

import json
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class FeedbackEntry:
    """Single feedback entry.

    Attributes:
        timestamp: ISO timestamp of the entry.
        prompt: User prompt that triggered matching.
        matched_workflow: Workflow that was matched (or None).
        match_confidence: Confidence score of the match.
        match_type: Type of match (exact, semantic, generalized, none).
        user_correction: Correct workflow if user provided correction.
        was_helpful: Whether the match was helpful (user feedback).
        metadata: Additional metadata.
    """

    timestamp: str
    prompt: str
    matched_workflow: Optional[str]
    match_confidence: float
    match_type: str  # exact, semantic, generalized, none, correction
    user_correction: Optional[str] = None
    was_helpful: Optional[bool] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedbackEntry":
        """Create from dictionary."""
        return cls(**data)


class FeedbackCollector:
    """Collects and stores feedback for learning.

    Feedback is used to:
    1. Add new sample_prompts to workflows
    2. Adjust similarity thresholds
    3. Identify gaps in workflow coverage

    Example:
        ```python
        collector = FeedbackCollector()

        # Record a match
        collector.record_match(
            prompt="create a dining table",
            matched_workflow="table_workflow",
            confidence=0.85,
            match_type="semantic",
        )

        # User corrects a wrong match
        collector.record_correction(
            prompt="create a stool",
            original_match="table_workflow",
            correct_workflow="chair_workflow",
        )

        # Get suggestions for new sample prompts
        new_prompts = collector.get_new_sample_prompts("chair_workflow")
        # Returns: ["create a stool"] (if corrected 3+ times)
        ```
    """

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        max_entries: int = 10000,
        auto_save: bool = True,
    ):
        """Initialize collector.

        Args:
            storage_path: Path to feedback storage file.
                         Defaults to ~/.blender-mcp/feedback.jsonl
            max_entries: Maximum entries to keep in memory and storage.
            auto_save: Whether to auto-save after each entry.
        """
        self._storage_path = storage_path or (
            Path.home() / ".blender-mcp" / "feedback.jsonl"
        )
        self._max_entries = max_entries
        self._auto_save = auto_save
        self._entries: List[FeedbackEntry] = []
        self._is_dirty = False

        self._load()

    def _load(self) -> None:
        """Load existing feedback from storage."""
        if not self._storage_path.exists():
            logger.debug(f"Feedback file not found: {self._storage_path}")
            return

        try:
            with open(self._storage_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        self._entries.append(FeedbackEntry.from_dict(data))
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse feedback line: {e}")

            logger.info(f"Loaded {len(self._entries)} feedback entries")

        except Exception as e:
            logger.warning(f"Failed to load feedback: {e}")

    def _save(self) -> None:
        """Save feedback to storage."""
        if not self._is_dirty:
            return

        try:
            # Ensure directory exists
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Keep only max entries
            entries_to_save = self._entries[-self._max_entries :]

            with open(self._storage_path, "w", encoding="utf-8") as f:
                for entry in entries_to_save:
                    f.write(json.dumps(entry.to_dict()) + "\n")

            self._is_dirty = False
            logger.debug(f"Saved {len(entries_to_save)} feedback entries")

        except Exception as e:
            logger.warning(f"Failed to save feedback: {e}")

    def record_match(
        self,
        prompt: str,
        matched_workflow: Optional[str],
        confidence: float,
        match_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FeedbackEntry:
        """Record a workflow match.

        Call this whenever the router matches a prompt to a workflow.
        This data helps improve future matching.

        Args:
            prompt: User prompt that triggered matching.
            matched_workflow: Workflow that was matched (or None if no match).
            confidence: Match confidence score (0.0 to 1.0).
            match_type: Type of match (exact, semantic, generalized, none).
            metadata: Additional metadata (e.g., similar_workflows).

        Returns:
            The created FeedbackEntry.
        """
        entry = FeedbackEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            prompt=prompt,
            matched_workflow=matched_workflow,
            match_confidence=confidence,
            match_type=match_type,
            user_correction=None,
            was_helpful=None,
            metadata=metadata or {},
        )

        self._entries.append(entry)
        self._is_dirty = True

        if self._auto_save:
            self._save()

        logger.debug(
            f"Recorded match: {prompt[:30]}... -> {matched_workflow} "
            f"({match_type}, {confidence:.1%})"
        )

        return entry

    def record_correction(
        self,
        prompt: str,
        original_match: Optional[str],
        correct_workflow: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FeedbackEntry:
        """Record user correction.

        Call this when the user indicates a different workflow should
        have been matched. This is valuable learning data.

        Args:
            prompt: Original prompt.
            original_match: What the router matched (or None).
            correct_workflow: What should have matched.
            metadata: Additional metadata.

        Returns:
            The created or updated FeedbackEntry.
        """
        # Try to find and update existing entry
        for entry in reversed(self._entries):
            if entry.prompt == prompt and entry.matched_workflow == original_match:
                entry.user_correction = correct_workflow
                entry.was_helpful = False
                self._is_dirty = True

                if self._auto_save:
                    self._save()

                logger.info(
                    f"Recorded correction: {prompt[:30]}... "
                    f"{original_match} -> {correct_workflow}"
                )
                return entry

        # Create new correction entry if not found
        entry = FeedbackEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            prompt=prompt,
            matched_workflow=original_match,
            match_confidence=0.0,
            match_type="correction",
            user_correction=correct_workflow,
            was_helpful=False,
            metadata=metadata or {},
        )

        self._entries.append(entry)
        self._is_dirty = True

        if self._auto_save:
            self._save()

        logger.info(
            f"Recorded new correction: {prompt[:30]}... -> {correct_workflow}"
        )

        return entry

    def record_helpful(
        self,
        prompt: str,
        matched_workflow: str,
        was_helpful: bool = True,
    ) -> bool:
        """Record whether a match was helpful.

        Call this when the user indicates whether the matched workflow
        was actually helpful for their task.

        Args:
            prompt: Original prompt.
            matched_workflow: Workflow that was matched.
            was_helpful: Whether the match was helpful.

        Returns:
            True if an entry was found and updated, False otherwise.
        """
        for entry in reversed(self._entries):
            if entry.prompt == prompt and entry.matched_workflow == matched_workflow:
                entry.was_helpful = was_helpful
                self._is_dirty = True

                if self._auto_save:
                    self._save()

                logger.debug(
                    f"Recorded helpful={was_helpful}: {prompt[:30]}... "
                    f"-> {matched_workflow}"
                )
                return True

        return False

    def get_new_sample_prompts(
        self,
        workflow_name: str,
        min_corrections: int = 3,
    ) -> List[str]:
        """Get prompts that should be added as sample_prompts.

        Returns prompts that were corrected to this workflow multiple times.
        These are good candidates for adding to the workflow's sample_prompts
        to improve future matching.

        Args:
            workflow_name: Workflow to get prompts for.
            min_corrections: Minimum corrections needed to include a prompt.

        Returns:
            List of prompts to add.
        """
        prompt_counts: Dict[str, int] = {}

        for entry in self._entries:
            if entry.user_correction == workflow_name:
                prompt_counts[entry.prompt] = prompt_counts.get(entry.prompt, 0) + 1

        return [
            prompt
            for prompt, count in prompt_counts.items()
            if count >= min_corrections
        ]

    def get_failed_matches(
        self,
        limit: int = 100,
    ) -> List[FeedbackEntry]:
        """Get entries where no workflow was matched.

        These represent gaps in workflow coverage.

        Args:
            limit: Maximum entries to return.

        Returns:
            List of entries with no match.
        """
        failed = [
            entry
            for entry in reversed(self._entries)
            if entry.match_type == "none" or entry.matched_workflow is None
        ]
        return failed[:limit]

    def get_low_confidence_matches(
        self,
        max_confidence: float = 0.5,
        limit: int = 100,
    ) -> List[FeedbackEntry]:
        """Get entries with low confidence matches.

        These might benefit from additional sample_prompts.

        Args:
            max_confidence: Maximum confidence threshold.
            limit: Maximum entries to return.

        Returns:
            List of low-confidence entries.
        """
        low_conf = [
            entry
            for entry in reversed(self._entries)
            if entry.match_confidence <= max_confidence
            and entry.matched_workflow is not None
        ]
        return low_conf[:limit]

    def get_corrections_for_workflow(
        self,
        workflow_name: str,
    ) -> List[FeedbackEntry]:
        """Get all corrections pointing to a workflow.

        Args:
            workflow_name: Workflow name.

        Returns:
            List of correction entries.
        """
        return [
            entry
            for entry in self._entries
            if entry.user_correction == workflow_name
        ]

    def get_corrections_from_workflow(
        self,
        workflow_name: str,
    ) -> List[FeedbackEntry]:
        """Get all corrections away from a workflow.

        These indicate when a workflow was incorrectly matched.

        Args:
            workflow_name: Workflow name.

        Returns:
            List of correction entries.
        """
        return [
            entry
            for entry in self._entries
            if entry.matched_workflow == workflow_name
            and entry.user_correction is not None
            and entry.user_correction != workflow_name
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """Get feedback statistics.

        Returns:
            Dictionary with statistics.
        """
        total = len(self._entries)
        if total == 0:
            return {
                "total_entries": 0,
                "corrections": 0,
                "correction_rate": 0.0,
                "helpful_rate": 0.0,
                "by_match_type": {},
                "avg_confidence": 0.0,
            }

        corrections = sum(1 for e in self._entries if e.user_correction is not None)

        helpful_entries = [e for e in self._entries if e.was_helpful is not None]
        helpful_true = sum(1 for e in helpful_entries if e.was_helpful)

        by_type: Dict[str, int] = {}
        for e in self._entries:
            by_type[e.match_type] = by_type.get(e.match_type, 0) + 1

        confidences = [e.match_confidence for e in self._entries]
        avg_confidence = sum(confidences) / len(confidences)

        return {
            "total_entries": total,
            "corrections": corrections,
            "correction_rate": corrections / total if total > 0 else 0.0,
            "helpful_entries": len(helpful_entries),
            "helpful_rate": helpful_true / len(helpful_entries)
            if helpful_entries
            else 0.0,
            "by_match_type": by_type,
            "avg_confidence": avg_confidence,
        }

    def get_workflow_statistics(
        self,
        workflow_name: str,
    ) -> Dict[str, Any]:
        """Get statistics for a specific workflow.

        Args:
            workflow_name: Workflow name.

        Returns:
            Dictionary with workflow-specific statistics.
        """
        matches = [
            e for e in self._entries if e.matched_workflow == workflow_name
        ]
        corrections_to = self.get_corrections_for_workflow(workflow_name)
        corrections_from = self.get_corrections_from_workflow(workflow_name)

        if not matches:
            return {
                "workflow_name": workflow_name,
                "total_matches": 0,
                "corrections_to": len(corrections_to),
                "corrections_from": len(corrections_from),
            }

        confidences = [e.match_confidence for e in matches]
        helpful = [e for e in matches if e.was_helpful is not None]

        return {
            "workflow_name": workflow_name,
            "total_matches": len(matches),
            "avg_confidence": sum(confidences) / len(confidences),
            "min_confidence": min(confidences),
            "max_confidence": max(confidences),
            "corrections_to": len(corrections_to),
            "corrections_from": len(corrections_from),
            "helpful_count": sum(1 for e in helpful if e.was_helpful),
            "unhelpful_count": sum(1 for e in helpful if not e.was_helpful),
        }

    def clear(self) -> None:
        """Clear all feedback entries.

        Warning: This deletes all stored feedback data.
        """
        self._entries.clear()
        self._is_dirty = True
        self._save()
        logger.info("Cleared all feedback entries")

    def export_for_training(
        self,
        output_path: Optional[Path] = None,
    ) -> Dict[str, List[str]]:
        """Export corrections as training data.

        Returns prompts grouped by their corrected workflow,
        suitable for adding to sample_prompts.

        Args:
            output_path: Optional path to save JSON export.

        Returns:
            Dict of workflow_name -> list of prompts.
        """
        training_data: Dict[str, List[str]] = {}

        for entry in self._entries:
            if entry.user_correction:
                workflow = entry.user_correction
                if workflow not in training_data:
                    training_data[workflow] = []
                if entry.prompt not in training_data[workflow]:
                    training_data[workflow].append(entry.prompt)

        if output_path:
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(training_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Exported training data to {output_path}")
            except Exception as e:
                logger.warning(f"Failed to export training data: {e}")

        return training_data

    def get_entries(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[FeedbackEntry]:
        """Get recent entries with pagination.

        Args:
            limit: Maximum entries to return.
            offset: Number of entries to skip from the end.

        Returns:
            List of entries.
        """
        if offset >= len(self._entries):
            return []

        start = max(0, len(self._entries) - offset - limit)
        end = len(self._entries) - offset

        return self._entries[start:end]

    def save(self) -> None:
        """Manually save feedback to storage."""
        self._is_dirty = True
        self._save()

    def get_info(self) -> Dict[str, Any]:
        """Get collector information.

        Returns:
            Dictionary with collector info.
        """
        return {
            "storage_path": str(self._storage_path),
            "max_entries": self._max_entries,
            "current_entries": len(self._entries),
            "auto_save": self._auto_save,
            "statistics": self.get_statistics(),
        }
