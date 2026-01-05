import pytest
from datetime import datetime, timedelta

@pytest.mark.integration
@pytest.mark.auth
class TestAuthAPI:
    
    def test_register_endpoint(self, client):
        response = client.post(
            "/api/auth/register",
            json={"username": "apiuser", "email": "api@example.com", "password": "password123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "apiuser"
        assert data["email"] == "api@example.com"
    
    def test_register_duplicate(self, client, test_user):
        response = client.post(
            "/api/auth/register",
            json={"username": "testuser", "email": "new@example.com", "password": "password123"}
        )
        
        assert response.status_code == 400
    
    def test_login_endpoint(self, client, test_user):
        response = client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "password123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user):
        response = client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401

@pytest.mark.integration
@pytest.mark.tasks
class TestTaskAPI:
    
    def test_create_task_endpoint(self, client, auth_headers):
        response = client.post(
            "/api/tasks/",
            json={"title": "API Task", "priority": "medium"},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "API Task"
        assert data["priority"] == "medium"
    
    def test_create_task_unauthorized(self, client):
        response = client.post(
            "/api/tasks/",
            json={"title": "Unauthorized Task", "priority": "medium"}
        )
        
        assert response.status_code == 401
    
    def test_get_all_tasks_endpoint(self, client, auth_headers):
        for i in range(3):
            client.post(
                "/api/tasks/",
                json={"title": f"Task {i}", "priority": "medium"},
                headers=auth_headers
            )
        
        response = client.get("/api/tasks/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
    
    def test_get_task_by_id_endpoint(self, client, auth_headers):
        create_response = client.post(
            "/api/tasks/",
            json={"title": "Single Task", "priority": "high"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Single Task"
    
    def test_update_task_endpoint(self, client, auth_headers):
        create_response = client.post(
            "/api/tasks/",
            json={"title": "Original", "priority": "low"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/tasks/{task_id}",
            json={"title": "Updated", "completed": True},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"
        assert data["completed"] is True
    
    def test_delete_task_endpoint(self, client, auth_headers):
        create_response = client.post(
            "/api/tasks/",
            json={"title": "Task to delete", "priority": "medium"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
        
        assert response.status_code == 204
    
    def test_delete_completed_tasks_endpoint(self, client, auth_headers):
        for i in range(2):
            create_response = client.post(
                "/api/tasks/",
                json={"title": f"Task {i}", "priority": "medium"},
                headers=auth_headers
            )
            task_id = create_response.json()["id"]
            client.put(
                f"/api/tasks/{task_id}",
                json={"completed": True},
                headers=auth_headers
            )
        
        response = client.delete("/api/tasks/completed/all", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] >= 2

@pytest.mark.integration
@pytest.mark.tasks
class TestSubtaskAPI:
    
    def test_add_subtask_endpoint(self, client, auth_headers):
        create_response = client.post(
            "/api/tasks/",
            json={"title": "Parent Task", "priority": "medium"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        response = client.post(
            f"/api/tasks/{task_id}/subtasks",
            json={"title": "Subtask 1"},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Subtask 1"
        assert data["task_id"] == task_id
    
    def test_toggle_subtask_endpoint(self, client, auth_headers):
        create_response = client.post(
            "/api/tasks/",
            json={"title": "Parent Task", "priority": "medium"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        subtask_response = client.post(
            f"/api/tasks/{task_id}/subtasks",
            json={"title": "Subtask"},
            headers=auth_headers
        )
        subtask_id = subtask_response.json()["id"]
        
        response = client.put(
            f"/api/tasks/{task_id}/subtasks/{subtask_id}",
            json={"completed": True},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True
    
    def test_delete_subtask_endpoint(self, client, auth_headers):
        create_response = client.post(
            "/api/tasks/",
            json={"title": "Parent Task", "priority": "medium"},
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        subtask_response = client.post(
            f"/api/tasks/{task_id}/subtasks",
            json={"title": "Subtask to delete"},
            headers=auth_headers
        )
        subtask_id = subtask_response.json()["id"]
        
        response = client.delete(
            f"/api/tasks/{task_id}/subtasks/{subtask_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
