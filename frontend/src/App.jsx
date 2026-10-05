import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Cases from "./pages/Cases";
import Evidence from "./pages/Evidence";
import Timeline from "./pages/Timeline";
import Artifacts from "./pages/Artifacts";
import Analysis from "./pages/Analysis";
import AIInvestigation from "./pages/AIInvestigation";
import Reports from "./pages/Reports";
import AuditLogs from "./pages/AuditLogs";

function AppLayout() {
  return (
    <div className="app-layout">
      <Sidebar />

      <div className="main-area">
        <Navbar />

        <main className="content">
          <Routes>
            <Route
              path="/"
              element={<Dashboard />}
            />

            <Route
              path="/cases"
              element={<Cases />}
            />

            <Route
              path="/evidence"
              element={<Evidence />}
            />

            <Route
              path="/timeline"
              element={<Timeline />}
            />

            <Route
              path="/artifacts"
              element={<Artifacts />}
            />

            <Route
              path="/analysis"
              element={<Analysis />}
            />

            <Route
              path="/ai-investigation"
              element={<AIInvestigation />}
            />

            <Route
              path="/reports"
              element={<Reports />}
            />

            <Route
              path="/audit"
              element={<AuditLogs />}
            />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;