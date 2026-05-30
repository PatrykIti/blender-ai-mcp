def test_consolidate_authoritative_next_actions_ranks_and_dedupes():
    from server.adapters.mcp.areas.reference_feedback import _consolidate_authoritative_next_actions
    from server.adapters.mcp.contracts.reference import ReferenceCompactRepairContract

    actions = _consolidate_authoritative_next_actions(
        next_actions=["Run reference_compare_stage_checkpoint", "Round the head"],
        correction_focus=[
            "head silhouette",
            "Round the head",
        ],  # 2nd dups a next_action after prefixing? no -> distinct
        recommended_support_tools=["scene_measure_dimensions"],
        recommended_repair=ReferenceCompactRepairContract(tool_name="macro_finish_form", reason="seam gap"),
    )
    # Deterministic next_actions lead, in order.
    assert actions[0] == "Run reference_compare_stage_checkpoint"
    assert actions[1] == "Round the head"
    # correction_focus is prefixed and appended.
    assert "Address mismatch: head silhouette" in actions
    # repair + support tool included.
    assert any(a.startswith("Run repair macro_finish_form") for a in actions)
    assert "Run support check scene_measure_dimensions" in actions
    # No case-insensitive duplicates.
    lowered = [a.lower() for a in actions]
    assert len(lowered) == len(set(lowered))


def test_consolidate_authoritative_next_actions_is_bounded_and_handles_empties():
    from server.adapters.mcp.areas.reference_feedback import _consolidate_authoritative_next_actions

    assert (
        _consolidate_authoritative_next_actions(
            next_actions=[], correction_focus=[], recommended_support_tools=[], recommended_repair=None
        )
        == []
    )
    many = _consolidate_authoritative_next_actions(
        next_actions=[f"step {i}" for i in range(20)],
        correction_focus=[],
        recommended_support_tools=[],
        recommended_repair=None,
        max_items=6,
    )
    assert len(many) == 6
