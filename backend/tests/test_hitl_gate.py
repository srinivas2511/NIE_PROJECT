from app.hitl.gate import CONFIDENCE_THRESHOLD, requires_approval


def test_sensitive_agent_type_always_flagged():
    flagged, reason = requires_approval("workflow", confidence=1.0, sensitive=False)
    assert flagged is True
    assert "Task Automation" in reason


def test_sensitive_data_flagged_regardless_of_confidence():
    flagged, reason = requires_approval("rag", confidence=1.0, sensitive=True)
    assert flagged is True
    assert "sensitive" in reason


def test_low_confidence_flagged():
    flagged, reason = requires_approval(
        "rag", confidence=CONFIDENCE_THRESHOLD - 0.01, sensitive=False
    )
    assert flagged is True
    assert "threshold" in reason


def test_high_confidence_non_sensitive_non_sensitive_agent_passes():
    flagged, reason = requires_approval("rag", confidence=CONFIDENCE_THRESHOLD, sensitive=False)
    assert flagged is False
    assert reason is None
