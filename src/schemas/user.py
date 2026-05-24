from pydantic import BaseModel



class Userreq(BaseModel):
    name : str
    email : str
    password : str


class User_login(BaseModel):
    email : str
    password : str

class User_Q(BaseModel):
    question:str