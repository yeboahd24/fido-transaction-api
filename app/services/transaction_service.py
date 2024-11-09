from app.models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionTable,
    TransactionType,
    transactions_table,
)
from fastapi import HTTPException

from app.utils.encryption import encrypt_data, decrypt_data
from databases import Database
from fastapi import Request

from sqlalchemy import update, select
from uuid import uuid4
from datetime import datetime
import os


database = Database(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)


class TransactionService:
    @staticmethod
    async def create_transaction(
        db: Database, request: Request, transaction: TransactionCreate
    ):
        user = request.state.user
        transaction_data = transaction.dict()
        transaction_data.update(
            {
                "user_id": str(user.id),
                "id": str(uuid4()),
                "full_name": encrypt_data(transaction_data["full_name"]),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "total_transactions": 0,
                "total_credit": 0.0,
                "total_debit": 0.0,
                "average_transaction_value": 0.0,
            }
        )

        query = TransactionTable.__table__.insert().values(**transaction_data)
        await db.execute(query)

        # Update aggregated fields based on the new transaction
        await TransactionService.update_aggregated_fields(db, user.id, transaction_data)

        result = Transaction(**transaction_data)
        if result:
            result_dict = dict(result)
            result_dict["full_name"] = decrypt_data(result_dict["full_name"])
            return {
                "id": result_dict["id"],
                "full_name": result_dict["full_name"],
                "transaction_date": result_dict["transaction_date"],
                "transaction_amount": result_dict["transaction_amount"],
                "transaction_type": result_dict["transaction_type"],
                "created_at": result_dict["created_at"],
                "updated_at": result_dict["updated_at"],
            }

    @staticmethod
    async def update_aggregated_fields(
        db: Database, user_id: str, transaction: Transaction
    ):
        # Fetch all transactions for the user
        transactions = await db.fetch_all(
            TransactionTable.__table__.select().where(
                TransactionTable.user_id == str(user_id)
            )
        )

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
        total_transactions = len(transactions)
        average_transaction_value = (total_debit + total_credit) / total_transactions

        # Update transaction data
        query = (
            update(transactions_table)
            .where(transactions_table.c.id == transaction["id"])
            .values(
                total_transactions=total_transactions,
                total_credit=total_credit,
                total_debit=total_debit,
                average_transaction_value=average_transaction_value,
            )
        )
        await db.execute(query)

    @staticmethod
    async def update_transaction(
        db: Database, transaction_id: str, request: Request, update_data: dict
    ):
        try:
            user_id = str(request.state.user.id)

            query = select(transactions_table).where(
                (transactions_table.c.id == transaction_id)
                & (transactions_table.c.user_id == user_id)
            )
            existing_transaction = await db.fetch_one(query)

            if not existing_transaction:
                raise HTTPException(
                    status_code=404,
                    detail="Transaction not found or you don't have permission",
                )

            if "full_name" in update_data:
                update_data["full_name"] = encrypt_data(update_data["full_name"])

            update_data["updated_at"] = datetime.utcnow()

            query = (
                transactions_table.update()
                .where(
                    (transactions_table.c.id == transaction_id)
                    & (transactions_table.c.user_id == user_id)
                )
                .values(**update_data)
            )
            await db.execute(query)

            # Fetch updated transaction
            query = select(transactions_table).where(
                transactions_table.c.id == transaction_id
            )
            result = await db.fetch_one(query)
            if result:
                result_dict = dict(result)
                result_dict["full_name"] = decrypt_data(result_dict["full_name"])
                return {
                    "id": result_dict["id"],
                    "full_name": result_dict["full_name"],
                    "transaction_date": result_dict["transaction_date"],
                    "transaction_amount": result_dict["transaction_amount"],
                    "transaction_type": result_dict["transaction_type"],
                    "created_at": result_dict["created_at"],
                    "updated_at": result_dict["updated_at"],
                }

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def delete_transaction(db: Database, transaction_id: str, request: Request):
        user_id = str(request.state.user.id)

        query = select(transactions_table).where(
            (transactions_table.c.id == transaction_id)
            & (transactions_table.c.user_id == user_id)
        )
        existing_transaction = await db.fetch_one(query)

        if not existing_transaction:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found or you don't have permission",
            )

        # Delete the transaction
        query = transactions_table.delete().where(
            (transactions_table.c.id == transaction_id)
            & (transactions_table.c.user_id == user_id)
        )
        await db.execute(query)
        return {"message": "Transaction deleted successfully"}

    @staticmethod
    async def get_user_transactions(
        db: Database, request: Request, transaction_date: str
    ):
        try:
            parsed_date = datetime.strptime(transaction_date, "%Y-%m-%d")
            user_id = str(request.state.user.id)

            query = select(transactions_table).where(
                (transactions_table.c.user_id == user_id)
                & (transactions_table.c.transaction_date == parsed_date)
            )

            results = await db.fetch_all(query)  # Changed to fetch_all
            if results:
                transactions = []
                for result in results:
                    result_dict = dict(result)
                    result_dict["full_name"] = decrypt_data(result_dict["full_name"])

                    formatted_transaction = {
                        "id": result_dict["id"],
                        "full_name": result_dict["full_name"],
                        "transaction_date": result_dict["transaction_date"],
                        "transaction_amount": result_dict["transaction_amount"],
                        "transaction_type": result_dict["transaction_type"],
                        "created_at": result_dict["created_at"],
                        "updated_at": result_dict["updated_at"],
                    }
                    transactions.append(formatted_transaction)
                return transactions
            return []

        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Please use YYYY-MM-DD"
            )
