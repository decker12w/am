# Build stage — installs deps via uv
FROM python:3.12-slim AS builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy workspace root files needed for uv to resolve the workspace
COPY pyproject.toml uv.lock ./
COPY backend/pyproject.toml ./backend/pyproject.toml

# Sync only backend package dependencies (no dev extras)
RUN uv sync --frozen --no-dev --package backend

# Runtime stage — lean image with only what's needed
FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY backend/app ./app
COPY models ./models

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV STAGE=production

EXPOSE 8000

CMD ["uvicorn", "app.main:application", "--host", "0.0.0.0", "--port", "8000"]
