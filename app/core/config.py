from pydantic import BaseSettings
from typing import List, Optional
import secrets

class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "PDF Processing API"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "2eaKXj8k8XrkKCkNeJundkb5h2ZjVcaOmVER5wWxAoc"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:3001",
        "https://text-extraction-frontend.vercel.app",
        "https://text-extraction-backend-production.up.railway.app"
    ]
    ALLOWED_HOSTS: List[str] = [
        "localhost", 
        "127.0.0.1",
        "text-extraction-backend-production.up.railway.app",
        "*.railway.app"
    ]
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:ZcTFzqMwcuuGpPITtIMZXPqDCjLAjLts@crossover.proxy.rlwy.net:53116/railway"
    
    # Redis (for caching and task queue)
    REDIS_URL: str = "redis://localhost:6379"
    
    # File storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf"]
    
    # Batch processing
    BATCH_SIZE: int = 10
    MAX_CONCURRENT_TASKS: int = 5
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Environment
    ENVIRONMENT: str = "development"

    # LlamaParse configuration
    LLAMAPARSE_API_KEY: Optional[str] = "llx-0B6C8wzvjvXj0CzYFYObg36zwx9cGTCps1VdBOgDkNzMORfy"
    LLAMAPARSE_RESULT_TYPE: str = "text"  # text | markdown | json
    USE_LLAMAPARSE: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
