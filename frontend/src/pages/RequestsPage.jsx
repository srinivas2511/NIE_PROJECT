import { useEffect, useState } from "react";
import { createRequest, listRequests } from "../api/requests";
import { useAuth } from "../context/AuthContext";

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
          <span>{user?.full_name}</span>
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
          </li>
        ))}
        {requests.length === 0 && <li className="empty">No requests yet.</li>}
      </ul>
    </div>
  );
}
