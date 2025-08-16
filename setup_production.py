#!/usr/bin/env python3
"""
Gurukul Platform - Production Setup Script
Automated setup and configuration for production deployment
"""

import os
import sys
import shutil
import secrets
import string
from pathlib import Path
from typing import Dict, List

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class ProductionSetup:
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

    def generate_secure_key(self, length: int = 32) -> str:
        """Generate a secure random key"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def setup_environment_file(self):
        """Setup production environment file"""
        self.print_status("Setting up production environment file...")
        
        env_template = self.backend_dir / ".env.production.template"
        env_file = self.backend_dir / ".env"
        
        if not env_template.exists():
            self.print_status("Environment template not found", "ERROR")
            return False
        
        if env_file.exists():
            backup_file = self.backend_dir / ".env.backup"
            shutil.copy2(env_file, backup_file)
            self.print_status(f"Backed up existing .env to .env.backup", "WARNING")
        
        # Read template
        template_content = env_template.read_text()
        
        # Generate secure keys
        jwt_secret = self.generate_secure_key(64)
        encryption_key = self.generate_secure_key(64)
        secret_key = self.generate_secure_key(64)
        mongo_password = self.generate_secure_key(32)
        redis_password = self.generate_secure_key(32)
        
        # Replace placeholders
        replacements = {
            "generate_secure_jwt_secret_minimum_32_characters": jwt_secret,
            "generate_secure_encryption_key_minimum_32_characters": encryption_key,
            "generate_secure_secret_key_for_sessions": secret_key,
            "generate_secure_password_here": mongo_password,
            "generate_secure_redis_password_here": redis_password,
        }
        
        production_content = template_content
        for placeholder, value in replacements.items():
            production_content = production_content.replace(placeholder, value)
        
        # Write production .env file
        env_file.write_text(production_content)
        
        self.print_status("Production environment file created", "SUCCESS")
        self.print_status("⚠️ Please update API keys and database URLs in Backend/.env", "WARNING")
        return True

    def setup_gitignore(self):
        """Setup .gitignore for security"""
        self.print_status("Setting up .gitignore...")
        
        gitignore_file = self.project_root / ".gitignore"
        
        security_entries = [
            "# Environment files",
            ".env",
            ".env.local",
            ".env.production",
            ".env.staging",
            "",
            "# Logs",
            "logs/",
            "*.log",
            "",
            "# Database",
            "*.db",
            "*.sqlite",
            "",
            "# Cache",
            "__pycache__/",
            "*.pyc",
            ".pytest_cache/",
            "node_modules/",
            "",
            "# IDE",
            ".vscode/",
            ".idea/",
            "",
            "# OS",
            ".DS_Store",
            "Thumbs.db",
            "",
            "# SSL certificates",
            "*.pem",
            "*.key",
            "*.crt",
            "",
            "# Backup files",
            "*.backup",
            "*.bak"
        ]
        
        if gitignore_file.exists():
            existing_content = gitignore_file.read_text()
        else:
            existing_content = ""
        
        # Add security entries if not present
        for entry in security_entries:
            if entry and entry not in existing_content:
                existing_content += f"\n{entry}"
        
        gitignore_file.write_text(existing_content)
        self.print_status(".gitignore updated with security entries", "SUCCESS")

    def create_ssl_directory(self):
        """Create SSL directory for certificates"""
        self.print_status("Creating SSL directory...")
        
        ssl_dir = self.project_root / "nginx" / "ssl"
        ssl_dir.mkdir(parents=True, exist_ok=True)
        
        # Create placeholder files
        readme_content = """# SSL Certificates

Place your SSL certificates in this directory:

- certificate.crt (or .pem)
- private.key
- ca_bundle.crt (if required)

For Let's Encrypt certificates:
- fullchain.pem
- privkey.pem

Make sure to update nginx configuration to use the correct certificate paths.
"""
        
        (ssl_dir / "README.md").write_text(readme_content)
        self.print_status("SSL directory created", "SUCCESS")

    def create_logs_directory(self):
        """Create logs directory"""
        self.print_status("Creating logs directory...")
        
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Create log rotation config
        logrotate_content = """# Log rotation configuration
# Place this in /etc/logrotate.d/gurukul

/path/to/gurukul/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        docker-compose -f /path/to/gurukul/docker-compose.production.yml restart nginx
    endscript
}
"""
        
        (logs_dir / "logrotate.conf").write_text(logrotate_content)
        self.print_status("Logs directory created", "SUCCESS")

    def setup_monitoring_init(self):
        """Setup MongoDB initialization scripts"""
        self.print_status("Setting up MongoDB initialization...")
        
        init_dir = self.project_root / "monitoring" / "mongodb-init"
        init_dir.mkdir(parents=True, exist_ok=True)
        
        init_script = """// MongoDB initialization script
// This script runs when MongoDB container starts for the first time

// Create application database
db = db.getSiblingDB('gurukul');

// Create collections with proper indexes
db.createCollection('users');
db.createCollection('memories');
db.createCollection('interactions');
db.createCollection('subjects');
db.createCollection('lessons');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.memories.createIndex({ "user_id": 1, "persona_id": 1 });
db.memories.createIndex({ "timestamp": -1 });
db.interactions.createIndex({ "user_id": 1, "timestamp": -1 });
db.subjects.createIndex({ "name": 1 }, { unique: true });
db.lessons.createIndex({ "subject": 1, "topic": 1 });

print("MongoDB initialization completed successfully");
"""
        
        (init_dir / "01-init.js").write_text(init_script)
        self.print_status("MongoDB initialization script created", "SUCCESS")

    def run_setup(self):
        """Run complete production setup"""
        print(f"{Colors.BOLD}🔧 Gurukul Platform - Production Setup{Colors.END}")
        print("=" * 60)
        
        setup_steps = [
            self.setup_environment_file,
            self.setup_gitignore,
            self.create_ssl_directory,
            self.create_logs_directory,
            self.setup_monitoring_init
        ]
        
        success_count = 0
        for step in setup_steps:
            try:
                if step():
                    success_count += 1
            except Exception as e:
                self.print_status(f"Setup step failed: {str(e)}", "ERROR")
        
        print("\n" + "=" * 60)
        print(f"{Colors.BOLD}📋 Setup Summary{Colors.END}")
        print("=" * 60)
        
        if success_count == len(setup_steps):
            self.print_status("✅ Production setup completed successfully!", "SUCCESS")
            print(f"\n{Colors.GREEN}🚀 Next Steps:{Colors.END}")
            print("1. Update API keys in Backend/.env")
            print("2. Configure your domain in ALLOWED_ORIGINS")
            print("3. Add SSL certificates to nginx/ssl/")
            print("4. Run: python production_readiness_check.py")
            print("5. Deploy: ./deploy_production.sh")
        else:
            self.print_status(f"⚠️ Setup completed with {len(setup_steps) - success_count} issues", "WARNING")
        
        return success_count == len(setup_steps)

def main():
    """Main setup function"""
    setup = ProductionSetup()
    return 0 if setup.run_setup() else 1

if __name__ == "__main__":
    sys.exit(main())
