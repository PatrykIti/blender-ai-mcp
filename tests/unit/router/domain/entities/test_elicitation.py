"""Tests for domain-neutral clarification plan entities."""

from server.router.domain.entities.elicitation import (
    ClarificationPlan,
    ClarificationRequirement,
)


def test_clarification_requirement_and_plan_are_serializable_domain_models():
    """Clarification entities should stay MCP-neutral and domain-serializable."""

    requirement = ClarificationRequirement(
        field_name="height",
        prompt="Overall height in meters",
        value_type="float",
        default=1.0,
    )
    plan = ClarificationPlan(
        goal="chair",
        workflow_name="chair_workflow",
        requirements=(requirement,),
    )

    assert plan.goal == "chair"
    assert plan.workflow_name == "chair_workflow"
    assert plan.requirements[0].field_name == "height"
    assert plan.is_empty is False
