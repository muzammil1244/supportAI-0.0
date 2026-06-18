#!/bin/bash

echo "Starting Celery Worker..."
uv run celery -A src.celery_app worker --loglevel=info &

echo "Starting FastAPI..."
uv run uvicorn main:app --host 0.0.0.0 --port $PORT