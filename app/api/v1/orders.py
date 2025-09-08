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

router = APIRouter()

@router.post("", response_model=APIResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new order."""
    try:
        order = order_service.create_order(order_data, current_user["user_id"])
        
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
        order = order_service.update_order(order_id, order_data, current_user["user_id"])
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
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
        success = order_service.delete_order(order_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
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



