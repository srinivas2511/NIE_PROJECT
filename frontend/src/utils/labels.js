const STATUS_LABELS = {
  received: "Received",
  completed: "Completed",
  failed: "Failed",
  denied: "Access Denied",
  partially_denied: "Partially Denied",
  pending_approval: "Pending Approval",
  rejected: "Rejected",
};

export function humanizeStatus(status) {
  if (!status) return status;
  return STATUS_LABELS[status] ?? status.replace(/_/g, " ");
}

const AGENT_LABELS = {
  rag: "Knowledge Base",
  security: "Security Check",
  analytics: "Analytics",
  workflow: "Task Automation",
  validation: "Validation Review",
};

export function humanizeAgent(agentType) {
  if (!agentType) return agentType;
  return AGENT_LABELS[agentType] ?? agentType.replace(/_/g, " ");
}
