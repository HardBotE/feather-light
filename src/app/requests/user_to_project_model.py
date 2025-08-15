from pydantic import BaseModel

class UserToProject(BaseModel):
    id:int
    user_id: int
    project_id: int