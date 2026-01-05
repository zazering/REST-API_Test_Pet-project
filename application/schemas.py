from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str


class SubtaskResponse(BaseModel):
    id: int
    title: str
    completed: bool
    task_id: int


class SubtaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    deadline: Optional[datetime] = None
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    category: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    completed: Optional[bool] = None
    deadline: Optional[datetime] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    category: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool
    deadline: Optional[datetime] = None
    priority: str
    category: Optional[str] = None
    created_at: Optional[datetime] = None
    position: int
    subtasks: List[SubtaskResponse] = []
    
    class Config:
        from_attributes = True


class TaskPositionUpdate(BaseModel):
    task_positions: List[tuple]
