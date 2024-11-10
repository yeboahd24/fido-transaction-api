import pytest
from unittest.mock import Mock, patch
from uuid import UUID
from fastapi import HTTPException
from databases import Database
from app.models.user import User, UserCreate
from app.schemas.user import UserLogin
from app.services.auth_service import AuthService
from app.utils.jwt import TokenService


@pytest.fixture
def mock_database():
    return Mock(spec=Database)


@pytest.fixture
def sample_user():
    # Create a mock encrypted password that matches what we'll use in the test
    mock_encrypted_password = "gAAAAABk6JH6dVRPO8vZ9q9j_YWJ8OX5YbYT6YQ9nQ9W1q2X3D4="
    return User(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        username="testuser",
        email="test@example.com",
        hashed_password=mock_encrypted_password,
    )


@pytest.fixture
def sample_user_create():
    return UserCreate(
        username="testuser", email="test@example.com", password="password123"
    )


@pytest.fixture
def sample_user_login():
    return UserLogin(username="testuser", password="password123")


class TestAuthService:
    @pytest.mark.asyncio
    async def test_login_user_successful(
        self, mock_database, sample_user, sample_user_login
    ):
        # Mock get_user_by_username
        async def mock_get_user(*args, **kwargs):
            return sample_user

        # Mock the encryption/decryption process
        def mock_decrypt(*args, **kwargs):
            return "password123".encode()

        def mock_encrypt(*args, **kwargs):
            return "gAAAAABk6JH6dVRPO8vZ9q9j_YWJ8OX5YbYT6YQ9nQ9W1q2X3D4=".encode()

        with patch(
            "app.services.auth_service.AuthService.get_user_by_username",
            side_effect=mock_get_user,
        ), patch(
            "app.utils.encryption.Fernet.decrypt",
            side_effect=mock_decrypt,
        ), patch(
            "app.utils.encryption.Fernet.encrypt",
            side_effect=mock_encrypt,
        ):
            # Mock token creation
            expected_token = "dummy_token"
            with patch.object(
                TokenService, "create_access_token", return_value=expected_token
            ):
                result = await AuthService.login_user(sample_user_login, mock_database)

                assert result["access_token"] == expected_token
                assert result["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_user_invalid_username(self, mock_database, sample_user_login):
        async def mock_get_user(*args, **kwargs):
            return None

        with patch(
            "app.services.auth_service.AuthService.get_user_by_username",
            side_effect=mock_get_user,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await AuthService.login_user(sample_user_login, mock_database)

            assert exc_info.value.status_code == 500
            assert exc_info.value.detail == "401: Incorrect username or password"

    @pytest.mark.asyncio
    async def test_login_user_invalid_password(
        self, mock_database, sample_user, sample_user_login
    ):
        async def mock_get_user(*args, **kwargs):
            return sample_user

        def mock_decrypt(*args, **kwargs):
            return "wrong_password".encode()

        with patch(
            "app.services.auth_service.AuthService.get_user_by_username",
            side_effect=mock_get_user,
        ), patch(
            "app.utils.encryption.Fernet.decrypt",
            side_effect=mock_decrypt,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await AuthService.login_user(sample_user_login, mock_database)

            assert exc_info.value.status_code == 500
            assert exc_info.value.detail == "401: Incorrect username or password"

    @pytest.mark.asyncio
    async def test_register_user_successful(self, mock_database, sample_user_create):
        # Mock database responses for checking existing user
        mock_database.fetch_one.return_value = None
        mock_database.execute.return_value = None

        # Mock password hashing
        hashed_password = "hashed_password_123"
        with patch("app.utils.encryption.hash_password", return_value=hashed_password):
            with patch(
                "app.services.auth_service.uuid4",
                return_value=UUID("12345678-1234-5678-1234-567812345678"),
            ):
                result = await AuthService.register_user(
                    sample_user_create, mock_database
                )

        assert result["username"] == sample_user_create.username
        assert result["email"] == sample_user_create.email
        assert "id" in result
        assert "hashed_password" not in result

    @pytest.mark.asyncio
    async def test_register_user_existing_email(
        self, mock_database, sample_user_create
    ):
        # Mock database response for existing user with same email
        mock_database.fetch_one.return_value = {"email": sample_user_create.email}

        with pytest.raises(HTTPException) as exc_info:
            await AuthService.register_user(sample_user_create, mock_database)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "User with this email already exists"

    @pytest.mark.asyncio
    async def test_register_user_existing_username(
        self, mock_database, sample_user_create
    ):
        # Mock database responses - no user with same email, but username exists
        mock_database.fetch_one.side_effect = [
            None,
            {"username": sample_user_create.username},
        ]

        with pytest.raises(HTTPException) as exc_info:
            await AuthService.register_user(sample_user_create, mock_database)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "User with this username already exists"

