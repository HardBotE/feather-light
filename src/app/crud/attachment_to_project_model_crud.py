from sqlalchemy.orm import Session

from src.app.db.db import engine
from src.app.models.attachment_to_project_table import AttachmentToProject



def create_attachment_to_project(data):
    with Session(engine) as session:
        with session.begin():
            new_project=AttachmentToProject(**data)
            session.add(new_project)
        return new_project.id

def update_attachment_to_project(object_id,data):
    with Session(engine) as session:
        with session.begin():
            new_session={
                session.query(AttachmentToProject).filter(AttachmentToProject.id==object_id).update(data)
            }
            return new_session

def delete_attachment_to_project(object_id):
    with Session(engine) as session:
        with session.begin():
            session.query(AttachmentToProject).filter(AttachmentToProject.id==object_id).delete()
        return {"data":None}

def get_attachment_to_project(object_id):
    with Session(engine) as session:
        with session.begin():
            return {
                session.query(AttachmentToProject).filter(AttachmentToProject.id == object_id).first()
            }