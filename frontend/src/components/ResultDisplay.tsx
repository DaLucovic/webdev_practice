// Returning null from a component renders nothing — React's equivalent of
// a conditional st.write() in Streamlit.

import type { CalculateResponse } from "../types/calculator";

interface Props {
  result: CalculateResponse | null;
}

export function ResultDisplay({ result }: Props) {
  if (!result) return null;

  return (
    <div className="result-box" role="status" aria-live="polite">
      <span className="result-expression">{result.expression}</span>
      {" = "}
      <span className="result-value">{result.result}</span>
    </div>
  );
}
