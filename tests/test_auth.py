import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException, status
from app.models.user import UserCreate
from app.schemas.user import UserLogin
from app.services.auth_service import AuthService, get_current_user
from databases import Database
from uuid import uuid4


# Mock the database
@pytest.fixture
def mock_database():
    return AsyncMock(spec=Database)


# Mock the TokenService
@pytest.fixture
def mock_token_service():
    with patch("app.services.auth_service.TokenService") as mock:
        yield mock


# Mock the hash_password and verify_password functions
@pytest.fixture
def mock_encryption():
    with patch("app.services.auth_service.hash_password") as mock_hash:
        with patch("app.services.auth_service.verify_password") as mock_verify:
            yield mock_hash, mock_verify


# Test login_user method
@pytest.mark.asyncio
async def test_login_user_success(mock_database, mock_token_service, mock_encryption):
    mock_hash, mock_verify = mock_encryption
    mock_verify.return_value = True
    mock_token_service.create_access_token.return_value = "access_token"

    user_login = UserLogin(username="testuser", password="testpassword")
    mock_user_dict = {
        "id": uuid4(),  # Generate a valid UUID
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashedpassword",
    }
    mock_database.fetch_one.return_value = mock_user_dict  # Use a dictionary

    result = await AuthService.login_user(user_login, mock_database)

    assert result == {"access_token": "access_token", "token_type": "bearer"}
    mock_database.fetch_one.assert_called_once()
    mock_verify.assert_called_once_with("testpassword", "hashedpassword")
    mock_token_service.create_access_token.assert_called_once()


@pytest.mark.asyncio
async def test_login_user_invalid_credentials(mock_database, mock_encryption):
    mock_hash, mock_verify = mock_encryption
    mock_verify.return_value = False

    user_login = UserLogin(username="testuser", password="wrongpassword")
    mock_user_dict = {
        "id": uuid4(),  # Generate a valid UUID
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashedpassword",
    }
    mock_database.fetch_one.return_value = mock_user_dict  # Use a dictionary

    with pytest.raises(HTTPException) as exc_info:
        await AuthService.login_user(user_login, mock_database)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    # assert exc_info.value.detail == "Incorrect username or password"
    mock_database.fetch_one.assert_called_once()
    mock_verify.assert_called_once_with("wrongpassword", "hashedpassword")


@pytest.mark.asyncio
async def test_register_user_existing_email(mock_database):
    mock_database.fetch_one.return_value = {
        "id": uuid4(),  # Generate a valid UUID
        "username": "existinguser",
        "email": "existing@example.com",
        "hashed_password": "hashedpassword",
    }  # Use a dictionary

    user_create = UserCreate(
        username="newuser", email="existing@example.com", password="newpassword"
    )
    with pytest.raises(HTTPException) as exc_info:
        await AuthService.register_user(user_create, mock_database)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "User with this email already exists"
    mock_database.fetch_one.assert_called_once()


# Test get_current_user method
@pytest.mark.asyncio
async def test_get_current_user_success(mock_database):
    mock_database.fetch_one.return_value = {
        "id": uuid4(),  # Generate a valid UUID
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashedpassword",
    }  # Use a dictionary

    payload = {"user_id": str(uuid4())}  # Generate a valid UUID and convert to string
    result = await get_current_user(payload, mock_database)

    assert result.username == "testuser"
    assert result.email == "test@example.com"
    mock_database.fetch_one.assert_called_once()


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_database):
    payload = {"user_id": None}
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(payload, mock_database)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token"
    mock_database.fetch_one.assert_not_called()


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(mock_database):
    mock_database.fetch_one.return_value = None

    payload = {"user_id": str(uuid4())}  # Generate a valid UUID and convert to string
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(payload, mock_database)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token"
    mock_database.fetch_one.assert_called_once()

