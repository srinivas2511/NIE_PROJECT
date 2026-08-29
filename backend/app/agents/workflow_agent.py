from app.agents.base import AgentResult, BaseAgent
from app.workflow.functions import FUNCTION_REGISTRY
from app.workflow.planner import plan_steps

# Deterministic against a known mock dataset -- little genuine uncertainty,
# but not 1.0 since keyword-based step/department matching can still
# misinterpret the request.
CONFIDENCE = 0.85


class WorkflowAgent(BaseAgent):
    agent_type = "workflow"

    def run(self, description: str, prior_results: list[AgentResult], role: str) -> AgentResult:
        steps = plan_steps(description)
        executed = [
            {"function_name": step.function_name, "output": FUNCTION_REGISTRY[step.function_name](description)}
            for step in steps
        ]

        step_lines = [
            f"{i}. {step['function_name']}: {step['output']}"
            for i, step in enumerate(executed, start=1)
        ]
        text = f"[Workflow] Executed {len(executed)} step(s):\n" + "\n".join(step_lines)

        function_names = ", ".join(step["function_name"] for step in executed)
        explanation = (
            f"Multi-step task automation against {len(executed)} simulated enterprise "
            f"function(s) ({function_names}), each deterministic given the request text "
            "and a fixed mock dataset; the persisted record is in workflow_executions."
        )

        return AgentResult(
            text=text, confidence=CONFIDENCE, explanation=explanation, workflow_steps=executed
        )
