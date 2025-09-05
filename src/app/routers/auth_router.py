

import jwt
from fastapi import APIRouter,status,Request,Response,HTTPException
from starlette.responses import JSONResponse

from src.app.auth.auth import decode_token, return_token
from src.app.crud.user_crud import register
from src.app.requests.user_model import RegisterUserModel, LoginUserModel

router=APIRouter(prefix='/api',tags=['auth-router'])


@router.post('/auth')
def register_user(user:RegisterUserModel):
    register(user)
    return JSONResponse(
        status_code=201,
        content={
            "message":"Successfully created account."
        }
    )

@router.post('/login')
def login_user(user:LoginUserModel,response: Response):
    jwt_token=return_token(user)
    response.set_cookie(key='jwt',value=jwt_token,max_age=3600,httponly=True)
    return {
            "message": "Successfully logged in",
            "token":jwt_token
        }


def get_user(request:Request):
    token=request.cookies.get('jwt')

    if not token:
        raise HTTPException(401,'No token provided')

    try:
        data=decode_token(token)
    except jwt.DecodeError:
        raise HTTPException(401,'Invalid token or unexpected error occourred.')

    return data['user_id']