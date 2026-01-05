from domain.models import Task, User, Subtask
from domain.interfaces import ITaskRepository, IUserRepository
from .database import SessionLocal
from .orm_models import TaskModel, UserModel, SubtaskModel
from typing import Optional, List
from datetime import datetime


class TaskRepository(ITaskRepository):
    def __init__(self):
        self.db = SessionLocal()
    
    def create(self, title: str, user_id: int, deadline: Optional[datetime] = None, priority: str = "medium", category: Optional[str] = None) -> Task:
        max_position = self.db.query(TaskModel).filter(TaskModel.user_id == user_id).count()
        db_task = TaskModel(
            title=title, 
            completed=False, 
            deadline=deadline, 
            user_id=user_id,
            priority=priority,
            category=category,
            created_at=datetime.utcnow(),
            position=max_position
        )
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return self._task_to_domain(db_task)
    
    def get_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == user_id).first()
        if db_task:
            return self._task_to_domain(db_task)
        return None
    
    def get_all_by_user(self, user_id: int) -> List[Task]:
        db_tasks = self.db.query(TaskModel).filter(TaskModel.user_id == user_id).order_by(TaskModel.position).all()
        return [self._task_to_domain(t) for t in db_tasks]
    
    def update(self, task_id: int, user_id: int, title: Optional[str] = None, completed: Optional[bool] = None, deadline: Optional[datetime] = None, priority: Optional[str] = None, category: Optional[str] = None) -> Optional[Task]:
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == user_id).first()
        if not db_task:
            return None
        
        if title is not None:
            db_task.title = title
        if completed is not None:
            db_task.completed = completed
        if deadline is not None:
            db_task.deadline = deadline
        if priority is not None:
            db_task.priority = priority
        if category is not None:
            db_task.category = category
        
        self.db.commit()
        self.db.refresh(db_task)
        return self._task_to_domain(db_task)
    
    def delete(self, task_id: int, user_id: int) -> bool:
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == user_id).first()
        if db_task:
            self.db.delete(db_task)
            self.db.commit()
            return True
        return False
    
    def delete_completed(self, user_id: int) -> int:
        count = self.db.query(TaskModel).filter(TaskModel.user_id == user_id, TaskModel.completed == True).delete()
        self.db.commit()
        return count
    
    def update_positions(self, user_id: int, task_positions: List[tuple]) -> bool:
        for task_id, position in task_positions:
            db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == user_id).first()
            if db_task:
                db_task.position = position
        self.db.commit()
        return True
    
    def add_subtask(self, task_id: int, user_id: int, title: str) -> Optional[Subtask]:
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == user_id).first()
        if not db_task:
            return None
        
        db_subtask = SubtaskModel(title=title, completed=False, task_id=task_id)
        self.db.add(db_subtask)
        self.db.commit()
        self.db.refresh(db_subtask)
        return Subtask(id=db_subtask.id, title=db_subtask.title, completed=db_subtask.completed, task_id=db_subtask.task_id)
    
    def toggle_subtask(self, subtask_id: int, task_id: int, user_id: int, completed: bool) -> Optional[Subtask]:
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == user_id).first()
        if not db_task:
            return None
        
        db_subtask = self.db.query(SubtaskModel).filter(SubtaskModel.id == subtask_id, SubtaskModel.task_id == task_id).first()
        if not db_subtask:
            return None
        
        db_subtask.completed = completed
        self.db.commit()
        self.db.refresh(db_subtask)
        return Subtask(id=db_subtask.id, title=db_subtask.title, completed=db_subtask.completed, task_id=db_subtask.task_id)
    
    def delete_subtask(self, subtask_id: int, task_id: int, user_id: int) -> bool:
        db_task = self.db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == user_id).first()
        if not db_task:
            return False
        
        db_subtask = self.db.query(SubtaskModel).filter(SubtaskModel.id == subtask_id, SubtaskModel.task_id == task_id).first()
        if db_subtask:
            self.db.delete(db_subtask)
            self.db.commit()
            return True
        return False
    
    def _task_to_domain(self, db_task: TaskModel) -> Task:
        subtasks = [Subtask(id=s.id, title=s.title, completed=s.completed, task_id=s.task_id) for s in db_task.subtasks]
        return Task(
            id=db_task.id,
            title=db_task.title,
            completed=db_task.completed,
            deadline=db_task.deadline,
            user_id=db_task.user_id,
            priority=db_task.priority,
            category=db_task.category,
            created_at=db_task.created_at,
            position=db_task.position,
            subtasks=subtasks
        )


class UserRepository(IUserRepository):
    def __init__(self):
        self.db = SessionLocal()
    
    def create(self, username: str, email: str, hashed_password: str) -> User:
        db_user = UserModel(username=username, email=email, hashed_password=hashed_password)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return User(id=db_user.id, username=db_user.username, email=db_user.email, hashed_password=db_user.hashed_password)
    
    def get_by_username(self, username: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.username == username).first()
        if db_user:
            return User(id=db_user.id, username=db_user.username, email=db_user.email, hashed_password=db_user.hashed_password)
        return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if db_user:
            return User(id=db_user.id, username=db_user.username, email=db_user.email, hashed_password=db_user.hashed_password)
        return None
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            return User(id=db_user.id, username=db_user.username, email=db_user.email, hashed_password=db_user.hashed_password)
        return None
