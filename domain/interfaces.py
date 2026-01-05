from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from .models import Task, User, Subtask

class ITaskRepository(ABC):
    @abstractmethod
    def create(self, title: str, user_id: int, deadline: Optional[datetime] = None, priority: str = "medium", category: Optional[str] = None) -> Task:
        pass
    
    @abstractmethod
    def get_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        pass
    
    @abstractmethod
    def get_all_by_user(self, user_id: int) -> List[Task]:
        pass
    
    @abstractmethod
    def update(self, task_id: int, user_id: int, title: Optional[str] = None, completed: Optional[bool] = None, deadline: Optional[datetime] = None, priority: Optional[str] = None, category: Optional[str] = None) -> Optional[Task]:
        pass
    
    @abstractmethod
    def delete(self, task_id: int, user_id: int) -> bool:
        pass
    
    @abstractmethod
    def delete_completed(self, user_id: int) -> int:
        pass
    
    @abstractmethod
    def update_positions(self, user_id: int, task_positions: List[tuple]) -> bool:
        pass
    
    @abstractmethod
    def add_subtask(self, task_id: int, user_id: int, title: str) -> Optional[Subtask]:
        pass
    
    @abstractmethod
    def toggle_subtask(self, subtask_id: int, task_id: int, user_id: int, completed: bool) -> Optional[Subtask]:
        pass
    
    @abstractmethod
    def delete_subtask(self, subtask_id: int, task_id: int, user_id: int) -> bool:
        pass

class IUserRepository(ABC):
    @abstractmethod
    def create(self, username: str, email: str, hashed_password: str) -> User:
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass
