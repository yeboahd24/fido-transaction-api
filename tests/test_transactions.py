# import pytest
# from unittest.mock import AsyncMock, MagicMock, patch
# from app.models.transaction import TransactionCreate, TransactionType
# from app.services.transaction_service import TransactionService
#
#
# @pytest.fixture
# def mock_db():
#     """Fixture to create a mock database connection."""
#     return AsyncMock()
#
#
# @pytest.fixture
# def mock_request():
#     """Fixture to create a mock request with user state."""
#     request = MagicMock()
#     request.state.user = MagicMock(id="test_user_id")
#     return request
#
#
# @pytest.mark.asyncio
# @patch("app.utils.encryption.decrypt_data", return_value="John Doe")
# @patch("app.utils.encryption.encrypt_data", return_value="encrypted_full_name")
# async def test_create_transaction(mock_encrypt, mock_decrypt, mock_db, mock_request):
#     # Arrange
#     transaction_data = TransactionCreate(
#         full_name="John Doe",
#         transaction_amount=100.0,
#         transaction_type=TransactionType.credit,
#         transaction_date="2024-01-01",
#         user_id=str(mock_request.state.user.id),  # Include user_id here if needed
#     )
#
#     TransactionService.update_aggregated_fields = AsyncMock()
#
#     # Act
#     result = await TransactionService.create_transaction(
#         mock_db, mock_request, transaction_data
#     )
#
#     # Assert
#     assert result["full_name"] == "John Doe"
#     assert result["transaction_amount"] == 100.0
#
#
# ##########################
