from enum import Enum as E
from pydantic import BaseModel, Field
from datetime import datetime

from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy import Column, String, Float, DateTime, Enum, TIMESTAMP
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class TransactionType(str, E):
    credit = "credit"
    debit = "debit"


class TransactionBase(BaseModel):
    user_id: str
    full_name: str
    transaction_date: datetime
    transaction_amount: float
    transaction_type: TransactionType


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(TransactionBase):
    pass


class Transaction(TransactionBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True


class TransactionTable(Base):
    __tablename__ = "transactions"

    id = Column(SQLAlchemyUUID, primary_key=True, default=uuid4)
    user_id = Column(
        String(255), nullable=False
    )  # User ID associated with the transaction
    full_name = Column(String(255), nullable=False)  # Full name of the user
    transaction_date = Column(
        DateTime, default=datetime.utcnow, nullable=False
    )  # Date and time of transaction
    transaction_amount = Column(
        Float, nullable=False
    )  # Amount involved in the transaction
    transaction_type = Column(
        Enum(TransactionType), nullable=False
    )  # Enum type (credit or debit)

    # New columns for statistics
    total_transactions = Column(
        Float, default=0, nullable=False
    )  # Running total of transactions
    total_credit = Column(
        Float, default=0, nullable=False
    )  # Running total for credit transactions
    total_debit = Column(
        Float, default=0, nullable=False
    )  # Running total for debit transactions
    average_transaction_value = Column(
        Float, default=0, nullable=False
    )  # Average transaction value

    created_at = Column(TIMESTAMP, default=datetime.utcnow)  # Created timestamp
    updated_at = Column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow
    )  # Updated timestamp

    def __repr__(self):
        return (
            f"<Transaction(id={self.id}, user_id={self.user_id}, full_name={self.full_name}, "
            f"transaction_date={self.transaction_date}, transaction_amount={self.transaction_amount}, "
            f"transaction_type={self.transaction_type}, total_transactions={self.total_transactions}, "
            f"total_credit={self.total_credit}, total_debit={self.total_debit}, "
            f"average_transaction_value={self.average_transaction_value})>"
        )


transactions_table = TransactionTable.__table__
