from sqlalchemy.orm import Session

from app.models.user import User

from app.schemas.auth_schema import RegisterRequest

from app.core.security import hash_password

from app.core.security import verify_password



def create_user(

    db: Session,

    user_data: RegisterRequest

):

    existing_email = (

        db.query(User)

        .filter(

            User.email == user_data.email

        )

        .first()

    )

    if existing_email:

        return None


    user = User(

        username=user_data.username,

        email=user_data.email,

        full_name=user_data.full_name,

        hashed_password=hash_password(

            user_data.password

        )

    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user



def authenticate_user(

    db: Session,

    email: str,

    password: str

):

    user = (

        db.query(User)

        .filter(

            User.email == email

        )

        .first()

    )


    if not user:

        return None


    if not verify_password(

        password,

        user.hashed_password

    ):

        return None


    return user