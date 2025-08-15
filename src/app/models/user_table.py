from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = 'users'

    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    email:Mapped[str]=mapped_column(unique=True,nullable=False)
    password:Mapped[str]=mapped_column(nullable=False)