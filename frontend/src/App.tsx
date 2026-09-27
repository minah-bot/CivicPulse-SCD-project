import { NavLink, Route, Routes } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Stats from "./pages/Stats";
import Submit from "./pages/Submit";

function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>CivicPulse</h1>

        <nav className="app-nav">
          <NavLink to="/" end>
            Submit Complaint
          </NavLink>

          <NavLink to="/dashboard">
            Dashboard
          </NavLink>

          <NavLink to="/stats">
            Statistics
          </NavLink>
        </nav>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<Submit />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/stats" element={<Stats />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
