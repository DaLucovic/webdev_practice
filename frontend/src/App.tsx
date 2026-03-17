import { useEffect, useState } from "react";
import { calculate, clearHistory, getHistory } from "./api/calculator";
import { ErrorMessage } from "./components/ErrorMessage";
import { ExpressionInput } from "./components/ExpressionInput";
import { HistoryList } from "./components/HistoryList";
import { ResultDisplay } from "./components/ResultDisplay";
import type { CalculateResponse, HistoryEntry } from "./types/calculator";

export default function App() {
  const [expression, setExpression] = useState("");
  const [result, setResult] = useState<CalculateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [isClearing, setIsClearing] = useState(false);

  // useEffect runs side effects — code that doesn't belong in the render itself.
  // The empty [] means "run once when the component first mounts", like an __init__.
  // Here we load any existing history the server already has when the page opens.
  useEffect(() => {
    getHistory()
      .then(setHistory)
      .catch(() => {}); // silently ignore — history failing to load is non-critical
  }, []);

  async function handleSubmit() {
    setError(null);
    setResult(null);
    setIsLoading(true);

    try {
      const response = await calculate(expression);
      setResult(response);
      // Re-fetch history so the new entry appears immediately.
      const updated = await getHistory();
      setHistory(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleClearHistory() {
    setIsClearing(true);
    try {
      await clearHistory();
      setHistory([]);
    } finally {
      setIsClearing(false);
    }
  }

  function handleSelect(expr: string) {
    setExpression(expr);
  }

  return (
    <>
      <div className="bg">
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <div className="orb orb-3" />
      </div>
      <main className="container">
        <h1>Expression Calculator</h1>

        <ExpressionInput
          value={expression}
          isLoading={isLoading}
          onChange={setExpression}
          onSubmit={handleSubmit}
        />

        <ResultDisplay result={result} />
        {/* key={error} causes React to remount on each new error, re-triggering the shake animation */}
        <ErrorMessage key={error} message={error} />

        <HistoryList
          entries={history}
          isClearing={isClearing}
          onClear={handleClearHistory}
          onSelect={handleSelect}
        />
      </main>
    </>
  );
}
