from app.services.analytics_service import AnalyticsService
from fastapi import APIRouter, Request, Depends
from databases import Database
from app.utils.database import get_database
from typing import Optional

router = APIRouter()


# @router.get("/", response_model=List[AnalyticsData], status_code=status.HTTP_200_OK)
# async def get_user_analytics(request: Request, db: Database = Depends(get_database)):
#     analytics_data = await AnalyticsService.analytics(db=db, request=request)
#     return analytics_data
#

# @router.get("/{transaction_date}")
# async def get_user_analytics_by_date(
#     transaction_date: str, request: Request, db: Database = Depends(get_database)
# ):
#     user_id = str(request.state.user.id)
#     return await AnalyticsService.get_user_analytics_by_date(
#         user_id=user_id, transaction_date=transaction_date, db=db
#     )


@router.get("/")
async def get_analytics(
    request: Request,
    transaction_date: Optional[str] = None,
    db: Database = Depends(get_database),
):
    return await AnalyticsService.analytics(
        db=db, request=request, transaction_date=transaction_date
    )
