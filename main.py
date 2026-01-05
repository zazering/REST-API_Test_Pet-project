from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from presentation.routers import router as task_router
from presentation.auth_routers import router as auth_router
from infrastructure.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TodoList API", version="1.0.0")

app.include_router(auth_router)
app.include_router(task_router)

app.mount("/static", StaticFiles(directory="presentation/static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("presentation/static/index.html")
