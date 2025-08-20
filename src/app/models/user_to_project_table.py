from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from src.app.db.base import Base



class UserToProjectTable(Base):
    __tablename__ = 'user_to_project'

    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    user_id:Mapped[int]=mapped_column(ForeignKey('users.id'))
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'))
    role:Mapped[str]=mapped_column()