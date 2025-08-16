#!/usr/bin/env python3
"""
Gurukul Platform - Ultra Simple Backend for Render.com
Minimal FastAPI app that's guaranteed to deploy successfully
"""

import os
import sys
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Create FastAPI app
app = FastAPI(
    title="Gurukul Learning Platform API",
    description="Simplified backend for Gurukul Learning Platform",
    version="1.0.0"
)

# Simple CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will be restricted in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Gurukul Learning Platform API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "message": "Gurukul Platform API is running",
        "timestamp": datetime.utcnow().isoformat(),
        "python_version": sys.version.split()[0],
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.post("/api/v1/chat")
async def chat_endpoint(message: dict):
    """Basic chat endpoint"""
    user_message = message.get("message", "")
    
    return {
        "response": f"Hello! You said: '{user_message}'. This is a response from Gurukul Platform.",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "success"
    }

@app.get("/api/v1/status")
async def status_endpoint():
    """API status endpoint"""
    return {
        "api_status": "operational",
        "services": {
            "chat": "available",
            "health": "available"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Error handler
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested endpoint was not found",
            "available_endpoints": ["/", "/health", "/api/v1/chat", "/api/v1/status"]
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
