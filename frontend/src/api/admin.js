import client from "./client";

export async function listUsers() {
  const { data } = await client.get("/api/admin/users");
  return data;
}

export async function updateUser(id, payload) {
  const { data } = await client.patch(`/api/admin/users/${id}`, payload);
  return data;
}

export async function getPermissionsMatrix() {
  const { data } = await client.get("/api/admin/permissions");
  return data;
}

export async function togglePermission(role, agentType, allowed) {
  const { data } = await client.post("/api/admin/permissions/toggle", {
    role,
    agent_type: agentType,
    allowed,
  });
  return data;
}

export async function listAuditLogs(eventType) {
  const { data } = await client.get("/api/admin/audit-logs", {
    params: eventType ? { event_type: eventType } : {},
  });
  return data;
}

export async function getMetrics() {
  const { data } = await client.get("/api/admin/metrics");
  return data;
}

export async function getLatestRagEvaluation() {
  const { data } = await client.get("/api/admin/rag-evaluation");
  return data;
}

export async function runRagEvaluation() {
  // No client-side timeout override needed -- axios defaults to none, and
  // this call realistically takes a couple of minutes (~12 real LLM calls).
  const { data } = await client.post("/api/admin/rag-evaluation/run");
  return data;
}

export async function getDecisionTrace(subtaskId) {
  const { data } = await client.get(`/api/admin/trace/${subtaskId}`);
  return data;
}
