import enum

from pydantic import BaseModel, EmailStr


class LoginUserModel(BaseModel):
    email: EmailStr
    password: str


class RegisterUserModel(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str


class UserRoles(enum.Enum):
    OWNER = "owner"
    PARTICIPANT = "participant"


class UserAccess(BaseModel):
    user_id: int
    user_role: str
