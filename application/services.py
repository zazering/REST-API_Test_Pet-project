from domain.models import Task, User, Subtask
from domain.interfaces import ITaskRepository, IUserRepository
from .schemas import TaskCreate, TaskUpdate, UserCreate
from infrastructure.auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from typing import List, Optional
from datetime import timedelta


class TaskService:
    def __init__(self, repository: ITaskRepository):
        self.repository = repository
    
    def create_task(self, task_data: TaskCreate, user_id: int) -> Task:
        return self.repository.create(
            title=task_data.title, 
            user_id=user_id, 
            deadline=task_data.deadline,
            priority=task_data.priority,
            category=task_data.category
        )
    
    def get_task(self, task_id: int, user_id: int) -> Optional[Task]:
        return self.repository.get_by_id(task_id, user_id)
    
    def get_all_tasks(self, user_id: int) -> List[Task]:
        return self.repository.get_all_by_user(user_id)
    
    def update_task(self, task_id: int, user_id: int, task_data: TaskUpdate) -> Optional[Task]:
        return self.repository.update(
            task_id, 
            user_id, 
            task_data.title, 
            task_data.completed, 
            task_data.deadline,
            task_data.priority,
            task_data.category
        )
    
    def delete_task(self, task_id: int, user_id: int) -> bool:
        return self.repository.delete(task_id, user_id)
    
    def delete_completed_tasks(self, user_id: int) -> int:
        return self.repository.delete_completed(user_id)
    
    def update_task_positions(self, user_id: int, task_positions: List[tuple]) -> bool:
        return self.repository.update_positions(user_id, task_positions)
    
    def add_subtask(self, task_id: int, user_id: int, title: str) -> Optional[Subtask]:
        return self.repository.add_subtask(task_id, user_id, title)
    
    def toggle_subtask(self, subtask_id: int, task_id: int, user_id: int, completed: bool) -> Optional[Subtask]:
        return self.repository.toggle_subtask(subtask_id, task_id, user_id, completed)
    
    def delete_subtask(self, subtask_id: int, task_id: int, user_id: int) -> bool:
        return self.repository.delete_subtask(subtask_id, task_id, user_id)


class AuthService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    def register_user(self, user_data: UserCreate) -> Optional[User]:
        existing_user = self.user_repository.get_by_username(user_data.username)
        if existing_user:
            return None
        
        existing_email = self.user_repository.get_by_email(user_data.email)
        if existing_email:
            return None
        
        hashed_password = get_password_hash(user_data.password)
        return self.user_repository.create(user_data.username, user_data.email, hashed_password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.user_repository.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_token(self, username: str) -> str:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        return access_token
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.user_repository.get_by_username(username)
