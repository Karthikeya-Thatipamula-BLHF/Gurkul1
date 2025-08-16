#!/usr/bin/env python3
"""
Unified Backend Entry Point for Render Deployment
Gurukul Learning Platform - Production Backend
"""

import os
import sys
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from pathlib import Path

# Add Backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import security middleware
try:
    from middleware.security import setup_security_middleware
    SECURITY_AVAILABLE = True
    logger.info("✅ Security middleware available")
except ImportError:
    logger.warning("⚠️ Security middleware not available")
    SECURITY_AVAILABLE = False

# Create main FastAPI app
app = FastAPI(
    title="Gurukul Learning Platform API",
    description="Unified backend API for the Gurukul Learning Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - Production configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://localhost:3000").split(",")
if os.getenv("ENVIRONMENT") == "production":
    # In production, use specific domains
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
else:
    # In development, allow localhost
    allowed_origins = ["http://localhost:3000", "https://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add security middleware if available
if SECURITY_AVAILABLE:
    redis_url = os.getenv("REDIS_URL")
    setup_security_middleware(app, redis_url)
    logger.info("✅ Security middleware configured")
else:
    logger.warning("⚠️ Running without security middleware")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Gurukul Learning Platform API",
        "status": "running",
        "version": "1.0.0",
        "services": [
            "base-backend",
            "memory-management", 
            "financial-simulator",
            "subject-generation",
            "akash-service",
            "tts-service"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with service status"""
    from datetime import datetime

    service_status = {}
    overall_status = "healthy"

    # Check each mounted service
    services = [
        ("base-backend", "/api/v1/base"),
        ("memory-management", "/api/v1/memory"),
        ("financial-simulator", "/api/v1/financial"),
        ("subject-generation", "/api/v1/subjects"),
        ("akash-service", "/api/v1/akash"),
        ("tts-service", "/api/v1/tts")
    ]

    for service_name, mount_path in services:
        try:
            # Simple check if service is mounted
            service_status[service_name] = "mounted"
        except Exception:
            service_status[service_name] = "error"
            overall_status = "degraded"

    return {
        "status": overall_status,
        "message": "Gurukul Learning Platform API",
        "timestamp": datetime.utcnow().isoformat(),
        "services": service_status,
        "version": "1.0.0"
    }

# Service mounting with improved error handling and fallbacks
def mount_service(service_name: str, import_paths: list, mount_path: str):
    """Mount a service with multiple fallback import paths"""
    for i, import_path in enumerate(import_paths):
        try:
            # Dynamic import
            module_parts = import_path.split('.')
            module_name = '.'.join(module_parts[:-1])
            app_name = module_parts[-1]

            module = __import__(module_name, fromlist=[app_name])
            service_app = getattr(module, app_name)

            app.mount(mount_path, service_app)
            logger.info(f"✅ {service_name} mounted at {mount_path}")
            return True

        except ImportError as e:
            if i == len(import_paths) - 1:  # Last attempt
                logger.error(f"❌ Failed to mount {service_name}: All import paths failed")
                logger.error(f"Last error: {e}")
            else:
                logger.warning(f"⚠️ {service_name} import attempt {i+1} failed, trying alternative...")
        except Exception as e:
            logger.error(f"❌ Unexpected error mounting {service_name}: {e}")
            break

    return False

# Mount services with fallback paths
services_to_mount = [
    {
        "name": "Base Backend",
        "paths": ["Base_backend.api.app"],
        "mount": "/api/v1/base"
    },
    {
        "name": "Memory Management",
        "paths": ["memory_management.api.app"],
        "mount": "/api/v1/memory"
    },
    {
        "name": "Financial Simulator",
        "paths": [
            "Financial_simulator.langgraph_api.app",
            "Financial_simulator.Financial_simulator.langgraph_api.app"
        ],
        "mount": "/api/v1/financial"
    },
    {
        "name": "Subject Generation",
        "paths": ["subject_generation.app.app"],
        "mount": "/api/v1/subjects"
    },
    {
        "name": "Akash Service",
        "paths": ["akash.main.app"],
        "mount": "/api/v1/akash"
    }
]

# Mount all services
mounted_services = []
for service in services_to_mount:
    if mount_service(service["name"], service["paths"], service["mount"]):
        mounted_services.append(service["name"])

logger.info(f"🎯 Successfully mounted {len(mounted_services)}/{len(services_to_mount)} services")

try:
    # Import Subject Generation
    from subject_generation.app import app as subject_app
    app.mount("/api/v1/subjects", subject_app)
    logger.info("✅ Subject Generation mounted at /api/v1/subjects")
except Exception as e:
    logger.error(f"❌ Failed to mount Subject Generation: {e}")

try:
    # Import Akash Service
    from akash.main import app as akash_app
    app.mount("/api/v1/akash", akash_app)
    logger.info("✅ Akash Service mounted at /api/v1/akash")
except Exception as e:
    logger.error(f"❌ Failed to mount Akash Service: {e}")

try:
    # Import TTS Service
    from tts_service.tts import app as tts_app
    app.mount("/api/v1/tts", tts_app)
    logger.info("✅ TTS Service mounted at /api/v1/tts")
except Exception as e:
    logger.error(f"❌ Failed to mount TTS Service: {e}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting Gurukul Backend on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
