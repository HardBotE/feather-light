from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase


class Base(DeclarativeBase):
    pass

class AttachmentToProject(Base):
    __tablename__ = 'attachment_to_project'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id:Mapped[int]=mapped_column(ForeignKey('users.id'))
    project_id:Mapped[int]=mapped_column(ForeignKey('projects.id'))
    uri:Mapped[str]=mapped_column()
    name:Mapped[str]=mapped_column()
