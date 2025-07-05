import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from langchain_community.utilities import SQLDatabase

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB_REAL_ESTATE = os.getenv("POSTGRES_DB_REAL_ESTATE")
POSTGRES_DB_CHECKPOINT = os.getenv("POSTGRES_DB_CHECKPOINT")
USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"

REAL_ESTATE_DB_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_REAL_ESTATE}"
CHECKPOINT_DB_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_CHECKPOINT}"

if USE_SQLITE:
    DATABASE_URL = "sqlite:///real_estate.db"
else:
    DATABASE_URL = REAL_ESTATE_DB_URL

# SQLAlchemy ORM for real estate data
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Langchain SQL interface for real estate DB (used by SQLDatabaseToolkit)
langchain_db = SQLDatabase.from_uri(DATABASE_URL)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
