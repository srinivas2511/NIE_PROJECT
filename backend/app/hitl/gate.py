CONFIDENCE_THRESHOLD = 0.5
SENSITIVE_AGENT_TYPES = {"workflow"}  # performs real actions, not just reporting


def requires_approval(agent_type: str, confidence: float, sensitive: bool) -> tuple[bool, str | None]:
    """FR-7: route sensitive or low-confidence operations to Human-in-the-Loop
    approval before completion, instead of auto-completing."""
    if agent_type in SENSITIVE_AGENT_TYPES:
        return True, f"agent type '{agent_type}' is inherently sensitive (performs real actions)"
    if sensitive:
        return True, "this operation touched sensitive/restricted enterprise data"
    if confidence < CONFIDENCE_THRESHOLD:
        return (
            True,
            f"confidence {confidence:.0%} is below the {CONFIDENCE_THRESHOLD:.0%} approval threshold",
        )
    return False, None
