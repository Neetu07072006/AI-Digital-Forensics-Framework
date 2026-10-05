import { useEffect, useState } from "react";
import { apiJson } from "../api";

function Cases() {
  const [cases, setCases] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [form, setForm] = useState({
    case_name: "",
    description: "",
    investigator: "",
    status: "Open",
    priority: "Medium"
  });

  useEffect(() => {
    loadCases();
  }, []);

  async function loadCases() {
    try {
      setLoading(true);

      const data = await apiJson(
        "/api/cases/"
      );

      setCases(
        Array.isArray(data)
          ? data
          : []
      );
    } catch (error) {
      setMessage(
        error.message ||
        "Unable to connect to the backend."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleChange(event) {
    setForm({
      ...form,
      [event.target.name]: event.target.value
    });
  }

  async function createCase(event) {
    event.preventDefault();

    try {
      setMessage("");

      const data = await apiJson(
        "/api/cases/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(form)
        }
      );

      setCases((previous) => [
        data,
        ...previous
      ]);

      setForm({
        case_name: "",
        description: "",
        investigator: "",
        status: "Open",
        priority: "Medium"
      });

      setShowForm(false);
      setMessage(
        "Case created successfully."
      );
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Cases</h2>
          <p>
            Create and manage digital forensic investigations.
          </p>
        </div>

        <button
          className="primary-btn"
          onClick={() => {
            setShowForm(!showForm);
            setMessage("");
          }}
        >
          {showForm ? "Cancel" : "+ New Case"}
        </button>
      </div>

      {message && (
        <div className="message-box">
          {message}
        </div>
      )}

      {showForm && (
        <section className="form-panel">
          <div className="panel-header">
            <h3>Create New Case</h3>
            <p>
              Enter the basic information for this investigation.
            </p>
          </div>

          <form
            onSubmit={createCase}
            className="case-form"
          >
            <div className="form-group">
              <label>Case Name</label>

              <input
                type="text"
                name="case_name"
                value={form.case_name}
                onChange={handleChange}
                placeholder="Example: Malware Investigation"
                required
              />
            </div>

            <div className="form-group">
              <label>Investigator</label>

              <input
                type="text"
                name="investigator"
                value={form.investigator}
                onChange={handleChange}
                placeholder="Investigator name"
                required
              />
            </div>

            <div className="form-group full-width">
              <label>Description</label>

              <textarea
                name="description"
                value={form.description}
                onChange={handleChange}
                placeholder="Describe the investigation..."
                rows="4"
              />
            </div>

            <div className="form-group">
              <label>Status</label>

              <select
                name="status"
                value={form.status}
                onChange={handleChange}
              >
                <option value="Open">
                  Open
                </option>

                <option value="Under Investigation">
                  Under Investigation
                </option>

                <option value="Closed">
                  Closed
                </option>
              </select>
            </div>

            <div className="form-group">
              <label>Priority</label>

              <select
                name="priority"
                value={form.priority}
                onChange={handleChange}
              >
                <option value="Low">
                  Low
                </option>

                <option value="Medium">
                  Medium
                </option>

                <option value="High">
                  High
                </option>

                <option value="Critical">
                  Critical
                </option>
              </select>
            </div>

            <div className="form-actions">
              <button
                type="button"
                className="secondary-btn"
                onClick={() =>
                  setShowForm(false)
                }
              >
                Cancel
              </button>

              <button
                type="submit"
                className="primary-btn"
              >
                Create Case
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Investigation Cases</h3>

            <p>
              {cases.length} case
              {cases.length !== 1
                ? "s"
                : ""} registered
            </p>
          </div>
        </div>

        {loading ? (
          <div className="empty-state">
            Loading cases...
          </div>
        ) : cases.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              ◫
            </div>

            <h3>No Cases Yet</h3>

            <p>
              Create your first forensic investigation.
            </p>
          </div>
        ) : (
          <div className="case-table">
            <div className="table-row table-heading">
              <span>ID</span>
              <span>Case Name</span>
              <span>Investigator</span>
              <span>Priority</span>
              <span>Status</span>
            </div>

            {cases.map((item) => (
              <div
                className="table-row"
                key={item.case_id}
              >
                <span>
                  #{item.case_id}
                </span>

                <span>
                  <strong>
                    {item.case_name}
                  </strong>
                </span>

                <span>
                  {item.investigator}
                </span>

                <span>
                  <span
                    className={`priority ${item.priority.toLowerCase()}`}
                  >
                    {item.priority}
                  </span>
                </span>

                <span>
                  <span className="case-status">
                    {item.status}
                  </span>
                </span>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Cases;