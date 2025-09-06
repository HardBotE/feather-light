from typing import List

from pydantic import BaseModel, Field, ConfigDict

from src.app.requests.attachment_to_project_model import AttachmentToProjectReturn


class ProjectOut(BaseModel):
    id: int
    name: str
    description: str


class ProjectCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str


class ProjectSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    # noinspection PyDataclass
    attachments: List[AttachmentToProjectReturn] = Field(default_factory=list)
