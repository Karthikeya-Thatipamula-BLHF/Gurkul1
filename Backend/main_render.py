#!/usr/bin/env python3
"""
Gurukul Platform - Render.com Optimized Backend
Simplified backend for reliable Render deployment
"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Gurukul Learning Platform API",
    description="Unified backend API for the Gurukul Learning Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "https://gurukul-frontend.onrender.com").split(",")
if os.getenv("ENVIRONMENT") == "production":
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
else:
    allowed_origins = ["http://localhost:3000", "https://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Check environment variables
        required_vars = ["MONGODB_URI", "GROQ_API_KEY", "OPENAI_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "message": f"Missing environment variables: {', '.join(missing_vars)}",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        # Test database connection
        try:
            from pymongo import MongoClient
            client = MongoClient(os.getenv("MONGODB_URI"), serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            db_status = "connected"
            client.close()
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            db_status = "disconnected"
        
        return {
            "status": "healthy",
            "message": "Gurukul Learning Platform API",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "database": db_status,
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Gurukul Learning Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Basic chat endpoint
@app.post("/api/v1/chat")
async def chat_endpoint(message: dict):
    """Basic chat endpoint"""
    try:
        user_message = message.get("message", "")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Simple response for now
        response = {
            "response": f"Hello! You said: {user_message}. This is a basic response from Gurukul Platform.",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success"
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Basic memory endpoint
@app.post("/api/v1/memory")
async def memory_endpoint(data: dict):
    """Basic memory endpoint"""
    try:
        # Simple memory storage simulation
        return {
            "message": "Memory stored successfully",
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Memory endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Environment info endpoint (for debugging)
@app.get("/api/v1/env-info")
async def env_info():
    """Environment information (for debugging)"""
    if os.getenv("ENVIRONMENT") != "production":
        return {
            "python_version": sys.version,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "has_mongodb": bool(os.getenv("MONGODB_URI")),
            "has_groq_key": bool(os.getenv("GROQ_API_KEY")),
            "has_openai_key": bool(os.getenv("OPENAI_API_KEY")),
            "allowed_origins": allowed_origins
        }
    else:
        return {"message": "Environment info not available in production"}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested endpoint was not found",
            "path": str(request.url.path)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("🚀 Gurukul Platform API starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Python version: {sys.version}")
    logger.info("✅ Startup complete")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("🛑 Gurukul Platform API shutting down...")

# Main entry point
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main_render:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
