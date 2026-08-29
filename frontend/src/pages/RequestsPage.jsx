import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createRequest, listRequests } from "../api/requests";
import { useAuth } from "../context/AuthContext";

function confidenceTier(confidence) {
  if (confidence == null) return null;
  if (confidence < 0.4) return "low";
  if (confidence < 0.7) return "medium";
  return "high";
}

export default function RequestsPage() {
  const { user, logout } = useAuth();
  const [requests, setRequests] = useState([]);
  const [text, setText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    listRequests().then(setRequests).catch(() => setError("Could not load requests."));
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!text.trim()) return;
    setError("");
    setIsSubmitting(true);
    try {
      const created = await createRequest(text);
      setRequests((prev) => [created, ...prev]);
      setText("");
    } catch {
      setError("Could not submit your request.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="requests-page">
      <header>
        <h1>Enterprise Assistant</h1>
        <div>
          <span>
            {user?.full_name} <span className="user-role">({user?.role})</span>
          </span>
          {user?.role === "admin" && <Link to="/approvals">Approvals</Link>}
          <button type="button" onClick={logout}>
            Log out
          </button>
        </div>
      </header>

      <form onSubmit={handleSubmit} className="request-form">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Ask the assistant something, e.g. 'Generate this month's headcount report for Engineering.'"
          rows={3}
        />
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Submitting..." : "Submit request"}
        </button>
      </form>
      {error && <p className="error">{error}</p>}

      <ul className="request-list">
        {requests.map((r) => (
          <li key={r.id}>
            <p className="request-text">{r.text}</p>
            <span className={`status status-${r.status}`}>{r.status}</span>
            <span className="request-time">
              {new Date(r.created_at).toLocaleString()}
            </span>
            {r.subtasks?.length > 0 && (
              <ul className="subtask-list">
                {r.subtasks.map((s) => (
                  <li key={s.id}>
                    <span className="subtask-agent">{s.agent_type}</span>
                    <span className={`status status-${s.status}`}>{s.status}</span>
                    {s.confidence != null && (
                      <span className={`confidence confidence-${confidenceTier(s.confidence)}`}>
                        {Math.round(s.confidence * 100)}% confidence
                      </span>
                    )}
                    <p className="subtask-result">{s.result}</p>
                    {s.explanation && <p className="subtask-explanation">Why: {s.explanation}</p>}
                    {s.approved_by_email && (
                      <p className="subtask-explanation">
                        Reviewed by {s.approved_by_email} at{" "}
                        {new Date(s.approved_at).toLocaleString()}
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
        {requests.length === 0 && <li className="empty">No requests yet.</li>}
      </ul>
    </div>
  );
}
