#!/usr/bin/env python3
"""
Gurukul Platform - Automated Render.com Deployment Script
Comprehensive deployment automation for production-ready deployment
"""

import os
import sys
import json
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("Backend/.env")

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class RenderDeployer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.backend_dir = self.project_root / "Backend"
        self.frontend_dir = self.project_root / "new frontend"
        
    def print_status(self, message: str, status: str = "INFO"):
        """Print colored status message"""
        color = Colors.BLUE
        if status == "SUCCESS":
            color = Colors.GREEN
        elif status == "ERROR":
            color = Colors.RED
        elif status == "WARNING":
            color = Colors.YELLOW
        
        print(f"{color}[{status}]{Colors.END} {message}")

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        self.print_status("Checking deployment prerequisites...")
        
        # Check Git
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
            self.print_status("✅ Git is installed", "SUCCESS")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_status("❌ Git is not installed or not in PATH", "ERROR")
            return False
        
        # Check if we're in a git repository
        if not (self.project_root / ".git").exists():
            self.print_status("❌ Not in a Git repository", "ERROR")
            self.print_status("Initialize with: git init && git add . && git commit -m 'Initial commit'", "WARNING")
            return False
        
        # Check required files
        required_files = [
            "Backend/requirements_production.txt",
            "Backend/main.py",
            "new frontend/package.json",
            "render.yaml"
        ]
        
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                self.print_status(f"❌ Required file missing: {file_path}", "ERROR")
                return False
        
        self.print_status("✅ All prerequisites met", "SUCCESS")
        return True

    def validate_environment_variables(self) -> Dict[str, str]:
        """Validate and collect environment variables"""
        self.print_status("Validating environment variables...")
        
        required_vars = {
            "MONGODB_URI": "MongoDB connection string (MongoDB Atlas recommended)",
            "GROQ_API_KEY": "Groq API key for AI services",
            "OPENAI_API_KEY": "OpenAI API key",
            "GEMINI_API_KEY": "Google Gemini API key",
            "SUPABASE_URL": "Supabase project URL",
            "SUPABASE_KEY": "Supabase anon key"
        }
        
        env_vars = {}
        missing_vars = []
        
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value:
                missing_vars.append(f"{var}: {description}")
            else:
                env_vars[var] = value
                self.print_status(f"✅ {var} configured", "SUCCESS")
        
        if missing_vars:
            self.print_status("❌ Missing required environment variables:", "ERROR")
            for var in missing_vars:
                print(f"   • {var}")
            print("\nPlease set these environment variables before deployment.")
            return {}
        
        return env_vars

    def prepare_backend(self) -> bool:
        """Prepare backend for deployment"""
        self.print_status("Preparing backend for deployment...")
        
        # Check if requirements file exists
        req_file = self.backend_dir / "requirements_production.txt"
        if not req_file.exists():
            self.print_status("❌ requirements_production.txt not found", "ERROR")
            return False
        
        # Validate main.py
        main_file = self.backend_dir / "main.py"
        if not main_file.exists():
            self.print_status("❌ main.py not found in Backend directory", "ERROR")
            return False
        
        # Check for .env file and warn about security
        env_file = self.backend_dir / ".env"
        if env_file.exists():
            self.print_status("⚠️ .env file found - ensure it's in .gitignore", "WARNING")
        
        self.print_status("✅ Backend preparation complete", "SUCCESS")
        return True

    def prepare_frontend(self) -> bool:
        """Prepare frontend for deployment"""
        self.print_status("Preparing frontend for deployment...")
        
        # Check package.json
        package_file = self.frontend_dir / "package.json"
        if not package_file.exists():
            self.print_status("❌ package.json not found in frontend directory", "ERROR")
            return False
        
        # Validate build script
        try:
            with open(package_file) as f:
                package_data = json.load(f)
                scripts = package_data.get("scripts", {})
                
                if "build:production" not in scripts:
                    self.print_status("❌ build:production script not found in package.json", "ERROR")
                    return False
                
                if "preview" not in scripts:
                    self.print_status("❌ preview script not found in package.json", "ERROR")
                    return False
                    
        except json.JSONDecodeError:
            self.print_status("❌ Invalid package.json format", "ERROR")
            return False
        
        self.print_status("✅ Frontend preparation complete", "SUCCESS")
        return True

    def create_deployment_checklist(self) -> bool:
        """Create a deployment checklist"""
        self.print_status("Creating deployment checklist...")
        
        checklist = """
# 🚀 Render.com Deployment Checklist

## Pre-Deployment Steps
- [ ] All code committed to Git repository
- [ ] Environment variables configured
- [ ] Dependencies updated and tested
- [ ] Security review completed

## Render.com Setup Steps
1. **Create Render Account**: Sign up at https://render.com
2. **Connect GitHub**: Link your GitHub repository
3. **Create Services**: Use the render.yaml configuration
4. **Set Environment Variables**: Configure in Render dashboard
5. **Deploy**: Trigger deployment

## Required Environment Variables in Render Dashboard
- MONGODB_URI: Your MongoDB Atlas connection string
- GROQ_API_KEY: Your Groq API key
- OPENAI_API_KEY: Your OpenAI API key
- GEMINI_API_KEY: Your Google Gemini API key
- SUPABASE_URL: Your Supabase project URL
- SUPABASE_KEY: Your Supabase anon key

## Post-Deployment Verification
- [ ] Backend health check: https://your-backend.onrender.com/health
- [ ] Frontend loads: https://your-frontend.onrender.com
- [ ] API endpoints working
- [ ] Database connections established
- [ ] Authentication working

## Monitoring
- [ ] Set up Render monitoring
- [ ] Configure alerts
- [ ] Monitor logs
- [ ] Performance testing

## Troubleshooting
- Check Render logs for errors
- Verify environment variables
- Test API endpoints individually
- Check database connectivity
"""
        
        checklist_file = self.project_root / "RENDER_DEPLOYMENT_CHECKLIST.md"
        try:
            checklist_file.write_text(checklist, encoding='utf-8')
            self.print_status("✅ Deployment checklist created", "SUCCESS")
            return True
        except UnicodeEncodeError:
            # Fallback for Windows encoding issues
            checklist_simple = checklist.encode('ascii', 'ignore').decode('ascii')
            checklist_file.write_text(checklist_simple, encoding='utf-8')
            self.print_status("✅ Deployment checklist created (simplified)", "SUCCESS")
            return True

    def generate_deployment_guide(self) -> bool:
        """Generate comprehensive deployment guide"""
        self.print_status("Generating deployment guide...")
        
        guide = f"""# 🚀 Gurukul Platform - Render.com Deployment Guide

## Quick Start

### 1. Prerequisites
- Git repository with your code
- Render.com account
- Required API keys (see environment variables section)

### 2. One-Click Deployment
1. Fork/clone this repository
2. Connect to Render.com
3. Import repository
4. Configure environment variables
5. Deploy!

## Detailed Steps

### Step 1: Prepare Your Repository
```bash
# Ensure all changes are committed
git add .
git commit -m "Prepare for production deployment"
git push origin main
```

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Connect your repository

### Step 3: Configure Services
The `render.yaml` file automatically configures:
- **Backend Service**: Python web service
- **Frontend Service**: Node.js static site
- **Database**: PostgreSQL database
- **Redis**: Cache service

### Step 4: Set Environment Variables
In Render dashboard, configure these variables:

#### Backend Environment Variables
```
MONGODB_URI=your_mongodb_atlas_connection_string
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

#### Frontend Environment Variables
```
VITE_API_BASE_URL=https://your-backend.onrender.com
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Step 5: Deploy
1. Click "Deploy" in Render dashboard
2. Monitor build logs
3. Wait for deployment to complete

### Step 6: Verify Deployment
- Backend: https://your-backend.onrender.com/health
- Frontend: https://your-frontend.onrender.com

## Troubleshooting

### Common Issues
1. **Build Failures**: Check requirements.txt and package.json
2. **Environment Variables**: Verify all required vars are set
3. **Database Connection**: Check MongoDB URI format
4. **API Errors**: Verify API keys are valid

### Getting Help
- Check Render logs
- Review this deployment guide
- Contact support if needed

## Cost Optimization
- Use Render's free tier for development
- Upgrade to paid plans for production
- Monitor usage and optimize resources

## Security Best Practices
- Never commit API keys to repository
- Use environment variables for all secrets
- Enable HTTPS (automatic on Render)
- Regular security updates

---

**Your Gurukul Platform is now ready for production! 🎉**
"""
        
        guide_file = self.project_root / "RENDER_DEPLOYMENT_GUIDE.md"
        try:
            guide_file.write_text(guide, encoding='utf-8')
            self.print_status("✅ Deployment guide created", "SUCCESS")
            return True
        except UnicodeEncodeError:
            # Fallback for Windows encoding issues
            guide_simple = guide.encode('ascii', 'ignore').decode('ascii')
            guide_file.write_text(guide_simple, encoding='utf-8')
            self.print_status("✅ Deployment guide created (simplified)", "SUCCESS")
            return True

    def run_deployment_preparation(self) -> bool:
        """Run complete deployment preparation"""
        print(f"{Colors.BOLD}🚀 Gurukul Platform - Render.com Deployment Preparation{Colors.END}")
        print("=" * 70)
        
        steps = [
            ("Checking prerequisites", self.check_prerequisites),
            ("Validating environment variables", lambda: bool(self.validate_environment_variables())),
            ("Preparing backend", self.prepare_backend),
            ("Preparing frontend", self.prepare_frontend),
            ("Creating deployment checklist", self.create_deployment_checklist),
            ("Generating deployment guide", self.generate_deployment_guide)
        ]
        
        success_count = 0
        for step_name, step_func in steps:
            self.print_status(f"Running: {step_name}...")
            try:
                if step_func():
                    success_count += 1
                else:
                    self.print_status(f"❌ Failed: {step_name}", "ERROR")
            except Exception as e:
                self.print_status(f"❌ Error in {step_name}: {str(e)}", "ERROR")
        
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}📊 Deployment Preparation Summary{Colors.END}")
        print("=" * 70)
        
        if success_count == len(steps):
            self.print_status("✅ All preparation steps completed successfully!", "SUCCESS")
            print(f"\n{Colors.GREEN}🚀 Next Steps:{Colors.END}")
            print("1. Review RENDER_DEPLOYMENT_GUIDE.md")
            print("2. Set up your Render.com account")
            print("3. Configure environment variables")
            print("4. Deploy using render.yaml")
            print("5. Verify deployment health")
            return True
        else:
            self.print_status(f"⚠️ {len(steps) - success_count} steps failed", "WARNING")
            print("Please fix the issues above before deploying.")
            return False

def main():
    """Main deployment preparation function"""
    deployer = RenderDeployer()
    success = deployer.run_deployment_preparation()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
