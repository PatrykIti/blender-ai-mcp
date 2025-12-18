"""
Tests for FeedbackCollector.

TASK-046-6
"""

import pytest
import json
from pathlib import Path
from datetime import datetime

from server.router.application.learning.feedback_collector import (
    FeedbackCollector,
    FeedbackEntry,
)


class TestFeedbackEntry:
    """Tests for FeedbackEntry dataclass."""

    def test_create_entry(self):
        """Test creating a feedback entry."""
        entry = FeedbackEntry(
            timestamp="2024-01-15T10:30:00",
            prompt="create a phone",
            matched_workflow="phone_workflow",
            match_confidence=0.85,
            match_type="semantic",
        )

        assert entry.prompt == "create a phone"
        assert entry.matched_workflow == "phone_workflow"
        assert entry.match_confidence == 0.85

    def test_to_dict(self):
        """Test converting entry to dict."""
        entry = FeedbackEntry(
            timestamp="2024-01-15T10:30:00",
            prompt="create a phone",
            matched_workflow="phone_workflow",
            match_confidence=0.85,
            match_type="semantic",
        )

        d = entry.to_dict()

        assert d["prompt"] == "create a phone"
        assert d["matched_workflow"] == "phone_workflow"
        assert d["match_type"] == "semantic"

    def test_from_dict(self):
        """Test creating entry from dict."""
        d = {
            "timestamp": "2024-01-15T10:30:00",
            "prompt": "create a phone",
            "matched_workflow": "phone_workflow",
            "match_confidence": 0.85,
            "match_type": "semantic",
            "user_correction": None,
            "was_helpful": None,
            "metadata": {},
        }

        entry = FeedbackEntry.from_dict(d)

        assert entry.prompt == "create a phone"
        assert entry.matched_workflow == "phone_workflow"


class TestFeedbackCollector:
    """Tests for FeedbackCollector class."""

    @pytest.fixture
    def collector(self, tmp_path):
        """Create collector with temp storage."""
        storage_path = tmp_path / "feedback.jsonl"
        return FeedbackCollector(storage_path=storage_path, auto_save=True)

    def test_init_creates_empty_collector(self, collector):
        """Test initialization creates empty collector."""
        assert len(collector._entries) == 0

    def test_record_match(self, collector):
        """Test recording a match."""
        entry = collector.record_match(
            prompt="create a phone",
            matched_workflow="phone_workflow",
            confidence=0.85,
            match_type="semantic",
        )

        assert entry.prompt == "create a phone"
        assert len(collector._entries) == 1

    def test_record_match_with_metadata(self, collector):
        """Test recording match with metadata."""
        entry = collector.record_match(
            prompt="create a phone",
            matched_workflow="phone_workflow",
            confidence=0.85,
            match_type="semantic",
            metadata={"similar": ["table_workflow"]},
        )

        assert entry.metadata["similar"] == ["table_workflow"]

    def test_record_correction_updates_existing(self, collector):
        """Test recording correction updates existing entry."""
        # First record a match
        collector.record_match(
            prompt="create a stool",
            matched_workflow="table_workflow",
            confidence=0.68,
            match_type="semantic",
        )

        # Then correct it
        entry = collector.record_correction(
            prompt="create a stool",
            original_match="table_workflow",
            correct_workflow="chair_workflow",
        )

        assert entry.user_correction == "chair_workflow"
        assert entry.was_helpful is False
        assert len(collector._entries) == 1  # Updated, not added

    def test_record_correction_creates_new(self, collector):
        """Test recording correction creates new entry if not found."""
        entry = collector.record_correction(
            prompt="create a stool",
            original_match=None,
            correct_workflow="chair_workflow",
        )

        assert entry.user_correction == "chair_workflow"
        assert entry.match_type == "correction"
        assert len(collector._entries) == 1

    def test_record_helpful(self, collector):
        """Test recording helpful feedback."""
        collector.record_match(
            prompt="create a phone",
            matched_workflow="phone_workflow",
            confidence=0.85,
            match_type="semantic",
        )

        result = collector.record_helpful(
            prompt="create a phone",
            matched_workflow="phone_workflow",
            was_helpful=True,
        )

        assert result is True
        assert collector._entries[0].was_helpful is True

    def test_record_helpful_not_found(self, collector):
        """Test recording helpful returns False if not found."""
        result = collector.record_helpful(
            prompt="unknown",
            matched_workflow="unknown",
            was_helpful=True,
        )

        assert result is False

    def test_get_new_sample_prompts(self, collector):
        """Test getting prompts for new sample_prompts."""
        # Record same prompt corrected 3 times (from different original matches)
        for i in range(3):
            collector.record_correction(
                prompt="zrób fotel",
                original_match=f"workflow_{i}",  # Different original to create separate entries
                correct_workflow="chair_workflow",
            )

        prompts = collector.get_new_sample_prompts("chair_workflow", min_corrections=3)

        assert "zrób fotel" in prompts

    def test_get_new_sample_prompts_below_threshold(self, collector):
        """Test that prompts below threshold are not returned."""
        # Record only 2 corrections
        for _ in range(2):
            collector.record_correction(
                prompt="zrób fotel",
                original_match=None,
                correct_workflow="chair_workflow",
            )

        prompts = collector.get_new_sample_prompts("chair_workflow", min_corrections=3)

        assert "zrób fotel" not in prompts

    def test_get_failed_matches(self, collector):
        """Test getting failed matches."""
        collector.record_match(
            prompt="create something weird",
            matched_workflow=None,
            confidence=0.0,
            match_type="none",
        )
        collector.record_match(
            prompt="create a phone",
            matched_workflow="phone_workflow",
            confidence=0.85,
            match_type="semantic",
        )

        failed = collector.get_failed_matches()

        assert len(failed) == 1
        assert failed[0].prompt == "create something weird"

    def test_get_low_confidence_matches(self, collector):
        """Test getting low confidence matches."""
        collector.record_match(
            prompt="create a phone",
            matched_workflow="phone_workflow",
            confidence=0.85,
            match_type="semantic",
        )
        collector.record_match(
            prompt="create a thing",
            matched_workflow="table_workflow",
            confidence=0.35,
            match_type="semantic",
        )

        low_conf = collector.get_low_confidence_matches(max_confidence=0.5)

        assert len(low_conf) == 1
        assert low_conf[0].prompt == "create a thing"

    def test_get_corrections_for_workflow(self, collector):
        """Test getting corrections to a workflow."""
        collector.record_correction(
            prompt="stool",
            original_match="table_workflow",
            correct_workflow="chair_workflow",
        )
        collector.record_correction(
            prompt="bench",
            original_match="table_workflow",
            correct_workflow="chair_workflow",
        )

        corrections = collector.get_corrections_for_workflow("chair_workflow")

        assert len(corrections) == 2

    def test_get_corrections_from_workflow(self, collector):
        """Test getting corrections away from a workflow."""
        collector.record_match(
            prompt="stool",
            matched_workflow="table_workflow",
            confidence=0.6,
            match_type="semantic",
        )
        collector.record_correction(
            prompt="stool",
            original_match="table_workflow",
            correct_workflow="chair_workflow",
        )

        corrections = collector.get_corrections_from_workflow("table_workflow")

        assert len(corrections) == 1

    def test_get_statistics_empty(self, collector):
        """Test statistics with empty collector."""
        stats = collector.get_statistics()

        assert stats["total_entries"] == 0
        assert stats["corrections"] == 0
        assert stats["correction_rate"] == 0.0

    def test_get_statistics_with_entries(self, collector):
        """Test statistics with entries."""
        collector.record_match(
            prompt="phone",
            matched_workflow="phone_workflow",
            confidence=0.85,
            match_type="semantic",
        )
        collector.record_match(
            prompt="table",
            matched_workflow="table_workflow",
            confidence=0.90,
            match_type="exact",
        )
        collector.record_correction(
            prompt="stool",
            original_match="table_workflow",
            correct_workflow="chair_workflow",
        )

        stats = collector.get_statistics()

        assert stats["total_entries"] == 3
        assert stats["corrections"] == 1
        assert "semantic" in stats["by_match_type"]
        assert "exact" in stats["by_match_type"]

    def test_get_workflow_statistics(self, collector):
        """Test workflow-specific statistics."""
        collector.record_match(
            prompt="phone 1",
            matched_workflow="phone_workflow",
            confidence=0.85,
            match_type="semantic",
        )
        collector.record_match(
            prompt="phone 2",
            matched_workflow="phone_workflow",
            confidence=0.90,
            match_type="exact",
        )

        stats = collector.get_workflow_statistics("phone_workflow")

        assert stats["workflow_name"] == "phone_workflow"
        assert stats["total_matches"] == 2
        assert stats["avg_confidence"] == 0.875

    def test_clear(self, collector):
        """Test clearing all entries."""
        collector.record_match(
            prompt="phone",
            matched_workflow="phone_workflow",
            confidence=0.85,
            match_type="semantic",
        )

        collector.clear()

        assert len(collector._entries) == 0

    def test_persistence(self, tmp_path):
        """Test that entries persist to disk."""
        storage_path = tmp_path / "feedback.jsonl"

        # Create and populate collector
        collector1 = FeedbackCollector(storage_path=storage_path, auto_save=True)
        collector1.record_match(
            prompt="phone",
            matched_workflow="phone_workflow",
            confidence=0.85,
            match_type="semantic",
        )

        # Create new collector from same file
        collector2 = FeedbackCollector(storage_path=storage_path, auto_save=True)

        assert len(collector2._entries) == 1
        assert collector2._entries[0].prompt == "phone"

    def test_export_for_training(self, collector):
        """Test exporting corrections as training data."""
        collector.record_correction(
            prompt="stool 1",
            original_match=None,
            correct_workflow="chair_workflow",
        )
        collector.record_correction(
            prompt="stool 2",
            original_match=None,
            correct_workflow="chair_workflow",
        )
        collector.record_correction(
            prompt="desk",
            original_match=None,
            correct_workflow="table_workflow",
        )

        training = collector.export_for_training()

        assert "chair_workflow" in training
        assert len(training["chair_workflow"]) == 2
        assert "table_workflow" in training
        assert len(training["table_workflow"]) == 1

    def test_get_entries_pagination(self, collector):
        """Test getting entries with pagination."""
        for i in range(10):
            collector.record_match(
                prompt=f"prompt {i}",
                matched_workflow="phone_workflow",
                confidence=0.5,
                match_type="semantic",
            )

        # Get last 3 entries
        entries = collector.get_entries(limit=3, offset=0)
        assert len(entries) == 3
        assert entries[-1].prompt == "prompt 9"

        # Get with offset
        entries = collector.get_entries(limit=3, offset=3)
        assert len(entries) == 3
        assert entries[-1].prompt == "prompt 6"

    def test_get_info(self, collector):
        """Test getting collector info."""
        info = collector.get_info()

        assert "storage_path" in info
        assert "max_entries" in info
        assert "current_entries" in info
        assert "auto_save" in info
        assert "statistics" in info
