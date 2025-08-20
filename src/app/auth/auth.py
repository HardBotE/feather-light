import os
from datetime import datetime, timedelta

import bcrypt
from sqlalchemy.orm import Session

import jwt
from fastapi import HTTPException

from src.app.db.db import engine
from src.app.models.user_table import Users
from src.app.requests.user_model import LoginUserModel


def create_token(user_id):
    exp_date=(datetime.now()+timedelta(hours=1)).timestamp()
    return jwt.encode({
        "user_id":user_id,
        "exp":exp_date
    },os.getenv("JWT_SECRET"), algorithm='HS256')

def decode_token(token):
    try:
        return jwt.decode(token,os.getenv("JWT_SECRET"),algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401,'Token expired, login again.')
    except jwt.InvalidTokenError:
        raise HTTPException(401,'Invalid token')

def return_token(credentials:LoginUserModel):
    with Session(engine) as session:
        with session.begin():
            user=session.query(Users).filter(Users.email==credentials.email).first()
            if not user:
                raise HTTPException(401,'No user with the given email address.')

            if not bcrypt.checkpw(credentials.password.encode('utf-8'),user.password.encode('utf-8')):
                raise HTTPException(401,'Invalid credentials!')

        token=create_token(user.id)

    return token


