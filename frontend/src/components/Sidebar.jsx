import { NavLink, useNavigate } from "react-router-dom";

const links = [
  { path: "/", label: "Dashboard", icon: "▦" },
  { path: "/cases", label: "Cases", icon: "◫" },
  { path: "/evidence", label: "Evidence", icon: "◈" },
  { path: "/timeline", label: "Timeline", icon: "◷" },
  { path: "/artifacts", label: "Artifacts", icon: "⌁" },
  { path: "/analysis", label: "AI Analysis", icon: "◆" },
  {
    path: "/ai-investigation",
    label: "AI Investigation",
    icon: "✦"
  },
  { path: "/reports", label: "Reports", icon: "▤" },
  { path: "/audit", label: "Audit Logs", icon: "◉" }
];

function Sidebar() {
  const navigate = useNavigate();

  const user = JSON.parse(
    localStorage.getItem("forensics_user") || "null"
  );

  function handleLogout() {
    localStorage.removeItem("forensics_token");
    localStorage.removeItem("forensics_user");
    navigate("/login");
  }

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">⚖</div>

        <div>
          <h2>Forensics AI</h2>
          <span>
            Investigation Framework
          </span>
        </div>
      </div>

      <nav className="nav-menu">
        {links.map(link => (
          <NavLink
            key={link.path}
            to={link.path}
            className={({ isActive }) =>
              `nav-item ${
                isActive ? "active" : ""
              }`
            }
          >
            <span className="nav-icon">
              {link.icon}
            </span>

            <span>{link.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        {user && (
          <div className="sidebar-user">
            <div className="user-avatar">
              {user.username
                ?.charAt(0)
                .toUpperCase()}
            </div>

            <div>
              <strong>
                {user.username}
              </strong>

              <span>
                {user.role}
              </span>
            </div>
          </div>
        )}

        <div className="system-status">
          <span className="status-dot"></span>
          <span>System Online</span>
        </div>

        <button
          className="logout-btn"
          onClick={handleLogout}
        >
          Logout
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;