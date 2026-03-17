// These types mirror the Pydantic models in app/models/calculator.py.
// TypeScript interfaces are purely compile-time — they disappear at runtime,
// unlike Pydantic which validates at runtime. When you change a backend model,
// update the matching interface here.

export interface CalculateRequest {
  expression: string;
}

export interface CalculateResponse {
  expression: string;
  result: number;
}

export interface HistoryEntry {
  expression: string;
  result: number;
  timestamp: string; // ISO 8601 string — use new Date(timestamp) to parse
}

// FastAPI sends two possible error shapes:
//   - Pydantic validation errors: detail is an array of objects
//   - HTTPException errors: detail is a plain string
type ValidationDetail = { loc: string[]; msg: string; type: string };
export type ApiErrorDetail = string | ValidationDetail[];
