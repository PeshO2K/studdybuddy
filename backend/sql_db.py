
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()


# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"  # for dev only

# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread":False})

POSTGRES_DATABASE_URL = os.getenv('POSTGRES_DATABASE_URL')
engine = create_engine(POSTGRES_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
