from src.celery.celery_app import celery__date_app
from src.celery.email_connection import simple_send_by_date
from src.schemas.email_schema import Email_schema_by_date
import asyncio



@celery__date_app.task
def send_email_by_date(
    to: str,
    user_name:str,
    name:str,
    description:str,
    doctor:str,
    date:str):
    
    email_obj = Email_schema_by_date(
        email=to,
        user_name=user_name,
        appointment_name=name,
        description=description,
        doctor=doctor,
        date=date

                                     )
    asyncio.run(simple_send_by_date(email_obj))
    print(f"email sent successfully {to}")