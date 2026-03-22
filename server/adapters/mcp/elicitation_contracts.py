"""Adapter-layer clarification contracts and FastMCP elicitation mapping."""

from __future__ import annotations

from hashlib import sha1
from typing import Any, Literal

from pydantic import BaseModel, Field, create_model

from server.router.domain.entities.elicitation import (
    ClarificationPlan,
    ClarificationRequirement,
)


class ClarificationFieldPayload(BaseModel):
    """Serializable compatibility payload for one missing field."""

    field_id: str
    field_name: str
    prompt: str
    value_type: str
    required: bool = True
    choices: list[str] | None = None
    allows_multiple: bool = False
    default: Any | None = None
    context: str | None = None
    description: str | None = None
    error: str | None = None


class ClarificationFallbackPayload(BaseModel):
    """Typed `needs_input` payload for non-elicitation clients."""

    question_set_id: str
    goal: str
    workflow_name: str
    fields: list[ClarificationFieldPayload]


def _stable_field_id(workflow_name: str, field_name: str) -> str:
    digest = sha1(f"{workflow_name}:{field_name}".encode("utf-8")).hexdigest()[:10]
    return f"field_{digest}"


def build_clarification_plan(
    goal: str,
    workflow_name: str,
    unresolved_fields: list[dict[str, Any]],
) -> ClarificationPlan:
    """Build a domain-neutral clarification plan from router unresolved payloads."""

    requirements: list[ClarificationRequirement] = []
    for unresolved in unresolved_fields:
        choices = unresolved.get("enum")
        if choices is not None:
            choices = tuple(str(choice) for choice in choices)
        requirements.append(
            ClarificationRequirement(
                field_name=unresolved["param"],
                prompt=unresolved.get("description") or unresolved["param"],
                value_type=unresolved.get("type", "string"),
                required=True,
                choices=choices,
                allows_multiple=False,
                default=unresolved.get("default"),
                context=unresolved.get("context"),
                description=unresolved.get("description"),
                error=unresolved.get("error"),
            )
        )

    return ClarificationPlan(
        goal=goal,
        workflow_name=workflow_name,
        requirements=tuple(requirements),
    )


def build_fallback_payload(plan: ClarificationPlan) -> ClarificationFallbackPayload:
    """Build the typed `needs_input` fallback payload for non-elicitation surfaces."""

    question_set_hash = sha1(
        f"{plan.goal}:{plan.workflow_name}:{','.join(req.field_name for req in plan.requirements)}".encode(
            "utf-8"
        )
    ).hexdigest()[:12]
    return ClarificationFallbackPayload(
        question_set_id=f"qs_{question_set_hash}",
        goal=plan.goal,
        workflow_name=plan.workflow_name,
        fields=[
            ClarificationFieldPayload(
                field_id=_stable_field_id(plan.workflow_name, requirement.field_name),
                field_name=requirement.field_name,
                prompt=requirement.prompt,
                value_type=requirement.value_type,
                required=requirement.required,
                choices=list(requirement.choices) if requirement.choices is not None else None,
                allows_multiple=requirement.allows_multiple,
                default=requirement.default,
                context=requirement.context,
                description=requirement.description,
                error=requirement.error,
            )
            for requirement in plan.requirements
        ],
    )


def build_elicitation_response_type(plan: ClarificationPlan) -> type[BaseModel]:
    """Build a dynamic Pydantic model accepted by `ctx.elicit(...)`."""

    model_fields: dict[str, tuple[Any, Any]] = {}

    for requirement in plan.requirements:
        field_type: Any
        choices = requirement.choices
        if choices:
            field_type = Literal.__getitem__(choices)
        elif requirement.value_type == "float":
            field_type = float
        elif requirement.value_type == "int":
            field_type = int
        elif requirement.value_type == "bool":
            field_type = bool
        else:
            field_type = str

        model_fields[requirement.field_name] = (
            field_type,
            Field(
                ...,
                description=requirement.description or requirement.prompt,
                examples=[requirement.default] if requirement.default is not None else None,
            ),
        )

    model_name = f"{plan.workflow_name.title().replace('_', '')}ClarificationAnswers"
    return create_model(model_name, **model_fields)  # type: ignore[call-arg]


def coerce_elicitation_answers(data: Any) -> dict[str, Any]:
    """Normalize accepted elicitation data into a plain dict."""

    if hasattr(data, "model_dump"):
        return data.model_dump()
    if isinstance(data, dict):
        return data
    raise TypeError(f"Unsupported elicitation answer payload: {type(data).__name__}")
