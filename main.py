from fastapi import FastAPI
from src.routes.auth import auth_router
from src.routes.chat import chat_route
from src.routes.admin import admin_route

from src.model.user import User 
from src.db.DataBase import Base,DB

app = FastAPI(title="MyApp")



# join routes

Base.metadata.create_all(bind=DB)
app.include_router(auth_router)
app.include_router(chat_route)
app.include_router(admin_route)





