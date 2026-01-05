from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from application.services import TaskService
from application.schemas import TaskCreate, TaskUpdate, TaskResponse, SubtaskCreate, SubtaskResponse, TaskPositionUpdate
from domain.models import User
from .dependencies import get_task_service, get_current_user_or_none
from typing import List, Optional


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, current_user: Optional[User] = Depends(get_current_user_or_none), service: TaskService = Depends(get_task_service)):
    if current_user is None:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    
    result = service.create_task(task, current_user.id)
    return result


@router.get("/", response_model=List[TaskResponse])
def get_all_tasks(current_user: Optional[User] = Depends(get_current_user_or_none), service: TaskService = Depends(get_task_service)):
    if current_user is None:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    
    return service.get_all_tasks(current_user.id)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, current_user: Optional[User] = Depends(get_current_user_or_none), service: TaskService = Depends(get_task_service)):
    if current_user is None:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    
    task = service.get_task(task_id, current_user.id)
    if task is None:
        return JSONResponse(status_code=404, content={"detail": "Task not found"})
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_data: TaskUpdate, current_user: Optional[User] = Depends(get_current_user_or_none), service: TaskService = Depends(get_task_service)):
    if current_user is None:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    
    task = service.update_task(task_id, current_user.id, task_data)
    if task is None:
        return JSONResponse(status_code=404, content={"detail": "Task not found"})
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, current_user: Optional[User] = Depends(get_current_user_or_none), service: TaskService = Depends(get_task_service)):
    if current_user is None:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    
    deleted = service.delete_task(task_id, current_user.id)
    if not deleted:
        return JSONResponse(status_code=404, content={"detail": "Task not found"})
    return Response(status_code=204)


@router.delete("/completed/all", status_code=200)
def delete_completed_tasks(current_user: Optional[User] = Depends(get_current_user_or_none), service: TaskService = Depends(get_task_service)):
    if current_user is None:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    
    count = service.delete_completed_tasks(current_user.id)
    return {"deleted": count}


@router.put("/positions/update", status_code=200)
def update_task_positions(positions: dict, current_user: Optional[User] = Depends(get_current_user_or_none), service: TaskService = Depends(get_task_service)):
    if current_user is None:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    
    task_positions = [(int(k), v) for k, v in positions.items()]
    service.update_task_positions(current_user.id, task_positions)
    return {"success": True}


@router.post("/{task_id}/subtasks", response_model=SubtaskResponse, status_code=201)
def add_subtask(task_id: int, subtask: SubtaskCreate, current_user: Optional[User] = Depends(get_current_user_or_none), service: TaskService = Depends(get_task_service)):
    if current_user is None:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    
    result = service.add_subtask(task_id, current_user.id, subtask.title)
    if result is None:
        return JSONResponse(status_code=404, content={"detail": "Task not found"})
    return result


@router.put("/{task_id}/subtasks/{subtask_id}", response_model=SubtaskResponse)
def toggle_subtask(task_id: int, subtask_id: int, data: dict, current_user: Optional[User] = Depends(get_current_user_or_none), service: TaskService = Depends(get_task_service)):
    if current_user is None:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    
    completed = data.get("completed", False)
    result = service.toggle_subtask(subtask_id, task_id, current_user.id, completed)
    if result is None:
        return JSONResponse(status_code=404, content={"detail": "Subtask not found"})
    return result


@router.delete("/{task_id}/subtasks/{subtask_id}", status_code=204)
def delete_subtask(task_id: int, subtask_id: int, current_user: Optional[User] = Depends(get_current_user_or_none), service: TaskService = Depends(get_task_service)):
    if current_user is None:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    
    deleted = service.delete_subtask(subtask_id, task_id, current_user.id)
    if not deleted:
        return JSONResponse(status_code=404, content={"detail": "Subtask not found"})
    return Response(status_code=204)
