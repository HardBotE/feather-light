from typing import List

from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.params import Depends, Query, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.app.auth.auth import get_user, check_project_permission
from src.app.crud.attachment_to_project_model_crud import (
    create_attachment_to_project,
    get_all_attachment_id,
    delete_attachment_to_project,
    get_all_attachments,
)
from src.app.crud.project_crud import (
    create_project,
    get_project,
    update_project,
    delete_project,
    project_exists,
)
from src.app.crud.user_crud import return_id_by_email
from src.app.crud.user_to_project_table_crud import (
    validate_role,
    create_user_for_project,
    get_all_projects_info,
    delete_all_participants,
    delete_all_owners,
)
from src.app.db.db import engine
from src.app.requests.attachment_to_project_model import (
    AttachmentToProjectUpload,
    AttachmentToProjectReturn,
)
from src.app.requests.project_model import ProjectCreate, ProjectSchema
from src.app.requests.user_model import UserRoles
from src.app.requests.user_to_project_model import CreateUserToProjectRole
from src.app.documents.aws_s3 import upload_mock, delete_mock

projects_router = APIRouter(prefix="/api/projects")


@projects_router.get("/", response_model=List[ProjectSchema], status_code=200)
def get_all_projects(user_id: int = Depends(get_user)):
    all_projects = get_all_projects_info(user_id)
    return all_projects


@projects_router.post("/", status_code=201)
def call_create_project(project_data: ProjectCreate, user_id: int = Depends(get_user)):
    try:
        with Session(engine) as session:
            with session.begin():
                new_project = ProjectCreate(
                    name=project_data.name, description=project_data.description
                )
                out_project = create_project(session, new_project)

                new_user_to_project = CreateUserToProjectRole(
                    user_id=user_id,
                    project_id=out_project.id,
                    role=UserRoles.OWNER.value,
                )
                create_user_for_project(session, new_user_to_project)

                return {
                    "message": "successfully created project",
                    "project": {
                        "id": out_project.id,
                        "name": out_project.name,
                        "desc": out_project.description,
                    },
                    "user": new_user_to_project,
                }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=e)


project_router = APIRouter(prefix="/api/project")


@project_router.get("/{project_id}/info", status_code=200)
def get_project_info(project_id: int, user_id: int = Depends(get_user)):
    if not project_exists(project_id):
        raise HTTPException(404, "Unable to find project with given ID")

    if not (check_project_permission(project_id=project_id, user_id=user_id)):
        raise HTTPException(403, "Unauthorized")

    project_data = get_project(project_id)

    return {"message": "successfully retrieved data", "project": project_data}


@project_router.put("/{project_id}/info", status_code=200)
def update_project_info(
    project_id: int, project_data: ProjectCreate, user_id: int = Depends(get_user)
):
    if not project_exists(project_id):
        raise HTTPException(404, "Unable to find project with given ID")

    if not (check_project_permission(project_id=project_id, user_id=user_id)):
        raise HTTPException(403, "Unauthorized")

    update_project(project_id, project_data)
    new_data = get_project(project_id)

    return {"message": "successfully updated data", "updated_data": new_data}


@project_router.get("/{project_id}/documents", status_code=200)
def return_documents(project_id: int, user_id: int = Depends(get_user)):
    if not project_exists(project_id):
        raise HTTPException(404, "Unable to find project with given ID")

    if not (check_project_permission(project_id=project_id, user_id=user_id)):
        raise HTTPException(403, "Unauthorized")

    documents = get_all_attachments(project_id)

    return {
        "message": "successfully retrieved data",
        "documents": [
            AttachmentToProjectReturn.model_validate(document) for document in documents
        ],
    }


@project_router.post("/{project_id}/documents", status_code=201)
def upload_file(
    project_id: int, file: UploadFile = File(...), user_id: int = Depends(get_user)
):
    if not project_exists(project_id):
        raise HTTPException(404, "Unable to find project with given ID")

    if not (check_project_permission(project_id=project_id, user_id=user_id)):
        raise HTTPException(403, "Unauthorized")

    try:
        document = upload_mock(file, project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {e}")

    attachment_data = AttachmentToProjectUpload(
        user_id=user_id,
        project_id=project_id,
        uri=document.get("url"),
        key=document.get("key"),
        mimetype=document.get("mime"),
        name=file.filename,
    )

    try:
        create_attachment_to_project(attachment_data)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

    return {"message": "upload successful"}


@project_router.post("/{project_id}/invite", status_code=201)
def invite_user_to_project(
    project_id: int,
    user: str = Query(..., description="The email of the destination"),
    sender_id: int = Depends(get_user),
):
    if not project_exists(project_id):
        raise HTTPException(404, "Unable to find project with given ID")

    if not (
        check_project_permission(
            project_id=project_id, user_id=sender_id, role=[UserRoles.OWNER.value]
        )
    ):
        raise HTTPException(403, "Unauthorized")

    invited_user = return_id_by_email(user)

    if not invited_user:
        raise HTTPException(404, "User Not Found")

    if invited_user == sender_id:
        raise HTTPException(403, "Owner cannot invite him/her self")

    user_already_added = validate_role(
        project_id=project_id, user_id=invited_user, role=[UserRoles.PARTICIPANT.value]
    )

    if user_already_added:
        raise HTTPException(409, "User Already Added")

    try:
        with Session(engine) as session:
            with session.begin():
                data = CreateUserToProjectRole(
                    user_id=invited_user,
                    project_id=project_id,
                    role=UserRoles.PARTICIPANT.value,
                )
                create_user_for_project(session, data)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

    return {"message": "successfully added user to the project"}


@project_router.delete("/{project_id}", status_code=204)
def call_delete_project(project_id: int, user_id: int = Depends(get_user)):
    if not project_exists(project_id):
        raise HTTPException(404, "Unable to find project with given ID")

    if not (
        check_project_permission(
            project_id=project_id, user_id=user_id, role=[UserRoles.OWNER.value]
        )
    ):
        raise HTTPException(403, "Unauthorized")

    delete_all_participants(project_id)

    project_attachments = get_all_attachment_id(
        project_id
    )  # tuple a return, elso az id, masodik a kulcs

    for attachment in project_attachments:
        try:
            delete_mock(attachment[1])
        except Exception as e:
            raise HTTPException(500, f"S3 delete failed: {e}")

        delete_attachment_to_project(attachment[0])

    delete_all_owners(project_id)
    delete_project(project_id)
    return
