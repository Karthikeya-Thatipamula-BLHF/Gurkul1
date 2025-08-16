#!/usr/bin/env python3
"""
Gurukul Platform - Simple Render.com Deployment Script
Windows-compatible deployment preparation
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv("Backend/.env")

def print_status(message, status="INFO"):
    """Print status message"""
    prefix = {
        "INFO": "[INFO]",
        "SUCCESS": "[SUCCESS]", 
        "ERROR": "[ERROR]",
        "WARNING": "[WARNING]"
    }
    print(f"{prefix.get(status, '[INFO]')} {message}")

def check_prerequisites():
    """Check deployment prerequisites"""
    print_status("Checking deployment prerequisites...")
    
    # Check Git
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        print_status("Git is installed", "SUCCESS")
    except:
        print_status("Git is not installed", "ERROR")
        return False
    
    # Check if in git repo
    if not Path(".git").exists():
        print_status("Not in a Git repository", "ERROR")
        return False
    
    # Check required files
    required_files = [
        "Backend/main.py",
        "new frontend/package.json",
        "render.yaml"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print_status(f"Required file missing: {file_path}", "ERROR")
            return False
    
    print_status("All prerequisites met", "SUCCESS")
    return True

def validate_environment():
    """Validate environment variables"""
    print_status("Validating environment variables...")
    
    required_vars = [
        "MONGODB_URI",
        "GROQ_API_KEY", 
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print_status(f"{var} configured", "SUCCESS")
    
    if missing_vars:
        print_status("Missing environment variables:", "ERROR")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print_status("All environment variables configured", "SUCCESS")
    return True

def prepare_backend():
    """Prepare backend for deployment"""
    print_status("Preparing backend...")
    
    # Check main.py
    if not Path("Backend/main.py").exists():
        print_status("Backend/main.py not found", "ERROR")
        return False
    
    # Check requirements
    req_file = Path("Backend/requirements_production.txt")
    if not req_file.exists():
        print_status("Creating requirements_production.txt...", "INFO")
        # Create basic requirements file
        requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
pymongo==4.6.0
python-dotenv==1.0.0
python-multipart==0.0.6
requests==2.31.0
pydantic==2.5.0
"""
        req_file.write_text(requirements)
        print_status("requirements_production.txt created", "SUCCESS")
    
    print_status("Backend preparation complete", "SUCCESS")
    return True

def prepare_frontend():
    """Prepare frontend for deployment"""
    print_status("Preparing frontend...")
    
    package_file = Path("new frontend/package.json")
    if not package_file.exists():
        print_status("Frontend package.json not found", "ERROR")
        return False
    
    print_status("Frontend preparation complete", "SUCCESS")
    return True

def create_deployment_guide():
    """Create deployment guide"""
    print_status("Creating deployment guide...")
    
    guide = """# Gurukul Platform - Render.com Deployment Guide

## Quick Deployment Steps

### 1. Prepare Repository
```bash
git add .
git commit -m "Production deployment"
git push origin main
```

### 2. Deploy to Render.com

#### Backend Service:
1. Go to https://render.com
2. New Web Service
3. Connect GitHub repository
4. Configure:
   - Name: gurukul-backend
   - Environment: Python 3
   - Build Command: cd Backend && pip install -r requirements_production.txt
   - Start Command: cd Backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT

#### Frontend Service:
1. New Static Site
2. Connect GitHub repository  
3. Configure:
   - Name: gurukul-frontend
   - Build Command: cd "new frontend" && npm ci && npm run build
   - Publish Directory: new frontend/dist

### 3. Environment Variables

Set these in Render dashboard:

#### Backend:
```
MONGODB_URI=your_mongodb_connection_string
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=https://gurukul-frontend.onrender.com
```

#### Frontend:
```
VITE_API_BASE_URL=https://gurukul-backend.onrender.com
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
NODE_ENV=production
```

### 4. Verify Deployment

- Backend Health: https://gurukul-backend.onrender.com/health
- Frontend: https://gurukul-frontend.onrender.com
- API Docs: https://gurukul-backend.onrender.com/docs

## Troubleshooting

1. Check Render logs for errors
2. Verify environment variables
3. Test API endpoints individually
4. Check database connectivity

Your Gurukul Platform is ready for production!
"""
    
    try:
        Path("RENDER_DEPLOYMENT_GUIDE.md").write_text(guide, encoding='utf-8')
        print_status("Deployment guide created", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"Error creating guide: {e}", "ERROR")
        return False

def main():
    """Main deployment preparation"""
    print("=" * 60)
    print("Gurukul Platform - Render.com Deployment Preparation")
    print("=" * 60)
    
    steps = [
        ("Checking prerequisites", check_prerequisites),
        ("Validating environment", validate_environment),
        ("Preparing backend", prepare_backend),
        ("Preparing frontend", prepare_frontend),
        ("Creating deployment guide", create_deployment_guide)
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print_status(f"Running: {step_name}...")
        try:
            if step_func():
                success_count += 1
            else:
                print_status(f"Failed: {step_name}", "ERROR")
        except Exception as e:
            print_status(f"Error in {step_name}: {e}", "ERROR")
    
    print("\n" + "=" * 60)
    print("Deployment Preparation Summary")
    print("=" * 60)
    
    if success_count == len(steps):
        print_status("All preparation steps completed successfully!", "SUCCESS")
        print("\nNext Steps:")
        print("1. Review RENDER_DEPLOYMENT_GUIDE.md")
        print("2. Go to https://render.com and create account")
        print("3. Deploy backend and frontend services")
        print("4. Configure environment variables")
        print("5. Verify deployment")
        return True
    else:
        print_status(f"{len(steps) - success_count} steps failed", "WARNING")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
