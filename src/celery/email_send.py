from src.celery.celery_app import celery_app
from src.celery.email_connection import simple_send , EmailSchema
import asyncio

@celery_app.task
def send_email(to: str):
    email_obj = EmailSchema(email=to)
    asyncio.run(simple_send(email_obj))
    print(f"email sent successfully {to}")