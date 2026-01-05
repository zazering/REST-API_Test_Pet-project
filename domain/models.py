from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class Subtask:
    id: Optional[int] = None
    title: str = ""
    completed: bool = False
    task_id: Optional[int] = None

@dataclass
class Task:
    id: Optional[int] = None
    title: str = ""
    completed: bool = False
    deadline: Optional[datetime] = None
    user_id: Optional[int] = None
    priority: str = "medium"
    category: Optional[str] = None
    created_at: Optional[datetime] = None
    position: int = 0
    subtasks: List[Subtask] = field(default_factory=list)

@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    hashed_password: str = ""
