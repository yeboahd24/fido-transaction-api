from app.models.transaction import Transaction
from app.services.analytics_service import AnalyticsService


async def process_transaction(transaction: Transaction):
    # Update user statistics
    await AnalyticsService.update_user_statistics(transaction.user_id, transaction)
