import { useEffect, useState } from "react";

import { getComplaints } from "../api/client";
import type {
  Category,
  ComplaintList,
  Priority,
  Status,
} from "../api/types";

const PAGE_SIZE = 10;

const categories: Category[] = [
  "water",
  "electricity",
  "sanitation",
  "roads",
  "streetlights",
  "other",
];

const priorities: Priority[] = [
  "high",
  "normal",
  "low",
];

const statuses: Status[] = [
  "open",
  "in_progress",
  "resolved",
  "rejected",
];

function Dashboard() {
  const [data, setData] = useState<ComplaintList | null>(null);

  const [page, setPage] = useState(1);
  const [category, setCategory] = useState("");
  const [priority, setPriority] = useState("");
  const [status, setStatus] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadComplaints() {
    setLoading(true);
    setError("");

    try {
      const complaints = await getComplaints({
        page,
        page_size: PAGE_SIZE,
        category: category || undefined,
        priority: priority || undefined,
        status: (status || undefined) as Status | undefined,
      });

      setData(complaints);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load complaints.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadComplaints();
  }, [page, category, priority, status]);

  function handleCategoryChange(
    event: React.ChangeEvent<HTMLSelectElement>,
  ) {
    setCategory(event.target.value);
    setPage(1);
  }

  function handlePriorityChange(
    event: React.ChangeEvent<HTMLSelectElement>,
  ) {
    setPriority(event.target.value);
    setPage(1);
  }

  function handleStatusChange(
    event: React.ChangeEvent<HTMLSelectElement>,
  ) {
    setStatus(event.target.value);
    setPage(1);
  }

  function clearFilters() {
    setCategory("");
    setPriority("");
    setStatus("");
    setPage(1);
  }

  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <section>
      <h1>Complaint Dashboard</h1>

      <div>
        <label htmlFor="category-filter">
          Category
        </label>

        <select
          id="category-filter"
          value={category}
          onChange={handleCategoryChange}
        >
          <option value="">All categories</option>

          {categories.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="priority-filter">
          Priority
        </label>

        <select
          id="priority-filter"
          value={priority}
          onChange={handlePriorityChange}
        >
          <option value="">All priorities</option>

          {priorities.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="status-filter">
          Status
        </label>

        <select
          id="status-filter"
          value={status}
          onChange={handleStatusChange}
        >
          <option value="">All statuses</option>

          {statuses.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>

      <button type="button" onClick={clearFilters}>
        Clear Filters
      </button>

      <p>
        Total complaints: {total}
      </p>

      {loading && <p>Loading complaints...</p>}

      {!loading && error && (
        <section>
          <p role="alert">{error}</p>

          <button
            type="button"
            onClick={() => void loadComplaints()}
          >
            Retry
          </button>
        </section>
      )}

      {!loading && !error && data && data.items.length > 0 && (
        <div>
          {data.items.map((complaint) => (
            <article key={complaint.id}>
              <h2>{complaint.category}</h2>

              <p>{complaint.text}</p>

              <p>
                <strong>Location:</strong>{" "}
                {complaint.location}
              </p>

              <p>
                <strong>Priority:</strong>{" "}
                {complaint.priority}
              </p>

              <p>
                <strong>Status:</strong>{" "}
                {complaint.status}
              </p>

              <p>
                <strong>Triaged by:</strong>{" "}
                {complaint.triaged_by}
              </p>

              <p>
                <strong>Summary:</strong>{" "}
                {complaint.ai_summary ??
                  "No summary available."}
              </p>
            </article>
          ))}
        </div>
      )}

      {!loading &&
        !error &&
        data &&
        data.items.length === 0 && (
          <p>No complaints found.</p>
        )}

      {!loading && !error && data && total > 0 && (
        <nav aria-label="Complaint pagination">
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => setPage((current) => current - 1)}
          >
            Previous
          </button>

          <span>
            {" "}
            Page {page} of {totalPages}{" "}
          </span>

          <button
            type="button"
            disabled={page >= totalPages}
            onClick={() => setPage((current) => current + 1)}
          >
            Next
          </button>
        </nav>
      )}
    </section>
  );
}

export default Dashboard;
