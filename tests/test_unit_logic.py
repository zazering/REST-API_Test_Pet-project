import pytest
from datetime import datetime, timedelta
from domain.models import Task, User
from application.schemas import TaskCreate, UserCreate

@pytest.mark.unit
@pytest.mark.auth
class TestAuthService:
    
    def test_register_user_success(self, auth_service):
        user_data = UserCreate(username="newuser", email="new@example.com", password="pass123")
        user = auth_service.register_user(user_data)
        
        assert user is not None
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.hashed_password != "pass123"
    
    def test_register_duplicate_username(self, auth_service, test_user):
        user_data = UserCreate(username="testuser", email="another@example.com", password="pass123")
        user = auth_service.register_user(user_data)
        
        assert user is None
    
    def test_register_duplicate_email(self, auth_service, test_user):
        user_data = UserCreate(username="anotheruser", email="test@example.com", password="pass123")
        user = auth_service.register_user(user_data)
        
        assert user is None
    
    def test_authenticate_user_success(self, auth_service, test_user):
        user = auth_service.authenticate_user("testuser", "password123")
        
        assert user is not None
        assert user.username == "testuser"
    
    def test_authenticate_user_wrong_password(self, auth_service, test_user):
        user = auth_service.authenticate_user("testuser", "wrongpassword")
        
        assert user is None
    
    def test_authenticate_user_not_exists(self, auth_service):
        user = auth_service.authenticate_user("nonexistent", "password123")
        
        assert user is None
    
    def test_create_token(self, auth_service):
        token = auth_service.create_token("testuser")
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

@pytest.mark.unit
@pytest.mark.tasks
class TestTaskService:
    
    def test_create_task_basic(self, task_service, test_user):
        task_data = TaskCreate(title="Test Task", priority="medium")
        task = task_service.create_task(task_data, test_user.id)
        
        assert task is not None
        assert task.title == "Test Task"
        assert task.priority == "medium"
        assert task.completed is False
        assert task.user_id == test_user.id
    
    @pytest.mark.parametrize("priority", ["low", "medium", "high"])
    def test_create_task_with_priorities(self, task_service, test_user, priority):
        task_data = TaskCreate(title=f"Task {priority}", priority=priority)
        task = task_service.create_task(task_data, test_user.id)
        
        assert task.priority == priority
    
    @pytest.mark.parametrize("category", ["work", "personal", "study", "sport"])
    def test_create_task_with_categories(self, task_service, test_user, category):
        task_data = TaskCreate(title=f"Task {category}", priority="medium", category=category)
        task = task_service.create_task(task_data, test_user.id)
        
        assert task.category == category
    
    def test_create_task_with_deadline(self, task_service, test_user):
        deadline = datetime.utcnow() + timedelta(days=7)
        task_data = TaskCreate(title="Task with deadline", priority="high", deadline=deadline)
        task = task_service.create_task(task_data, test_user.id)
        
        assert task.deadline is not None
        assert task.deadline.date() == deadline.date()
    
    def test_get_task_by_id(self, task_service, test_user):
        task_data = TaskCreate(title="Findable Task", priority="medium")
        created_task = task_service.create_task(task_data, test_user.id)
        
        found_task = task_service.get_task(created_task.id, test_user.id)
        
        assert found_task is not None
        assert found_task.id == created_task.id
        assert found_task.title == "Findable Task"
    
    def test_get_task_not_found(self, task_service, test_user):
        task = task_service.get_task(99999, test_user.id)
        
        assert task is None
    
    def test_get_all_tasks(self, task_service, test_user):
        for i in range(5):
            task_data = TaskCreate(title=f"Task {i}", priority="medium")
            task_service.create_task(task_data, test_user.id)
        
        tasks = task_service.get_all_tasks(test_user.id)
        
        assert len(tasks) == 5
    
    def test_update_task_title(self, task_service, test_user):
        from application.schemas import TaskUpdate
        
        task_data = TaskCreate(title="Original Title", priority="medium")
        task = task_service.create_task(task_data, test_user.id)
        
        update_data = TaskUpdate(title="Updated Title")
        updated_task = task_service.update_task(task.id, test_user.id, update_data)
        
        assert updated_task.title == "Updated Title"
    
    def test_toggle_task_completion(self, task_service, test_user):
        from application.schemas import TaskUpdate
        
        task_data = TaskCreate(title="Task to complete", priority="medium")
        task = task_service.create_task(task_data, test_user.id)
        
        assert task.completed is False
        
        update_data = TaskUpdate(completed=True)
        updated_task = task_service.update_task(task.id, test_user.id, update_data)
        
        assert updated_task.completed is True
    
    def test_delete_task(self, task_service, test_user):
        task_data = TaskCreate(title="Task to delete", priority="medium")
        task = task_service.create_task(task_data, test_user.id)
        
        result = task_service.delete_task(task.id, test_user.id)
        
        assert result is True
        assert task_service.get_task(task.id, test_user.id) is None
    
    def test_delete_completed_tasks(self, task_service, test_user):
        from application.schemas import TaskUpdate
        
        for i in range(3):
            task_data = TaskCreate(title=f"Task {i}", priority="medium")
            task = task_service.create_task(task_data, test_user.id)
            if i < 2:
                update_data = TaskUpdate(completed=True)
                task_service.update_task(task.id, test_user.id, update_data)
        
        deleted_count = task_service.delete_completed_tasks(test_user.id)
        
        assert deleted_count == 2
        remaining_tasks = task_service.get_all_tasks(test_user.id)
        assert len(remaining_tasks) == 1

@pytest.mark.unit
@pytest.mark.tasks
class TestSubtaskOperations:
    
    def test_add_subtask(self, task_service, test_user):
        task_data = TaskCreate(title="Parent Task", priority="medium")
        task = task_service.create_task(task_data, test_user.id)
        
        subtask = task_service.add_subtask(task.id, test_user.id, "Subtask 1")
        
        assert subtask is not None
        assert subtask.title == "Subtask 1"
        assert subtask.completed is False
        assert subtask.task_id == task.id
    
    def test_toggle_subtask(self, task_service, test_user):
        task_data = TaskCreate(title="Parent Task", priority="medium")
        task = task_service.create_task(task_data, test_user.id)
        subtask = task_service.add_subtask(task.id, test_user.id, "Subtask 1")
        
        updated_subtask = task_service.toggle_subtask(subtask.id, task.id, test_user.id, True)
        
        assert updated_subtask.completed is True
    
    def test_delete_subtask(self, task_service, test_user):
        task_data = TaskCreate(title="Parent Task", priority="medium")
        task = task_service.create_task(task_data, test_user.id)
        subtask = task_service.add_subtask(task.id, test_user.id, "Subtask to delete")
        
        result = task_service.delete_subtask(subtask.id, task.id, test_user.id)
        
        assert result is True
