import { useEffect, useRef, useState } from "react";

export function Fox() {
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [rotation, setRotation] = useState(0);
  const [eyeOffset, setEyeOffset] = useState({ x: 0, y: 0 });

  const tOffRef = useRef({ x: 0, y: 0 });
  const cOffRef = useRef({ x: 0, y: 0 });
  const tRotRef = useRef(0);
  const cRotRef = useRef(0);
  const tEyeRef = useRef({ x: 0, y: 0 });
  const cEyeRef = useRef({ x: 0, y: 0 });
  const rafRef = useRef<number>(0);

  useEffect(() => {
    function onMouseMove(e: MouseEvent) {
      const vcx = window.innerWidth / 2;
      const vcy = window.innerHeight / 2;

      tOffRef.current = {
        x: ((e.clientX - vcx) / vcx) * 40,
        y: ((e.clientY - vcy) / vcy) * 20,
      };

      // Fox head centre in viewport (fixed: left 2rem ≈ 32px + 40px half-width)
      const foxX = 72;
      const foxY = window.innerHeight - 72;
      const dx = e.clientX - foxX;
      const dy = e.clientY - foxY;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;

      // Head leans toward cursor, clamped ±25°
      const rawAngle = Math.atan2(dx, -dy) * (180 / Math.PI);
      tRotRef.current = Math.max(-25, Math.min(25, rawAngle * 0.4));

      // Pupils track cursor direction, max 2.5 px from centre
      tEyeRef.current = {
        x: (dx / dist) * 2.5,
        y: (dy / dist) * 2.5,
      };
    }

    function loop() {
      const L = 0.07;
      cOffRef.current.x += (tOffRef.current.x - cOffRef.current.x) * L;
      cOffRef.current.y += (tOffRef.current.y - cOffRef.current.y) * L;
      cRotRef.current += (tRotRef.current - cRotRef.current) * L;
      cEyeRef.current.x += (tEyeRef.current.x - cEyeRef.current.x) * 0.1;
      cEyeRef.current.y += (tEyeRef.current.y - cEyeRef.current.y) * 0.1;

      setOffset({ x: cOffRef.current.x, y: cOffRef.current.y });
      setRotation(cRotRef.current);
      setEyeOffset({ x: cEyeRef.current.x, y: cEyeRef.current.y });

      rafRef.current = requestAnimationFrame(loop);
    }

    window.addEventListener("mousemove", onMouseMove);
    rafRef.current = requestAnimationFrame(loop);

    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      cancelAnimationFrame(rafRef.current);
    };
  }, []);

  const ex = eyeOffset.x;
  const ey = eyeOffset.y;

  return (
    <div
      className="fox-wrapper"
      style={{ transform: `translate(${offset.x}px, ${offset.y}px)` }}
    >
      <div className="fox-container">
        {/* Rotation pivots around the head centre (50% 65% of the SVG height) */}
        <div
          className="fox-rotate"
          style={{ transform: `rotate(${rotation}deg)` }}
        >
          <svg
            className="fox-svg"
            width="80"
            height="80"
            viewBox="0 0 80 80"
            aria-hidden
          >
            {/* Left ear */}
            <polygon points="8,46 18,8 30,44" fill="#e4761b" />
            <polygon points="13,43 18,17 26,41" fill="#f6851b" />
            {/* Right ear */}
            <polygon points="72,46 62,8 50,44" fill="#e4761b" />
            <polygon points="67,43 62,17 54,41" fill="#f6851b" />
            {/* Head */}
            <ellipse cx="40" cy="52" rx="28" ry="24" fill="#f6851b" />
            {/* Forehead band */}
            <ellipse cx="40" cy="40" rx="20" ry="14" fill="#e4761b" opacity="0.55" />
            {/* Face cream */}
            <ellipse cx="40" cy="59" rx="17" ry="16" fill="#fdebd0" />
            {/* Left eye white */}
            <circle cx="28" cy="50" r="6.5" fill="white" />
            {/* Right eye white */}
            <circle cx="52" cy="50" r="6.5" fill="white" />
            {/* Left pupil */}
            <circle cx={28 + ex} cy={50 + ey} r="4" fill="#1a0a00" />
            {/* Right pupil */}
            <circle cx={52 + ex} cy={50 + ey} r="4" fill="#1a0a00" />
            {/* Eye glints */}
            <circle cx={27 + ex} cy={48.5 + ey} r="1.4" fill="white" />
            <circle cx={51 + ex} cy={48.5 + ey} r="1.4" fill="white" />
            {/* Nose */}
            <ellipse cx="40" cy="66" rx="5" ry="3.5" fill="#cd6116" />
            {/* Mouth */}
            <path
              d="M35,69 Q40,73 45,69"
              stroke="#cd6116"
              strokeWidth="1.5"
              fill="none"
              strokeLinecap="round"
            />
          </svg>
        </div>
        <div className="fox-shadow" />
      </div>
    </div>
  );
}
