from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel 

class EmailSchema(BaseModel):
    email: EmailStr




conf = ConnectionConfig(
    MAIL_USERNAME = "muzammil844641@gmail.com",
    MAIL_PASSWORD = "rgfj etmf eedb feba",
    MAIL_FROM = "muzammil844641@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME="Mohammad muzammil (Saas project)",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def simple_send(email: EmailSchema) :
    html = """<p>hi you are login successfully to saas project that mad by muzammil </p> """

    message = MessageSchema(
        subject="Login Successfully ",
        recipients=[email.email],
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)
    
async def simple_send_by_date(
        email:EmailStr,
        user_name: str,
        appointment_name: str,
        description: str,
        doctor: str,
        date: str):
    
    html = f"""
    <h3>Appointment Reminder</h3>
    <p>Hi {user_name},</p>
    <p>This is a reminder that you have an appointment today. Here are the details:</p>
    <table border="1" cellpadding="5" cellspacing="0">
      <tr><th>Name</th><td>{appointment_name}</td></tr>
      <tr><th>Description</th><td>{description}</td></tr>
      <tr><th>Doctor</th><td>{doctor}</td></tr>
      <tr><th>Date</th><td>{date}</td></tr>
    </table>
    <p>Please be on time. Wishing you the best!</p>
    """

    message = MessageSchema(
        subject="Appointment Reminder",
        recipients=[str(email.email)],  
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
