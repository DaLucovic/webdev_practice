import type { HistoryEntry } from "../types/calculator";

interface Props {
  entries: HistoryEntry[];
  isClearing: boolean;
  onClear: () => void;
  onSelect: (expression: string) => void;
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

export function HistoryList({ entries, isClearing, onClear, onSelect }: Props) {
  if (entries.length === 0) return null;

  // Newest first, max 8 visible
  const visible = [...entries].reverse().slice(0, 8);

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

      <div className="history-list-wrapper">
        {/* Each entry uses its timestamp as the key — timestamps are unique per entry. */}
        <ul className="history-list">
          {visible.map((entry, i) => (
            <li
              key={entry.timestamp}
              className="history-entry"
              style={{ "--i": i } as React.CSSProperties}
              onClick={() => onSelect(entry.expression)}
              title="Click to use this expression"
            >
              <span className="history-expression">{entry.expression}</span>
              <span className="history-equals"> = </span>
              <span className="history-result">{entry.result}</span>
              <span className="history-time">{formatTime(entry.timestamp)}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
