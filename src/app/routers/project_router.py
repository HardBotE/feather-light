
from typing import List

from fastapi import APIRouter, Request, UploadFile,HTTPException
from fastapi.params import Depends, Query, File
from sqlalchemy.orm import  Session
from sqlalchemy.exc import SQLAlchemyError

from src.app.crud.attachment_to_project_model_crud import create_attachment_to_project, get_all_attachment_id, \
    delete_attachment_to_project, get_all_attachments
from src.app.crud.project_crud import create_project, get_project, \
    update_project, delete_project
from src.app.crud.user_crud import does_user_exist, return_id_by_email
from src.app.crud.user_to_project_table_crud import validate_role, create_user_for_project, get_all_projects_info, \
    delete_all_participants, delete_all_owners
from src.app.db.db import engine
from src.app.models.user_to_project_table import UserToProjectTable
from src.app.requests.attachment_to_project_model import AttachmentToProject, AttachmentToProjectUpload
from src.app.requests.project_model import ProjectCreate, ProjectOut, ProjectSchema
from src.app.requests.user_model import UserRoles
from src.app.requests.user_to_project_model import CreateUserToProjectRole
from src.app.routers.auth_router import get_user
from src.app.documents.aws_s3 import upload_mock, delete_mock

projects_router=APIRouter(prefix='/api/projects')

@projects_router.get('/',response_model=List[ProjectSchema],status_code=200)
def get_all_projects(user_id: int =Depends(get_user)):
    all_projects=get_all_projects_info(user_id)
    return all_projects

@projects_router.post('/',status_code=201)
def call_create_project(project_data:ProjectCreate,user_id: int =Depends(get_user)):
    try:
        with Session(engine) as session:
            with session.begin():
                new_project= ProjectCreate(name=project_data.name,description=project_data.description)
                out_project=create_project(session,new_project)

                new_user_to_project=CreateUserToProjectRole(user_id=user_id,project_id=out_project.id,role=UserRoles.OWNER)
                create_user_for_project(session,new_user_to_project)

                return {"message":"successfully created project","project":{"id":out_project.id,"name":out_project.name,"desc":out_project.description},'user':new_user_to_project}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail=e)

project_router=APIRouter(prefix='/api/project')

@project_router.get('/{project_id}/info',status_code=200)
def get_project_info(project_id,user_id: int =Depends(get_user)):

   is_owner=validate_role(project_id,user_id,UserRoles.OWNER.value)
   is_participant=validate_role(project_id,user_id,UserRoles.PARTICIPANT.value)

   if not (is_owner or  is_participant):
       raise HTTPException(403,'Unauthorized')

   project_data=get_project(project_id)

   return {'message':'successfully retrieved data','project':project_data}

@project_router.put('/{project_id}/info',status_code=200)
def update_project_info(project_id,project_data:ProjectCreate,user_id: int =Depends(get_user)):

    project=get_project(project_id)

    is_owner = validate_role(project_id, user_id, UserRoles.OWNER.value)
    is_participant = validate_role(project_id, user_id, UserRoles.PARTICIPANT.value)

    if not (is_owner or  is_participant):
        raise HTTPException(403,'Unauthorized')

    update_project(project_id,project_data)
    new_data=get_project(project_id)

    return {'message':'successfully updated data','updated_data':new_data}

@project_router.get('/{project_id}/documents',status_code=200)
def return_documents(project_id,user_id:int=Depends(get_user)):

    project = get_project(project_id)

    is_owner = validate_role(project_id, user_id, UserRoles.OWNER.value)
    is_participant = validate_role(project_id, user_id, UserRoles.PARTICIPANT.value)

    if not is_owner and not is_participant:
        raise HTTPException(403, 'Unauthorized')

    documents=get_all_attachments(project_id)

    return {"message":"successfully retrieved data","documents":documents}

@project_router.post('/{project_id}/documents',status_code=201)
async def upload_file(project_id: int,file: UploadFile=File(...),user_id:int=Depends(get_user)):

    project = get_project(project_id)

    is_owner = validate_role(project_id, user_id, UserRoles.OWNER.value)
    is_participant = validate_role(project_id, user_id, UserRoles.PARTICIPANT.value)

    if not is_owner and not is_participant:
        raise HTTPException(403,'Unauthorized')

    try:
        document = await upload_mock(file, project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {e}")

    attachment_data=AttachmentToProjectUpload(user_id=user_id,
                                              project_id=project_id,
                                              uri=document.get('url'),
                                              key=document.get('key'),
                                              mimetype=document.get('mime'),
                                              name=file.filename)

    try:
        create_attachment_to_project(attachment_data)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

    return {
        "message":"upload successful"
    }
@project_router.post('/{project_id}/invite',status_code=201)
def invite_user_to_project(project_id,user:str=Query(...,description='The email of the destination'),sender_id:int=Depends(get_user)):

    project = get_project(project_id)

    is_owner=validate_role(project_id,sender_id,UserRoles.OWNER.value)

    if not is_owner:
        raise HTTPException(403,'Unauthorized')

    if not does_user_exist(user):
        raise HTTPException(404,'User Not Found')

    invited_user=return_id_by_email(user)

    if not invited_user:
        raise HTTPException(404, "User Not Found")

    try:
        with Session(engine) as session:
            with session.begin():
                data=CreateUserToProjectRole(user_id=invited_user,project_id=project_id,role=UserRoles.PARTICIPANT.value)
                create_user_for_project(session,data)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

    return {"message":'successfully added user to the project'}

@project_router.delete('/{project_id}',status_code=204)
async def call_delete_project(project_id,user_id: int =Depends(get_user)):

    project = get_project(project_id)

    is_owner = validate_role(project_id, user_id, UserRoles.OWNER.value)

    if not is_owner:
        raise HTTPException(403,'Unauthorized')

    delete_all_participants(project_id)

    project_attachments=get_all_attachment_id(project_id) #tuple a return, elso az id, masodik a kulcs

    for attachment in project_attachments:
        try:
            await delete_mock(attachment[1])
        except Exception as e:
            raise HTTPException(500, f"S3 delete failed: {e}")

        delete_attachment_to_project(attachment[0])

    delete_all_owners(project_id)

    delete_project(project_id)

    return
