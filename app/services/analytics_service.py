from app.models.transaction import TransactionType
from redis import Redis
import os
from app.schemas.transaction import AnalyticsData
import json
from typing import Optional
from app.models.user import User, users_table
from databases import Database
from fastapi import Request
from sqlalchemy import select
from fastapi import HTTPException
from datetime import datetime
from app.utils.encryption import decrypt_data
from app.models.transaction import (
    transactions_table,
)


redis = Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), db=0)


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

    @staticmethod
    async def analytics(
        db: Database, request: Request, transaction_date: Optional[str] = None
    ):
        try:
            user_id = str(request.state.user.id)

            # Base query
            query = select(transactions_table).where(
                transactions_table.c.user_id == user_id
            )

            # Add date filter if provided
            if transaction_date:
                try:
                    parsed_date = datetime.strptime(transaction_date, "%Y-%m-%d")
                    query = query.where(
                        transactions_table.c.transaction_date == parsed_date
                    )
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid date format. Please use YYYY-MM-DD",
                    )

            # Add ordering
            query = query.order_by(transactions_table.c.total_transactions.desc())

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
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
