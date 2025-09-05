from sqlalchemy.orm import  Mapped, mapped_column
from src.app.db.base import Base



class UsersTable(Base):
    __tablename__ = 'users'

    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    email:Mapped[str]=mapped_column(unique=True,nullable=False)
    password:Mapped[str]=mapped_column(nullable=False)