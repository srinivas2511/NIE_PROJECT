from app.agents.base import AgentResult, BaseAgent
from app.workflow.functions import FUNCTION_REGISTRY
from app.workflow.planner import plan_steps

# Deterministic against a known mock dataset -- little genuine uncertainty,
# but not 1.0 since keyword-based step/department matching can still
# misinterpret the request.
CONFIDENCE = 0.85


def _format_output(output: dict) -> str:
    # Human-readable "key: value, key: value" instead of Python dict repr,
    # which would otherwise leak straight into the UI (FR-10).
    return ", ".join(f"{key.replace('_', ' ')}: {value}" for key, value in output.items())


class WorkflowAgent(BaseAgent):
    agent_type = "workflow"

    def run(self, description: str, prior_results: list[AgentResult], role: str) -> AgentResult:
        steps = plan_steps(description)
        executed = [
            {"function_name": step.function_name, "output": FUNCTION_REGISTRY[step.function_name](description)}
            for step in steps
        ]

        step_lines = [
            f"{i}. {step['function_name'].replace('_', ' ').title()} — {_format_output(step['output'])}"
            for i, step in enumerate(executed, start=1)
        ]
        text = f"Executed {len(executed)} step(s):\n" + "\n".join(step_lines)

        function_names = ", ".join(
            step["function_name"].replace("_", " ").title() for step in executed
        )
        explanation = (
            f"Multi-step task automation against {len(executed)} simulated enterprise "
            f"function(s) ({function_names}), each deterministic given the request text "
            "and a fixed mock dataset."
        )

        # NFR-6: retrieve_data reads real (simulated) enterprise headcount/
        # expense data, which is "data access" the same way rag's retrieval
        # is, not just a generic action.
        data_access_events = (
            [{"action": "workflow.retrieve_data", "context": {"function": "retrieve_data"}}]
            if any(step["function_name"] == "retrieve_data" for step in executed)
            else []
        )

        return AgentResult(
            text=text,
            confidence=CONFIDENCE,
            explanation=explanation,
            workflow_steps=executed,
            data_access_events=data_access_events,
        )
