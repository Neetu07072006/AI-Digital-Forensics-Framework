function Navbar() {
  return (
    <header className="navbar">
      <div>
        <h1>Investigation Dashboard</h1>
        <p>AI-powered digital forensic investigation</p>
      </div>

      <div className="investigator">
        <div className="avatar">I</div>
        <div>
          <strong>Investigator</strong>
          <span>Forensic Analyst</span>
        </div>
      </div>
    </header>
  );
}

export default Navbar;