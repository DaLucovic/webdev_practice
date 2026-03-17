// This module owns all communication with the FastAPI backend.
// Think of it like a Python service layer — routes never call fetch() directly.
//
// The /api prefix is stripped by the Vite dev proxy (see vite.config.ts)
// and forwarded to http://localhost:8000.

import type { ApiErrorDetail, CalculateResponse, HistoryEntry } from "../types/calculator";

// import.meta.env is Vite's equivalent of os.environ in Python.
// Falls back to "/api" so the dev proxy still works if the variable is unset.
const BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

// fetch() is the browser's built-in HTTP client — equivalent to requests.post() in Python.
// It is always async; you must await it (or .then() it).

function extractErrorMessage(detail: ApiErrorDetail): string {
  if (typeof detail === "string") return detail;
  // Pydantic validation error: array of objects — surface the first message.
  return detail[0]?.msg ?? "An unknown validation error occurred.";
}

export async function calculate(expression: string): Promise<CalculateResponse> {
  const response = await fetch(`${BASE}/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    // JSON.stringify is the JS equivalent of json.dumps()
    body: JSON.stringify({ expression }),
  });

  if (!response.ok) {
    const body = await response.json();
    throw new Error(extractErrorMessage(body.detail));
  }

  return response.json() as Promise<CalculateResponse>;
}

export async function getHistory(): Promise<HistoryEntry[]> {
  const response = await fetch(`${BASE}/history`);
  if (!response.ok) throw new Error("Failed to fetch history.");
  return response.json() as Promise<HistoryEntry[]>;
}

export async function clearHistory(): Promise<void> {
  const response = await fetch(`${BASE}/history`, { method: "DELETE" });
  if (!response.ok) throw new Error("Failed to clear history.");
}
