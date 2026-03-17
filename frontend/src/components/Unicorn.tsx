import { useEffect, useRef, useState } from "react";

export function Unicorn() {
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [flip, setFlip] = useState(false);

  const targetRef = useRef({ x: 0, y: 0 });
  const currentRef = useRef({ x: 0, y: 0 });
  const rafRef = useRef<number>(0);

  useEffect(() => {
    function onMouseMove(e: MouseEvent) {
      const cx = window.innerWidth / 2;
      const cy = window.innerHeight / 2;
      targetRef.current = {
        x: ((e.clientX - cx) / cx) * 50,
        y: ((e.clientY - cy) / cy) * 25,
      };
      setFlip(e.clientX < cx);
    }

    function loop() {
      const cur = currentRef.current;
      const tgt = targetRef.current;
      cur.x += (tgt.x - cur.x) * 0.05;
      cur.y += (tgt.y - cur.y) * 0.05;
      setOffset({ x: cur.x, y: cur.y });
      rafRef.current = requestAnimationFrame(loop);
    }

    window.addEventListener("mousemove", onMouseMove);
    rafRef.current = requestAnimationFrame(loop);

    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      cancelAnimationFrame(rafRef.current);
    };
  }, []);

  return (
    <div
      className="unicorn-wrapper"
      style={{ transform: `translate(${offset.x}px, ${offset.y}px)` }}
    >
      <div className="unicorn-inner">
        <span className="unicorn-sparkle s1" />
        <span className="unicorn-sparkle s2" />
        <span className="unicorn-sparkle s3" />
        <span
          className="unicorn-emoji"
          style={{ transform: flip ? "scaleX(-1)" : undefined }}
        >
          🦄
        </span>
        <span className="unicorn-shadow" />
      </div>
    </div>
  );
}
