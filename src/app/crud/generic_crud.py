import os
from typing import TypeVar, Generic

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
"""
TODO ASK OPINION
T=TypeVar('T')
D=TypeVar('D')

load_dotenv(".env")

DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DATABASE_USER')}:{os.getenv('DB_PASSWORD')}@localhost:5432/{os.getenv('DB_NAME')}"

engine=create_engine(DATABASE_URL)

class GenericCRUD(Generic[T]):
    def __init__(self,table: T):
        self.table=table

    def create_factory(self,data):
        with Session(engine) as session:
            data_obj=self.table(**data)
            session.add(T(data))
"""