from fastapi import APIRouter, status, Request, Depends
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.services.transaction_service import TransactionService
from databases import Database
from app.utils.database import get_database
from fastapi import HTTPException

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    request: Request,
    db: Database = Depends(get_database),
):
    return await TransactionService.create_transaction(
        request=request, transaction=transaction, db=db
    )


@router.get("/{transaction_date}")
async def get_transactions(
    request: Request,
    transaction_date: str,  # Format: YYYY-MM-DD
    db: Database = Depends(get_database),
):
    transaction = await TransactionService.get_user_transactions(
        db, request=request, transaction_date=transaction_date
    )
    if transaction:
        return transaction
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")


@router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: str,
    update_data: TransactionUpdate,
    request: Request,
    db: Database = Depends(get_database),
):
    update_dict = update_data.dict(exclude_unset=True)
    updated_transaction = await TransactionService.update_transaction(
        db, transaction_id=transaction_id, request=request, update_data=update_dict
    )
    return updated_transaction


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: str, request: Request, db: Database = Depends(get_database)
):
    return await TransactionService.delete_transaction(
        db, transaction_id=transaction_id, request=request
    )
