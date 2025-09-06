from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.db.base import Base


class ProjectsTable(Base):
    __tablename__ = "projects"

    class Config:
        orm_mode = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()

    attachments = relationship("AttachmentToProjectTable", back_populates="project")
