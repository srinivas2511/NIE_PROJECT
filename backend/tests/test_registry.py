import pytest

from app.agents.registry import AGENT_REGISTRY, get_agent, humanize_agent_type


@pytest.mark.parametrize("agent_type", ["rag", "security", "analytics", "workflow", "validation"])
def test_get_agent_returns_instance_with_matching_agent_type(agent_type):
    agent = get_agent(agent_type)
    assert agent.agent_type == agent_type


def test_get_agent_raises_for_unregistered_type():
    with pytest.raises(ValueError):
        get_agent("does_not_exist")


def test_registry_keys_match_each_agent_instance_agent_type():
    for agent_type, agent in AGENT_REGISTRY.items():
        assert agent.agent_type == agent_type


def test_humanize_agent_type_known_types():
    assert humanize_agent_type("rag") == "Knowledge Base"
    assert humanize_agent_type("workflow") == "Task Automation"


def test_humanize_agent_type_unknown_falls_back_to_underscore_replacement():
    assert humanize_agent_type("some_new_agent") == "some new agent"
