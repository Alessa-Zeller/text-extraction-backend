from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.schemas.order_schemas import OrderCreate, OrderUpdate, OrderResponse

class OrderService:
    def __init__(self):
        # In-memory storage for orders (in production, use a real database)
        self._orders: Dict[int, Dict[str, Any]] = {}
        self._next_id = 1
        
        # Initialize with some sample orders
        self._initialize_sample_orders()
    
    def _initialize_sample_orders(self):
        """Initialize with some sample orders for testing"""
        sample_orders = [
            {
                "patient_first_name": "John",
                "patient_last_name": "Doe",
                "patient_date_of_birth": "1990-01-15",
                "order_status": "pending",
                "notes": "Initial consultation",
                "created_by": "admin_123"
            },
            {
                "patient_first_name": "Jane",
                "patient_last_name": "Smith",
                "patient_date_of_birth": "1985-05-20",
                "order_status": "processing",
                "notes": "Follow-up appointment",
                "created_by": "user_456"
            },
            {
                "patient_first_name": "Bob",
                "patient_last_name": "Johnson",
                "patient_date_of_birth": "1992-12-03",
                "order_status": "completed",
                "notes": "Annual checkup completed",
                "created_by": "admin_123"
            }
        ]
        
        for order_data in sample_orders:
            self.create_order(OrderCreate(**order_data), order_data["created_by"])
    
    def create_order(self, order_data: OrderCreate, created_by: str) -> OrderResponse:
        """Create a new order"""
        order_id = self._next_id
        self._next_id += 1
        
        now = datetime.utcnow()
        order_dict = {
            "id": order_id,
            "patient_first_name": order_data.patient_first_name,
            "patient_last_name": order_data.patient_last_name,
            "patient_date_of_birth": order_data.patient_date_of_birth,
            "order_status": order_data.order_status,
            "notes": order_data.notes,
            "created_at": now,
            "updated_at": now,
            "created_by": created_by
        }
        
        self._orders[order_id] = order_dict
        return OrderResponse(**order_dict)
    
    def get_order(self, order_id: int) -> Optional[OrderResponse]:
        """Get a single order by ID"""
        order_dict = self._orders.get(order_id)
        if order_dict:
            return OrderResponse(**order_dict)
        return None
    
    def get_orders(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        status: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> List[OrderResponse]:
        """Get orders with pagination and filtering"""
        orders = list(self._orders.values())
        
        # Apply filters
        if status:
            orders = [o for o in orders if o["order_status"] == status]
        
        if created_by:
            orders = [o for o in orders if o["created_by"] == created_by]
        
        # Sort by created_at descending (newest first)
        orders.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        paginated_orders = orders[skip:skip + limit]
        
        return [OrderResponse(**order) for order in paginated_orders]
    
    def update_order(self, order_id: int, order_data: OrderUpdate, updated_by: str) -> Optional[OrderResponse]:
        """Update an existing order"""
        if order_id not in self._orders:
            return None
        
        order_dict = self._orders[order_id]
        
        # Update only provided fields
        update_data = order_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            order_dict[field] = value
        
        order_dict["updated_at"] = datetime.utcnow()
        
        return OrderResponse(**order_dict)
    
    def delete_order(self, order_id: int) -> bool:
        """Delete an order"""
        if order_id in self._orders:
            del self._orders[order_id]
            return True
        return False
    
    def get_order_stats(self) -> Dict[str, Any]:
        """Get order statistics"""
        orders = list(self._orders.values())
        
        # Count by status
        status_counts = {}
        for order in orders:
            status = order["order_status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Get recent orders (last 5)
        recent_orders = sorted(orders, key=lambda x: x["created_at"], reverse=True)[:5]
        
        # Count orders created today
        today = datetime.utcnow().date()
        orders_today = sum(1 for order in orders if order["created_at"].date() == today)
        
        return {
            "total_orders": len(orders),
            "orders_by_status": status_counts,
            "recent_orders": [OrderResponse(**order) for order in recent_orders],
            "orders_today": orders_today
        }
    
    def get_orders_count(self) -> int:
        """Get total number of orders"""
        return len(self._orders)

# Global instance
order_service = OrderService()
