from fastapi import FastAPI

from src.app.db.db import start_db
from src.app.routers.auth_router import router as auth_router
from src.app.routers.document_router import document_router
from src.app.routers.project_router import  project_router
from src.app.routers.project_router import  projects_router
app=FastAPI()

start_db()
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(projects_router)
app.include_router(document_router)

@app.get("/healthz")
def healthz():
    return {"status":"ok","status_code":200}
