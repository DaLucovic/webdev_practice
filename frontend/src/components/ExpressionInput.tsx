// A "controlled component": React owns the input value via `value` + `onChange`.
// This is different from plain HTML where the DOM owns the value.
// The pattern: user types → onChange fires → parent updates state → React re-renders input.
//
// Props are the component's public API — like function parameters in Python.

interface Props {
  value: string;
  isLoading: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
}

export function ExpressionInput({ value, isLoading, onChange, onSubmit }: Props) {
  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") onSubmit();
  }

  return (
    <div className="input-row">
      <input
        type="text"
        value={value}
        placeholder="e.g. 2 + 3 * (10 / 2)"
        disabled={isLoading}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        className="expression-input"
        aria-label="Mathematical expression"
        autoFocus
      />
      <button
        onClick={onSubmit}
        disabled={isLoading || value.trim() === ""}
        className="submit-button"
      >
        {isLoading ? (
          <>
            <span className="spinner" aria-hidden="true" />
            Calculating…
          </>
        ) : (
          "Calculate"
        )}
      </button>
    </div>
  );
}
