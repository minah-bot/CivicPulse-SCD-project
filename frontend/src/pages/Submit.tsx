import { useState } from "react";
import type { FormEvent } from "react";

import { createComplaint } from "../api/client";
import type { ComplaintOut } from "../api/types";
function Submit() {
  const [text, setText] = useState("");
  const [location, setLocation] = useState("");
  const [contact, setContact] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ComplaintOut | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setResult(null);

    const trimmedText = text.trim();
    const trimmedLocation = location.trim();
    const trimmedContact = contact.trim();

    if (trimmedText.length < 10 || trimmedText.length > 2000) {
      setError("Complaint text must be between 10 and 2000 characters.");
      return;
    }

    if (
      trimmedLocation.length < 3 ||
      trimmedLocation.length > 200
    ) {
      setError("Location must be between 3 and 200 characters.");
      return;
    }

    setLoading(true);

    try {
      const complaint = await createComplaint({
        text: trimmedText,
        location: trimmedLocation,
        reporter_contact: trimmedContact || null,
      });

      setResult(complaint);
      setText("");
      setLocation("");
      setContact("");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to submit complaint.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <h1>Submit a Complaint</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="complaint-text">
            Complaint
          </label>

          <textarea
            id="complaint-text"
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder="Describe the civic issue..."
            minLength={10}
            maxLength={2000}
            required
            rows={6}
          />

          <small>
            {text.length}/2000 characters
          </small>
        </div>

        <div>
          <label htmlFor="location">
            Location
          </label>

          <input
            id="location"
            type="text"
            value={location}
            onChange={(event) => setLocation(event.target.value)}
            placeholder="Enter the location of the issue"
            minLength={3}
            maxLength={200}
            required
          />
        </div>

        <div>
          <label htmlFor="contact">
            Contact information (optional)
          </label>

          <input
            id="contact"
            type="text"
            value={contact}
            onChange={(event) => setContact(event.target.value)}
            placeholder="Phone or email"
          />
        </div>

        {error && (
          <p role="alert">
            {error}
          </p>
        )}

        <button type="submit" disabled={loading}>
          {loading ? "Submitting..." : "Submit Complaint"}
        </button>
      </form>

      {result && (
        <section>
          <h2>Complaint Submitted</h2>

          <p>
            <strong>Category:</strong>{" "}
            {result.category}
          </p>

          <p>
            <strong>Priority:</strong>{" "}
            {result.priority}
          </p>

          <p>
            <strong>Status:</strong>{" "}
            {result.status}
          </p>

          <p>
            <strong>AI Summary:</strong>{" "}
            {result.ai_summary ?? "No summary available."}
          </p>

          <p>
            <strong>Triaged by:</strong>{" "}
            {result.triaged_by}
          </p>
        </section>
      )}
    </section>
  );
}

export default Submit;