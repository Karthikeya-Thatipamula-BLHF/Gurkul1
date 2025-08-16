#!/usr/bin/env python3
"""
Gurukul Platform - Production Health Check Script
Comprehensive health monitoring for all services
"""

import requests
import time
import sys
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message: str, status: str = "INFO"):
    """Print colored status message"""
    color = Colors.BLUE
    if status == "SUCCESS":
        color = Colors.GREEN
    elif status == "ERROR":
        color = Colors.RED
    elif status == "WARNING":
        color = Colors.YELLOW
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{color}[{status}]{Colors.END} {timestamp} - {message}")

def check_service_health(name: str, url: str, timeout: int = 10) -> Tuple[bool, str]:
    """Check if a service is healthy"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return True, f"HTTP {response.status_code}"
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def check_docker_services() -> Dict[str, bool]:
    """Check Docker container status"""
    import subprocess
    
    services = {
        "gurukul-mongodb-prod": False,
        "gurukul-redis-prod": False,
        "gurukul-backend-prod": False,
        "gurukul-frontend-prod": False,
        "gurukul-nginx-prod": False
    }
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        for line in result.stdout.split('\n')[1:]:  # Skip header
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    status = parts[1].strip()
                    if name in services:
                        services[name] = "Up" in status
                        
    except subprocess.CalledProcessError:
        print_status("Failed to check Docker services", "ERROR")
    
    return services

def main():
    """Main health check function"""
    print(f"{Colors.BOLD}🏥 Gurukul Platform - Production Health Check{Colors.END}")
    print("=" * 60)
    
    # Service endpoints to check
    services = [
        ("Frontend", "http://localhost:3000"),
        ("Backend API", "http://localhost:8000/health"),
        ("Backend Docs", "http://localhost:8000/docs"),
        ("MongoDB", "http://localhost:8000/health"),  # Backend health includes DB
        ("Redis", "http://localhost:8000/health"),    # Backend health includes Redis
    ]
    
    # Check Docker containers
    print_status("Checking Docker containers...")
    docker_services = check_docker_services()
    
    all_containers_healthy = True
    for service_name, is_running in docker_services.items():
        if is_running:
            print_status(f"✅ {service_name} is running", "SUCCESS")
        else:
            print_status(f"❌ {service_name} is not running", "ERROR")
            all_containers_healthy = False
    
    print()
    
    # Check HTTP endpoints
    print_status("Checking HTTP endpoints...")
    all_endpoints_healthy = True
    
    for service_name, url in services:
        print_status(f"Checking {service_name}...")
        is_healthy, message = check_service_health(service_name, url)
        
        if is_healthy:
            print_status(f"✅ {service_name} is healthy ({message})", "SUCCESS")
        else:
            print_status(f"❌ {service_name} is unhealthy ({message})", "ERROR")
            all_endpoints_healthy = False
    
    print()
    
    # Overall health summary
    if all_containers_healthy and all_endpoints_healthy:
        print_status("🎉 All services are healthy!", "SUCCESS")
        print()
        print(f"{Colors.GREEN}🌐 Application URLs:{Colors.END}")
        print(f"   Frontend: http://localhost:3000")
        print(f"   Backend API: http://localhost:8000")
        print(f"   API Documentation: http://localhost:8000/docs")
        print(f"   Health Check: http://localhost:8000/health")
        return 0
    else:
        print_status("⚠️ Some services are unhealthy!", "ERROR")
        print()
        print(f"{Colors.YELLOW}🔧 Troubleshooting:{Colors.END}")
        print(f"   Check logs: docker-compose -f docker-compose.production.yml logs")
        print(f"   Restart services: docker-compose -f docker-compose.production.yml restart")
        print(f"   Check status: docker-compose -f docker-compose.production.yml ps")
        return 1

if __name__ == "__main__":
    sys.exit(main())
