"""
Predefined Workflows Module.

Contains workflow definitions for common modeling patterns.
"""

from .base import BaseWorkflow, WorkflowDefinition, WorkflowStep
from .phone_workflow import PhoneWorkflow, phone_workflow
from .tower_workflow import TowerWorkflow, tower_workflow
from .screen_cutout_workflow import ScreenCutoutWorkflow, screen_cutout_workflow
from .registry import WorkflowRegistry, get_workflow_registry

__all__ = [
    # Base classes
    "BaseWorkflow",
    "WorkflowDefinition",
    "WorkflowStep",
    # Workflow classes
    "PhoneWorkflow",
    "TowerWorkflow",
    "ScreenCutoutWorkflow",
    # Singleton instances
    "phone_workflow",
    "tower_workflow",
    "screen_cutout_workflow",
    # Registry
    "WorkflowRegistry",
    "get_workflow_registry",
]
