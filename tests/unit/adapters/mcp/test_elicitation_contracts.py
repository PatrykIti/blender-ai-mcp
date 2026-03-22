"""Tests for MCP elicitation contract mapping."""

from __future__ import annotations

from server.adapters.mcp.elicitation_contracts import (
    build_clarification_plan,
    build_elicitation_response_type,
    build_fallback_payload,
    coerce_elicitation_answers,
)


def test_clarification_plan_maps_router_unresolved_fields():
    """Router unresolved payloads should map into a stable clarification plan."""

    plan = build_clarification_plan(
        goal="chair",
        workflow_name="chair_workflow",
        unresolved_fields=[
            {
                "param": "leg_style",
                "type": "string",
                "description": "Leg style",
                "enum": ["straight", "angled"],
                "default": "straight",
                "context": "chair legs",
            }
        ],
    )

    assert plan.workflow_name == "chair_workflow"
    assert plan.requirements[0].field_name == "leg_style"
    assert plan.requirements[0].choices == ("straight", "angled")


def test_fallback_payload_and_dynamic_response_type_are_stable():
    """The same clarification plan should drive fallback payloads and native elicitation schemas."""

    plan = build_clarification_plan(
        goal="chair",
        workflow_name="chair_workflow",
        unresolved_fields=[
            {
                "param": "height",
                "type": "float",
                "description": "Overall height",
                "default": 1.0,
            }
        ],
    )

    payload = build_fallback_payload(plan)
    response_type = build_elicitation_response_type(plan)
    answers = response_type(height=1.2)

    assert payload.fields[0].field_name == "height"
    assert payload.question_set_id.startswith("qs_")
    assert coerce_elicitation_answers(answers) == {"height": 1.2}
