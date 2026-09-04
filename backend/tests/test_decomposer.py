from app.orchestrator.decomposer import decompose


def test_keyword_match_routes_to_matching_agents():
    plans = decompose("What is the remote work policy document?")
    agent_types = [p.agent_type for p in plans]
    assert "rag" in agent_types
    assert agent_types[-1] == "validation"  # trailing validation subtask always present


def test_multiple_keyword_matches_produce_multiple_subtasks():
    plans = decompose("Who has permission to view the security access report?")
    agent_types = {p.agent_type for p in plans}
    assert "security" in agent_types
    assert "analytics" in agent_types
    assert "validation" in agent_types


def test_no_keyword_match_falls_back_to_workflow():
    plans = decompose("xyzzy plugh")
    agent_types = [p.agent_type for p in plans]
    assert agent_types == ["workflow", "validation"]


def test_every_plan_carries_original_text():
    text = "Generate a headcount report for Engineering"
    plans = decompose(text)
    assert all(p.description == text for p in plans)
