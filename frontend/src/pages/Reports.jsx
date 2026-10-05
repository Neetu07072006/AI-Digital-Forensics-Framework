import { useEffect, useState } from "react";
import { apiFetch, apiJson } from "../api";

function Reports() {
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState("");
  const [reports, setReports] = useState([]);
  const [loadingCases, setLoadingCases] = useState(true);
  const [loadingReports, setLoadingReports] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    loadCases();
  }, []);

  useEffect(() => {
    if (selectedCase) {
      loadReports(selectedCase);
    } else {
      setReports([]);
    }
  }, [selectedCase]);

  async function loadCases() {
    try {
      setLoadingCases(true);
      setError("");

      const data = await apiJson(
        "/api/cases/"
      );

      const caseList = Array.isArray(data)
        ? data
        : [];

      setCases(caseList);

      if (caseList.length > 0) {
        setSelectedCase(
          String(caseList[0].case_id)
        );
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingCases(false);
    }
  }

  async function loadReports(caseId) {
    try {
      setLoadingReports(true);
      setError("");

      const data = await apiJson(
        `/api/reports/${caseId}`
      );

      setReports(
        Array.isArray(data)
          ? data
          : []
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingReports(false);
    }
  }

  async function generateReport() {
    if (!selectedCase) {
      setError(
        "Please select a case"
      );
      return;
    }

    try {
      setGenerating(true);
      setError("");
      setMessage("");

      await apiJson(
        `/api/reports/${selectedCase}/generate`,
        {
          method: "POST"
        }
      );

      setMessage(
        "Forensic report generated successfully."
      );

      await loadReports(
        selectedCase
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  }

  async function downloadReport() {
    if (!selectedCase) {
      return;
    }

    try {
      setError("");

      const response = await apiFetch(
        `/api/reports/${selectedCase}/download`
      );

      if (!response.ok) {
        let message =
          "Failed to download report.";

        try {
          const data =
            await response.json();

          message =
            data.detail || message;
        } catch {
        }

        throw new Error(message);
      }

      const blob =
        await response.blob();

      const url =
        window.URL.createObjectURL(
          blob
        );

      const link =
        document.createElement("a");

      link.href = url;
      link.download =
        `case_${selectedCase}_forensic_report.pdf`;

      document.body.appendChild(
        link
      );

      link.click();

      link.remove();

      window.URL.revokeObjectURL(
        url
      );
    } catch (err) {
      setError(err.message);
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

  function getRiskClass(level) {
    if (!level) {
      return "";
    }

    return level.toLowerCase();
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

  const latestReport =
    reports[0];

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>
            Forensic Reports
          </h1>

          <p>
            Generate and download complete digital
            forensic investigation reports.
          </p>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {message && (
        <div className="success-message">
          {message}
        </div>
      )}

      <div className="report-controls">
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
          className="primary-button"
          onClick={generateReport}
          disabled={
            !selectedCase ||
            generating
          }
        >
          {generating
            ? "Generating..."
            : "Generate Forensic Report"}
        </button>
      </div>

      {selectedCase &&
        latestReport && (
          <div className="latest-report">
            <div className="report-main-card">
              <div className="report-icon">
                PDF
              </div>

              <div className="report-info">
                <span className="report-label">
                  LATEST REPORT
                </span>

                <h2>
                  {latestReport.report_title}
                </h2>

                <p>
                  Generated by{" "}
                  <strong>
                    {
                      latestReport.generated_by
                    }
                  </strong>
                </p>

                <p>
                  {formatDate(
                    latestReport.created_at
                  )}
                </p>
              </div>

              <div className="report-actions">
                <div
                  className={`risk-badge ${getRiskClass(
                    latestReport.risk_level
                  )}`}
                >
                  {
                    latestReport.risk_level
                  }
                </div>

                <button
                  className="download-button"
                  onClick={
                    downloadReport
                  }
                >
                  Download PDF
                </button>
              </div>
            </div>

            <div className="report-summary">
              <div>
                <span>
                  Risk Score
                </span>

                <strong>
                  {latestReport.risk_score ??
                    0}
                </strong>
              </div>

              <div>
                <span>
                  Risk Level
                </span>

                <strong>
                  {latestReport.risk_level ||
                    "Informational"}
                </strong>
              </div>

              <div>
                <span>
                  Report ID
                </span>

                <strong>
                  #
                  {
                    latestReport.report_id
                  }
                </strong>
              </div>
            </div>

            {latestReport.summary && (
              <div className="report-description">
                <h3>
                  Investigation Summary
                </h3>

                <p>
                  {latestReport.summary}
                </p>
              </div>
            )}
          </div>
        )}

      {selectedCase &&
        !latestReport &&
        !loadingReports && (
          <div className="empty-state">
            <div className="empty-icon">
              ▤
            </div>

            <h3>
              No report generated
            </h3>

            <p>
              Generate a forensic report for the
              selected case.
            </p>
          </div>
        )}

      {loadingReports && (
        <div className="loading">
          Loading reports...
        </div>
      )}

      {reports.length > 1 && (
        <div className="report-history">
          <div className="section-title">
            <h2>
              Report History
            </h2>

            <span>
              {reports.length} reports
            </span>
          </div>

          <div className="report-history-list">
            {reports.map(report => (
              <div
                className="report-history-item"
                key={report.report_id}
              >
                <div className="history-report-icon">
                  PDF
                </div>

                <div className="history-report-info">
                  <strong>
                    {
                      report.report_title
                    }
                  </strong>

                  <span>
                    Report #
                    {report.report_id}
                  </span>

                  <small>
                    {formatDate(
                      report.created_at
                    )}
                  </small>
                </div>

                <div
                  className={`risk-badge ${getRiskClass(
                    report.risk_level
                  )}`}
                >
                  {report.risk_level}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Reports;