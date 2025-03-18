# Build stage
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR = /uv_venv

COPY ./pyproject.toml .
RUN uv add gunicorn
RUN uv sync

# Production stage
FROM python:3.13-slim AS production

RUN useradd --create-home validacijas
USER validacijas

WORKDIR /validacijas

COPY app app
COPY etalonu_validacijas.py config.py ./

COPY --from=builder /uv_venv/.venv .venv

ENV FLASK_APP=etalonu_validacijas.py
ENV FLASK_CONFIG=docker
ENV PATH="/validacijas/.venv/bin:$PATH"

EXPOSE 5000
CMD ["gunicorn", "-b", ":5000", "--access-logfile", "-", "--error-logfile", "-", "etalonu_validacijas:app"]
