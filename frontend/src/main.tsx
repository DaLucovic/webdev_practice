// This is the entry point — Vite loads this file first.
// StrictMode runs component code twice in development to surface side-effect bugs.
// It has no effect in production builds.

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./App.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
