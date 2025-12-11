"""
Unit tests for ConditionEvaluator parentheses support.

Tests TASK-056-2: Parentheses support and operator precedence
"""

import pytest
from server.router.application.evaluator.condition_evaluator import ConditionEvaluator


class TestParenthesesSupport:
    """Test TASK-056-2: Parentheses and operator precedence."""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator with test context."""
        ev = ConditionEvaluator()
        ev.set_context({
            "A": True,
            "B": False,
            "C": True,
            "D": False,
            "E": True,
        })
        return ev

    def test_simple_parentheses(self, evaluator):
        """Test basic parentheses grouping."""
        # (A and B) or C = (True and False) or True = True
        assert evaluator.evaluate("(A and B) or C") is True

        # A and (B or C) = True and (False or True) = True
        assert evaluator.evaluate("A and (B or C)") is True

    def test_operator_precedence_without_parentheses(self, evaluator):
        """Test correct operator precedence: not > and > or."""
        # A or B and C = A or (B and C) = True or False = True
        assert evaluator.evaluate("A or B and C") is True

        # not A or B = (not A) or B = False or False = False
        assert evaluator.evaluate("not A or B") is False

        # not A and B = (not A) and B = False and False = False
        assert evaluator.evaluate("not A and B") is False

    def test_parentheses_override_precedence(self, evaluator):
        """Test that parentheses override default precedence."""
        # (A or B) and C = (True or False) and True = True
        assert evaluator.evaluate("(A or B) and C") is True

        # A or (B and C) = True or (False and True) = True
        assert evaluator.evaluate("A or (B and C)") is True

        # not (A or B) = not (True or False) = not True = False
        assert evaluator.evaluate("not (A or B)") is False

    def test_nested_parentheses(self, evaluator):
        """Test nested parentheses."""
        # ((A and B) or C) and D = ((True and False) or True) and False = False
        assert evaluator.evaluate("((A and B) or C) and D") is False

        # A and (B or (C and D)) = True and (False or (True and False)) = False
        assert evaluator.evaluate("A and (B or (C and D))") is False

        # (A or (B and C)) and (D or E) = (True or False) and (False or True) = True
        assert evaluator.evaluate("(A or (B and C)) and (D or E)") is True

    def test_complex_expression(self, evaluator):
        """Test complex expression with multiple operators and parentheses."""
        # (A and B) or (C and D) or E
        # = (True and False) or (True and False) or True
        # = False or False or True = True
        assert evaluator.evaluate("(A and B) or (C and D) or E") is True

        # not ((A or B) and (C or D))
        # = not ((True or False) and (True or False))
        # = not (True and True) = not True = False
        assert evaluator.evaluate("not ((A or B) and (C or D))") is False

    def test_multiple_and_operators(self, evaluator):
        """Test multiple AND operators in sequence."""
        # A and C and E = True and True and True = True
        assert evaluator.evaluate("A and C and E") is True

        # A and B and C = True and False and True = False
        assert evaluator.evaluate("A and B and C") is False

    def test_multiple_or_operators(self, evaluator):
        """Test multiple OR operators in sequence."""
        # B or D or A = False or False or True = True
        assert evaluator.evaluate("B or D or A") is True

        # B or D = False or False = False
        assert evaluator.evaluate("B or D") is False

    def test_mixed_operators_with_parentheses(self, evaluator):
        """Test mixed operators with various parentheses combinations."""
        # (A or B) and (C or D) = (True or False) and (True or False) = True
        assert evaluator.evaluate("(A or B) and (C or D)") is True

        # not (A and B) or C = not (True and False) or True = True or True = True
        assert evaluator.evaluate("not (A and B) or C") is True

        # (not A) and (not B) = False and True = False
        assert evaluator.evaluate("(not A) and (not B)") is False

    def test_parentheses_with_comparisons(self, evaluator):
        """Test parentheses with comparison operators."""
        ev = ConditionEvaluator()
        ev.set_context({
            "x": 5,
            "y": 10,
            "z": 3,
        })

        # (x > z) and (y > x) = (5 > 3) and (10 > 5) = True and True = True
        assert ev.evaluate("(x > z) and (y > x)") is True

        # (x > y) or (z < x) = (5 > 10) or (3 < 5) = False or True = True
        assert ev.evaluate("(x > y) or (z < x)") is True

        # not (x > y) = not (5 > 10) = not False = True
        assert ev.evaluate("not (x > y)") is True

    def test_whitespace_handling(self, evaluator):
        """Test that whitespace doesn't affect evaluation."""
        # Test with various whitespace patterns
        assert evaluator.evaluate("(A and B)or C") is True
        assert evaluator.evaluate("( A and B ) or C") is True
        assert evaluator.evaluate("(  A  and  B  )  or  C") is True

    def test_empty_parentheses_invalid(self, evaluator):
        """Test that empty parentheses are handled gracefully."""
        # This should fail-open (return True)
        result = evaluator.evaluate("()")
        assert result is True  # Fail-open behavior


class TestOperatorPrecedence:
    """Test operator precedence rules."""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator with test context."""
        ev = ConditionEvaluator()
        ev.set_context({
            "T": True,
            "F": False,
        })
        return ev

    def test_not_has_highest_precedence(self, evaluator):
        """Test that NOT has highest precedence."""
        # not T and F = (not T) and F = False and False = False
        assert evaluator.evaluate("not T and F") is False

        # not T or F = (not T) or F = False or False = False
        assert evaluator.evaluate("not T or F") is False

    def test_and_before_or(self, evaluator):
        """Test that AND has higher precedence than OR."""
        # T or F and F = T or (F and F) = T or F = True
        assert evaluator.evaluate("T or F and F") is True

        # F and F or T = (F and F) or T = F or T = True
        assert evaluator.evaluate("F and F or T") is True

    def test_precedence_chain(self, evaluator):
        """Test full precedence chain: () > not > and > or."""
        # not T and F or T
        # = (not T) and F or T    (not highest)
        # = (False and F) or T    (and higher than or)
        # = False or T = True
        assert evaluator.evaluate("not T and F or T") is True

        # (not T and F) or T = (False and False) or True = True
        assert evaluator.evaluate("(not T and F) or T") is True

        # not (T and F) or T = not (True and False) or True = True or True = True
        assert evaluator.evaluate("not (T and F) or T") is True

        # not (T and F or T)
        # = not ((T and F) or T)  (and before or)
        # = not (False or True) = not True = False
        assert evaluator.evaluate("not (T and F or T)") is False
