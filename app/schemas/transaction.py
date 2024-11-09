from pydantic import BaseModel
from datetime import datetime
from app.models.transaction import TransactionType
from typing import Optional


class TransactionCreate(BaseModel):
    full_name: str
    transaction_date: datetime
    transaction_amount: float
    transaction_type: TransactionType


#
# class AnalyticsData(BaseModel):
#     average_transaction_value: float
#     busiest_day: datetime
#


class TransactionUpdate(BaseModel):
    full_name: Optional[str] = None
    transaction_date: Optional[datetime] = None
    transaction_amount: Optional[float] = None
    transaction_type: Optional[str] = None


class AnalyticsData(BaseModel):
    full_name: str
    total_transactions: float
    total_credit: float
    total_debit: float
    average_transaction_value: float
