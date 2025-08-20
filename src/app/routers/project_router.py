from http.client import HTTPException

from fastapi import APIRouter, Request, UploadFile
from fastapi.params import Depends, Query
from sqlalchemy.orm import  Session

from src.app.crud.project_crud import create_project, get_project, \
    update_project, delete_project
from src.app.crud.user_crud import does_user_exist, return_id_by_email
from src.app.crud.user_to_project_table_crud import validate_role, create_user_for_project
from src.app.db.db import engine
from src.app.models.user_to_project_table import UserToProjectTable
from src.app.requests.attachment_to_project_model import AttachmentToProject
from src.app.requests.project_model import ProjectCreate, ProjectOut
from src.app.requests.user_model import UserRoles
from src.app.requests.user_to_project_model import CreateUserToProjectRole
from src.app.routers.auth_router import get_user

projects_router=APIRouter(prefix='/api/projects')


@projects_router.get('/')
def get_all_projects(user_id:Depends(get_user)):
    pass

@projects_router.post('/')
def call_create_project(project_data:ProjectCreate,user_id: int =Depends(get_user)):
    with Session(engine) as session:
        with session.begin():
            new_project= ProjectCreate(name=project_data.name,description=project_data.description)
            out_project=create_project(session,new_project)

            new_user_to_project=CreateUserToProjectRole(user_id=user_id,project_id=out_project.id,role=UserRoles.OWNER)
            create_user_for_project(session,new_user_to_project)

            return {"message":"successfully created project","project":{"id":out_project.id,"name":out_project.name,"desc":out_project.description},'user':new_user_to_project}


project_router=APIRouter(prefix='/api/project')

@project_router.get('/{project_id}/info')
def get_project_info(project_id,user_id: int =Depends(get_user)):

   is_owner=validate_role(project_id,user_id,UserRoles.OWNER)
   is_participant=validate_role(project_id,user_id,UserRoles.PARTICIPANT)

   if not (is_owner or  is_participant):
       raise HTTPException(403,'Unauthorized')

   project_data=get_project(project_id)

   return {'message':'successfully retrieved data','project':project_data}

@project_router.put('/{project_id}/info')
def update_project_info(project_id,project_data:ProjectCreate,user_id: int =Depends(get_user)):

    is_owner = validate_role(project_id, user_id, UserRoles.OWNER)
    is_participant = validate_role(project_id, user_id, UserRoles.PARTICIPANT)

    if not (is_owner or  is_participant):
        raise HTTPException(403,'Unauthorized')

    update_project(project_id,project_data)
    new_data=get_project(project_id)

    return {'message':'successfully updated data','updated_data':new_data}

@project_router.get('/{project_id}/documents')
def return_documents():
    pass

@project_router.post('/{project_id}/documents')
def upload_file(project_id: int,file: UploadFile,user_id:int=Depends(get_user)):
    is_owner = validate_role(project_id, user_id, UserRoles.OWNER)
    is_participant = validate_role(project_id, user_id, UserRoles.PARTICIPANT)

    if not is_owner and not is_participant:
        raise HTTPException(403,'Unauthorized')

    attachment_to_project_data=AttachmentToProject(user_id=user_id,project_id=project_id,uri=None,name=None)





@project_router.post('/{project_id}/invite')
def invite_user_to_project(project_id,user:str=Query(...,description='The email of the destination'),sender_id:int=Depends(get_user)):

    is_owner=validate_role(project_id,sender_id,UserRoles.OWNER)

    if not is_owner:
        raise HTTPException(403,'Unauthorized')

    if not does_user_exist(user):
        raise HTTPException(404,'User Not Found')

    invited_user=return_id_by_email(user)

    with Session(engine) as session:
        with session.begin():
            data=CreateUserToProjectRole(user_id=invited_user,project_id=project_id,role=UserRoles.PARTICIPANT.value)
            create_user_for_project(session,data)

    return {"message":'successfully added user to the project'}

@project_router.delete('/{project_id}')
def call_delete_project(project_id,user_id: int =Depends(get_user)):
    is_owner = validate_role(project_id, user_id, UserRoles.OWNER)

    if not is_owner:
        raise HTTPException(403,'Unauthorized')
    """
    delete_project(project_id)
    TODO DELETE- USERS
    TODO DELETE- DOCUMENTS
    """
    return {"data":None}
