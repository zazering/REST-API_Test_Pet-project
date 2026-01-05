import pytest
import time

@pytest.mark.e2e
@pytest.mark.slow
class TestEndToEndFlow:
    
    def test_complete_user_journey(self, client):
        register_response = client.post(
            "/api/auth/register",
            json={"username": "e2euser", "email": "e2e@example.com", "password": "password123"}
        )
        assert register_response.status_code == 200
        
        login_response = client.post(
            "/api/auth/login",
            data={"username": "e2euser", "password": "password123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        task_response = client.post(
            "/api/tasks/",
            json={"title": "E2E Task", "priority": "high", "category": "work"},
            headers=headers
        )
        assert task_response.status_code == 201
        task_id = task_response.json()["id"]
        
        subtask_response = client.post(
            f"/api/tasks/{task_id}/subtasks",
            json={"title": "E2E Subtask"},
            headers=headers
        )
        assert subtask_response.status_code == 201
        subtask_id = subtask_response.json()["id"]
        
        toggle_subtask = client.put(
            f"/api/tasks/{task_id}/subtasks/{subtask_id}",
            json={"completed": True},
            headers=headers
        )
        assert toggle_subtask.status_code == 200
        
        complete_task = client.put(
            f"/api/tasks/{task_id}",
            json={"completed": True},
            headers=headers
        )
        assert complete_task.status_code == 200
        assert complete_task.json()["completed"] is True
        
        tasks_response = client.get("/api/tasks/", headers=headers)
        assert tasks_response.status_code == 200
        tasks = tasks_response.json()
        assert any(t["id"] == task_id for t in tasks)
    
    @pytest.mark.parametrize("priority,category", [
        ("high", "work"),
        ("medium", "personal"),
        ("low", "study"),
    ])
    def test_task_creation_variations(self, client, test_user, auth_headers, priority, category):
        response = client.post(
            "/api/tasks/",
            json={"title": f"{category} task", "priority": priority, "category": category},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == priority
        assert data["category"] == category

@pytest.mark.e2e
class TestStaticFiles:
    
    def test_index_page_loads(self, client):
        response = client.get("/")
        
        assert response.status_code == 200
        assert b"Todo List" in response.content
    
    def test_static_css_loads(self, client):
        response = client.get("/static/style.css")
        
        assert response.status_code == 200
        assert b"background" in response.content
    
    def test_static_js_loads(self, client):
        response = client.get("/static/app.js")
        
        assert response.status_code == 200
        assert b"function" in response.content
