import type { HistoryEntry } from "../types/calculator";

interface Props {
  entries: HistoryEntry[];
  isClearing: boolean;
  onClear: () => void;
}

// Format the ISO timestamp the backend sends into a readable local time.
// new Date(isoString) parses it; toLocaleTimeString() formats it for the user's locale.
function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function HistoryList({ entries, isClearing, onClear }: Props) {
  if (entries.length === 0) return null;

  return (
    <section className="history">
      <div className="history-header">
        <h2>History</h2>
        <button
          className="clear-button"
          onClick={onClear}
          disabled={isClearing}
        >
          {isClearing ? "Clearing…" : "Clear"}
        </button>
      </div>

      {/* Each entry uses its timestamp as the key — timestamps are unique per entry. */}
      <ul className="history-list">
        {entries.map((entry) => (
          <li key={entry.timestamp} className="history-entry">
            <span className="history-expression">{entry.expression}</span>
            <span className="history-equals"> = </span>
            <span className="history-result">{entry.result}</span>
            <span className="history-time">{formatTime(entry.timestamp)}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
