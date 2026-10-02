from logic_engine import KnowledgeBase


def test_safe_case():
    """
    Test Case 1:
    TargetVisible + HasDust
    should derive SafeToEngage
    but should NOT derive Retreat.
    """

    kb = KnowledgeBase()

    # Add facts
    kb.tell_fact("TargetVisible")
    kb.tell_fact("HasDust")

    # Add rules
    kb.tell_rule(
        ["TargetVisible", "HasDust"],
        "SafeToEngage"
    )

    kb.tell_rule(
        ["SafeToEngage", "BloodseekerMissing"],
        "Retreat"
    )

    # Run forward chaining
    kb.forward_chain()

    # Expected results
    assert "SafeToEngage" in kb.facts
    assert "Retreat" not in kb.facts


def test_unsafe_case():
    """
    Test Case 2:
    TargetVisible + HasDust + BloodseekerMissing
    should derive both SafeToEngage and Retreat.
    """

    kb = KnowledgeBase()

    # Add facts
    kb.tell_fact("TargetVisible")
    kb.tell_fact("HasDust")
    kb.tell_fact("BloodseekerMissing")

    # Add rules
    kb.tell_rule(
        ["TargetVisible", "HasDust"],
        "SafeToEngage"
    )

    kb.tell_rule(
        ["SafeToEngage", "BloodseekerMissing"],
        "Retreat"
    )

    # Run forward chaining
    kb.forward_chain()

    # Expected results
    assert "SafeToEngage" in kb.facts
    assert "Retreat" in kb.facts


if __name__ == "__main__":
    test_safe_case()
    test_unsafe_case()

    print("All Logic Engine Test Cases Passed!")