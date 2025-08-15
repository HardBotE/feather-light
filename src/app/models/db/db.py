import os

import bcrypt
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from src.app.models.user_table import Users

load_dotenv("config.env")

DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DATABASE_USER')}:{os.getenv('DB_PASSWORD')}@localhost:5432/{os.getenv('DB_NAME')}"

engine=create_engine(DATABASE_URL)

def register(credentials):
    with Session(engine) as session:
        with session.begin():
            email,password,password_confirm=credentials

            if password!=password_confirm:
                raise ValueError('Passwords don\'t match!')

            password=password.encode('utf-8')
            salt=bcrypt.gensalt(rounds=12)
            hashed_password= bcrypt.hashpw(password,salt).decode('utf-8')
            session.add(Users(email=email,password=hashed_password))

            session.commit()

def login(credentials):
    with Session(engine) as session:
        with session.begin():
            email,password=credentials

            user=session.query(Users)



def create_project(project):
    with Session(engine) as session:
        with session.begin():
            session.add(project)
            session.commit()