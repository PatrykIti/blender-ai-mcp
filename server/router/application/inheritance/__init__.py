"""
Proportion Inheritance Module.

Enables workflows to inherit and combine proportion rules.
TASK-046-4
"""

from server.router.application.inheritance.proportion_inheritance import (
    InheritedProportions,
    ProportionInheritance,
    ProportionRule,
)

__all__ = [
    "ProportionInheritance",
    "ProportionRule",
    "InheritedProportions",
]
