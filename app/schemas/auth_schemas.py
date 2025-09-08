from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional

class UserLoginSchema(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="User password")

class UserRegistrationSchema(BaseModel):
    """Schema for user registration."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="User password")
    full_name: Optional[str] = Field(None, max_length=100, description="User full name")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class TokenSchema(BaseModel):
    """Schema for authentication token."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

class TokenRefreshSchema(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str = Field(..., description="Refresh token")

class UserProfileSchema(BaseModel):
    """Schema for user profile."""
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    full_name: Optional[str] = Field(None, description="User full name")
    is_admin: bool = Field(default=False, description="Whether user is admin")
    created_at: Optional[str] = Field(None, description="Account creation timestamp")
    last_login: Optional[str] = Field(None, description="Last login timestamp")
