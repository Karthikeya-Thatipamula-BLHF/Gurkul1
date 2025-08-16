"""
Security middleware for Gurukul Platform
Comprehensive security enhancements for production deployment
"""

import os
import time
import hashlib
import logging
from typing import Dict, List, Optional, Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import redis
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware"""
    
    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client
        self.rate_limits = {
            "default": {"requests": 100, "window": 60},  # 100 requests per minute
            "auth": {"requests": 5, "window": 60},       # 5 auth attempts per minute
            "api": {"requests": 1000, "window": 3600},   # 1000 API calls per hour
        }
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main security middleware dispatcher"""
        
        # Security headers
        start_time = time.time()
        
        try:
            # Rate limiting
            if not await self._check_rate_limit(request):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"error": "Rate limit exceeded", "retry_after": 60}
                )
            
            # Input validation
            if not await self._validate_request(request):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": "Invalid request format"}
                )
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            response = self._add_security_headers(response)
            
            # Log request
            await self._log_request(request, response, time.time() - start_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal server error"}
            )
    
    async def _check_rate_limit(self, request: Request) -> bool:
        """Check rate limiting"""
        if not self.redis_client:
            return True  # Skip if Redis not available
        
        try:
            client_ip = self._get_client_ip(request)
            endpoint = request.url.path
            
            # Determine rate limit type
            limit_type = "default"
            if "/auth" in endpoint:
                limit_type = "auth"
            elif "/api" in endpoint:
                limit_type = "api"
            
            limits = self.rate_limits[limit_type]
            key = f"rate_limit:{client_ip}:{limit_type}"
            
            # Check current count
            current = self.redis_client.get(key)
            if current is None:
                # First request
                self.redis_client.setex(key, limits["window"], 1)
                return True
            
            current_count = int(current)
            if current_count >= limits["requests"]:
                return False
            
            # Increment counter
            self.redis_client.incr(key)
            return True
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True  # Allow request if rate limiting fails
    
    async def _validate_request(self, request: Request) -> bool:
        """Validate request format and content"""
        try:
            # Check content length
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
                return False
            
            # Check for suspicious patterns
            suspicious_patterns = [
                "<script", "javascript:", "data:text/html",
                "eval(", "document.cookie", "window.location"
            ]
            
            # Check URL for suspicious content
            url_str = str(request.url).lower()
            for pattern in suspicious_patterns:
                if pattern in url_str:
                    logger.warning(f"Suspicious pattern detected in URL: {pattern}")
                    return False
            
            # Check headers for suspicious content
            for header_name, header_value in request.headers.items():
                header_str = f"{header_name}:{header_value}".lower()
                for pattern in suspicious_patterns:
                    if pattern in header_str:
                        logger.warning(f"Suspicious pattern detected in header: {pattern}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Request validation error: {e}")
            return True  # Allow request if validation fails
    
    def _add_security_headers(self, response: Response) -> Response:
        """Add comprehensive security headers"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self' https://*.supabase.co wss://*.supabase.co"
            ),
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            ),
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers (for reverse proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def _log_request(self, request: Request, response: Response, duration: float):
        """Log request for security monitoring"""
        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "method": request.method,
                "path": request.url.path,
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("User-Agent", ""),
                "status_code": response.status_code,
                "duration": round(duration, 3),
                "content_length": response.headers.get("content-length", "0")
            }
            
            # Log to structured logger
            logger.info("Request processed", extra=log_data)
            
            # Store in Redis for monitoring (if available)
            if self.redis_client:
                key = f"request_log:{int(time.time())}"
                self.redis_client.setex(key, 3600, str(log_data))  # Keep for 1 hour
                
        except Exception as e:
            logger.error(f"Request logging error: {e}")


class InputSanitizer:
    """Input sanitization utilities"""
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(input_str, str):
            return ""
        
        # Truncate if too long
        if len(input_str) > max_length:
            input_str = input_str[:max_length]
        
        # Remove dangerous characters
        dangerous_chars = ["<", ">", "\"", "'", "&", "script", "javascript"]
        for char in dangerous_chars:
            input_str = input_str.replace(char, "")
        
        return input_str.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format"""
        if not api_key or len(api_key) < 10:
            return False
        
        # Check for suspicious patterns
        suspicious = ["test", "demo", "example", "placeholder"]
        return not any(pattern in api_key.lower() for pattern in suspicious)


def setup_security_middleware(app, redis_url: Optional[str] = None):
    """Setup security middleware for FastAPI app"""
    redis_client = None
    
    if redis_url:
        try:
            import redis
            redis_client = redis.from_url(redis_url)
            redis_client.ping()  # Test connection
            logger.info("✅ Redis connected for security middleware")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            redis_client = None
    
    # Add security middleware
    app.add_middleware(SecurityMiddleware, redis_client=redis_client)
    logger.info("✅ Security middleware configured")
    
    return app
