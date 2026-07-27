// Typed client for the PAISAI API. Every figure returned carries its provenance,
// or is an explicit "unavailable" — the client preserves that distinction so the
// UI can render fact vs. forecast vs. missing honestly.

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
  "http://localhost:8000";

export type Provenance =
  | "Verified"
  | "Calculated"
  | "Estimated"
  | "Projected"
  | "User Provided"
  | "Assumed";

export interface ProvenancedValue {
  value: number;
  provenance: Provenance;
  label?: string;
  unit?: string;
  source?: string;
  as_of?: string;
  method?: string;
  note?: string;
  inputs?: ProvenancedValue[];
}

export interface Unavailable {
  available: false;
  reason: string;
  label?: string;
}

export type Figure = ProvenancedValue | Unavailable;

export function isUnavailable(
  f: Figure | Record<string, ProvenancedValue>,
): f is Unavailable {
  return (f as Unavailable).available === false;
}

export interface DashboardInput {
  assets?: number;
  liabilities?: number;
  monthly_income?: number;
  monthly_expenses?: number;
  liquid_savings?: number;
  holdings?: Record<string, number>;
}

export interface DashboardResult {
  net_worth: Figure;
  savings_rate: Figure;
  emergency_fund_months: Figure;
  portfolio_weights: Record<string, ProvenancedValue> | Unavailable;
  notes: string[];
}

export interface JournalEntryInput {
  date: string;
  asset: string;
  action: string;
  thesis: string;
  expected_outcome: string;
  time_horizon: string;
  review_date: string;
  confidence: string;
  market_context?: string;
  expected_return?: number;
  risk_factors?: string[];
  assumptions?: string[];
  alternatives?: { option: string; rejection_reason: string }[];
  sources?: string[];
  emotional_state?: string;
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly detail?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    });
  } catch (e) {
    // Network/CORS failure — be honest that the backend is unreachable.
    throw new ApiError(
      "Could not reach the PAISAI API. Is the backend running?",
      0,
      String(e),
    );
  }
  const text = await res.text();
  const body = text ? JSON.parse(text) : null;
  if (!res.ok) {
    throw new ApiError(
      body?.error || `Request failed (${res.status})`,
      res.status,
      body?.detail,
    );
  }
  return body as T;
}

export const api = {
  health: () => request<{ status: string; version: string }>("/health"),

  dashboard: (input: DashboardInput) =>
    request<DashboardResult>("/v1/dashboard", {
      method: "POST",
      body: JSON.stringify(input),
    }),

  createJournalEntry: (entry: JournalEntryInput) =>
    request<{ id: string; entry: Record<string, unknown> }>("/v1/journal", {
      method: "POST",
      body: JSON.stringify(entry),
    }),

  reviewDue: (onOrBefore: string) =>
    request<{ count: number; entries: Record<string, unknown>[] }>(
      `/v1/journal/review-due?on_or_before=${encodeURIComponent(onOrBefore)}`,
    ),

  verifyAudit: () =>
    request<{ intact: boolean; records_checked?: number; detail?: string }>(
      "/v1/audit/verify",
    ),

  fund: (schemeCode: string) =>
    request<{ scheme_code: string; nav: Figure; limitations: string[] }>(
      `/v1/fund/${encodeURIComponent(schemeCode)}`,
    ),
};

// --- formatting helpers -----------------------------------------------------

export function formatFigureValue(f: ProvenancedValue): string {
  const { value, unit } = f;
  if (unit === "fraction") return `${(value * 100).toFixed(1)}%`;
  if (unit === "months") return `${value.toFixed(1)} months`;
  if (unit === "currency" || unit === undefined || unit === "") {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(value);
  }
  return `${value}`;
}
