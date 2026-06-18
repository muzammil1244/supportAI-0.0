#!/bin/bash
uv run celery -A src.celery_app worker --loglevel=info &
uv run uvicorn main:app --host 0.0.0.0 --port $PORT
