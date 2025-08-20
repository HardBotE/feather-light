import enum

from pydantic import BaseModel

from src.app.requests.user_model import UserRoles


class UserToProjectOut(BaseModel):
    id:int
    user_id: int
    project_id: int
    role:UserRoles

class CreateUserToProjectRole(BaseModel):
    user_id: int
    project_id: int
    role:str