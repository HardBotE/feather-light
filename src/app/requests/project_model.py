from pydantic import BaseModel

class ProjectOut(BaseModel):
    id:int
    name:str
    description:str

class ProjectCreate(BaseModel):
    name:str
    description:str

