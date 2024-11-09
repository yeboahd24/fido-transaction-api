from app.models.transaction import TransactionType
from redis import Redis
import os
from app.schemas.transaction import AnalyticsData
import json
from app.models.user import User, users_table
from databases import Database
from fastapi import Request

from app.utils.encryption import decrypt_data
from app.models.transaction import (
    transactions_table,
)

from sqlalchemy import select

redis = Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), db=0)


# class AnalyticsService:
#     @staticmethod
#     async def get_user_analytics(user: User, db: Database):
#         from app.services.transaction_service import TransactionService
#
#         # Check if analytics data is cached in Redis
#         cache_key = f"analytics:{user.id}"
#         cached_data = await redis.get(cache_key)
#         if cached_data:
#             return AnalyticsData(**eval(cached_data.decode()))
#
#         # Fetch and process user transactions
#         transactions = await TransactionService.get_user_transactions(user.id)
#         total_debit = sum(
#             t.transaction_amount
#             for t in transactions
#             if t.transaction_type == TransactionType.debit
#         )
#         total_credit = sum(
#             t.transaction_amount
#             for t in transactions
#             if t.transaction_type == TransactionType.credit
#         )
#         average_transaction = (total_debit + total_credit) / len(transactions)
#
#         transaction_counts = {t.transaction_date.date(): 0 for t in transactions}
#         for t in transactions:
#             transaction_counts[t.transaction_date.date()] += 1
#         busiest_day = max(transaction_counts, key=transaction_counts.get)
#
#         analytics_data = AnalyticsData(
#             average_transaction_value=average_transaction,
#             busiest_day=busiest_day,
#         )
#
#         await redis.set(
#             cache_key, str(analytics_data.dict()), ex=3600
#         )  # Cache for 1 hour
#
#         return analytics_data
#
#     @staticmethod
#     async def update_user_statistics(user_id: str, transaction: Transaction):
#         # Update user statistics
#         user = await UserService.get_user(user_id)
#         if not user:
#             return
#         user.total_transactions += 1
#         user.total_credit += transaction.transaction_amount
#         if transaction.transaction_type == TransactionType.debit:
#             user.total_debit += transaction.transaction_amount
#             user.average_transaction_value = (
#                 user.total_debit + user.total_credit
#             ) / user.total_transactions
#         else:
#             user.average_transaction_value = (
#                 user.total_debit + user.total_credit
#             ) / user.total_transactions
#
#         await AnalyticsService.get_user_analytics(user)
#         return user
#


class UserService:
    @staticmethod
    async def get_user(user_id: str, db: Database):
        query = users_table.select().where(users_table.c.id == user_id)
        user_record = await db.fetch_one(query)
        if user_record:
            return User(**user_record)
        return None


class AnalyticsService:
    @staticmethod
    async def get_user_analytics(user_id: str, db: Database):
        from app.services.transaction_service import TransactionService

        # Check if analytics data is cached in Redis
        cache_key = f"analytics:{user_id}"
        cached_data = await redis.get(cache_key)
        if cached_data:
            return AnalyticsData(**json.loads(cached_data.decode()))  # Use json.loads

        # Fetch and process user transactions
        transactions = await TransactionService.get_user_transactions(user_id)
        total_debit = sum(
            t.transaction_amount
            for t in transactions
            if t.transaction_type == TransactionType.debit
        )
        total_credit = sum(
            t.transaction_amount
            for t in transactions
            if t.transaction_type == TransactionType.credit
        )

        average_transaction = (
            (total_debit + total_credit) / len(transactions)
            if transactions
            else 0  # Avoid division by zero
        )

        transaction_counts = {t.transaction_date.date(): 0 for t in transactions}
        for t in transactions:
            transaction_counts[t.transaction_date.date()] += 1

        busiest_day = (
            max(transaction_counts, key=transaction_counts.get)
            if transaction_counts
            else None
        )

        analytics_data = AnalyticsData(
            average_transaction_value=average_transaction,
            total_debit=total_debit,
            total_credit=total_credit,
            transaction_count=len(transactions),
            busiest_day=busiest_day.isoformat() if busiest_day else None,
        )

        # Cache the analytics data for 1 hour
        await redis.set(cache_key, json.dumps(analytics_data.dict()), ex=3600)

        return analytics_data

    # @staticmethod
    # async def analytics(db: Database, request: Request):
    #     user_id = str(request.state.user.id)
    #     analytics_data = await AnalyticsService.get_user_analytics(user_id, db)
    #     return analytics_data
    #
    # @staticmethod
    # async def analytics(db: Database, request: Request):
    #     try:
    #         user_id = str(request.state.user.id)
    #         analytics_data = await AnalyticsService.get_user_analytics(user_id, db)
    #         if analytics_data is None:
    #             return JSONResponse(
    #                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #                 content={"detail": "Error getting user analytics"},
    #             )
    #         return analytics_data
    #     except Exception as e:
    #         return JSONResponse(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             content={"detail": "Internal server error"},
    #         )
    #
    #
    # @staticmethod
    # async def analytics(db: Database, request: Request):
    #     user_id = str(request.state.user.id)
    #
    #     query = select(transactions_table).where(
    #         (transactions_table.c.user_id == user_id)
    #     )
    #
    #     results = await db.fetch_all(query)
    #     if results:
    #         analytics_data = []
    #         for result in results:
    #             result_dict = dict(result)
    #             result_dict["full_name"] = decrypt_data(result_dict["full_name"])
    #             analytics_data.append(
    #                 AnalyticsData(
    #                     full_name=result_dict["full_name"],
    #                     total_transactions=result_dict["total_transactions"],
    #                     total_credit=result_dict["total_credit"],
    #                     total_debit=result_dict["total_debit"],
    #                     average_transaction_value=result_dict[
    #                         "average_transaction_value"
    #                     ],
    #                 )
    #             )
    #         return analytics_data
    #     return []

    @staticmethod
    async def analytics(db: Database, request: Request):
        user_id = str(request.state.user.id)

        query = (
            select(transactions_table)
            .where((transactions_table.c.user_id == user_id))
            .order_by(transactions_table.c.total_transactions.desc())
        )

        results = await db.fetch_all(query)
        if results:
            result_dict = dict(results[0])
            result_dict["full_name"] = decrypt_data(result_dict["full_name"])
            return [
                {
                    "full_name": result_dict["full_name"],
                    "total_transactions": result_dict["total_transactions"],
                    "total_credit": result_dict["total_credit"],
                    "total_debit": result_dict["total_debit"],
                    "average_transaction_value": result_dict[
                        "average_transaction_value"
                    ],
                }
            ]
        return []
