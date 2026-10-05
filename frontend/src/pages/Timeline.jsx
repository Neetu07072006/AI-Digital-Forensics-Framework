import { useEffect, useState } from "react";
import { apiJson } from "../api";

function Timeline() {
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState("");
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    loadCases();
  }, []);

  async function loadCases() {
    try {
      const data = await apiJson(
        "/api/cases/"
      );

      setCases(
        Array.isArray(data)
          ? data
          : []
      );
    } catch {
      setMessage(
        "Unable to load cases."
      );
    }
  }

  async function loadTimeline(caseId) {
    if (!caseId) {
      setEvents([]);
      return;
    }

    try {
      setLoading(true);

      const data = await apiJson(
        `/api/timeline/${caseId}`
      );

      setEvents(
        Array.isArray(data)
          ? data
          : []
      );
    } catch {
      setMessage(
        "Unable to load timeline."
      );
    } finally {
      setLoading(false);
    }
  }

  async function generateTimeline() {
    if (!selectedCase) {
      setMessage(
        "Please select a case."
      );
      return;
    }

    try {
      setGenerating(true);
      setMessage("");

      const data = await apiJson(
        `/api/timeline/${selectedCase}/generate`,
        {
          method: "POST"
        }
      );

      setMessage(
        `${data.events_generated} timeline events generated.`
      );

      await loadTimeline(
        selectedCase
      );
    } catch (error) {
      setMessage(error.message);
    } finally {
      setGenerating(false);
    }
  }

  function eventClass(severity) {
    return severity
      ? severity.toLowerCase()
      : "informational";
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Forensic Timeline</h2>

          <p>
            Reconstruct the chronological sequence of investigation events.
          </p>
        </div>
      </div>

      {message && (
        <div className="message-box">
          {message}
        </div>
      )}

      <section className="form-panel">
        <div className="panel-header">
          <h3>Timeline Controls</h3>

          <p>
            Select a case and generate its forensic timeline.
          </p>
        </div>

        <div className="timeline-controls">
          <div className="form-group">
            <label>
              Investigation Case
            </label>

            <select
              value={selectedCase}
              onChange={event => {
                const value =
                  event.target.value;

                setSelectedCase(value);
                loadTimeline(value);
              }}
            >
              <option value="">
                Select case
              </option>

              {cases.map(item => (
                <option
                  key={item.case_id}
                  value={item.case_id}
                >
                  #{item.case_id} -{" "}
                  {item.case_name}
                </option>
              ))}
            </select>
          </div>

          <button
            className="primary-btn timeline-button"
            onClick={generateTimeline}
            disabled={
              generating ||
              !selectedCase
            }
          >
            {generating
              ? "Generating..."
              : "Generate Timeline"}
          </button>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <h3>Timeline Events</h3>

          <p>
            {events.length} event
            {events.length !== 1
              ? "s"
              : ""} recorded
          </p>
        </div>

        {loading ? (
          <div className="empty-state">
            Loading timeline...
          </div>
        ) : events.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              ◷
            </div>

            <h3>
              No Timeline Events
            </h3>

            <p>
              Select a case and generate its timeline.
            </p>
          </div>
        ) : (
          <div className="timeline">
            {events.map(event => (
              <div
                className="timeline-event"
                key={event.event_id}
              >
                <div className="timeline-dot">
                  ●
                </div>

                <div className="timeline-card">
                  <div className="timeline-header">
                    <div>
                      <span
                        className={`severity-badge ${eventClass(
                          event.severity
                        )}`}
                      >
                        {event.severity}
                      </span>

                      <h3>
                        {event.title}
                      </h3>
                    </div>

                    <time>
                      {new Date(
                        event.event_time
                      ).toLocaleString()}
                    </time>
                  </div>

                  <p>
                    {event.description}
                  </p>

                  <div className="timeline-source">
                    Source:{" "}
                    {event.source ||
                      "Unknown"}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Timeline;