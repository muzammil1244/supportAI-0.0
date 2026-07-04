#!/bin/bash
uv run celery -A src.celery.celery_app worker --loglevel=info --concurrency=1 --pool=prefork &
uv run uvicorn main:app --host 0.0.0.0 --port $PORT