from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional

from app.core.security import get_current_user
from app.schemas.order_schemas import (
    OrderCreate, 
    OrderUpdate, 
    OrderResponse, 
    OrderListResponse,
    OrderStatsResponse
)
from app.schemas.pdf_schemas import APIResponseSchema
from app.services.order_service import order_service
from app.services.activity_service import activity_service
from app.schemas.activity_schemas import ActivityTypeEnum

router = APIRouter()

@router.post("", response_model=APIResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new order."""
    try:
        order = order_service.create_order(order_data, current_user["user_id"])
        
        # Log order creation activity
        try:
            activity_service.log_user_activity(
                user_id=current_user["user_id"],
                activity_type=ActivityTypeEnum.ORDER_CREATE,
                description=f"Created order for patient: {order_data.patient_first_name} {order_data.patient_last_name}",
                details={
                    "order_id": order.id,
                    "patient_name": f"{order_data.patient_first_name} {order_data.patient_last_name}",
                    "patient_dob": order_data.patient_date_of_birth,
                    "order_status": order_data.order_status,
                    "notes": order_data.notes
                }
            )
        except Exception as e:
            # Don't fail order creation if activity logging fails
            pass
        
        return APIResponseSchema(
            success=True,
            message="Order created successfully",
            data=order
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )

@router.get("", response_model=APIResponseSchema)
async def get_orders(
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of orders to return"),
    status: Optional[str] = Query(None, description="Filter by order status"),
    current_user: dict = Depends(get_current_user)
):
    """Get orders with pagination and filtering."""
    try:
        orders = order_service.get_orders(skip=skip, limit=limit, status=status)
        total_count = order_service.get_orders_count()
        
        # Calculate pagination info
        pages = (total_count + limit - 1) // limit
        current_page = (skip // limit) + 1
        
        response_data = OrderListResponse(
            orders=orders,
            total=total_count,
            page=current_page,
            size=limit,
            pages=pages
        )
        
        return APIResponseSchema(
            success=True,
            message=f"Retrieved {len(orders)} orders",
            data=response_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve orders: {str(e)}"
        )

@router.get("/{order_id}", response_model=APIResponseSchema)
async def get_order(
    order_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get a single order by ID."""
    try:
        order = order_service.get_order(order_id)
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        return APIResponseSchema(
            success=True,
            message="Order retrieved successfully",
            data=order
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve order: {str(e)}"
        )

@router.put("/{order_id}", response_model=APIResponseSchema)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing order."""
    try:
        # Get the original order for comparison
        original_order = order_service.get_order(order_id)
        if not original_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order = order_service.update_order(order_id, order_data, current_user["user_id"])
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Log order update activity
        try:
            # Determine what fields were changed
            changes = {}
            update_data = order_data.dict(exclude_unset=True)
            for field, new_value in update_data.items():
                original_value = getattr(original_order, field, None)
                if original_value != new_value:
                    changes[field] = {
                        "old_value": original_value,
                        "new_value": new_value
                    }
            
            activity_service.log_user_activity(
                user_id=current_user["user_id"],
                activity_type=ActivityTypeEnum.ORDER_UPDATE,
                description=f"Updated order #{order_id} for patient: {order.patient_first_name} {order.patient_last_name}",
                details={
                    "order_id": order_id,
                    "patient_name": f"{order.patient_first_name} {order.patient_last_name}",
                    "changes": changes,
                    "updated_fields": list(update_data.keys())
                }
            )
        except Exception as e:
            # Don't fail order update if activity logging fails
            pass
        
        return APIResponseSchema(
            success=True,
            message="Order updated successfully",
            data=order
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update order: {str(e)}"
        )

@router.delete("/{order_id}", response_model=APIResponseSchema)
async def delete_order(
    order_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete an order."""
    try:
        # Get the order details before deletion for logging
        order_to_delete = order_service.get_order(order_id)
        if not order_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        success = order_service.delete_order(order_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Log order deletion activity
        try:
            activity_service.log_user_activity(
                user_id=current_user["user_id"],
                activity_type=ActivityTypeEnum.ORDER_DELETE,
                description=f"Deleted order #{order_id} for patient: {order_to_delete.patient_first_name} {order_to_delete.patient_last_name}",
                details={
                    "order_id": order_id,
                    "patient_name": f"{order_to_delete.patient_first_name} {order_to_delete.patient_last_name}",
                    "patient_dob": order_to_delete.patient_date_of_birth,
                    "order_status": order_to_delete.order_status,
                    "notes": order_to_delete.notes,
                    "created_at": order_to_delete.created_at.isoformat(),
                    "updated_at": order_to_delete.updated_at.isoformat()
                }
            )
        except Exception as e:
            # Don't fail order deletion if activity logging fails
            pass
        
        return APIResponseSchema(
            success=True,
            message="Order deleted successfully",
            data={"order_id": order_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete order: {str(e)}"
        )



