from sqlalchemy.orm import Session

from src.app.db.db import engine
from src.app.models.attachment_to_project_table import AttachmentToProject
from src.app.requests.attachment_to_project_model import AttachmentToProjectUpload, AttachmentToProjectReturn, \
    AttachmentToProjectUpdate


def create_attachment_to_project(data:AttachmentToProjectUpload):
    with Session(engine) as session:
        with session.begin():
            new_data=AttachmentToProject(user_id=data.user_id,project_id=data.project_id,uri=data.uri,
                                         name=data.name,mimetype=data.mimetype,key=data.key)
            session.add(new_data)


def update_attachment_to_project(object_id,new_document):
    with Session(engine) as session:
        with session.begin():
            update_document:AttachmentToProjectUpdate=AttachmentToProjectUpdate(user_id=new_document.user_id,name=new_document.name)
            new_session={
                session.query(AttachmentToProject).filter(AttachmentToProject.id==object_id).update(update_document.model_dump(exclude_unset=True))
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
            document=session.query(AttachmentToProject).filter(AttachmentToProject.id == object_id).first()
            attachment_object:AttachmentToProjectReturn = AttachmentToProjectReturn(user_id=document.user_id,
                                                                                    project_id=document.project_id,
                                                                                    uri=document.uri,
                                                                                    mimetype=document.mimetype,
                                                                                    key=document.key,
                                                                                    name=document.name)
            return attachment_object


def get_all_attachment_id(project_id):
    with Session(engine) as session:
        with session.begin():
            return session.query(AttachmentToProject.id,AttachmentToProject.key).filter_by(project_id=project_id).all()

