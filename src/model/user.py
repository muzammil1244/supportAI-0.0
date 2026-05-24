from src.db.DataBase import Base
from sqlalchemy import Column , String , Integer



class User (Base):

    __tablename__ = "users"
    id = Column(Integer , autoincrement=True , primary_key=True)
    email = Column(String(50),unique=True )
    name = Column(String(50))
    password = Column(String)