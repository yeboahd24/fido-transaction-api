from fastapi import APIRouter, Depends, status
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService

# from fastapi.security import OAuth2PasswordRequestForm
from databases import Database
from app.utils.database import get_database
from app.schemas.user import UserLogin

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, database: Database = Depends(get_database)):
    return await AuthService.register_user(user, database)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    user: UserLogin,
    database: Database = Depends(get_database),
):
    return await AuthService.login_user(user, database)
