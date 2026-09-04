"""Tests for shared macro-tool contracts."""

from server.adapters.mcp.contracts.macro import (
    MacroActionRecordContract,
    MacroExecutionReportContract,
    MacroVerificationRecommendationContract,
)
from server.adapters.mcp.contracts.output_schema import get_output_schema


def test_macro_execution_report_contract_supports_shared_macro_envelope():
    """Macro report contract should support bounded action and verification summaries."""

    report = MacroExecutionReportContract(
        status="needs_followup",
        macro_name="macro_cutout_recess",
        intent="Create a rounded screen recess on the front shell",
        actions_taken=[
            MacroActionRecordContract(
                status="applied",
                action="create_cutter",
                tool_name="modeling_create_primitive",
                summary="Created cube cutter",
            ),
            MacroActionRecordContract(
                status="applied",
                action="apply_boolean",
                tool_name="modeling_add_modifier",
                summary="Applied boolean difference",
            ),
        ],
        objects_created=["screen_recess_cutter"],
        objects_modified=["body_shell"],
        verification_recommended=[
            MacroVerificationRecommendationContract(
                tool_name="scene_measure_gap",
                reason="Confirm recess depth/contact against target front surface",
                priority="high",
            )
        ],
        requires_followup=True,
    )

    assert report.macro_name == "macro_cutout_recess"
    assert report.actions_taken[0].action == "create_cutter"
    assert report.verification_recommended[0].tool_name == "scene_measure_gap"
    assert report.requires_followup is True


def test_macro_execution_report_output_schema_is_machine_readable():
    """Macro report contract should expose a stable object schema for future macro tools."""

    schema = get_output_schema(MacroExecutionReportContract)

    assert schema["type"] == "object"
    assert "macro_name" in schema["properties"]
    assert "actions_taken" in schema["properties"]
    assert "verification_recommended" in schema["properties"]
