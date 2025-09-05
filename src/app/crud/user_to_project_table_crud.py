from sqlalchemy import select, func, delete
from sqlalchemy.orm import Session, joinedload

from src.app.db.db import engine
from src.app.models.attachment_to_project_table import AttachmentToProjectTable
from src.app.models.project_table import ProjectsTable
from src.app.models.user_to_project_table import UserToProjectTable
from src.app.requests.project_model import ProjectSchema
from src.app.requests.user_model import UserRoles
from src.app.requests.user_to_project_model import CreateUserToProjectRole


def create_user_for_project(session: Session,data:CreateUserToProjectRole):
    new_data = UserToProjectTable(
        user_id=data.user_id,
        project_id=data.project_id,
        role=data.role,
    )
    session.add(new_data)

    return new_data

def update_user_from_project(object_id,data):
    with Session(engine) as session:
        with session.begin():
            new_session={
                session.query(UserToProjectTable).filter(UserToProjectTable.id==object_id).update(data)
            }
            return new_session

def delete_user_from_project(object_id):
    with Session(engine) as session:
        with session.begin():
            session.query(UserToProjectTable).filter(UserToProjectTable.id==object_id).delete()
        return {"data":None}

def get_user_from_project(object_id):
    with Session(engine) as session:
        with session.begin():
            return {
                session.query(UserToProjectTable).filter(UserToProjectTable.id == object_id).first()
            }

def get_all_projects_for_user(user_id):
    with Session(engine) as session:
        with session.begin():
            return {
                session.query(UserToProjectTable).filter(UserToProjectTable.user_id==user_id).all()
            }

def validate_role(project_id:int,user_id:int,role:str):
    with Session(engine) as session:
        with session.begin():
            user = session.query(UserToProjectTable).filter(
                UserToProjectTable.project_id == project_id,
                UserToProjectTable.user_id == user_id,
                UserToProjectTable.role==role
            ).first()

            return user is not None

def get_all_projects_info(user_id:int):
    with (Session(engine) as session):
        with session.begin():
            projects=( session.query(ProjectsTable).join(UserToProjectTable).filter(
                UserToProjectTable.user_id==user_id).options(joinedload(ProjectsTable.attachments)).all()
                       )
            schemas = [ProjectSchema.model_validate(project) for project in projects]

            return schemas

def delete_all_participants(project_id:int):
    with (Session(engine) as session):
        with session.begin():
            session.execute(delete(UserToProjectTable).where(
                UserToProjectTable.role==UserRoles.PARTICIPANT.value,UserToProjectTable.project_id==project_id))

def delete_all_owners(project_id:int):
    with (Session(engine) as session):
        with session.begin():
            session.execute(delete(UserToProjectTable).where(
                UserToProjectTable.role==UserRoles.OWNER.value,UserToProjectTable.project_id==project_id))
