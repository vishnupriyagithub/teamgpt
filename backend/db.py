from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
  
  DATABASE_URL,
  pool_pre_ping=True,
  pool_recycle=300,
  pool_size=10,
  max_overflow=20
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()