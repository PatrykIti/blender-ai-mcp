"""
Proportion Inheritance Module.

Enables workflows to inherit and combine proportion rules.
TASK-046-4
"""

from server.router.application.inheritance.proportion_inheritance import (
    ProportionInheritance,
    ProportionRule,
    InheritedProportions,
)

__all__ = [
    "ProportionInheritance",
    "ProportionRule",
    "InheritedProportions",
]
