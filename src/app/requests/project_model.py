from pydantic import BaseModel

class Project(BaseModel):
    id:int
    owner_id:int
    name:str
    description:str

