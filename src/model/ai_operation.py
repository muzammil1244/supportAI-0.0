from src.db.DataBase import Base
from sqlalchemy import Column , String , Integer

class ai_Database(Base):
    __tablename__= "ai_db"
    id = Column(Integer , primary_key=True , autoincrement=True)
    name = Column(String)
    description = Column(String)
    date = Column(String)
    doctor = Column(String)
    number = Column(String)
    create_by = Column(Integer)
    create_date = Column(String)