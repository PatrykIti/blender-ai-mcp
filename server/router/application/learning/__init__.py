"""
Feedback Learning Module.

Collects and learns from user feedback to improve workflow matching.
TASK-046-6
"""

from server.router.application.learning.feedback_collector import (
    FeedbackCollector,
    FeedbackEntry,
)

__all__ = [
    "FeedbackCollector",
    "FeedbackEntry",
]
