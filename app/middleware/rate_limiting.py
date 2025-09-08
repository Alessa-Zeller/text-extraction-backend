from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from collections import defaultdict, deque
from typing import Dict, Deque
import asyncio

from app.core.config import settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm."""
    
    def __init__(self, app, calls: int = None, period: int = None):
        super().__init__(app)
        self.calls = calls or settings.RATE_LIMIT_REQUESTS
        self.period = period or settings.RATE_LIMIT_WINDOW
        self.clients: Dict[str, Deque[float]] = defaultdict(deque)
        
    def get_client_id(self, request: Request) -> str:
        """Get client identifier (IP address)."""
        # In production, consider using X-Forwarded-For header if behind proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        
        # Skip rate limiting for certain endpoints
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        client_id = self.get_client_id(request)
        now = time.time()
        
        # Clean old requests outside the time window
        client_requests = self.clients[client_id]
        while client_requests and client_requests[0] <= now - self.period:
            client_requests.popleft()
        
        # Check if rate limit is exceeded
        if len(client_requests) >= self.calls:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate Limit Exceeded",
                    "message": f"Too many requests. Limit: {self.calls} requests per {self.period} seconds",
                    "retry_after": int(self.period - (now - client_requests[0])) + 1,
                    "type": "rate_limit_error"
                },
                headers={
                    "X-RateLimit-Limit": str(self.calls),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(client_requests[0] + self.period)),
                    "Retry-After": str(int(self.period - (now - client_requests[0])) + 1)
                }
            )
        
        # Add current request timestamp
        client_requests.append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        remaining = max(0, self.calls - len(client_requests))
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        if client_requests:
            response.headers["X-RateLimit-Reset"] = str(int(client_requests[0] + self.period))
        
        return response

# Cleanup task to prevent memory leaks
class RateLimitCleanup:
    """Background task to clean up old rate limit data."""
    
    def __init__(self, middleware: RateLimitMiddleware):
        self.middleware = middleware
        self.cleanup_interval = 300  # 5 minutes
        
    async def cleanup_loop(self):
        """Periodically clean up old client data."""
        while True:
            await asyncio.sleep(self.cleanup_interval)
            now = time.time()
            
            # Remove clients with no recent requests
            clients_to_remove = []
            for client_id, requests in self.middleware.clients.items():
                # Remove old requests
                while requests and requests[0] <= now - self.middleware.period:
                    requests.popleft()
                
                # If no recent requests, mark for removal
                if not requests:
                    clients_to_remove.append(client_id)
            
            # Remove inactive clients
            for client_id in clients_to_remove:
                del self.middleware.clients[client_id]
