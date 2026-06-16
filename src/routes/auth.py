from src.controller.auth import register , login 
from fastapi import APIRouter , Request , Depends
from sqlalchemy.orm import Session
from src.db.DataBase import get_db
from src.schemas.user import Userreq , User_login

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@auth_router.post("/register")
def register_route(body: Userreq,db:Session = Depends(get_db) ):
    return register(body,db)


@auth_router.post("/login")
def login_route(body:User_login , db:Session = Depends(get_db)):
    return login(body,db)



