#!/usr/bin/env python3
"""
Gurukul Platform - Production Readiness Validation
Comprehensive validation for production deployment
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class ProductionValidator:
    def __init__(self):
        self.results = {}
        self.issues = []
        self.warnings = []
        self.score = 0
        self.max_score = 0

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

    def add_score(self, points: int):
        """Add points to score"""
        self.score += points
        self.max_score += points

    def add_issue(self, issue: str):
        """Add critical issue"""
        self.issues.append(issue)
        self.max_score += 1

    def add_warning(self, warning: str):
        """Add warning"""
        self.warnings.append(warning)

    def validate_environment_file(self) -> bool:
        """Validate .env file configuration"""
        self.print_status("Validating environment configuration...")
        
        env_file = Path("Backend/.env")
        if not env_file.exists():
            self.add_issue("Backend/.env file not found")
            return False
        
        # Read .env file
        env_content = env_file.read_text()
        
        # Check for placeholder values
        placeholders = re.findall(r'your_.*_here|placeholder|changeme|example', env_content, re.IGNORECASE)
        if placeholders:
            self.add_issue(f"Found {len(placeholders)} placeholder values in .env file")
            return False
        
        # Check for required variables
        required_vars = [
            'MONGODB_URI', 'REDIS_PASSWORD', 'JWT_SECRET', 
            'GROQ_API_KEY', 'GEMINI_API_KEY', 'SUPABASE_URL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if f"{var}=" not in env_content or f"{var}=\n" in env_content:
                missing_vars.append(var)
        
        if missing_vars:
            self.add_issue(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        self.add_score(1)
        self.print_status("Environment configuration is valid", "SUCCESS")
        return True

    def validate_docker_files(self) -> bool:
        """Validate Docker configuration"""
        self.print_status("Validating Docker configuration...")
        
        required_files = [
            "Backend/Dockerfile",
            "new frontend/Dockerfile", 
            "docker-compose.yml",
            "docker-compose.production.yml"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.add_issue(f"Missing Docker files: {', '.join(missing_files)}")
            return False
        
        self.add_score(1)
        self.print_status("Docker configuration is valid", "SUCCESS")
        return True

    def validate_backend_services(self) -> bool:
        """Validate backend service structure"""
        self.print_status("Validating backend services...")
        
        backend_dir = Path("Backend")
        if not backend_dir.exists():
            self.add_issue("Backend directory not found")
            return False
        
        # Check main.py
        main_file = backend_dir / "main.py"
        if not main_file.exists():
            self.add_issue("Backend/main.py not found")
            return False
        
        # Check requirements.txt
        req_file = backend_dir / "requirements.txt"
        if not req_file.exists():
            self.add_issue("Backend/requirements.txt not found")
            return False
        
        # Check service directories
        service_dirs = [
            "Base_backend", "memory_management", "Financial_simulator",
            "subject_generation", "akash", "tts_service"
        ]
        
        missing_services = []
        for service in service_dirs:
            service_path = backend_dir / service
            if not service_path.exists():
                missing_services.append(service)
        
        if missing_services:
            self.add_warning(f"Missing service directories: {', '.join(missing_services)}")
        
        self.add_score(1)
        self.print_status("Backend services structure is valid", "SUCCESS")
        return True

    def validate_frontend(self) -> bool:
        """Validate frontend configuration"""
        self.print_status("Validating frontend configuration...")
        
        frontend_dir = Path("new frontend")
        if not frontend_dir.exists():
            self.add_issue("Frontend directory not found")
            return False
        
        # Check package.json
        package_file = frontend_dir / "package.json"
        if not package_file.exists():
            self.add_issue("Frontend package.json not found")
            return False
        
        # Check if build script exists
        try:
            with open(package_file) as f:
                package_data = json.load(f)
                if "build" not in package_data.get("scripts", {}):
                    self.add_issue("Build script not found in package.json")
                    return False
        except json.JSONDecodeError:
            self.add_issue("Invalid package.json format")
            return False
        
        self.add_score(1)
        self.print_status("Frontend configuration is valid", "SUCCESS")
        return True

    def validate_security(self) -> bool:
        """Validate security configuration"""
        self.print_status("Validating security configuration...")
        
        # Check if .env is in .gitignore
        gitignore_file = Path(".gitignore")
        if gitignore_file.exists():
            gitignore_content = gitignore_file.read_text()
            if ".env" not in gitignore_content:
                self.add_warning(".env file should be in .gitignore")
        else:
            self.add_warning(".gitignore file not found")
        
        # Check for exposed secrets in code
        sensitive_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']'
        ]
        
        for py_file in Path(".").rglob("*.py"):
            if py_file.name.startswith("."):
                continue
            try:
                content = py_file.read_text()
                for pattern in sensitive_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.add_warning(f"Potential hardcoded secret in {py_file}")
            except:
                continue
        
        self.add_score(1)
        self.print_status("Security validation completed", "SUCCESS")
        return True

    def run_validation(self) -> bool:
        """Run all validations"""
        print(f"{Colors.BOLD}🔍 Gurukul Platform - Production Readiness Check{Colors.END}")
        print("=" * 60)
        
        validations = [
            self.validate_environment_file,
            self.validate_docker_files,
            self.validate_backend_services,
            self.validate_frontend,
            self.validate_security
        ]
        
        all_passed = True
        for validation in validations:
            try:
                if not validation():
                    all_passed = False
            except Exception as e:
                self.add_issue(f"Validation error: {str(e)}")
                all_passed = False
        
        return all_passed

    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print(f"{Colors.BOLD}📊 Validation Summary{Colors.END}")
        print("=" * 60)
        
        if self.issues:
            print(f"{Colors.RED}❌ Critical Issues ({len(self.issues)}):{Colors.END}")
            for issue in self.issues:
                print(f"   • {issue}")
            print()
        
        if self.warnings:
            print(f"{Colors.YELLOW}⚠️ Warnings ({len(self.warnings)}):{Colors.END}")
            for warning in self.warnings:
                print(f"   • {warning}")
            print()
        
        score_percentage = (self.score / self.max_score * 100) if self.max_score > 0 else 0
        
        if not self.issues:
            print(f"{Colors.GREEN}✅ Production Ready! Score: {self.score}/{self.max_score} ({score_percentage:.1f}%){Colors.END}")
            print(f"{Colors.GREEN}🚀 Ready for deployment!{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Not Production Ready! Score: {self.score}/{self.max_score} ({score_percentage:.1f}%){Colors.END}")
            print(f"{Colors.RED}🛠️ Please fix critical issues before deployment{Colors.END}")

def main():
    """Main validation function"""
    validator = ProductionValidator()
    
    success = validator.run_validation()
    validator.print_summary()
    
    return 0 if success and not validator.issues else 1

if __name__ == "__main__":
    sys.exit(main())
