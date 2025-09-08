from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class OrderBase(BaseModel):
    patient_first_name: str = Field(..., min_length=1, max_length=100, description="Patient's first name")
    patient_last_name: str = Field(..., min_length=1, max_length=100, description="Patient's last name")
    patient_date_of_birth: str = Field(..., description="Patient's date of birth")
    order_status: str = Field(default="pending", description="Order status")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    patient_first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    patient_last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    patient_date_of_birth: Optional[str] = None
    order_status: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)

class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None

    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    page: int
    size: int
    pages: int

class OrderStatsResponse(BaseModel):
    total_orders: int
    orders_by_status: dict
    recent_orders: List[OrderResponse]
    orders_today: int
