from fastapi import APIRouter , Depends
from src.schemas.graph_schema import Query
from sqlalchemy.orm import Session
from src.db.DataBase import get_db
from src.controller.chat import chat_agent
from src.helper.is_authanticat import is_authenticated
from src.helper.chat_his import get_history
from src.redis.connection import redis_client




chat_route = APIRouter(
    prefix="/user",
    tags=["USER"]
)

@chat_route.post("/chat",)
def chat_user_route(body:Query , db:Session = Depends(get_db) , is_user : User_q = Depends(is_authenticated)):
    history = get_history(is_user)
    return chat_agent(body,db, is_user, history)

@chat_route.get("/test-redis")
def test():

    data = redis_client.lrange("chat:35", 0, -1)

    print(data)

    return {
        "data": data
    }