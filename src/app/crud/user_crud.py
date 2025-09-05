from fastapi import HTTPException

import bcrypt
from sqlalchemy.orm import Session


from ..db.db import engine
from ..models.user_table import UsersTable
from ..requests.user_model import RegisterUserModel, LoginUserModel


def register(credentials:RegisterUserModel):
    with Session(engine) as session:
        with session.begin():

            is_user_registered=session.query(UsersTable).filter(UsersTable.email==credentials.email).first()

            if is_user_registered:
                raise HTTPException(409, "User already registered")

            if credentials.password!=credentials.password_confirm:
                raise HTTPException(400,'Passwords don\'t match!')

            password=credentials.password.encode('utf-8')
            salt=bcrypt.gensalt(rounds=12)
            hashed_password= bcrypt.hashpw(password,salt).decode('utf-8')
            session.add(UsersTable(email=str(credentials.email),password=hashed_password))

def does_user_exist(email):
    with Session(engine) as session:
        with session.begin():
            is_user_registered = session.query(UsersTable).filter(UsersTable.email == email).first()

            return is_user_registered is not None

def return_id_by_email(email):
    with Session(engine) as session:
        with session.begin():
            is_user_registered = session.query(UsersTable).filter(UsersTable.email == email).first()

            return is_user_registered.id