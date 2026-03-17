import { useEffect, useRef, useState } from "react";
import type { CalculateResponse } from "../types/calculator";

interface Props {
  result: CalculateResponse | null;
}

function easeOutExpo(t: number): number {
  return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
}

function useAnimatedNumber(target: number, duration = 600): number {
  const [displayed, setDisplayed] = useState(target);
  const prevRef = useRef(target);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    const from = prevRef.current;
    prevRef.current = target;

    if (from === target) return;

    const startTime = performance.now();

    const to = target;

    function tick(now: number) {
      const elapsed = now - startTime;
      const t = Math.min(elapsed / duration, 1);
      const eased = easeOutExpo(t);
      setDisplayed(from + (to - from) * eased);

      if (t < 1) {
        rafRef.current = requestAnimationFrame(tick);
      } else {
        setDisplayed(to);
      }
    }

    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, [target, duration]);

  return displayed;
}

function formatResult(animated: number, target: number): string {
  const decimalPlaces = (target.toString().split(".")[1] ?? "").length;
  if (decimalPlaces === 0) {
    return Math.round(animated).toLocaleString();
  }
  return animated.toFixed(decimalPlaces);
}

export function ResultDisplay({ result }: Props) {
  const target = result?.result ?? 0;
  const animated = useAnimatedNumber(target);

  if (!result) return null;

  return (
    <div className="result-box" role="status" aria-live="polite">
      <span className="result-expression">{result.expression}</span>
      <span className="result-value">{formatResult(animated, result.result)}</span>
    </div>
  );
}
