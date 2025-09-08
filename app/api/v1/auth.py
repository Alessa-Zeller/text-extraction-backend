from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from datetime import timedelta
import hashlib
from typing import Dict

from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    get_current_user,
    security
)
from app.core.config import settings
from app.schemas.auth_schemas import (
    UserLoginSchema, 
    UserRegistrationSchema, 
    TokenSchema, 
    TokenRefreshSchema,
    UserProfileSchema
)
from app.schemas.pdf_schemas import APIResponseSchema

router = APIRouter()

# Mock user database (in production, use a real database)
MOCK_USERS = {
    "admin@example.com": {
        "user_id": "admin_123",
        "email": "admin@example.com",
        "hashed_password": get_password_hash("admin123"),
        "full_name": "Admin User",
        "is_admin": True,
        "created_at": "2024-01-01T00:00:00Z"
    },
    "user@example.com": {
        "user_id": "user_456",
        "email": "user@example.com",
        "hashed_password": get_password_hash("user123"),
        "full_name": "Regular User",
        "is_admin": False,
        "created_at": "2024-01-01T00:00:00Z"
    }
}

def get_user_by_email(email: str) -> Dict:
    """Get user by email from mock database."""
    return MOCK_USERS.get(email)

def create_user(user_data: UserRegistrationSchema) -> Dict:
    """Create a new user (mock implementation)."""
    if user_data.email in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_id = f"user_{hashlib.md5(user_data.email.encode()).hexdigest()[:8]}"
    
    new_user = {
        "user_id": user_id,
        "email": user_data.email,
        "hashed_password": get_password_hash(user_data.password),
        "full_name": user_data.full_name,
        "is_admin": False,
        "created_at": "2024-01-01T00:00:00Z"
    }
    
    MOCK_USERS[user_data.email] = new_user
    return new_user

@router.post("/register", response_model=APIResponseSchema, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegistrationSchema):
    """Register a new user."""
    try:
        user = create_user(user_data)
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["user_id"], "email": user["email"], "is_admin": user["is_admin"]},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user["user_id"], "email": user["email"]}
        )
        
        token_data = TokenSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return APIResponseSchema(
            success=True,
            message="User registered successfully",
            data=token_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=APIResponseSchema)
async def login_user(user_credentials: UserLoginSchema):
    """Authenticate user and return JWT tokens."""
    user = get_user_by_email(user_credentials.email)
    
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["user_id"], "email": user["email"], "is_admin": user["is_admin"]},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user["user_id"], "email": user["email"]}
    )
    
    token_data = TokenSchema(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return APIResponseSchema(
        success=True,
        message="Login successful",
        data=token_data
    )

@router.post("/refresh", response_model=APIResponseSchema)
async def refresh_token(token_data: TokenRefreshSchema):
    """Refresh access token using refresh token."""
    payload = verify_token(token_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    email = payload.get("email")
    
    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user to check if still exists and get current admin status
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id, "email": email, "is_admin": user["is_admin"]},
        expires_delta=access_token_expires
    )
    
    new_token_data = TokenSchema(
        access_token=access_token,
        refresh_token=token_data.refresh_token,  # Keep the same refresh token
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return APIResponseSchema(
        success=True,
        message="Token refreshed successfully",
        data=new_token_data
    )

@router.get("/profile", response_model=APIResponseSchema)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile."""
    user = get_user_by_email(current_user["email"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    profile_data = UserProfileSchema(
        user_id=user["user_id"],
        email=user["email"],
        full_name=user.get("full_name"),
        is_admin=user.get("is_admin", False),
        created_at=user.get("created_at")
    )
    
    return APIResponseSchema(
        success=True,
        message="Profile retrieved successfully",
        data=profile_data
    )

@router.post("/logout", response_model=APIResponseSchema)
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Logout user (in a real app, you'd invalidate the token)."""
    # In a production app, you would:
    # 1. Add the token to a blacklist
    # 2. Store blacklisted tokens in Redis with expiration
    # 3. Check blacklist in get_current_user function
    
    return APIResponseSchema(
        success=True,
        message="Logged out successfully",
        data={"user_id": current_user["user_id"]}
    )
