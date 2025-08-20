from http.client import HTTPException

from sqlalchemy.orm import Session

from src.app.db.db import engine
from src.app.models.project_table import Projects
from src.app.models.user_to_project_table import UserToProjectTable
from src.app.requests.project_model import  ProjectCreate


def create_project(session: Session, data: ProjectCreate) -> Projects:
    obj = Projects(name=data.name, description=data.description)
    session.add(obj)
    session.flush()
    return obj

def update_project(project_id,data):
    with Session(engine) as session:
        payload = data.model_dump(exclude_unset=True, exclude_none=True)

        if not payload:
            return None

        with session.begin():
            session.query(Projects).filter(Projects.id==project_id).update(payload)

def delete_project(project_id):
    with Session(engine) as session:
        with session.begin():
            session.query(Projects).filter(Projects.id==project_id).delete()

def get_project(project_id:int):
    with Session(engine) as session:
            data=session.get(Projects,project_id)
            if not data:
                raise HTTPException(404, "Project not found")
            return {"project_id":data.id,"name":data.name,"description":data.description}

