import { useEffect, useState } from "react";
import { apiJson } from "../api";

function Analysis() {
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
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

  async function loadAnalysis(
    caseId
  ) {
    if (!caseId) {
      setAnalysis(null);
      return;
    }

    try {
      setLoading(true);

      const data = await apiJson(
        `/api/analysis/${caseId}`
      );

      setAnalysis(data);
    } catch {
      setMessage(
        "Unable to load analysis."
      );
    } finally {
      setLoading(false);
    }
  }

  async function runAnalysis() {
    if (!selectedCase) {
      setMessage(
        "Please select a case."
      );
      return;
    }

    try {
      setAnalyzing(true);
      setMessage("");

      const data = await apiJson(
        `/api/analysis/${selectedCase}/analyze`,
        {
          method: "POST"
        }
      );

      setMessage(
        `Analysis completed. ${data.findings_detected} findings detected.`
      );

      await loadAnalysis(
        selectedCase
      );
    } catch (error) {
      setMessage(error.message);
    } finally {
      setAnalyzing(false);
    }
  }

  function riskClass(level) {
    if (!level) {
      return "";
    }

    return level.toLowerCase();
  }

  const findings = Array.isArray(
    analysis?.findings
  )
    ? analysis.findings
    : [];

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>AI Threat Analysis</h2>

          <p>
            Detect suspicious indicators and calculate forensic risk.
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
          <h3>
            Investigation Analysis
          </h3>

          <p>
            Run deterministic threat analysis against extracted artifacts.
          </p>
        </div>

        <div className="analysis-controls">
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
                loadAnalysis(value);
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
            className="primary-btn"
            onClick={runAnalysis}
            disabled={
              analyzing ||
              !selectedCase
            }
          >
            {analyzing
              ? "Analyzing..."
              : "Run Threat Analysis"}
          </button>
        </div>
      </section>

      {loading ? (
        <div className="empty-state">
          Loading analysis...
        </div>
      ) : analysis ? (
        <>
          <section className="risk-overview">
            <div className="risk-card">
              <span>Risk Score</span>

              <strong>
                {analysis.risk_score}
              </strong>

              <small>
                out of 100
              </small>
            </div>

            <div
              className={`risk-level ${riskClass(
                analysis.risk_level
              )}`}
            >
              <span>
                Risk Level
              </span>

              <strong>
                {analysis.risk_level}
              </strong>
            </div>

            <div className="risk-card">
              <span>Findings</span>

              <strong>
                {findings.length}
              </strong>

              <small>
                detected
              </small>
            </div>
          </section>

          <section className="panel">
            <div className="panel-header">
              <h3>
                Threat Findings
              </h3>

              <p>
                Findings ordered by risk score.
              </p>
            </div>

            {findings.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">
                  ✓
                </div>

                <h3>
                  No Threats Detected
                </h3>

                <p>
                  No suspicious indicators were identified
                  by the deterministic analysis engine.
                </p>
              </div>
            ) : (
              <div className="finding-list">
                {findings.map(
                  finding => (
                    <div
                      className="finding-card"
                      key={
                        finding.finding_id
                      }
                    >
                      <div className="finding-score">
                        {
                          finding.risk_score
                        }
                      </div>

                      <div className="finding-content">
                        <div className="finding-header">
                          <div>
                            <span
                              className={`severity-badge ${riskClass(
                                finding.severity
                              )}`}
                            >
                              {
                                finding.severity
                              }
                            </span>

                            <h3>
                              {
                                finding.title
                              }
                            </h3>
                          </div>

                          <span className="finding-type">
                            {
                              finding.finding_type
                            }
                          </span>
                        </div>

                        <p>
                          {
                            finding.description
                          }
                        </p>

                        {finding.evidence_reference && (
                          <div className="finding-reference">
                            <strong>
                              Evidence:
                            </strong>{" "}

                            <code>
                              {
                                finding.evidence_reference
                              }
                            </code>
                          </div>
                        )}
                      </div>
                    </div>
                  )
                )}
              </div>
            )}
          </section>
        </>
      ) : (
        <div className="empty-state">
          <div className="empty-icon">
            ◆
          </div>

          <h3>
            Select an Investigation
          </h3>

          <p>
            Select a case to view or run threat analysis.
          </p>
        </div>
      )}
    </div>
  );
}

export default Analysis;