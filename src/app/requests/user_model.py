from pydantic import BaseModel, EmailStr


class LoginUserModel(BaseModel):
    id:int | None=None
    email:EmailStr
    password:str

class RegisterUserModel(BaseModel):
    email:EmailStr
    password:str
    password_confirm:str

