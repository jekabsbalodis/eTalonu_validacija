# Build stage
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

COPY ./pyproject.toml .

RUN uv add gunicorn
RUN uv sync

# Production stage
FROM python:3.13-slim AS production

RUN useradd --create-home validacijas

WORKDIR /validacijas

COPY app app
COPY etalonu_validacijas.py config.py boot.sh ./
RUN chmod +x boot.sh

COPY --from=builder /.venv .venv

ENV FLASK_APP=etalonu_validacijas.py
ENV FLASK_CONFIG=docker

RUN chown -R validacijas:validacijas ./

USER validacijas

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]