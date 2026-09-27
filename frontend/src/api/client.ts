import type {
  ComplaintCreate,
  ComplaintList,
  ComplaintOut,
  ProvidersMeta,
  StatsResponse,
  Status,
} from "./types";

const API_BASE = "/api";

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const body = await response.json();
      message = body.detail || body.message || message;
    } catch {
      // Keep default message when response isn't JSON.
    }

    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function createComplaint(
  data: ComplaintCreate,
): Promise<ComplaintOut> {
  return request<ComplaintOut>("/complaints", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getComplaints(params?: {
  page?: number;
  page_size?: number;
  category?: string;
  priority?: string;
  status?: Status;
}): Promise<ComplaintList> {
  const query = new URLSearchParams();

  if (params?.page !== undefined) query.set("page", String(params.page));
  if (params?.page_size !== undefined) {
    query.set("page_size", String(params.page_size));
  }
  if (params?.category) query.set("category", params.category);
  if (params?.priority) query.set("priority", params.priority);
  if (params?.status) query.set("status", params.status);

  const queryString = query.toString();

  return request<ComplaintList>(
    `/complaints${queryString ? `?${queryString}` : ""}`,
  );
}

export async function updateComplaintStatus(
  id: string,
  status: Status,
): Promise<ComplaintOut> {
  return request<ComplaintOut>(`/complaints/${id}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export async function getStats(): Promise<StatsResponse> {
  return request<StatsResponse>("/stats");
}

export async function getProviders(): Promise<ProvidersMeta> {
  return request<ProvidersMeta>("/providers");
}
