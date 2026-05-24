from fastapi import APIRouter , Depends
from src.schemas.user import User_Q
from sqlalchemy.orm import Session
from src.db.DataBase import get_db
from src.controller.chat import chat_user






chat_route = APIRouter(
    prefix="/user",
    tags=["USER"]
)

@chat_route.post("/chat")
def login_route(body:User_Q , db:Session = Depends(get_db)):
    return chat_user(body,db)
