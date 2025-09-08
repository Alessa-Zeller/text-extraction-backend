from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
import logging

from app.core.security import get_current_user
from app.services.activity_service import activity_service
from app.schemas.activity_schemas import (
    ActivityLogCreate,
    ActivityLogResponse,
    ActivityLogListResponse,
    ActivityStatsResponse,
    ActivityTypeEnum
)
from app.schemas.pdf_schemas import APIResponseSchema

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=APIResponseSchema)
async def get_user_activities(
    skip: int = Query(0, ge=0, description="Number of activities to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of activities to return"),
    activity_type: Optional[ActivityTypeEnum] = Query(None, description="Filter by activity type"),
    current_user: dict = Depends(get_current_user)
):
    """Get activity logs for the current user."""
    try:
        result = activity_service.get_user_activities(
            user_id=current_user["user_id"],
            skip=skip,
            limit=limit,
            activity_type=activity_type
        )
        
        return APIResponseSchema(
            success=True,
            message=f"Retrieved {len(result.activities)} activities",
            data=result.dict()
        )
        
    except Exception as e:
        logger.error(f"Error getting user activities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving activities: {str(e)}"
        )

