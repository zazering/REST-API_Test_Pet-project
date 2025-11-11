from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://lola:123456l1@host:8000/todolist_database.db"
engine = create_engine(DATABASE_URL)
SessionLocall = sessionmaker(bing=engine, autocommit=False, autoflush=False)
Base = declarative_base()
