from http.client import HTTPException

from fastapi import APIRouter, Depends, UploadFile
from fastapi.params import File

from src.app.crud.attachment_to_project_model_crud import get_attachment_to_project, update_attachment_to_project, \
    delete_attachment_to_project
from src.app.crud.user_to_project_table_crud import validate_role
from src.app.documents.aws_s3 import download_mock, update_mock, delete_mock
from src.app.requests.attachment_to_project_model import AttachmentToProjectReturn, AttachmentToProjectUpdate
from src.app.requests.user_model import UserRoles
from src.app.routers.auth_router import get_user

document_router=APIRouter(prefix='/api/document/{document_id}')

@document_router.get('')
async def download_document(document_id:int,user_id:int=Depends(get_user)):

    document:AttachmentToProjectReturn=get_attachment_to_project(document_id)

    key = document.key
    project_id=document.project_id

    is_participant=validate_role(project_id,user_id,role=UserRoles.PARTICIPANT)
    is_owner=validate_role(project_id,user_id,role=UserRoles.OWNER)

    if not is_participant and not is_owner:
        raise HTTPException(403,'Unauthorized')

    return await download_mock(key)

@document_router.put('')
async def update_document(document_id:int,user_id:int=Depends(get_user),file: UploadFile=File(...)):

    document = get_attachment_to_project(document_id)
    project_id=document.project_id
    key=document.key
    mime = file.content_type

    is_participant = validate_role(project_id, user_id, role=UserRoles.PARTICIPANT) and document.user_id==user_id
    is_owner = validate_role(project_id, user_id, role=UserRoles.OWNER)

    if not is_participant and not is_owner:
        raise HTTPException(403, 'Unauthorized')

    await update_mock(key,mime,file)
    new_file:AttachmentToProjectUpdate=AttachmentToProjectUpdate(user_id=user_id,name=file.filename)
    update_attachment_to_project(document_id,new_file)

    return {"message":"document_updated"}


@document_router.delete('')
async def delete_document(document_id:int,user_id:int=Depends(get_user)):

    document:AttachmentToProjectReturn=get_attachment_to_project(document_id)
    print(document.model_dump())
    project_id=document.project_id
    key = document.key

    is_participant = validate_role(project_id, user_id, role=UserRoles.PARTICIPANT) and document.user_id==user_id
    is_owner = validate_role(document.project_id, user_id, role=UserRoles.OWNER)

    if not is_participant and not is_owner:
        raise HTTPException(403, 'Unauthorized')

    response=await delete_mock(key)

    delete_attachment_to_project(document_id)

    return {"message":"deleted","key":key,"response":response}
