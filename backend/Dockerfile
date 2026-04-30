FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY backend/pyproject.toml ./backend/pyproject.toml

RUN uv sync --frozen --no-dev --package backend

FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY backend/app ./app
COPY backend/scripts ./scripts
COPY models ./models
COPY data /data

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV STAGE=production

EXPOSE 8000

CMD ["sh", "-c", "python scripts/seed.py && uvicorn app.main:application --host 0.0.0.0 --port 8000"]