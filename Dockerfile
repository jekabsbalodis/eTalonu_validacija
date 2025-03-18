FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN useradd --create-home validacijas
USER validacijas

WORKDIR /validacijas

COPY ./pyproject.toml .
RUN uv add gunicorn
RUN uv sync

COPY app app
COPY etalonu_validacijas.py config.py ./

ENV FLASK_APP=etalonu_validacijas.py
ENV FLASK_CONFIG=docker

EXPOSE 5000
CMD ["uv", "run", "gunicorn", "-b", ":5000", "--access-logfile", "-", "--error-logfile", "-", "etalonu_validacijas:app"]
