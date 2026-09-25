import { NavLink, Route, Routes } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Stats from "./pages/Stats";
import Submit from "./pages/Submit";

function App() {
  return (
    <>
      <header>
        <nav>
          <NavLink to="/">Submit Complaint</NavLink>
          {" | "}
          <NavLink to="/dashboard">Dashboard</NavLink>
          {" | "}
          <NavLink to="/stats">Statistics</NavLink>
        </nav>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<Submit />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/stats" element={<Stats />} />
        </Routes>
      </main>
    </>
  );
}

export default App;
