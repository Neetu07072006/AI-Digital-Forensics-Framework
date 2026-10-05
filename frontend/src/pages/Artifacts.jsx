import { useEffect, useState } from "react";
import { apiJson } from "../api";

function Artifacts() {
  const [evidence, setEvidence] = useState([]);
  const [selectedEvidence, setSelectedEvidence] = useState("");
  const [artifacts, setArtifacts] = useState([]);
  const [extracting, setExtracting] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    loadEvidence();
  }, []);

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
      setMessage(
        "Unable to load evidence."
      );
    }
  }

  async function extractArtifacts() {
    if (!selectedEvidence) {
      setMessage(
        "Please select evidence."
      );
      return;
    }

    try {
      setExtracting(true);
      setMessage("");

      const data = await apiJson(
        `/api/artifacts/${selectedEvidence}/extract`,
        {
          method: "POST"
        }
      );

      setMessage(
        `Extraction completed. ${data.strings_found} strings, ${data.urls_found} URLs, ${data.ips_found} IPs and ${data.suspicious_keywords_found} suspicious indicators found.`
      );

      await loadArtifacts(
        selectedEvidence
      );
    } catch (error) {
      setMessage(error.message);
    } finally {
      setExtracting(false);
    }
  }

  async function loadArtifacts(
    evidenceId
  ) {
    if (!evidenceId) {
      setArtifacts([]);
      return;
    }

    try {
      const data = await apiJson(
        `/api/artifacts/${evidenceId}`
      );

      setArtifacts(
        Array.isArray(data)
          ? data
          : []
      );
    } catch {
      setMessage(
        "Unable to load artifacts."
      );
    }
  }

  const grouped = artifacts.reduce(
    (groups, artifact) => {
      if (
        !groups[
          artifact.artifact_type
        ]
      ) {
        groups[
          artifact.artifact_type
        ] = [];
      }

      groups[
        artifact.artifact_type
      ].push(artifact);

      return groups;
    },
    {}
  );

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Artifact Extraction</h2>

          <p>
            Extract forensic indicators from collected evidence.
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
          <h3>Extract Artifacts</h3>

          <p>
            Analyze files for strings, URLs, IP addresses,
            emails, and suspicious indicators.
          </p>
        </div>

        <div className="artifact-controls">
          <div className="form-group">
            <label>Evidence</label>

            <select
              value={selectedEvidence}
              onChange={event => {
                const value =
                  event.target.value;

                setSelectedEvidence(value);
                loadArtifacts(value);
              }}
            >
              <option value="">
                Select evidence
              </option>

              {evidence.map(item => (
                <option
                  key={item.evidence_id}
                  value={item.evidence_id}
                >
                  #{item.evidence_id} -{" "}
                  {item.file_name}
                </option>
              ))}
            </select>
          </div>

          <button
            className="primary-btn"
            onClick={extractArtifacts}
            disabled={
              extracting ||
              !selectedEvidence
            }
          >
            {extracting
              ? "Extracting..."
              : "Extract Artifacts"}
          </button>
        </div>
      </section>

      <section className="artifact-summary">
        {Object.entries(grouped).map(
          ([type, values]) => (
            <div
              className="artifact-stat"
              key={type}
            >
              <span>{type}</span>

              <strong>
                {values.length}
              </strong>
            </div>
          )
        )}
      </section>

      <section className="panel">
        <div className="panel-header">
          <h3>Extracted Artifacts</h3>

          <p>
            {artifacts.length} artifacts detected
          </p>
        </div>

        {artifacts.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              ⌁
            </div>

            <h3>No Artifacts</h3>

            <p>
              Select evidence and run artifact extraction.
            </p>
          </div>
        ) : (
          <div className="artifact-list">
            {artifacts.map(
              artifact => (
                <div
                  className="artifact-row"
                  key={artifact.artifact_id}
                >
                  <span
                    className={`artifact-type ${artifact.artifact_type.toLowerCase()}`}
                  >
                    {artifact.artifact_type}
                  </span>

                  <code>
                    {artifact.artifact_value}
                  </code>

                  <span className="artifact-source">
                    {artifact.source}
                  </span>
                </div>
              )
            )}
          </div>
        )}
      </section>
    </div>
  );
}

export default Artifacts;