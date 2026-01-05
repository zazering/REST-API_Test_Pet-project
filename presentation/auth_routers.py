from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from application.services import AuthService
from application.schemas import UserCreate, UserResponse, Token
from .dependencies import get_auth_service

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", status_code=201)
def register(user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    user = auth_service.register_user(user_data)
    if user is None:
        return JSONResponse(status_code=400, content={"detail": "Username or email already exists"})
    return {"id": user.id, "username": user.username, "email": user.email}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(get_auth_service)):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        return JSONResponse(status_code=401, content={"detail": "Incorrect username or password"})
    
    access_token = auth_service.create_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}
