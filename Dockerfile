FROM python:3.13.1-slim

RUN useradd validacijas

WORKDIR /home/validacijas

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY etalonu_validacijas.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP=etalonu_validacijas.py
ENV FLASK_CONFIG=docker

RUN chown -R validacijas:validacijas ./
USER validacijas

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]