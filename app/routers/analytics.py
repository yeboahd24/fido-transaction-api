from app.services.analytics_service import AnalyticsService
from app.schemas.transaction import AnalyticsData
from fastapi import APIRouter, status, Request, Depends
from databases import Database
from app.utils.database import get_database
from typing import List

router = APIRouter()


@router.get("/", response_model=List[AnalyticsData], status_code=status.HTTP_200_OK)
async def get_user_analytics(request: Request, db: Database = Depends(get_database)):
    analytics_data = await AnalyticsService.analytics(db=db, request=request)
    return analytics_data
