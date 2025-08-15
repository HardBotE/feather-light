from pydantic import BaseModel


class AttachmentToProject(BaseModel):
    id:int
    user_id: int
    project_id: int
    name:str
    uri:str | None=None