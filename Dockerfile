FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock README.md ./
COPY src/ ./src/
RUN poetry config virtualenvs.in-project true
RUN poetry install --without dev

FROM python:3.12-slim AS runtime
WORKDIR /app
RUN useradd --create-home sentinel
USER sentinel
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src ./src
CMD ["/app/.venv/bin/python", "-m", "sentinel"]