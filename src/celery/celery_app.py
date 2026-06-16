import os
from celery import Celery

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB   = os.getenv("REDIS_DB", "0")

broker_url  = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
backend_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

celery_app = Celery(
    "worker",
    broker=broker_url,
    backend=backend_url
)


celery__date_app = Celery(
    "worker2",
    broker=broker_url,
    backend=backend_url
)