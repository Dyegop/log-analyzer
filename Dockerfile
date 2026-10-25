FROM python:3.11-slim-bookworm AS builder

ENV UV_NO_CACHE=1 \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

RUN pip install --no-cache-dir uv==0.13.4

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv sync --locked --no-dev --no-editable


FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --no-create-home app && \
    mkdir /data && chown app:app /data

COPY --from=builder /app/.venv /app/.venv

USER app
WORKDIR /data

ENTRYPOINT ["log-analyzer"]
CMD ["--help"]
