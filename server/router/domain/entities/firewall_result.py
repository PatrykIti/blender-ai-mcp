"""
Firewall Result Entity.

Data class for firewall validation results.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


class FirewallAction(Enum):
    """Actions the firewall can take."""

    ALLOW = "allow"  # Let the call through unchanged
    BLOCK = "block"  # Block the call entirely
    MODIFY = "modify"  # Modify parameters
    AUTO_FIX = "auto_fix"  # Auto-fix issues (e.g., mode switch)


class FirewallRuleType(Enum):
    """Types of firewall rules."""

    MODE_VIOLATION = "mode_violation"
    SELECTION_REQUIRED = "selection_required"
    PARAMETER_OUT_OF_RANGE = "parameter_out_of_range"
    OBJECT_NOT_FOUND = "object_not_found"
    INVALID_OPERATION = "invalid_operation"
    DESTRUCTIVE_WARNING = "destructive_warning"


@dataclass
class FirewallViolation:
    """Represents a single firewall rule violation.

    Attributes:
        rule_type: Type of rule that was violated.
        message: Human-readable description.
        severity: Severity level (error, warning, info).
        can_auto_fix: Whether this can be automatically fixed.
        fix_description: Description of the auto-fix if applicable.
    """

    rule_type: FirewallRuleType
    message: str
    severity: str = "error"
    can_auto_fix: bool = False
    fix_description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule_type": self.rule_type.value,
            "message": self.message,
            "severity": self.severity,
            "can_auto_fix": self.can_auto_fix,
            "fix_description": self.fix_description,
        }


@dataclass
class FirewallResult:
    """Result of firewall validation.

    Attributes:
        allowed: Whether the call is allowed to proceed.
        action: Action taken by the firewall.
        violations: List of violations detected.
        modified_call: Modified tool call if action is MODIFY or AUTO_FIX.
        pre_steps: Additional tool calls to execute before (e.g., mode switch).
        message: Summary message for logging.
    """

    allowed: bool
    action: FirewallAction
    violations: List[FirewallViolation] = field(default_factory=list)
    modified_call: Optional[Dict[str, Any]] = None
    pre_steps: List[Dict[str, Any]] = field(default_factory=list)
    message: str = ""

    @property
    def has_violations(self) -> bool:
        """Check if any violations were detected."""
        return len(self.violations) > 0

    @property
    def was_modified(self) -> bool:
        """Check if the call was modified."""
        return self.action in (FirewallAction.MODIFY, FirewallAction.AUTO_FIX)

    @property
    def needs_pre_steps(self) -> bool:
        """Check if pre-steps are required."""
        return len(self.pre_steps) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "allowed": self.allowed,
            "action": self.action.value,
            "violations": [v.to_dict() for v in self.violations],
            "modified_call": self.modified_call,
            "pre_steps": self.pre_steps,
            "message": self.message,
        }

    @classmethod
    def allow(cls) -> "FirewallResult":
        """Create an allow result."""
        return cls(
            allowed=True,
            action=FirewallAction.ALLOW,
            message="Validation passed",
        )

    @classmethod
    def block(cls, message: str, violations: List[FirewallViolation] = None) -> "FirewallResult":
        """Create a block result."""
        return cls(
            allowed=False,
            action=FirewallAction.BLOCK,
            violations=violations or [],
            message=message,
        )

    @classmethod
    def auto_fix(
        cls,
        message: str,
        modified_call: Dict[str, Any] = None,
        pre_steps: List[Dict[str, Any]] = None,
        violations: List[FirewallViolation] = None,
    ) -> "FirewallResult":
        """Create an auto-fix result."""
        return cls(
            allowed=True,
            action=FirewallAction.AUTO_FIX,
            violations=violations or [],
            modified_call=modified_call,
            pre_steps=pre_steps or [],
            message=message,
        )

    @classmethod
    def modify(
        cls,
        message: str,
        modified_call: Dict[str, Any],
        violations: List[FirewallViolation] = None,
    ) -> "FirewallResult":
        """Create a modify result."""
        return cls(
            allowed=True,
            action=FirewallAction.MODIFY,
            violations=violations or [],
            modified_call=modified_call,
            message=message,
        )
