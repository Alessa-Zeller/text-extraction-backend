from fastapi import APIRouter

from app.api.v1 import auth, pdf, orders

api_router = APIRouter()

# Include authentication routes
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Include PDF processing routes
api_router.include_router(
    pdf.router,
    prefix="/pdf",
    tags=["PDF Processing"]
)

# Include order management routes
api_router.include_router(
    orders.router,
    prefix="/orders",
    tags=["Order Management"]
)
