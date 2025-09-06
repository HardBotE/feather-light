from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.app.db.base import Base


class AttachmentToProjectTable(Base):
    __tablename__ = "attachment_to_project"

    class Config:
        orm_mode = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    uri: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    mimetype: Mapped[str] = mapped_column()
    key: Mapped[str] = mapped_column()

    project = relationship("ProjectsTable", back_populates="attachments")
