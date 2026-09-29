import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";

import App from "../App";
import Submit from "../pages/Submit";
import Dashboard from "../pages/Dashboard";
import Stats from "../pages/Stats";

import * as api from "../api/client";

vi.mock("../api/client", () => ({
  createComplaint: vi.fn(),
  getComplaints: vi.fn(),
  updateComplaintStatus: vi.fn(),
  getStats: vi.fn(),
}));

describe("CivicPulse components", () => {
  it("renders the CivicPulse navigation", () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText("CivicPulse")).toBeInTheDocument();

    expect(
      screen.getByRole("link", { name: "Submit Complaint" })
    ).toBeInTheDocument();

    expect(
      screen.getByRole("link", { name: "Dashboard" })
    ).toBeInTheDocument();

    expect(
      screen.getByRole("link", { name: "Statistics" })
    ).toBeInTheDocument();
  });

  it("shows validation error for a complaint that is too short", async () => {
    render(
      <MemoryRouter>
        <Submit />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText("Complaint"), {
      target: { value: "Short" },
    });

    fireEvent.change(screen.getByLabelText("Location"), {
      target: { value: "Islamabad" },
    });

    fireEvent.click(
      screen.getByRole("button", { name: "Submit Complaint" })
    );

    expect(
      await screen.findByRole("alert")
    ).toHaveTextContent(
      "Complaint text must be between 10 and 2000 characters."
    );

    expect(api.createComplaint).not.toHaveBeenCalled();
  });

  it("submits a valid complaint successfully", async () => {
    vi.mocked(api.createComplaint).mockResolvedValue({
      id: "1",
      text: "There is a major water shortage in my area.",
      location: "Islamabad",
      reporter_contact: "03001234567",
      category: "water",
      priority: "normal",
      status: "open",
      ai_summary: null,
      triaged_by: "rules",
      triage_latency_ms: 10,
      created_at: "2026-09-29T10:00:00Z",
      updated_at: "2026-09-29T10:00:00Z",
    });

    render(
      <MemoryRouter>
        <Submit />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText("Complaint"), {
      target: {
        value: "There is a major water shortage in my area.",
      },
    });

    fireEvent.change(screen.getByLabelText("Location"), {
      target: { value: "Islamabad" },
    });

    fireEvent.change(screen.getByLabelText("Contact information (optional)"), {
      target: { value: "03001234567" },
    });

    fireEvent.click(
      screen.getByRole("button", { name: "Submit Complaint" })
    );

    await waitFor(() => {
      expect(api.createComplaint).toHaveBeenCalled();
    });
  });

  it("renders the complaint dashboard after loading", async () => {
    vi.mocked(api.getComplaints).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 10,
    });

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    expect(
      screen.getByText("Loading complaints...")
    ).toBeInTheDocument();

    await waitFor(() => {
      expect(
        screen.getByText("Complaint Dashboard")
      ).toBeInTheDocument();
    });

    expect(
      screen.getByText("Total complaints: 0")
    ).toBeInTheDocument();

    expect(
      screen.getByText("No complaints found.")
    ).toBeInTheDocument();
  });

  it("renders complaints returned by the dashboard API", async () => {
    vi.mocked(api.getComplaints).mockResolvedValue({
      items: [
        {
          id: "1",
          text: "Broken streetlights near the main road",
          location: "Islamabad",
          reporter_contact: "03001234567",
          category: "streetlights",
          priority: "high",
          status: "open",
          ai_summary: null,
          triaged_by: "rules",
          triage_latency_ms: 10,
          created_at: "2026-09-29T10:00:00Z",
          updated_at: "2026-09-29T10:00:00Z",
        },
      ],
      total: 1,
      page: 1,
      page_size: 10,
    });

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(
        screen.getByText("Broken streetlights near the main road")
      ).toBeInTheDocument();
    });

    expect(
      screen.getByText("Total complaints: 1")
    ).toBeInTheDocument();

    expect(screen.getByText("Islamabad")).toBeInTheDocument();

    expect(
      screen.getByRole("heading", { name: "streetlights" })
    ).toBeInTheDocument();

    expect(
      screen.getByText("high", { selector: "p" })
    ).toBeInTheDocument();

  });

  it("renders complaint statistics", async () => {
    vi.mocked(api.getStats).mockResolvedValue({
      by_category: {
        water: 5,
        electricity: 2,
        sanitation: 4,
        roads: 3,
        streetlights: 1,
        other: 2,
      },
      by_priority: {
        high: 2,
        normal: 4,
        low: 2,
      },
    });

    render(
      <MemoryRouter>
        <Stats />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: "Statistics" })
      ).toBeInTheDocument();
    });

    expect(screen.getByText("water:")).toBeInTheDocument();
    expect(screen.getByText("roads:")).toBeInTheDocument();
    expect(screen.getByText("high:")).toBeInTheDocument();
    expect(screen.getByText("normal:")).toBeInTheDocument();
  });

  it("clears complaint dashboard filters", async () => {
    vi.mocked(api.getComplaints).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 10,
    });

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(
        screen.getByText("Complaint Dashboard")
      ).toBeInTheDocument();
    });

    const categoryFilter = screen.getByLabelText("Category");

    fireEvent.change(categoryFilter, {
      target: { value: "water" },
    });

    expect(categoryFilter).toHaveValue("water");

    fireEvent.click(
      screen.getByRole("button", { name: "Clear Filters" })
    );

    expect(categoryFilter).toHaveValue("");
  });
});
