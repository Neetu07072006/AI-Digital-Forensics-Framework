import { useEffect, useState } from "react";
import { apiJson } from "../api";

function AIInvestigation() {
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState("");
  const [investigations, setInvestigations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingCases, setLoadingCases] = useState(true);
  const [error, setError] = useState("");

  const latestInvestigation =
    investigations[0];

  useEffect(() => {
    loadCases();
  }, []);

  useEffect(() => {
    if (selectedCase) {
      loadInvestigations(
        selectedCase
      );
    } else {
      setInvestigations([]);
    }
  }, [selectedCase]);

  async function loadCases() {
    try {
      setLoadingCases(true);
      setError("");

      const data = await apiJson(
        "/api/cases/"
      );

      const caseList = Array.isArray(
        data
      )
        ? data
        : [];

      setCases(caseList);

      if (caseList.length > 0) {
        setSelectedCase(
          String(
            caseList[0].case_id
          )
        );
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingCases(false);
    }
  }

  async function loadInvestigations(
    caseId
  ) {
    try {
      setError("");

      const data = await apiJson(
        `/api/ai/${caseId}`
      );

      setInvestigations(
        Array.isArray(data)
          ? data
          : []
      );
    } catch (err) {
      setError(err.message);
    }
  }

  async function runInvestigation() {
    if (!selectedCase) {
      setError(
        "Please select a case"
      );
      return;
    }

    try {
      setLoading(true);
      setError("");

      await apiJson(
        `/api/ai/${selectedCase}/investigate`,
        {
          method: "POST"
        }
      );

      await loadInvestigations(
        selectedCase
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

  if (loadingCases) {
    return (
      <div className="page">
        <div className="loading">
          Loading cases...
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>
            AI Investigation
          </h1>

          <p>
            Use Gemini to analyze forensic evidence,
            findings, and timeline information.
          </p>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="ai-controls">
        <div className="form-group">
          <label>
            Select Case
          </label>

          <select
            value={selectedCase}
            onChange={e =>
              setSelectedCase(
                e.target.value
              )
            }
          >
            <option value="">
              Select a case
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
          className="primary-button ai-run-button"
          onClick={runInvestigation}
          disabled={
            !selectedCase ||
            loading
          }
        >
          {loading
            ? "AI Investigating..."
            : "Run AI Investigation"}
        </button>
      </div>

      {!selectedCase && (
        <div className="empty-state">
          Select a case to begin AI investigation.
        </div>
      )}

      {selectedCase &&
        !latestInvestigation &&
        !loading && (
          <div className="empty-state">
            <div className="empty-icon">
              ◆
            </div>

            <h3>
              No AI investigation available
            </h3>

            <p>
              Run the AI investigation to generate a
              forensic summary, attack pattern,
              risk assessment, and recommendations.
            </p>
          </div>
        )}

      {latestInvestigation && (
        <div className="ai-results">
          <div className="ai-header-card">
            <div>
              <span className="ai-label">
                GEMINI INVESTIGATION
              </span>

              <h2>
                Investigation #
                {
                  latestInvestigation.investigation_id
                }
              </h2>

              <p>
                Generated on{" "}
                {formatDate(
                  latestInvestigation.created_at
                )}
              </p>
            </div>

            <div className="model-badge">
              {
                latestInvestigation.model
              }
            </div>
          </div>

          <div className="ai-grid">
            <section className="ai-card">
              <div className="ai-card-title">
                <span className="ai-card-icon">
                  ◉
                </span>

                <h3>
                  Investigation Summary
                </h3>
              </div>

              <p>
                {latestInvestigation.summary ||
                  "No summary available."}
              </p>
            </section>

            <section className="ai-card">
              <div className="ai-card-title">
                <span className="ai-card-icon">
                  ◆
                </span>

                <h3>
                  Attack Pattern
                </h3>
              </div>

              <p>
                {latestInvestigation.attack_pattern ||
                  "No attack pattern identified."}
              </p>
            </section>

            <section className="ai-card">
              <div className="ai-card-title">
                <span className="ai-card-icon">
                  !
                </span>

                <h3>
                  Risk Assessment
                </h3>
              </div>

              <p>
                {latestInvestigation.risk_assessment ||
                  "No risk assessment available."}
              </p>
            </section>

            <section className="ai-card recommendation-card">
              <div className="ai-card-title">
                <span className="ai-card-icon">
                  ✓
                </span>

                <h3>
                  Recommendations
                </h3>
              </div>

              <p>
                {latestInvestigation.recommendations ||
                  "No recommendations available."}
              </p>
            </section>
          </div>

          {investigations.length > 1 && (
            <section className="history-card">
              <div className="section-title">
                <h2>
                  Previous AI Investigations
                </h2>

                <span>
                  {investigations.length} investigations
                </span>
              </div>

              <div className="investigation-history">
                {investigations.map(
                  item => (
                    <div
                      className="history-item"
                      key={
                        item.investigation_id
                      }
                    >
                      <div>
                        <strong>
                          Investigation #
                          {
                            item.investigation_id
                          }
                        </strong>

                        <span>
                          {formatDate(
                            item.created_at
                          )}
                        </span>
                      </div>

                      <p>
                        {item.summary}
                      </p>
                    </div>
                  )
                )}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  );
}

export default AIInvestigation;