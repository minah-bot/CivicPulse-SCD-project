import { useEffect, useState } from "react";

import {
  getComplaints,
  updateComplaintStatus,
} from "../api/client";
import type {
  ComplaintList,
  Status,
} from "../api/types";
import { ALLOWED_TRANSITIONS } from "../api/types";

function Dashboard() {
  const [data, setData] = useState<ComplaintList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  async function loadComplaints() {
    setLoading(true);
    setError("");

    try {
      const complaints = await getComplaints({
        page: 1,
        page_size: 20,
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
  }, []);

  async function handleStatusChange(
    id: string,
    status: Status,
  ) {
    setError("");
    setUpdatingId(id);

    try {
      const updatedComplaint = await updateComplaintStatus(
        id,
        status,
      );

      setData((current) => {
        if (!current) {
          return current;
        }

        return {
          ...current,
          items: current.items.map((complaint) =>
            complaint.id === id
              ? updatedComplaint
              : complaint,
          ),
        };
      });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update complaint status.",
      );
    } finally {
      setUpdatingId(null);
    }
  }

  if (loading) {
    return <p>Loading complaints...</p>;
  }

  if (error && !data) {
    return (
      <section>
        <h1>Complaint Dashboard</h1>
        <p role="alert">{error}</p>

        <button
          type="button"
          onClick={() => void loadComplaints()}
        >
          Retry
        </button>
      </section>
    );
  }

  return (
    <section>
      <h1>Complaint Dashboard</h1>

      {error && (
        <p role="alert">
          {error}
        </p>
      )}

      <p>
        Total complaints: {data?.total ?? 0}
      </p>

      {data && data.items.length > 0 ? (
        <div>
          {data.items.map((complaint) => {
            const allowedStatuses =
              ALLOWED_TRANSITIONS[complaint.status];

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
                    <strong>Update status:</strong>{" "}

                    {allowedStatuses.map((status) => (
                      <button
                        key={status}
                        type="button"
                        disabled={updatingId === complaint.id}
                        onClick={() =>
                          void handleStatusChange(
                            complaint.id,
                            status,
                          )
                        }
                      >
                        {updatingId === complaint.id
                          ? "Updating..."
                          : status}
                      </button>
                    ))}
                  </div>
                )}
              </article>
            );
          })}
        </div>
      ) : (
        <p>No complaints found.</p>
      )}
    </section>
  );
}

export default Dashboard;
