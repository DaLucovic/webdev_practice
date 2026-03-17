# python:3.12-slim is the full CPython interpreter with non-essential system
# packages removed. Much smaller than python:3.12, no build tools included.
FROM python:3.12-slim

# Set working directory inside the container.
# All subsequent COPY and RUN paths are relative to this.
WORKDIR /app

# ── Dependencies ──────────────────────────────────────────────────────────────
# Copy the requirements file before the application code.
# Docker builds images in layers; each instruction is a cached layer.
# Because requirements.txt changes rarely, this layer is reused on every
# code-only change — pip install is skipped, making rebuilds much faster.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application code ──────────────────────────────────────────────────────────
# Copied after dependencies so code changes don't invalidate the pip layer.
COPY app/ ./app/

# Document which port the process listens on.
# EXPOSE is metadata only — it does not publish the port.
# You still need -p 8000:8000 (or docker-compose ports:) to reach it from the host.
EXPOSE 8000

# Run as a non-root user — a standard security practice.
# If the app is ever compromised, the attacker has no root access to the container.
RUN useradd --no-create-home appuser
USER appuser

# Start uvicorn without --reload (that flag watches the filesystem for changes,
# which is useful in development but wasteful and unnecessary in production).
# 0.0.0.0 is required: the default 127.0.0.1 is only reachable inside the
# container itself, so nothing outside could connect to it.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
