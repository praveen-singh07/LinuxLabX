from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.auth_schema import RegisterRequest
from app.schemas.auth_schema import LoginRequest

from app.services.auth_service import create_user
from app.services.auth_service import authenticate_user

from app.core.security import create_access_token


router = APIRouter(

    prefix="/auth",

    tags=["Authentication"]

)


@router.post("/register")

def register(

    user_data: RegisterRequest,

    db: Session = Depends(get_db)

):

    user = create_user(

        db,

        user_data

    )

    if user is None:

        raise HTTPException(

            status_code=400,

            detail="Email already exists"

        )

    return {

        "message":

        "User registered successfully"

    }



@router.post("/login")

def login(

    login_data: LoginRequest,

    db: Session = Depends(get_db)

):

    user = authenticate_user(

        db,

        login_data.email,

        login_data.password

    )

    if user is None:

        raise HTTPException(

            status_code=401,

            detail="Invalid email or password"

        )


    token = create_access_token(

        {

            "sub":

            user.email

        }

    )


    return {

        "access_token": token,

        "token_type": "bearer"

    }