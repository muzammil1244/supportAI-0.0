from pydantic import EmailStr, BaseModel 

class Email_schema_by_date(BaseModel):
    email: EmailStr
    user_name : str
    appointment_name:str
    description:str
    doctor:str
    date:str