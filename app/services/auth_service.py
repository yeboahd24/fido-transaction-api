import os
import jwt
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User, UserCreate, users_table
from app.schemas.user import UserLogin
from app.utils.encryption import hash_password, verify_password
from app.utils.jwt import TokenService
from typing import Optional
from databases import Database
from uuid import uuid4


database = Database(
    f"postgresql://postgres@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)


class AuthService:
    @staticmethod
    async def login_user(user_login: UserLogin, database: Database):
        try:
            # Verify user credentials
            user = await AuthService.get_user_by_username(user_login.username, database)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                )

            # Verify password
            if not verify_password(user_login.password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                )

            # Create token data
            token_data = {
                "sub": user.username,
                "user_id": str(user.id),
                "email": user.email,
            }

            # Create access token
            access_token = TokenService.create_access_token(token_data)

            return {"access_token": access_token, "token_type": "bearer"}

        except Exception as e:
            print(f"Login error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    @staticmethod
    async def register_user(user: UserCreate, database: Database):
        existing_user_query = users_table.select().where(
            users_table.c.email == user.email
        )
        existing_user = await database.fetch_one(existing_user_query)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        existing_username_query = users_table.select().where(
            users_table.c.username == user.username
        )

        username_exist = await database.fetch_one(existing_username_query)
        if username_exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username already exists",
            )

        # Hash the password and create a new user if no existing user is found
        hashed_password = hash_password(user.password)
        user_id = uuid4()
        new_user = User(
            id=user_id,
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
        )

        # Insert the new user into the database
        query = users_table.insert().values(**new_user.dict(exclude_unset=True))
        await database.execute(query)
        return AuthService.to_response(new_user)

    @staticmethod
    def to_response(user: User):
        return {"id": user.id, "username": user.username, "email": user.email}

    @staticmethod
    async def get_user_by_id(user_id: str, database: Database) -> Optional[User]:
        query = select(users_table).where(users_table.c.id == user_id)
        user_record = await database.fetch_one(query)
        if user_record:
            return User(**user_record)
        return None

    async def get_user_by_username(username: str, database: Database) -> Optional[User]:
        query = select(users_table).where(users_table.c.username == username)
        user_record = await database.fetch_one(query)
        if user_record:
            return User(**user_record)
        return None


async def get_current_user(payload: str, database: Database) -> Optional[User]:
    try:
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = await AuthService.get_user_by_id(user_id, database)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return user
