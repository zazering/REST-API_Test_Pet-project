from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from application.services import TaskService, AuthService
from infrastructure.repositories import TaskRepository, UserRepository
from infrastructure.auth import decode_access_token
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_task_service() -> TaskService:
    repository = TaskRepository()
    return TaskService(repository)


def get_auth_service() -> AuthService:
    repository = UserRepository()
    return AuthService(repository)


def get_current_user_or_none(token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service)):
    username = decode_access_token(token)
    if username is None:
        return None
    
    user = auth_service.get_user_by_username(username)
    return user
