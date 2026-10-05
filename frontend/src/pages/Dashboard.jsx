import { useEffect, useState } from "react";
import StatCard from "../components/StatCard";

const API_URL = "http://127.0.0.1:8001";

function Dashboard() {
  const [cases, setCases] = useState([]);
  const [evidence, setEvidence] = useState([]);
  const [backendStatus, setBackendStatus] = useState("Checking...");

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      const token = localStorage.getItem(
        "forensics_token"
      );

      if (!token) {
        setBackendStatus("Authentication Required");
        return;
      }

      const healthResponse = await fetch(
        `${API_URL}/api/health`
      );

      const healthData = await healthResponse.json();

      setBackendStatus(
        healthData.backend === "online"
          ? "Online"
          : "Offline"
      );

      const authHeaders = {
        Authorization: `Bearer ${token}`
      };

      const casesResponse = await fetch(
        `${API_URL}/api/cases/`,
        {
          headers: authHeaders
        }
      );

      if (casesResponse.status === 401) {
        localStorage.removeItem(
          "forensics_token"
        );
        localStorage.removeItem(
          "forensics_user"
        );
        window.location.href = "/login";
        return;
      }

      if (!casesResponse.ok) {
        throw new Error(
          "Failed to load cases"
        );
      }

      const casesData =
        await casesResponse.json();

      setCases(
        Array.isArray(casesData)
          ? casesData
          : []
      );

      const evidenceResponse = await fetch(
        `${API_URL}/api/evidence/`,
        {
          headers: authHeaders
        }
      );

      if (evidenceResponse.status === 401) {
        localStorage.removeItem(
          "forensics_token"
        );
        localStorage.removeItem(
          "forensics_user"
        );
        window.location.href = "/login";
        return;
      }

      if (!evidenceResponse.ok) {
        throw new Error(
          "Failed to load evidence"
        );
      }

      const evidenceData =
        await evidenceResponse.json();

      setEvidence(
        Array.isArray(evidenceData)
          ? evidenceData
          : []
      );
    } catch (error) {
      console.error(error);
      setBackendStatus("Offline");
      setCases([]);
      setEvidence([]);
    }
  }

  const highPriorityCases = cases.filter(
    (item) =>
      item.priority === "High" ||
      item.priority === "Critical"
  ).length;

  return (
    <div className="dashboard">
      <div className="page-header">
        <div>
          <h2>Overview</h2>
          <p>
            Monitor your digital forensic investigations
            from one place.
          </p>
        </div>

        <div className="connection-status">
          <span className="status-dot"></span>
          Backend {backendStatus}
        </div>
      </div>

      <div className="stats-grid">
        <StatCard
          title="Total Cases"
          value={cases.length}
          description="Registered investigations"
          icon="◫"
        />

        <StatCard
          title="Evidence Files"
          value={evidence.length}
          description="Digital evidence collected"
          icon="◈"
        />

        <StatCard
          title="High Priority"
          value={highPriorityCases}
          description="Cases requiring attention"
          icon="!"
        />

        <StatCard
          title="System Status"
          value={backendStatus}
          description="FastAPI backend connection"
          icon="✓"
        />
      </div>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Recent Cases</h3>
            <p>Latest forensic investigations</p>
          </div>
        </div>

        {cases.length === 0 ? (
          <div className="empty-state">
            No cases found.
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

            {cases.slice(0, 8).map((item) => (
              <div
                className="table-row"
                key={item.case_id}
              >
                <span>#{item.case_id}</span>
                <span>{item.case_name}</span>
                <span>{item.investigator}</span>
                <span>
                  <span
                    className={`priority ${item.priority.toLowerCase()}`}
                  >
                    {item.priority}
                  </span>
                </span>
                <span>{item.status}</span>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Dashboard;