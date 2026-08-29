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
