import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import {
  getPermissionsMatrix,
  listAuditLogs,
  listUsers,
  togglePermission,
  updateUser,
} from "../api/admin";
import { useAuth } from "../context/AuthContext";
import { humanizeAgent } from "../utils/labels";

const EVENT_TYPES = ["", "agent_action", "data_access", "approval"];

function UsersSection({ currentUserId }) {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    listUsers().then(setUsers).catch(() => setError("Could not load users."));
  }, []);

  async function handleRoleChange(user, role) {
    try {
      const updated = await updateUser(user.id, { role });
      setUsers((prev) => prev.map((u) => (u.id === user.id ? updated : u)));
    } catch {
      setError(`Could not update role for ${user.email}.`);
    }
  }

  async function handleActiveToggle(user) {
    try {
      const updated = await updateUser(user.id, { is_active: !user.is_active });
      setUsers((prev) => prev.map((u) => (u.id === user.id ? updated : u)));
    } catch {
      setError(`Could not update status for ${user.email}.`);
    }
  }

  return (
    <section className="admin-section">
      <h2>Users</h2>
      {error && <p className="error">{error}</p>}
      <table className="admin-table">
        <thead>
          <tr>
            <th>Email</th>
            <th>Name</th>
            <th>Role</th>
            <th>Active</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.email}</td>
              <td>{u.full_name}</td>
              <td>
                <select
                  value={u.role}
                  disabled={u.id === currentUserId}
                  onChange={(e) => handleRoleChange(u, e.target.value)}
                >
                  <option value="employee">employee</option>
                  <option value="hr">hr</option>
                  <option value="admin">admin</option>
                </select>
              </td>
              <td>
                <input
                  type="checkbox"
                  checked={u.is_active}
                  disabled={u.id === currentUserId}
                  onChange={() => handleActiveToggle(u)}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function PermissionsSection() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getPermissionsMatrix().then(setData).catch(() => setError("Could not load permissions."));
  }, []);

  async function handleToggle(role, agentType, allowed) {
    try {
      const updated = await togglePermission(role, agentType, allowed);
      setData(updated);
    } catch {
      setError("Could not update this permission.");
    }
  }

  if (!data) return <section className="admin-section"><h2>Permissions</h2>{error && <p className="error">{error}</p>}</section>;

  return (
    <section className="admin-section">
      <h2>Permissions</h2>
      {error && <p className="error">{error}</p>}
      <table className="admin-table">
        <thead>
          <tr>
            <th>Agent</th>
            {data.roles.map((role) => (
              <th key={role}>{role}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.agent_types.map((agentType) => (
            <tr key={agentType}>
              <td>{humanizeAgent(agentType)}</td>
              {data.roles.map((role) => {
                const allowed = data.matrix[role]?.includes(agentType);
                return (
                  <td key={role}>
                    <input
                      type="checkbox"
                      checked={allowed}
                      onChange={() => handleToggle(role, agentType, !allowed)}
                    />
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function AuditLogSection() {
  const [logs, setLogs] = useState([]);
  const [eventType, setEventType] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    listAuditLogs(eventType || undefined)
      .then(setLogs)
      .catch(() => setError("Could not load audit logs."));
  }, [eventType]);

  return (
    <section className="admin-section">
      <h2>Audit Log</h2>
      <label className="audit-filter">
        Event type
        <select value={eventType} onChange={(e) => setEventType(e.target.value)}>
          {EVENT_TYPES.map((t) => (
            <option key={t} value={t}>
              {t || "All"}
            </option>
          ))}
        </select>
      </label>
      {error && <p className="error">{error}</p>}
      <table className="admin-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Type</th>
            <th>Action</th>
            <th>User</th>
            <th>Role</th>
            <th>Request</th>
            <th>Subtask</th>
            <th>Context</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id}>
              <td>{new Date(log.created_at).toLocaleString()}</td>
              <td>{log.event_type}</td>
              <td>{log.action}</td>
              <td>{log.user_email ?? "—"}</td>
              <td>{log.role ?? "—"}</td>
              <td>{log.request_id ?? "—"}</td>
              <td>{log.subtask_id ?? "—"}</td>
              <td className="audit-context">{log.context ? JSON.stringify(log.context) : "—"}</td>
            </tr>
          ))}
          {logs.length === 0 && (
            <tr>
              <td colSpan={8}>No audit log entries.</td>
            </tr>
          )}
        </tbody>
      </table>
    </section>
  );
}

export default function AdminPage() {
  const { user } = useAuth();

  if (user && user.role !== "admin") {
    return <Navigate to="/requests" replace />;
  }

  return (
    <div className="requests-page">
      <header>
        <h1>Admin</h1>
      </header>
      {user && (
        <>
          <UsersSection currentUserId={user.id} />
          <PermissionsSection />
          <AuditLogSection />
        </>
      )}
    </div>
  );
}
