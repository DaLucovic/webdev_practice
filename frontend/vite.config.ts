import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // During development, any request the browser makes to /api/...
      // is silently forwarded to the FastAPI server on port 8000.
      // This sidesteps CORS entirely in dev — no browser error, no backend config needed.
      //
      // Example: fetch("/api/calculate") → http://localhost:8000/calculate
      "/api": {
        target: "http://localhost:8000",
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
