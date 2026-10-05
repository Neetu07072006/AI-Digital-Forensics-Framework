import { useEffect, useState } from "react";
import { apiJson } from "../api";

function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadLogs();
  }, []);

  async function loadLogs() {
    try {
      setLoading(true);
      setError("");

      const data = await apiJson(
        "/api/audit/"
      );

      setLogs(
        Array.isArray(data)
          ? data
          : []
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function formatDate(date) {
    if (!date) {
      return "N/A";
    }

    return new Date(
      date
    ).toLocaleString();
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>
            Audit Logs
          </h1>

          <p>
            Track investigation activity and
            security-related actions.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={loadLogs}
          disabled={loading}
        >
          {loading
            ? "Refreshing..."
            : "Refresh"}
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="audit-summary">
        <div className="audit-stat">
          <span>
            Total Events
          </span>

          <strong>
            {logs.length}
          </strong>
        </div>

        <div className="audit-stat">
          <span>
            Latest User
          </span>

          <strong>
            {logs.length > 0
              ? logs[0].username
              : "N/A"}
          </strong>
        </div>

        <div className="audit-stat">
          <span>
            Latest Activity
          </span>

          <strong>
            {logs.length > 0
              ? formatDate(
                  logs[0].timestamp
                )
              : "N/A"}
          </strong>
        </div>
      </div>

      {loading ? (
        <div className="loading">
          Loading audit logs...
        </div>
      ) : logs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">
            ◉
          </div>

          <h3>
            No audit logs
          </h3>

          <p>
            No recorded investigation activity
            is available yet.
          </p>
        </div>
      ) : (
        <div className="audit-card">
          <div className="audit-table-header">
            <span>USER</span>
            <span>ACTION</span>
            <span>RESOURCE</span>
            <span>DETAILS</span>
            <span>TIMESTAMP</span>
          </div>

          <div className="audit-list">
            {logs.map(log => (
              <div
                className="audit-row"
                key={log.audit_id}
              >
                <div className="audit-user">
                  <div className="audit-avatar">
                    {log.username
                      ?.charAt(0)
                      .toUpperCase()}
                  </div>

                  <span>
                    {log.username}
                  </span>
                </div>

                <div>
                  <span className="action-badge">
                    {log.action}
                  </span>
                </div>

                <div className="audit-resource">
                  {log.resource ||
                    "—"}
                </div>

                <div className="audit-details">
                  {log.details ||
                    "—"}
                </div>

                <div className="audit-time">
                  {formatDate(
                    log.timestamp
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default AuditLogs;