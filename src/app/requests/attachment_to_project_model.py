from pydantic import BaseModel, ConfigDict


class AttachmentToProject(BaseModel):
    id:int
    user_id: int
    project_id: int
    name:str
    uri:str | None=None

class AttachmentToProjectUpload(BaseModel):
    user_id: int
    project_id: int
    name:str
    uri:str | None=None
    mimetype:str
    key:str

class AttachmentToProjectReturn(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:int
    user_id: int
    project_id: int
    name: str
    uri: str | None = None
    mimetype: str
    key: str



class AttachmentToProjectUpdate(BaseModel):
    user_id:int
    name:str