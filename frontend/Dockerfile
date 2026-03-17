# ── Stage 1: Build ────────────────────────────────────────────────────────────
# node:20-alpine is a minimal Node.js image (~50 MB vs ~350 MB for node:20).
FROM node:20-alpine AS builder

WORKDIR /app

# Copy manifests before source so Docker can cache the install layer.
# npm ci ("clean install") is preferred over npm install in CI/production:
#   - Reads package-lock.json exactly — no version surprises
#   - Faster and more deterministic than npm install
COPY package.json package-lock.json ./
RUN npm ci

# Copy source and build. Vite outputs static files to dist/.
COPY . .
RUN npm run build

# ── Stage 2: Serve ────────────────────────────────────────────────────────────
# The builder stage is discarded here — node_modules (~300 MB) never enters
# the final image. nginx:alpine is ~25 MB.
FROM nginx:alpine

# Replace the default nginx config with our custom one (SPA routing + API proxy).
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy only the compiled output from the builder stage.
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

# "daemon off" keeps nginx in the foreground so Docker can track the process.
CMD ["nginx", "-g", "daemon off;"]
