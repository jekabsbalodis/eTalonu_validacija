#!/bin/bash
source venv/bin/activate
exec gunicorn -b :5000 --access-logfile - --error-logfile - etalonu_validacijas:app