import { useEffect, useState } from "react";

import { getStats } from "../api/client";
import type { StatsResponse } from "../api/types";

function Stats() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadStats() {
    setLoading(true);
    setError("");

    try {
      const result = await getStats();
      setStats(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load statistics.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadStats();
  }, []);

  if (loading) {
    return <p>Loading statistics...</p>;
  }

  if (error) {
    return (
      <section>
        <h1>Statistics</h1>
        <p role="alert">{error}</p>

        <button type="button" onClick={() => void loadStats()}>
          Retry
        </button>
      </section>
    );
  }

  if (!stats) {
    return <p>No statistics available.</p>;
  }

  return (
    <section>
      <h1>Statistics</h1>

      <h2>Complaints by Category</h2>

      <ul>
        {Object.entries(stats.by_category).map(([category, count]) => (
          <li key={category}>
            <strong>{category}:</strong> {count}
          </li>
        ))}
      </ul>

      <h2>Complaints by Priority</h2>

      <ul>
        {Object.entries(stats.by_priority).map(([priority, count]) => (
          <li key={priority}>
            <strong>{priority}:</strong> {count}
          </li>
        ))}
      </ul>
    </section>
  );
}

export default Stats;
