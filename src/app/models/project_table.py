from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.app.db.base import Base


class Projects(Base):
    __tablename__ = 'projects'

    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    name:Mapped[str]=mapped_column()
    description: Mapped[str] = mapped_column()


