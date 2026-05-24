from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base
from dotenv import load_dotenv
import os



load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

DB = create_engine(DB_URL)

Base = declarative_base()
sessionlocal = sessionmaker(bind=DB,autoflush=False)


def get_db():
    db = sessionlocal()
    try:
            yield db
    finally:
            db.close() 
        
