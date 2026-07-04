from fastapi import FastAPI
from src.routes.auth import auth_router
from src.routes.chat import chat_route
from src.routes.admin import admin_route
from fastapi.middleware.cors import CORSMiddleware
from src.model.user import User 
from src.db.DataBase import Base,DB

app = FastAPI(title="MyApp")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
          "https://supportai-0-0.onrender.com/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# join routes

Base.metadata.create_all(bind=DB)
app.include_router(auth_router)
app.include_router(chat_route)
app.include_router(admin_route)



# @app.get("/")
# def home():
#     return {"message": "working"}



