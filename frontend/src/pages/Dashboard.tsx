import { useEffect, useState } from "react";

import {
  getComplaints,
  updateComplaintStatus,
} from "../api/client";

import type {
  Category,
  ComplaintList,
  Priority,
  Status,
} from "../api/types";

import { ALLOWED_TRANSITIONS } from "../api/types";

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

  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [updateError, setUpdateError] = useState("");

  const [selectedStatuses, setSelectedStatuses] = useState<
    Record<string, Status>
  >({});

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

      const initialStatuses: Record<string, Status> = {};

      for (const complaint of complaints.items) {
        initialStatuses[complaint.id] = complaint.status;
      }

      setSelectedStatuses(initialStatuses);
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

  function handleSelectedStatusChange(
    complaintId: string,
    newStatus: Status,
  ) {
    setSelectedStatuses((current) => ({
      ...current,
      [complaintId]: newStatus,
    }));
  }

  async function handleStatusUpdate(
    complaintId: string,
    currentStatus: Status,
  ) {
    const newStatus = selectedStatuses[complaintId];

    if (!newStatus || newStatus === currentStatus) {
      return;
    }

    setUpdatingId(complaintId);
    setUpdateError("");

    try {
      const updatedComplaint = await updateComplaintStatus(
        complaintId,
        newStatus,
      );

      setData((current) => {
        if (!current) {
          return current;
        }

        return {
          ...current,
          items: current.items.map((complaint) =>
            complaint.id === complaintId
              ? updatedComplaint
              : complaint,
          ),
        };
      });

      setSelectedStatuses((current) => ({
        ...current,
        [complaintId]: updatedComplaint.status,
      }));
    } catch (err) {
      setUpdateError(
        err instanceof Error
          ? err.message
          : "Failed to update complaint status.",
      );
    } finally {
      setUpdatingId(null);
    }
  }

  const total = data?.total ?? 0;
  const totalPages = Math.max(
    1,
    Math.ceil(total / PAGE_SIZE),
  );

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

      <p>Total complaints: {total}</p>

      {updateError && (
        <p role="alert">{updateError}</p>
      )}

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

      {!loading &&
        !error &&
        data &&
        data.items.length > 0 && (
          <div>
            {data.items.map((complaint) => {
              const allowedStatuses =
                ALLOWED_TRANSITIONS[complaint.status];

              const currentSelection =
                selectedStatuses[complaint.id] ??
                complaint.status;

              return (
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

                  {allowedStatuses.length > 0 && (
                    <div>
                      <label
                        htmlFor={`status-${complaint.id}`}
                      >
                        Change status
                      </label>

                      <select
                        id={`status-${complaint.id}`}
                        value={currentSelection}
                        onChange={(event) =>
                          handleSelectedStatusChange(
                            complaint.id,
                            event.target.value as Status,
                          )
                        }
                        disabled={
                          updatingId === complaint.id
                        }
                      >
                        <option value={complaint.status}>
                          {complaint.status}
                        </option>

                        {allowedStatuses.map(
                          (nextStatus) => (
                            <option
                              key={nextStatus}
                              value={nextStatus}
                            >
                              {nextStatus}
                            </option>
                          ),
                        )}
                      </select>

                      <button
                        type="button"
                        disabled={
                          updatingId === complaint.id ||
                          currentSelection ===
                            complaint.status
                        }
                        onClick={() =>
                          void handleStatusUpdate(
                            complaint.id,
                            complaint.status,
                          )
                        }
                      >
                        {updatingId === complaint.id
                          ? "Updating..."
                          : "Update Status"}
                      </button>
                    </div>
                  )}
                </article>
              );
            })}
          </div>
        )}

      {!loading &&
        !error &&
        data &&
        data.items.length === 0 && (
          <p>No complaints found.</p>
        )}

      {!loading &&
        !error &&
        data &&
        total > 0 && (
          <nav aria-label="Complaint pagination">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() =>
                setPage((current) => current - 1)
              }
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
              onClick={() =>
                setPage((current) => current + 1)
              }
            >
              Next
            </button>
          </nav>
        )}
    </section>
  );
}

export default Dashboard;
