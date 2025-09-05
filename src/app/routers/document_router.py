

from fastapi import APIRouter, Depends, UploadFile,HTTPException
from fastapi.params import File

from src.app.crud.attachment_to_project_model_crud import get_attachment_to_project, update_attachment_to_project, \
    delete_attachment_to_project
from src.app.crud.user_to_project_table_crud import validate_role
from src.app.documents.aws_s3 import download_mock, update_mock, delete_mock
from src.app.requests.attachment_to_project_model import AttachmentToProjectReturn, AttachmentToProjectUpdate
from src.app.requests.user_model import UserRoles
from src.app.routers.auth_router import get_user

document_router=APIRouter(prefix='/api/document')

@document_router.get('/{document_id}',status_code=200)
async def download_document(document_id:int,user_id:int=Depends(get_user)):

    document:AttachmentToProjectReturn=get_attachment_to_project(document_id)

    key = document.key
    project_id=document.project_id

    is_participant=validate_role(project_id,user_id,role=UserRoles.PARTICIPANT.value)
    is_owner=validate_role(project_id,user_id,role=UserRoles.OWNER.value)

    if not is_participant and not is_owner:
        raise HTTPException(403,'Unauthorized')

    try:
        link = await download_mock(key)
    except Exception as e:
        raise HTTPException(500, f"S3 download failed: {e}")

    if not link:
        raise HTTPException(404, "Unable to download document")

    return {"message":"The download link is viable for 5 minutes","link":link}

@document_router.put('/{document_id}')
async def update_document(document_id:int,user_id:int=Depends(get_user),file: UploadFile=File(...)):

    document:AttachmentToProjectReturn = get_attachment_to_project(document_id)

    project_id=document.project_id
    key=document.key
    mime = file.content_type

    is_participant = validate_role(project_id, user_id, role=UserRoles.PARTICIPANT.value) and document.user_id==user_id
    is_owner = validate_role(project_id, user_id, role=UserRoles.OWNER.value)

    if not is_participant and not is_owner:
        raise HTTPException(403, 'Unauthorized')

    try:
        await update_mock(key,mime,file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 update failed: {e}")

    new_file:AttachmentToProjectUpdate=AttachmentToProjectUpdate(user_id=user_id,name=file.filename)
    update_attachment_to_project(document_id,new_file)

    return {"message":"document_updated"}


@document_router.delete('/{document_id}')
async def delete_document(document_id:int,user_id:int=Depends(get_user)):

    document:AttachmentToProjectReturn=get_attachment_to_project(document_id)
    project_id=document.project_id
    key = document.key

    is_participant = validate_role(project_id, user_id, role=UserRoles.PARTICIPANT.value) and document.user_id==user_id
    is_owner = validate_role(document.project_id, user_id, role=UserRoles.OWNER.value)

    if not is_participant and not is_owner:
        raise HTTPException(403, 'Unauthorized')

    try:
        await delete_mock(key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 delete failed: {e}")

    delete_attachment_to_project(document_id)

    return {"message":"deleted","key":key,"response":response}
