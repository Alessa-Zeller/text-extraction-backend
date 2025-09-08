from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ActivityTypeEnum(str, Enum):
    """Enum for activity types."""
    LOGIN = "login"
    LOGOUT = "logout"
    PDF_UPLOAD = "pdf_upload"
    PDF_BATCH_UPLOAD = "pdf_batch_upload"
    ORDER_CREATE = "order_create"
    ORDER_UPDATE = "order_update"
    ORDER_DELETE = "order_delete"
    ORDER_VIEW = "order_view"
    PROFILE_UPDATE = "profile_update"
    SYSTEM_ACCESS = "system_access"

class ActivityLogBase(BaseModel):
    """Base schema for activity log."""
    activity_type: ActivityTypeEnum = Field(..., description="Type of activity")
    description: str = Field(..., min_length=1, max_length=500, description="Activity description")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional activity details")
    ip_address: Optional[str] = Field(None, description="IP address of the user")
    user_agent: Optional[str] = Field(None, description="User agent string")

class ActivityLogCreate(ActivityLogBase):
    """Schema for creating activity log."""
    pass

class ActivityLogInDB(ActivityLogBase):
    """Schema for activity log in database."""
    id: int = Field(..., description="Activity log ID")
    user_id: str = Field(..., description="User ID who performed the activity")
    created_at: datetime = Field(..., description="When the activity occurred")
    
    class Config:
        from_attributes = True

class ActivityLogResponse(ActivityLogInDB):
    """Schema for activity log response."""
    pass

class ActivityLogListResponse(BaseModel):
    """Schema for activity log list response."""
    activities: List[ActivityLogResponse] = Field(..., description="List of activity logs")
    total: int = Field(..., description="Total number of activity logs")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    has_next: bool = Field(..., description="Whether there are more pages")

class ActivityStatsResponse(BaseModel):
    """Schema for activity statistics response."""
    total_activities: int = Field(..., description="Total number of activities")
    activities_by_type: Dict[str, int] = Field(..., description="Activities grouped by type")
    activities_by_day: Dict[str, int] = Field(..., description="Activities grouped by day")
    most_active_user: Optional[str] = Field(None, description="Most active user ID")
    recent_activities: List[ActivityLogResponse] = Field(..., description="Recent activities")