from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.database import Base
from datetime import datetime

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    tasks = relationship("TaskModel", back_populates="owner", cascade="all, delete-orphan")

class TaskModel(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    deadline = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    priority = Column(String, default="medium")
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    position = Column(Integer, default=0)
    
    owner = relationship("UserModel", back_populates="tasks")
    subtasks = relationship("SubtaskModel", back_populates="task", cascade="all, delete-orphan")

class SubtaskModel(Base):
    __tablename__ = "subtasks"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    
    task = relationship("TaskModel", back_populates="subtasks")
