import { useEffect, useState } from "react";
import { apiFetch, apiJson } from "../api";

function Evidence() {
  const [cases, setCases] = useState([]);
  const [evidence, setEvidence] = useState([]);
  const [selectedCase, setSelectedCase] = useState("");
  const [selectedEvidence, setSelectedEvidence] = useState(null);
  const [custody, setCustody] = useState([]);
  const [file, setFile] = useState(null);
  const [uploadedBy, setUploadedBy] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("success");
  const [verifying, setVerifying] = useState(null);

  useEffect(() => {
    loadCases();
    loadEvidence();
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
      showMessage(
        "Unable to load cases.",
        "error"
      );
    }
  }

  async function loadEvidence() {
    try {
      const data = await apiJson(
        "/api/evidence/"
      );

      setEvidence(
        Array.isArray(data)
          ? data
          : []
      );
    } catch {
      showMessage(
        "Unable to load evidence.",
        "error"
      );
    }
  }

  function showMessage(
    text,
    type = "success"
  ) {
    setMessage(text);
    setMessageType(type);
  }

  async function uploadEvidence(event) {
    event.preventDefault();

    if (!selectedCase) {
      showMessage(
        "Please select a case.",
        "error"
      );
      return;
    }

    if (!file) {
      showMessage(
        "Please select an evidence file.",
        "error"
      );
      return;
    }

    if (!uploadedBy.trim()) {
      showMessage(
        "Please enter the investigator name.",
        "error"
      );
      return;
    }

    const formData = new FormData();

    formData.append(
      "case_id",
      selectedCase
    );
    formData.append(
      "uploaded_by",
      uploadedBy
    );
    formData.append(
      "description",
      description
    );
    formData.append(
      "file",
      file
    );

    try {
      setLoading(true);
      setMessage("");

      const response = await apiFetch(
        "/api/evidence/upload",
        {
          method: "POST",
          body: formData
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
          "Evidence upload failed"
        );
      }

      showMessage(
        "Evidence uploaded successfully and SHA-256 hash generated."
      );

      setSelectedCase("");
      setFile(null);
      setUploadedBy("");
      setDescription("");

      const input = document.getElementById(
        "evidence-file"
      );

      if (input) {
        input.value = "";
      }

      await loadEvidence();
    } catch (error) {
      showMessage(
        error.message,
        "error"
      );
    } finally {
      setLoading(false);
    }
  }

  async function verifyEvidence(
    evidenceId
  ) {
    try {
      setVerifying(evidenceId);

      const formData = new FormData();

      formData.append(
        "performed_by",
        uploadedBy.trim() ||
        "Investigator"
      );

      const response = await apiFetch(
        `/api/evidence/${evidenceId}/verify`,
        {
          method: "POST",
          body: formData
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
          "Integrity verification failed"
        );
      }

      if (data.integrity_verified) {
        showMessage(
          `Integrity verified for ${data.file_name}.`
        );
      } else {
        showMessage(
          `Tampering detected in ${data.file_name}.`,
          "error"
        );
      }

      if (
        selectedEvidence &&
        selectedEvidence.evidence_id ===
          evidenceId
      ) {
        await loadCustody(evidenceId);
      }
    } catch (error) {
      showMessage(
        error.message,
        "error"
      );
    } finally {
      setVerifying(null);
    }
  }

  async function loadCustody(
    evidenceId
  ) {
    try {
      const data = await apiJson(
        `/api/evidence/${evidenceId}/custody`
      );

      setCustody(
        Array.isArray(data)
          ? data
          : []
      );
    } catch {
      showMessage(
        "Unable to load chain of custody.",
        "error"
      );
    }
  }

  async function showEvidenceDetails(
    item
  ) {
    setSelectedEvidence(item);
    await loadCustody(
      item.evidence_id
    );
  }

  function formatSize(bytes) {
    if (bytes < 1024) {
      return `${bytes} B`;
    }

    if (bytes < 1024 * 1024) {
      return `${(
        bytes / 1024
      ).toFixed(1)} KB`;
    }

    return `${(
      bytes /
      (1024 * 1024)
    ).toFixed(1)} MB`;
  }

  function getCaseName(caseId) {
    const item = cases.find(
      currentCase =>
        currentCase.case_id === caseId
    );

    return item
      ? item.case_name
      : `Case #${caseId}`;
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Evidence Management</h2>

          <p>
            Upload, verify, and track digital forensic evidence.
          </p>
        </div>
      </div>

      {message && (
        <div
          className={
            messageType === "error"
              ? "message-box error-message"
              : "message-box"
          }
        >
          {message}
        </div>
      )}

      <section className="form-panel">
        <div className="panel-header">
          <h3>Upload Evidence</h3>

          <p>
            Evidence is automatically protected using SHA-256.
          </p>
        </div>

        <form
          onSubmit={uploadEvidence}
          className="case-form"
        >
          <div className="form-group">
            <label>Case</label>

            <select
              value={selectedCase}
              onChange={event =>
                setSelectedCase(
                  event.target.value
                )
              }
              required
            >
              <option value="">
                Select investigation case
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

          <div className="form-group">
            <label>Uploaded By</label>

            <input
              type="text"
              value={uploadedBy}
              onChange={event =>
                setUploadedBy(
                  event.target.value
                )
              }
              placeholder="Investigator name"
              required
            />
          </div>

          <div className="form-group full-width">
            <label>Evidence File</label>

            <input
              id="evidence-file"
              type="file"
              onChange={event =>
                setFile(
                  event.target.files[0]
                )
              }
              required
            />
          </div>

          <div className="form-group full-width">
            <label>Description</label>

            <textarea
              value={description}
              onChange={event =>
                setDescription(
                  event.target.value
                )
              }
              placeholder="Describe the evidence..."
              rows="3"
            />
          </div>

          <div className="form-actions">
            <button
              type="submit"
              className="primary-btn"
              disabled={loading}
            >
              {loading
                ? "Uploading..."
                : "Upload Evidence"}
            </button>
          </div>
        </form>
      </section>

      <section className="panel">
        <div className="panel-header">
          <h3>Collected Evidence</h3>

          <p>
            {evidence.length} evidence file
            {evidence.length !== 1
              ? "s"
              : ""} registered
          </p>
        </div>

        {evidence.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              ◈
            </div>

            <h3>No Evidence Yet</h3>

            <p>
              Upload evidence to begin forensic analysis.
            </p>
          </div>
        ) : (
          <div className="evidence-list">
            {evidence.map(item => (
              <div
                className="evidence-card"
                key={item.evidence_id}
              >
                <div className="evidence-main">
                  <div className="evidence-icon">
                    ◈
                  </div>

                  <div className="evidence-info">
                    <h3>
                      {item.file_name}
                    </h3>

                    <div className="evidence-meta">
                      <span>
                        Case:{" "}
                        <strong>
                          {getCaseName(
                            item.case_id
                          )}
                        </strong>
                      </span>

                      <span>
                        Size:{" "}
                        {formatSize(
                          item.file_size
                        )}
                      </span>

                      <span>
                        Type:{" "}
                        {item.file_type ||
                          "Unknown"}
                      </span>

                      <span>
                        Uploaded by:{" "}
                        {item.uploaded_by}
                      </span>
                    </div>

                    <div className="hash-box">
                      <span>
                        SHA-256
                      </span>

                      <code>
                        {item.sha256_hash}
                      </code>
                    </div>
                  </div>
                </div>

                <div className="evidence-actions">
                  <button
                    className="secondary-btn"
                    onClick={() =>
                      showEvidenceDetails(
                        item
                      )
                    }
                  >
                    View Details
                  </button>

                  <button
                    className="verify-btn"
                    onClick={() =>
                      verifyEvidence(
                        item.evidence_id
                      )
                    }
                    disabled={
                      verifying ===
                      item.evidence_id
                    }
                  >
                    {verifying ===
                    item.evidence_id
                      ? "Verifying..."
                      : "Verify Integrity"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {selectedEvidence && (
        <section className="panel custody-panel">
          <div className="panel-header">
            <div className="details-header">
              <div>
                <h3>
                  Evidence Details
                </h3>

                <p>
                  {selectedEvidence.file_name}
                </p>
              </div>

              <button
                className="secondary-btn"
                onClick={() => {
                  setSelectedEvidence(
                    null
                  );
                  setCustody([]);
                }}
              >
                Close
              </button>
            </div>
          </div>

          <div className="evidence-details">
            <div className="detail-item">
              <span>
                Evidence ID
              </span>

              <strong>
                #{selectedEvidence.evidence_id}
              </strong>
            </div>

            <div className="detail-item">
              <span>Case ID</span>

              <strong>
                #{selectedEvidence.case_id}
              </strong>
            </div>

            <div className="detail-item">
              <span>File Size</span>

              <strong>
                {formatSize(
                  selectedEvidence.file_size
                )}
              </strong>
            </div>

            <div className="detail-item">
              <span>File Type</span>

              <strong>
                {selectedEvidence.file_type ||
                  "Unknown"}
              </strong>
            </div>

            <div className="detail-item">
              <span>Uploaded By</span>

              <strong>
                {selectedEvidence.uploaded_by}
              </strong>
            </div>

            <div className="detail-item full-detail">
              <span>
                SHA-256 Hash
              </span>

              <code>
                {selectedEvidence.sha256_hash}
              </code>
            </div>
          </div>

          <div className="custody-section">
            <h3>Chain of Custody</h3>

            {custody.length === 0 ? (
              <div className="empty-state">
                No custody records found.
              </div>
            ) : (
              <div className="custody-list">
                {custody.map(record => (
                  <div
                    className="custody-item"
                    key={record.custody_id}
                  >
                    <div className="custody-marker">
                      ✓
                    </div>

                    <div className="custody-content">
                      <div className="custody-top">
                        <strong>
                          {record.action}
                        </strong>

                        <span>
                          {new Date(
                            record.timestamp
                          ).toLocaleString()}
                        </span>
                      </div>

                      <p>
                        Performed by:{" "}
                        <strong>
                          {record.performed_by}
                        </strong>
                      </p>

                      {record.details && (
                        <code>
                          {record.details}
                        </code>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
}

export default Evidence;