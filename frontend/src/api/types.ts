export type Category =
  | "water"
  | "electricity"
  | "sanitation"
  | "roads"
  | "streetlights"
  | "other";

export type Priority = "high" | "normal" | "low";

export type Status =
  | "open"
  | "in_progress"
  | "resolved"
  | "rejected";

export type TriagedBy =
  | "llm:groq"
  | "llm:ollama"
  | "rules"
  | "rules:fallback";

export interface ComplaintCreate {
  text: string;
  location: string;
  reporter_contact?: string | null;
}

export interface ComplaintOut {
  id: string;
  text: string;
  location: string;
  reporter_contact: string | null;
  category: Category;
  priority: Priority;
  status: Status;
  ai_summary: string | null;
  triaged_by: TriagedBy;
  triage_latency_ms: number;
  created_at: string;
  updated_at: string;
}

export interface ComplaintList {
  items: ComplaintOut[];
  total: number;
  page: number;
  page_size: number;
}

export interface StatusUpdate {
  status: Status;
}

export interface ProviderOutcome {
  provider: string;
  latency_ms: number;
  fallback: boolean;
}

export interface ProvidersMeta {
  active_provider: string;
  recent_outcomes: ProviderOutcome[];
}

export interface StatsResponse {
  by_category: Record<Category, number>;
  by_priority: Record<Priority, number>;
}

export const ALLOWED_TRANSITIONS: Record<Status, Status[]> = {
  open: ["in_progress", "rejected"],
  in_progress: ["resolved", "rejected"],
  resolved: [],
  rejected: [],
};
