import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from app.schemas.activity_schemas import (
    ActivityLogCreate, 
    ActivityLogInDB, 
    ActivityLogResponse,
    ActivityLogListResponse,
    ActivityStatsResponse,
    ActivityTypeEnum
)

logger = logging.getLogger(__name__)

class ActivityService:
    """Service for managing activity logs."""
    
    def __init__(self):
        # In-memory storage for demo purposes
        # In production, this would be a database
        self._activities: List[ActivityLogInDB] = []
        self._next_id = 1
    
    def create_activity(self, activity_data: ActivityLogCreate, user_id: str) -> ActivityLogResponse:
        """Create a new activity log."""
        try:
            activity = ActivityLogInDB(
                id=self._next_id,
                user_id=user_id,
                activity_type=activity_data.activity_type,
                description=activity_data.description,
                details=activity_data.details,
                ip_address=activity_data.ip_address,
                user_agent=activity_data.user_agent,
                created_at=datetime.utcnow()
            )
            
            self._activities.append(activity)
            self._next_id += 1
            
            logger.info(f"Activity logged: {activity.activity_type} by user {user_id}")
            
            return ActivityLogResponse(
                id=activity.id,
                user_id=activity.user_id,
                activity_type=activity.activity_type,
                description=activity.description,
                details=activity.details,
                ip_address=activity.ip_address,
                user_agent=activity.user_agent,
                created_at=activity.created_at
            )
            
        except Exception as e:
            logger.error(f"Error creating activity log: {str(e)}")
            raise
    
    def get_user_activities(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 100,
        activity_type: Optional[ActivityTypeEnum] = None
    ) -> ActivityLogListResponse:
        """Get activities for a specific user."""
        try:
            # Filter activities by user
            user_activities = [
                activity for activity in self._activities 
                if activity.user_id == user_id
            ]
            
            # Filter by activity type if specified
            if activity_type:
                user_activities = [
                    activity for activity in user_activities 
                    if activity.activity_type == activity_type
                ]
            
            # Sort by created_at descending (most recent first)
            user_activities.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply pagination
            total = len(user_activities)
            paginated_activities = user_activities[skip:skip + limit]
            
            # Convert to response format
            activities = [
                ActivityLogResponse(
                    id=activity.id,
                    user_id=activity.user_id,
                    activity_type=activity.activity_type,
                    description=activity.description,
                    details=activity.details,
                    ip_address=activity.ip_address,
                    user_agent=activity.user_agent,
                    created_at=activity.created_at
                )
                for activity in paginated_activities
            ]
            
            return ActivityLogListResponse(
                activities=activities,
                total=total,
                page=skip // limit + 1 if limit > 0 else 1,
                size=limit,
                has_next=skip + limit < total
            )
            
        except Exception as e:
            logger.error(f"Error getting user activities: {str(e)}")
            raise
    
    def get_all_activities(
        self, 
        skip: int = 0, 
        limit: int = 100,
        activity_type: Optional[ActivityTypeEnum] = None
    ) -> ActivityLogListResponse:
        """Get all activities (admin only)."""
        try:
            # Filter by activity type if specified
            activities = self._activities.copy()
            if activity_type:
                activities = [
                    activity for activity in activities 
                    if activity.activity_type == activity_type
                ]
            
            # Sort by created_at descending (most recent first)
            activities.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply pagination
            total = len(activities)
            paginated_activities = activities[skip:skip + limit]
            
            # Convert to response format
            activity_responses = [
                ActivityLogResponse(
                    id=activity.id,
                    user_id=activity.user_id,
                    activity_type=activity.activity_type,
                    description=activity.description,
                    details=activity.details,
                    ip_address=activity.ip_address,
                    user_agent=activity.user_agent,
                    created_at=activity.created_at
                )
                for activity in paginated_activities
            ]
            
            return ActivityLogListResponse(
                activities=activity_responses,
                total=total,
                page=skip // limit + 1 if limit > 0 else 1,
                size=limit,
                has_next=skip + limit < total
            )
            
        except Exception as e:
            logger.error(f"Error getting all activities: {str(e)}")
            raise
    
    def get_activity_stats(self, user_id: Optional[str] = None) -> ActivityStatsResponse:
        """Get activity statistics."""
        try:
            # Filter activities by user if specified
            activities = self._activities.copy()
            if user_id:
                activities = [
                    activity for activity in activities 
                    if activity.user_id == user_id
                ]
            
            # Calculate statistics
            total_activities = len(activities)
            
            # Activities by type
            activities_by_type = defaultdict(int)
            for activity in activities:
                activities_by_type[activity.activity_type] += 1
            
            # Activities by day (last 7 days)
            activities_by_day = defaultdict(int)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            for activity in activities:
                if activity.created_at >= seven_days_ago:
                    day_key = activity.created_at.strftime("%Y-%m-%d")
                    activities_by_day[day_key] += 1
            
            # Most active user
            user_activity_counts = defaultdict(int)
            for activity in self._activities:
                user_activity_counts[activity.user_id] += 1
            
            most_active_user = max(user_activity_counts, key=user_activity_counts.get) if user_activity_counts else None
            
            # Recent activities (last 10)
            recent_activities = sorted(
                activities, 
                key=lambda x: x.created_at, 
                reverse=True
            )[:10]
            
            recent_activity_responses = [
                ActivityLogResponse(
                    id=activity.id,
                    user_id=activity.user_id,
                    activity_type=activity.activity_type,
                    description=activity.description,
                    details=activity.details,
                    ip_address=activity.ip_address,
                    user_agent=activity.user_agent,
                    created_at=activity.created_at
                )
                for activity in recent_activities
            ]
            
            return ActivityStatsResponse(
                total_activities=total_activities,
                activities_by_type=dict(activities_by_type),
                activities_by_day=dict(activities_by_day),
                most_active_user=most_active_user,
                recent_activities=recent_activity_responses
            )
            
        except Exception as e:
            logger.error(f"Error getting activity stats: {str(e)}")
            raise
    
    def log_user_activity(
        self,
        user_id: str,
        activity_type: ActivityTypeEnum,
        description: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ActivityLogResponse:
        """Convenience method to log user activity."""
        activity_data = ActivityLogCreate(
            activity_type=activity_type,
            description=description,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return self.create_activity(activity_data, user_id)

# Global activity service instance
activity_service = ActivityService()