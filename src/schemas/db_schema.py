from pydantic import BaseModel, Field
from typing import Literal , List



class create_db_schema(BaseModel):
    name:str 
    description:str
    appointment_date : str
    doctor : Literal["DR.RAMESH","DR.SURASH","DR.MISHRA"] 
    user_id : int 
    number : str



class update_db_schema(BaseModel):
    id:int



class ReadDBSchema(BaseModel):
    id: int

