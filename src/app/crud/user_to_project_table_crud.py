from sqlalchemy.orm import Session

from src.app.db.db import engine
from src.app.models.user_to_project_table import UserToProjectTable
from src.app.requests.user_model import UserRoles
from src.app.requests.user_to_project_model import CreateUserToProjectRole


def create_user_for_project(session: Session,data:CreateUserToProjectRole):
    new_data = UserToProjectTable(
        user_id=data.user_id,
        project_id=data.project_id,
        role=data.role,
    )
    session.add(new_data)
    session.commit()
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

def validate_role(project_id:int,user_id:int,role:UserRoles):
    with Session(engine) as session:
        with session.begin():
            user = session.query(UserToProjectTable).filter(
                UserToProjectTable.id == project_id,
                UserToProjectTable.user_id == user_id,
                UserToProjectTable.role==role.value
            ).first()
            return user is not None
