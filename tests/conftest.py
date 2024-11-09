import pytest
from unittest.mock import AsyncMock
import os
from cryptography.fernet import Fernet


def pytest_configure(config):
    """Set up global test configuration."""
    # Generate and set encryption key at the start of test session
    if "ENCRYPTION_KEY" not in os.environ:
        test_key = Fernet.generate_key()
        os.environ["ENCRYPTION_KEY"] = test_key.decode()


def pytest_unconfigure(config):
    """Clean up after all tests are done."""
    if "ENCRYPTION_KEY" in os.environ:
        del os.environ["ENCRYPTION_KEY"]


@pytest.fixture
def mock_database():
    return AsyncMock()


@pytest.fixture
def mock_token_service():
    from unittest.mock import patch

    with patch("app.utils.jwt.TokenService.create_access_token") as mock:
        mock.return_value = "fake-token"
        yield mock
